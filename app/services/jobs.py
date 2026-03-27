#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  app/services/jobs_service.py
#
#   CRUD service for the 'jobs' table in the Speechmatics Postgres database.
#   Reads the connection string from the SPEECHMATIC_CONNECTIONSTRING
#   environment variable.
#

import os
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras


class JobsService:
    CONNECTION_STRING = os.environ.get('SPEECHMATIC_CONNECTIONSTRING', '')

    def _connect(self):
        return psycopg2.connect(self.CONNECTION_STRING)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_job(self, department: str, pid: str, speechmatic_job_id: str) -> dict:
        """Insert a new job row and return the created record."""
        sql = """
            INSERT INTO jobs (department, pid, created_at, speechmatic_job_id)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, (department, pid, datetime.now(timezone.utc), speechmatic_job_id))
                row = cur.fetchone()
                conn.commit()
                return dict(row)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_job(self, department: str, pid: str) -> dict | None:
        """Return a single job by its primary key, or None if not found."""
        sql = "SELECT * FROM jobs WHERE department = %s AND pid = %s"
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, (department, pid))
                row = cur.fetchone()
                return dict(row) if row else None

    def get_job_by_speechmatic_id(self, speechmatic_job_id: str) -> dict | None:
        """Return a single job by its Speechmatics job id, or None if not found."""
        sql = "SELECT * FROM jobs WHERE speechmatic_job_id = %s"
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, (speechmatic_job_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def list_jobs(self) -> list[dict]:
        """Return all jobs ordered by creation date (newest first)."""
        sql = "SELECT * FROM jobs ORDER BY created_at DESC"
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)
                return [dict(row) for row in cur.fetchall()]

    def get_processable_jobs(self) -> list[dict]:
        """Return jobs that are marked done by Speechmatics but not yet processed."""
        sql = "SELECT * FROM jobs WHERE status = 'done' AND processed_at IS NULL"
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)
                return [dict(row) for row in cur.fetchall()]

    def get_running_jobs(self) -> list[dict]:
        """Return jobs whose status is still 'created' or 'running'."""
        sql = "SELECT * FROM jobs WHERE status IN ('created', 'running')"
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)
                return [dict(row) for row in cur.fetchall()]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update_job(self, job_id: int, **fields) -> dict | None:
        """Update arbitrary columns on a job row and return the updated record.

        Only the columns that exist on the table are accepted:
        department, pid, processed_at, speechmatic_job_id, transcription, summary.
        """
        allowed = {'department', 'pid', 'processed_at', 'speechmatic_job_id',
                   'transcription', 'summary', 'chapters', 'status'}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get_job(job_id)

        set_clause = ', '.join(f"{col} = %s" for col in updates)
        values = list(updates.values()) + [job_id]
        sql = f"UPDATE jobs SET {set_clause} WHERE id = %s RETURNING *"

        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, values)
                row = cur.fetchone()
                conn.commit()
                return dict(row) if row else None
            
    def update_job_status(self, job_id: int, status: str) -> dict | None:
        """Update the status column of a job row and return the updated record."""
        return self.update_job(job_id, status=status)
    

    def mark_processed(self, job_id: int, transcription: str, summary: str = None, chapters: str = None, status: str = 'done') -> dict | None:
        """Set processed_at, transcription and optionally summary, chapters and status on a job."""
        return self.update_job(
            job_id,
            processed_at=datetime.now(timezone.utc),
            transcription=transcription,
            summary=summary,
            chapters=chapters,
            status=status,
        )

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_job(self, job_id: int) -> bool:
        """Delete a job by its primary key. Returns True if a row was deleted."""
        sql = "DELETE FROM jobs WHERE id = %s"
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (job_id,))
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted