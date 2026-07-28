from pydantic import BaseModel, ConfigDict, field_validator
from src.integrations.parse_protocol_url import is_supported_spotify_uri
from dataclasses import dataclass, field, replace
from enum import Enum
from time import monotonic, sleep
from collections import deque
from threading import Lock, Event, Thread
from uuid import uuid4
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.app_version import CURRENT_APP_VERSION
import uvicorn


MAX_QUEUED_JOBS = 25
DEFAULT_FINISHED_JOB_RETENTION = 30 * 60
SPOTIFY_XPUI_ORIGIN = "https://xpui.app.spotify.com"
MAX_REQUEST_BYTES = 1024


class DownloadStatus(str, Enum):
    QUEUED = "queued"
    PREVIEWING = "previewing"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


ACTIVE_DOWNLOAD_STATUSES = frozenset([DownloadStatus.QUEUED, DownloadStatus.PREVIEWING, DownloadStatus.DOWNLOADING])
ALLOWED_UPDATE_STATUSES = frozenset([DownloadStatus.DOWNLOADING, DownloadStatus.COMPLETED, DownloadStatus.FAILED])
TERMINAL_STATUSES = frozenset([DownloadStatus.COMPLETED, DownloadStatus.FAILED])
HOST = "127.0.0.1"
PORT = 18492


@dataclass
class DownloadJob:
    request_id: str
    uri: str
    status: DownloadStatus = DownloadStatus.QUEUED
    created_at: float = field(default_factory=monotonic)
    updated_at: float = field(default_factory=monotonic)
    successful_count: int = 0
    failed_count: int = 0
    error: str | None = None


class QueueFullError(RuntimeError):
    pass


class DownloadJobStore:
    def __init__(self, max_queued_jobs: int=MAX_QUEUED_JOBS, retention_seconds: float=DEFAULT_FINISHED_JOB_RETENTION):
        self._max_queued_jobs: int = max_queued_jobs
        self._retention_seconds: float = retention_seconds
        self._jobs: dict[str, DownloadJob] = {}
        self._queue: deque[str] = deque()
        self._lock = Lock()
        self._active_request_id: str | None = None

    def enqueue(self, uri: str) -> tuple[DownloadJob, bool]:
        with self._lock:
            now = monotonic()
            self._remove_expired_jobs_locked(now)

            for job in self._jobs.values():
                if job.uri == uri and job.status in ACTIVE_DOWNLOAD_STATUSES:
                    return job, False

            if len(self._queue) >= self._max_queued_jobs:
                raise QueueFullError()

            new_job = DownloadJob(request_id=uuid4().hex, uri=uri)

            self._jobs[new_job.request_id] = new_job

            self._queue.append(new_job.request_id)

            return new_job, True

    def take_next(self) -> DownloadJob | None:
        with self._lock:
            if self._active_request_id is not None:
                return None

            if not self._queue:
                return None

            oldest_request_id = self._queue.popleft()

            oldest_request = self._jobs[oldest_request_id]

            oldest_request.status = DownloadStatus.PREVIEWING

            oldest_request.updated_at = monotonic()

            self._active_request_id = oldest_request_id

            return oldest_request

    def update_active_job(self, request_id: str, status: DownloadStatus, *, successful_count: int | None = None, failed_count: int | None = None, error: str | None = None) -> DownloadJob | None:
        if status not in ALLOWED_UPDATE_STATUSES:
            raise ValueError("Status cannot be assigned by update_active_job()")

        with self._lock:
            if self._active_request_id != request_id:
                return None

            job = self._jobs[request_id]

            job.status = status

            job.updated_at = monotonic()

            if successful_count is not None:
                job.successful_count = successful_count

            if failed_count is not None:
                job.failed_count = failed_count

            job.error = error

            if status in TERMINAL_STATUSES:
                self._active_request_id = None

            return job

    def _remove_expired_jobs_locked(self, now: float) -> None:
        marked_entries = []

        for request_id, job in self._jobs.items():
            if job.status in TERMINAL_STATUSES:
                if now - job.updated_at >= self._retention_seconds:
                    marked_entries.append(request_id)

        for req_id in marked_entries:
            del self._jobs[req_id]

    def get_job(self, request_id: str) -> DownloadJob | None:
        with self._lock:
            now = monotonic()
            self._remove_expired_jobs_locked(now)

            job = self._jobs.get(request_id)

            if job is None:
                return None

            return replace(job)


class DownloadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    uri: str

    @field_validator("uri")
    @classmethod
    def uri_validator(cls, uri: str) -> str:
        is_supported = is_supported_spotify_uri(uri)

        if not is_supported:
            raise ValueError("Invalid URI")

        return uri


class HealthResponse(BaseModel):
    service: str
    status: str
    version: str


class DownloadAcceptedResponse(BaseModel):
    request_id: str
    status: DownloadStatus


class DownloadStatusResponse(BaseModel):
    request_id: str
    uri: str
    status: DownloadStatus
    successful_count: int
    failed_count: int
    error: str | None


class ActionAcceptedResponse(BaseModel):
    status: str


def create_loopback_app(store: DownloadJobStore, show_window_event: Event) -> FastAPI:
    app = FastAPI(version=CURRENT_APP_VERSION, title="myMusic")

    @app.middleware("http")
    async def request_validation(request: Request, call_next):
        if request.method != "POST" or request.url.path != "/v1/downloads":
            return await call_next(request)

        content_type = request.headers.get("content-type", "")
        media_type = content_type.split(";")[0].strip().lower()

        if media_type != "application/json":
            return JSONResponse(
                status_code=415,
                content={"detail": "Content-Type must be application/json"}
            )

        body = await request.body()
        if len(body) > MAX_REQUEST_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body exceeds 1 KB"}
            )

        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[SPOTIFY_XPUI_ORIGIN],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/v1/health", response_model=HealthResponse)
    def get_health():
        return {
            "service": "mymusic",
            "status": "ok",
            "version": CURRENT_APP_VERSION,
        }

    @app.post("/v1/downloads", response_model=DownloadAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
    def create_download(request: DownloadRequest):
        try:
            job, _created = store.enqueue(request.uri)

        except QueueFullError as error:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Download queue is full"
            ) from error

        return {
            "request_id": job.request_id,
            "status": job.status,
        }

    @app.get("/v1/downloads/{request_id}", response_model=DownloadStatusResponse)
    def get_download_status(request_id: str):
        job = store.get_job(request_id)

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Download request not found"
            )

        return {
            "request_id": job.request_id,
            "uri": job.uri,
            "status": job.status,
            "successful_count": job.successful_count,
            "failed_count": job.failed_count,
            "error": job.error,
        }

    @app.post("/v1/window/show", response_model=ActionAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
    def action_accepted_response():
        show_window_event.set()

        return {
            "status": "accepted",
        }

    return app


class LoopbackServer:
    def __init__(self, store: DownloadJobStore, show_window_event: Event):
        self._app = create_loopback_app(store, show_window_event)
        self._config = uvicorn.Config(app=self._app, host=HOST, port=PORT, log_level="warning", access_log=False, loop="asyncio", http="h11", ws="none", lifespan="off")
        self._server = uvicorn.Server(config=self._config)
        self._thread = Thread(daemon=True, target=self._server.run)

    def start(self, startup_timeout: float=5.0) -> None:
        self._thread.start()
        deadline = monotonic() + startup_timeout

        while self._thread.is_alive() and not self._server.started and monotonic() < deadline:
            sleep(0.01)

        if not self._server.started:
            self._server.should_exit = True

            if self._thread.is_alive():
                self._thread.join(2.0)

            raise RuntimeError("Unable to start the server")

    def stop(self, join_timeout: float=5.0) -> None:
        self._server.should_exit = True

        if self._thread.is_alive():
            self._thread.join(join_timeout)
