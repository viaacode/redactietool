#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  app/services/jobs_cron.py
#
#   Background cron job that polls Speechmatics every 5 minutes for any jobs
#   that are marked as 'done' by the status endpoint but whose results have
#   not yet been fetched and stored (processed_at IS NULL).
#

import json

from apscheduler.schedulers.background import BackgroundScheduler
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.services.jobs import JobsService
from app.services.speechmatic_api import SpeechmaticsApi

config = ConfigParser()
logger = logging.get_logger(__name__, config=config)

_scheduler = BackgroundScheduler()


def fetch_pending_results():
    """Fetch and store results for all jobs that are done but not yet processed."""
    jobs_service = JobsService()
    speechmatics_api = SpeechmaticsApi()
    try:
        pending = jobs_service.get_pending_jobs()
    except Exception as ex:
        logger.error('cron: failed to query pending jobs', data={'error': str(ex)})
        return

    if not pending:
        return

    logger.info(f'cron: processing {len(pending)} pending job(s)')

    for job in pending:
        job_id = job['id']
        speechmatic_job_id = job['speechmatic_job_id']
        logger.info('cron: fetching result', data={'job_id': job_id, 'speechmatic_job_id': speechmatic_job_id})
        try:
            result = speechmatics_api.get_job_result(speechmatic_job_id)
            jobs_service.mark_processed(
                job_id=job_id,
                transcription=json.dumps(result.get('results')),
                summary=result.get('summary', {}).get('content'),
                chapters=json.dumps(result.get('chapters')),
                status='done',
            )
            logger.info('cron: job processed successfully', data={'job_id': job_id})
        except Exception as ex:
            logger.error('cron: failed to fetch/store result', data={'job_id': job_id, 'error': str(ex)})


def start_scheduler():
    """Start the background scheduler. Safe to call multiple times (no-op if already running)."""
    if _scheduler.running:
        return
    _scheduler.add_job(
        fetch_pending_results,
        trigger='interval',
        minutes=1,
        id='fetch_pending_results',
        replace_existing=True,
    )
    _scheduler.start()
    logger.info('cron: scheduler started — polling every 1 minute')
