from pydantic import ValidationError
from src.integrations.loopback_api import DownloadRequest, DownloadJobStore, DownloadStatus, QueueFullError
import unittest

class LoopbackAPITests(unittest.TestCase):
    def test_valid_uri_accepted(self):
        valid_track_uri = {"uri": "spotify:track:4uLU6hMCjMI75M1A2tKUQC"}
        validated_model = DownloadRequest.model_validate(valid_track_uri)

        self.assertEqual(validated_model.uri, valid_track_uri["uri"])

    def test_unsupported_uri_rejected(self):
        valid_track_uri = {"uri": "spotify:artist:4uLU6hMCjMI75M1A2tKUQC"}
        self.assertRaises(ValidationError, DownloadRequest.model_validate, valid_track_uri)

    def test_extra_field_rejected(self):
        self.assertRaises(ValidationError, DownloadRequest.model_validate, {"uri": "spotify:track:4uLU6hMCjMI75M1A2tKUQC", "unexpected": 1234})

    def test_non_string_uri_rejected(self):
        self.assertRaises(ValidationError, DownloadRequest.model_validate, {"uri": None})


class DownloadJobStoreTests(unittest.TestCase):
    def test_new_job(self):
        job, created = DownloadJobStore().enqueue("spotify:track:4uLU6hMCjMI75M1A2tKUQC")

        self.assertEqual(created, True)
        self.assertEqual(job.uri, "spotify:track:4uLU6hMCjMI75M1A2tKUQC")
        self.assertEqual(job.status, DownloadStatus.QUEUED)
        self.assertIsNotNone(job.request_id)

    def test_duplicate_active_job(self):
        store = DownloadJobStore(max_queued_jobs=1)
        job, created = store.enqueue("spotify:track:4uLU6hMCjMI75M1A2tKUQC")
        job2, created2 = store.enqueue("spotify:track:4uLU6hMCjMI75M1A2tKUQC")

        self.assertEqual(created, True)
        self.assertEqual(created2, False)
        self.assertEqual(job.request_id, job2.request_id)

    def test_full_queue(self):
        store = DownloadJobStore(max_queued_jobs=1)

        job, created = store.enqueue("spotify:track:4uLU6hMCjMI75M1A2tKUQC")

        self.assertEqual(created, True)
        with self.assertRaises(QueueFullError):
            store.enqueue("spotify:album:5qUp79PAejWMSXh0l04Zy9")

    def test_empty_store(self):
        store = DownloadJobStore(max_queued_jobs=1)
        empty = store.take_next()

        self.assertIsNone(empty)

    def test_claim_oldest(self):
        store = DownloadJobStore()
        job, created = store.enqueue("spotify:track:4uLU6hMCjMI75M1A2tKUQC")
        job2, created2 = store.enqueue("spotify:album:5qUp79PAejWMSXh0l04Zy9")

        job_updated = job.updated_at

        take_next = store.take_next()

        self.assertIsNotNone(take_next)
        self.assertEqual(job.request_id, take_next.request_id)
        self.assertEqual(take_next.status, DownloadStatus.PREVIEWING)
        self.assertGreaterEqual(take_next.updated_at, job_updated)

        take_next2 = store.take_next()

        self.assertIsNone(take_next2)

    def test_completion_releases_new_job(self):
        store = DownloadJobStore()
        job, created = store.enqueue("spotify:track:4uLU6hMCjMI75M1A2tKUQC")
        job2, created2 = store.enqueue("spotify:album:5qUp79PAejWMSXh0l04Zy9")

        take_next = store.take_next()

        store.update_active_job(job.request_id, DownloadStatus.DOWNLOADING)

        self.assertEqual(job.status, DownloadStatus.DOWNLOADING)

        store.take_next()

        take = store.take_next()

        self.assertIsNone(take)

        store.update_active_job(job.request_id, DownloadStatus.COMPLETED)

        job.successful_count = 1
        job.failed_count = 0

        self.assertEqual(job.status, DownloadStatus.COMPLETED)
        self.assertEqual(job.successful_count, 1)
        self.assertEqual(job.failed_count, 0)

        take_next2 = store.take_next()

        self.assertEqual(take_next2.status, DownloadStatus.PREVIEWING)

    def test_failure_store_error(self):
        store = DownloadJobStore()
        job, created = store.enqueue("spotify:track:4uLU6hMCjMI75M1A2tKUQC")
        job2, created2 = store.enqueue("spotify:album:5qUp79PAejWMSXh0l04Zy9")

        store.take_next()

        store.update_active_job(job.request_id, DownloadStatus.FAILED)
        job.failed_count = 1
        job.error = "Testing Failed Song"

        self.assertEqual(job.status, DownloadStatus.FAILED)
        self.assertEqual(job.error, "Testing Failed Song")
        self.assertEqual(job.failed_count, 1)

        store.take_next()

        self.assertEqual(job2.status, DownloadStatus.PREVIEWING)

    def test_invalid_transition(self):
        store = DownloadJobStore()
        job, created = store.enqueue("spotify:track:4uLU6hMCjMI75M1A2tKUQC")

        store.take_next()

        with self.assertRaises(ValueError):
            store.update_active_job(request_id=job.request_id, status=DownloadStatus.PREVIEWING)

        self.assertEqual(job.status, DownloadStatus.PREVIEWING)
