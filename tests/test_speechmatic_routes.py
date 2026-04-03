# -*- coding: utf-8 -*-
#
#  tests/test_speechmatic_routes.py
#
#   Integration tests for the three Speechmatics Flask routes.
#   All service classes (JobsService, SpeechmaticsApi, MediahavenApi, ConverterService)
#   are mocked so no real DB or HTTP calls are made.
#

import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# POST /speechmatic/generate
# ---------------------------------------------------------------------------

class TestGenerateTranscript:
    URL = '/speechmatic/generate'

    def _post(self, client, data):
        return client.post(self.URL, data=json.dumps(data), content_type='application/json')

    def test_unauthenticated_redirects(self, client):
        res = self._post(client, {'pid': 'abc', 'department': 'vrt'})
        assert res.status_code == HTTPStatus.FOUND

    def test_missing_pid_returns_400(self, auth_client):
        res = self._post(auth_client, {'department': 'vrt'})
        assert res.status_code == HTTPStatus.BAD_REQUEST

    def test_missing_department_returns_400(self, auth_client):
        res = self._post(auth_client, {'pid': 'abc123'})
        assert res.status_code == HTTPStatus.BAD_REQUEST

    def test_pid_not_found_in_mediahaven_returns_404(self, auth_client):
        with patch('app.redactietool.MediahavenApi') as MockMH, \
             patch('app.redactietool.JobsService') as MockJobs:
            MockMH.return_value.find_item_by_pid.return_value = None
            MockJobs.return_value.get_job.return_value = None
            res = self._post(auth_client, {'pid': 'unknown', 'department': 'vrt'})
        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_pending_job_already_exists_returns_409(self, auth_client):
        mam_data = {'Internal': {'PathToVideo': 'https://media.example.com/vid.mp4'}}
        pending_job = {'id': 1, 'status': 'running', 'processed_at': None, 'speechmatic_job_id': 'sm-1'}
        with patch('app.redactietool.MediahavenApi') as MockMH, \
             patch('app.redactietool.JobsService') as MockJobs:
            MockMH.return_value.find_item_by_pid.return_value = mam_data
            MockJobs.return_value.get_job.return_value = pending_job
            res = self._post(auth_client, {'pid': 'abc', 'department': 'vrt'})
        assert res.status_code == HTTPStatus.CONFLICT

    def test_completed_job_returns_409(self, auth_client):
        mam_data = {'Internal': {'PathToVideo': 'https://media.example.com/vid.mp4'}}
        done_job = {'id': 1, 'status': 'done', 'processed_at': '2026-01-01', 'speechmatic_job_id': 'sm-1'}
        with patch('app.redactietool.MediahavenApi') as MockMH, \
             patch('app.redactietool.JobsService') as MockJobs:
            MockMH.return_value.find_item_by_pid.return_value = mam_data
            MockJobs.return_value.get_job.return_value = done_job
            res = self._post(auth_client, {'pid': 'abc', 'department': 'vrt'})
        assert res.status_code == HTTPStatus.CONFLICT

    def test_no_video_url_in_mam_data_returns_404(self, auth_client):
        mam_data = {'Internal': {}}
        with patch('app.redactietool.MediahavenApi') as MockMH, \
             patch('app.redactietool.JobsService') as MockJobs:
            MockMH.return_value.find_item_by_pid.return_value = mam_data
            MockJobs.return_value.get_job.return_value = None
            res = self._post(auth_client, {'pid': 'abc', 'department': 'vrt'})
        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_converter_failure_returns_500(self, auth_client):
        mam_data = {'Internal': {'PathToVideo': 'https://media.example.com/vid.mp4'}}
        with patch('app.redactietool.MediahavenApi') as MockMH, \
             patch('app.redactietool.JobsService') as MockJobs, \
             patch('app.redactietool.ConverterService') as MockConverter:
            MockMH.return_value.find_item_by_pid.return_value = mam_data
            MockJobs.return_value.get_job.return_value = None
            MockConverter.return_value.get_media_url.return_value = None
            res = self._post(auth_client, {'pid': 'abc', 'department': 'vrt'})
        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_success_creates_new_job_and_returns_job_id(self, auth_client):
        mam_data = {'Internal': {'PathToVideo': 'https://media.example.com/video.mp4'}}
        with patch('app.redactietool.MediahavenApi') as MockMH, \
             patch('app.redactietool.JobsService') as MockJobs, \
             patch('app.redactietool.ConverterService') as MockConverter, \
             patch('app.redactietool.SpeechmaticsApi') as MockSM:
            MockMH.return_value.find_item_by_pid.return_value = mam_data
            MockJobs.return_value.get_job.return_value = None
            MockConverter.return_value.get_media_url.return_value = 'https://media.example.com/video.mp4?token=tok'
            MockSM.return_value.launch_job.return_value = 'new-sm-job-id'
            MockJobs.return_value.create_job.return_value = {'id': 1}
            res = self._post(auth_client, {'pid': 'abc', 'department': 'vrt', 'language': 'nl'})
        assert res.status_code == HTTPStatus.OK
        data = res.get_json()
        assert data['job_id'] == 'new-sm-job-id'
        assert data['pid'] == 'abc'
        assert data['department'] == 'vrt'

    def test_success_updates_existing_expired_job(self, auth_client):
        """A previously expired/rejected job should be re-submitted and updated."""
        mam_data = {'Internal': {'PathToVideo': 'https://media.example.com/video.mp4'}}
        expired_job = {'id': 1, 'status': 'expired', 'processed_at': '2026-01-01', 'speechmatic_job_id': 'old-sm'}
        with patch('app.redactietool.MediahavenApi') as MockMH, \
             patch('app.redactietool.JobsService') as MockJobs, \
             patch('app.redactietool.ConverterService') as MockConverter, \
             patch('app.redactietool.SpeechmaticsApi') as MockSM:
            MockMH.return_value.find_item_by_pid.return_value = mam_data
            MockJobs.return_value.get_job.return_value = expired_job
            MockConverter.return_value.get_media_url.return_value = 'https://media.example.com/video.mp4?token=tok'
            MockSM.return_value.launch_job.return_value = 'new-sm-id'
            MockJobs.return_value.update_job.return_value = {**expired_job, 'speechmatic_job_id': 'new-sm-id'}
            res = self._post(auth_client, {'pid': 'abc', 'department': 'vrt'})
        assert res.status_code == HTTPStatus.OK


# ---------------------------------------------------------------------------
# GET /<department>/<pid>/speechmatic/status
# ---------------------------------------------------------------------------

class TestTranscriptionStatus:
    def _url(self, dept='vrt', pid='abc123'):
        return f'/{dept}/{pid}/speechmatic/status'

    def test_unauthenticated_redirects(self, client):
        res = client.get(self._url())
        assert res.status_code == HTTPStatus.FOUND

    def test_job_not_found_returns_404(self, auth_client):
        with patch('app.redactietool.JobsService') as MockJobs, \
             patch('app.redactietool.SpeechmaticsApi'):
            MockJobs.return_value.get_job.return_value = None
            res = auth_client.get(self._url())
        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_processed_job_returns_status_from_db_without_calling_api(self, auth_client):
        job = {'id': 1, 'speechmatic_job_id': 'sm-1', 'status': 'done', 'processed_at': '2026-01-01'}
        with patch('app.redactietool.JobsService') as MockJobs, \
             patch('app.redactietool.SpeechmaticsApi') as MockSM:
            MockJobs.return_value.get_job.return_value = job
            res = auth_client.get(self._url())
        assert res.status_code == HTTPStatus.OK
        data = res.get_json()
        assert data['status'] == 'done'
        MockSM.return_value.get_job_status.assert_not_called()

    def test_unprocessed_job_fetches_status_from_speechmatics(self, auth_client):
        job = {'id': 1, 'speechmatic_job_id': 'sm-1', 'status': 'created', 'processed_at': None}
        with patch('app.redactietool.JobsService') as MockJobs, \
             patch('app.redactietool.SpeechmaticsApi') as MockSM:
            MockJobs.return_value.get_job.return_value = job
            MockSM.return_value.get_job_status.return_value = 'running'
            res = auth_client.get(self._url())
        assert res.status_code == HTTPStatus.OK
        data = res.get_json()
        assert data['status'] == 'running'

    def test_unprocessed_job_updates_status_in_db(self, auth_client):
        job = {'id': 1, 'speechmatic_job_id': 'sm-1', 'status': 'created', 'processed_at': None}
        with patch('app.redactietool.JobsService') as MockJobs, \
             patch('app.redactietool.SpeechmaticsApi') as MockSM:
            MockJobs.return_value.get_job.return_value = job
            MockSM.return_value.get_job_status.return_value = 'done'
            auth_client.get(self._url())
        MockJobs.return_value.update_job_status.assert_called_once_with(1, 'done')


# ---------------------------------------------------------------------------
# GET /<department>/<pid>/speechmatic/result
# ---------------------------------------------------------------------------

class TestTranscriptionResult:
    def _url(self, dept='vrt', pid='abc123'):
        return f'/{dept}/{pid}/speechmatic/result'

    def test_unauthenticated_redirects(self, client):
        res = client.get(self._url())
        assert res.status_code == HTTPStatus.FOUND

    def test_job_not_found_returns_404(self, auth_client):
        with patch('app.redactietool.JobsService') as MockJobs:
            MockJobs.return_value.get_job.return_value = None
            res = auth_client.get(self._url())
        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_not_yet_processed_returns_200_with_message(self, auth_client):
        job = {'id': 1, 'status': 'running', 'processed_at': None}
        with patch('app.redactietool.JobsService') as MockJobs:
            MockJobs.return_value.get_job.return_value = job
            res = auth_client.get(self._url())
        assert res.status_code == HTTPStatus.OK
        data = res.get_json()
        assert 'message' in data
        assert data['status'] == 'running'

    def test_processed_job_returns_full_result(self, auth_client):
        job = {
            'id': 1,
            'status': 'done',
            'processed_at': '2026-01-01T00:00:00',
            'transcription': 'Full transcript text',
            'summary': 'Brief summary',
            'chapters': [{'title': 'Ch1', 'start_time': 0, 'end_time': 300}],
        }
        with patch('app.redactietool.JobsService') as MockJobs:
            MockJobs.return_value.get_job.return_value = job
            res = auth_client.get(self._url())
        assert res.status_code == HTTPStatus.OK
        data = res.get_json()
        assert data['transcript'] == 'Full transcript text'
        assert data['summary'] == 'Brief summary'
        assert data['status'] == 'done'
        assert len(data['chapters']) == 1
