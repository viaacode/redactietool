#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  app/services/pending_subtitles_service.py
#
#   CRUD service for the 'pending_subtitles' table in the Postgres database.
#   Stores subtitle content when metadata is saved but the item is not yet
#   published, so the SRT can be uploaded later without the user re-selecting
#   the file.
#

import os

import psycopg2
import psycopg2.extras


class PendingSubtitlesService:
    CONNECTION_STRING = os.environ.get('POSTGRES_CONNECTIONSTRING', '')

    def _connect(self):
        return psycopg2.connect(self.CONNECTION_STRING)

    def save(self, department: str, pid: str, subtitle_type: str,
             srt_filename: str, srt_content: str) -> dict:
        """Upsert a pending subtitle row (insert or replace on conflict)."""
        sql = """
            INSERT INTO pending_subtitles
                (department, pid, subtitle_type, srt_filename, srt_content)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (department, pid) DO UPDATE SET
                subtitle_type = EXCLUDED.subtitle_type,
                srt_filename  = EXCLUDED.srt_filename,
                srt_content   = EXCLUDED.srt_content,
                created_at    = NOW()
            RETURNING *
        """
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, (department, pid, subtitle_type,
                                  srt_filename, srt_content))
                row = cur.fetchone()
                conn.commit()
                return dict(row)

    def get(self, department: str, pid: str) -> dict | None:
        """Return a pending subtitle row or None."""
        sql = "SELECT * FROM pending_subtitles WHERE department = %s AND pid = %s"
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, (department, pid))
                row = cur.fetchone()
                return dict(row) if row else None

    def delete(self, department: str, pid: str) -> bool:
        """Remove a pending subtitle once it has been uploaded."""
        sql = "DELETE FROM pending_subtitles WHERE department = %s AND pid = %s"
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (department, pid))
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted

    def rehydrate_to_disk(self, department: str, pid: str,
                          upload_folder: str) -> dict | None:
        """Fetch pending subtitle from DB, write SRT to disk, return a tp dict.

        The returned dict is compatible with the file-based pipeline
        (move_subtitle -> save_sidecar_xml -> FtpUploader).
        Returns None if no pending subtitle found.
        """
        row = self.get(department, pid)
        if not row:
            return None

        srt_filename = f"{pid}.srt"
        srt_path = os.path.join(upload_folder, srt_filename)
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(row['srt_content'])

        return {
            'pid': pid,
            'department': department,
            'subtitle_type': row['subtitle_type'],
            'srt_file': srt_filename,
        }
