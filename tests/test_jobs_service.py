# -*- coding: utf-8 -*-
#
#  tests/test_jobs_service.py
#
#   Unit tests for JobsService. psycopg2 is fully mocked so no real DB is needed.
#

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.jobs import JobsService


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

JOB_ROW = {
    'id': 1,
    'department': 'vrt',
    'pid': 'abc123',
    'speechmatic_job_id': 'sm-job-1',
    'status': 'created',
    'created_at': datetime(2026, 1, 1, tzinfo=timezone.utc),
    'processed_at': None,
    'transcription': None,
    'summary': None,
    'chapters': None,
}


def _mock_conn(fetchone=None, fetchall=None, rowcount=1):
    """Return a mock psycopg2 connection + cursor that behaves as context managers."""
    cur = MagicMock()
    cur.__enter__ = lambda s: cur
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = fetchall or []
    cur.rowcount = rowcount

    conn = MagicMock()
    conn.__enter__ = lambda s: conn
    conn.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value = cur
    return conn, cur


# ---------------------------------------------------------------------------
# create_job
# ---------------------------------------------------------------------------

class TestCreateJob:
    def test_returns_created_row_as_dict(self):
        conn, _ = _mock_conn(fetchone=JOB_ROW)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().create_job('vrt', 'abc123', 'sm-job-1')
        assert result['pid'] == 'abc123'
        assert result['department'] == 'vrt'
        assert result['speechmatic_job_id'] == 'sm-job-1'

    def test_commit_is_called(self):
        conn, _ = _mock_conn(fetchone=JOB_ROW)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            JobsService().create_job('vrt', 'abc123', 'sm-1')
        conn.commit.assert_called_once()


# ---------------------------------------------------------------------------
# get_job
# ---------------------------------------------------------------------------

class TestGetJob:
    def test_returns_dict_when_row_exists(self):
        conn, _ = _mock_conn(fetchone=JOB_ROW)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().get_job('vrt', 'abc123')
        assert result['id'] == 1

    def test_returns_none_when_not_found(self):
        conn, _ = _mock_conn(fetchone=None)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().get_job('vrt', 'unknown-pid')
        assert result is None


# ---------------------------------------------------------------------------
# get_job_by_speechmatic_id
# ---------------------------------------------------------------------------

class TestGetJobBySpeechmaticId:
    def test_returns_dict_when_found(self):
        conn, _ = _mock_conn(fetchone=JOB_ROW)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().get_job_by_speechmatic_id('sm-job-1')
        assert result['speechmatic_job_id'] == 'sm-job-1'

    def test_returns_none_when_not_found(self):
        conn, _ = _mock_conn(fetchone=None)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().get_job_by_speechmatic_id('unknown')
        assert result is None


# ---------------------------------------------------------------------------
# list_jobs
# ---------------------------------------------------------------------------

class TestListJobs:
    def test_returns_all_rows(self):
        rows = [JOB_ROW, {**JOB_ROW, 'id': 2, 'pid': 'xyz789'}]
        conn, _ = _mock_conn(fetchall=rows)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().list_jobs()
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['pid'] == 'xyz789'

    def test_returns_empty_list_when_no_rows(self):
        conn, _ = _mock_conn(fetchall=[])
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().list_jobs()
        assert result == []


# ---------------------------------------------------------------------------
# get_processable_jobs
# ---------------------------------------------------------------------------

class TestGetProcessableJobs:
    def test_returns_done_unprocessed_jobs(self):
        done_row = {**JOB_ROW, 'status': 'done', 'processed_at': None}
        conn, _ = _mock_conn(fetchall=[done_row])
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().get_processable_jobs()
        assert len(result) == 1
        assert result[0]['status'] == 'done'

    def test_returns_empty_when_none(self):
        conn, _ = _mock_conn(fetchall=[])
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            assert JobsService().get_processable_jobs() == []


# ---------------------------------------------------------------------------
# get_running_jobs
# ---------------------------------------------------------------------------

class TestGetRunningJobs:
    def test_returns_created_and_running_jobs(self):
        rows = [JOB_ROW, {**JOB_ROW, 'id': 2, 'status': 'running'}]
        conn, _ = _mock_conn(fetchall=rows)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().get_running_jobs()
        assert len(result) == 2

    def test_returns_empty_when_none(self):
        conn, _ = _mock_conn(fetchall=[])
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            assert JobsService().get_running_jobs() == []


# ---------------------------------------------------------------------------
# update_job
# ---------------------------------------------------------------------------

class TestUpdateJob:
    def test_updates_status_and_returns_row(self):
        updated = {**JOB_ROW, 'status': 'done'}
        conn, _ = _mock_conn(fetchone=updated)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().update_job(1, status='done')
        assert result['status'] == 'done'

    def test_returns_none_when_row_not_found(self):
        conn, _ = _mock_conn(fetchone=None)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().update_job(999, status='done')
        assert result is None

    def test_commit_is_called(self):
        conn, _ = _mock_conn(fetchone=JOB_ROW)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            JobsService().update_job(1, status='running')
        conn.commit.assert_called_once()


# ---------------------------------------------------------------------------
# update_job_status
# ---------------------------------------------------------------------------

class TestUpdateJobStatus:
    def test_delegates_to_update_job(self):
        updated = {**JOB_ROW, 'status': 'running'}
        conn, _ = _mock_conn(fetchone=updated)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().update_job_status(1, 'running')
        assert result['status'] == 'running'


# ---------------------------------------------------------------------------
# mark_processed
# ---------------------------------------------------------------------------

class TestMarkProcessed:
    def test_sets_processed_at_and_transcription(self):
        processed = {
            **JOB_ROW,
            'status': 'done',
            'transcription': 'Full text',
            'summary': 'Summary',
            'chapters': '[]',
            'processed_at': datetime(2026, 1, 2, tzinfo=timezone.utc),
        }
        conn, _ = _mock_conn(fetchone=processed)
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            result = JobsService().mark_processed(1, transcription='Full text', summary='Summary', chapters='[]')
        assert result['status'] == 'done'
        assert result['transcription'] == 'Full text'
        assert result['processed_at'] is not None


# ---------------------------------------------------------------------------
# delete_job
# ---------------------------------------------------------------------------

class TestDeleteJob:
    def test_returns_true_when_row_deleted(self):
        conn, cur = _mock_conn()
        cur.rowcount = 1
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            assert JobsService().delete_job(1) is True

    def test_returns_false_when_not_found(self):
        conn, cur = _mock_conn()
        cur.rowcount = 0
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            assert JobsService().delete_job(999) is False

    def test_commit_is_called(self):
        conn, cur = _mock_conn()
        cur.rowcount = 1
        with patch('app.services.jobs.psycopg2.connect', return_value=conn):
            JobsService().delete_job(1)
        conn.commit.assert_called_once()
