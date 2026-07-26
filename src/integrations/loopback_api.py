from pydantic import BaseModel, ConfigDict, field_validator
from src.integrations.parse_protocol_url import is_supported_spotify_uri
from dataclasses import dataclass, field
from enum import Enum
from time import monotonic
from collections import deque
from threading import Lock
from uuid import uuid4


MAX_QUEUED_JOBS = 25
DEFAULT_FINISHED_JOB_RETENTION = 30 * 60


class DownloadStatus(str, Enum):
    QUEUED = "queued"
    PREVIEWING = "previewing"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


ACTIVE_DOWNLOAD_STATUSES = frozenset([DownloadStatus.QUEUED, DownloadStatus.PREVIEWING, DownloadStatus.DOWNLOADING])
ALLOWED_UPDATE_STATUSES = frozenset([DownloadStatus.DOWNLOADING, DownloadStatus.COMPLETED, DownloadStatus.FAILED])
TERMINAL_STATUSES = frozenset([DownloadStatus.COMPLETED, DownloadStatus.FAILED])


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

