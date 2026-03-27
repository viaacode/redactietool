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
    """Sync status for in-progress jobs, then fetch results for any that are done."""
    jobs_service = JobsService()
    speechmatics_api = SpeechmaticsApi()

    # Step 1: update status for all jobs that are still in-flight.
    try:
        in_flight = jobs_service.get_running_jobs()
    except Exception as ex:
        logger.error('cron: failed to query in-flight jobs', data={'error': str(ex)})
        return

    for job in in_flight:
        job_id = job['id']
        speechmatic_job_id = job['speechmatic_job_id']
        try:
            remote_status = speechmatics_api.get_job_status(speechmatic_job_id)
            if remote_status != job['status']:
                jobs_service.update_job_status(job_id, remote_status)
                logger.info('cron: updated job status', data={'job_id': job_id, 'status': remote_status})
        except Exception as ex:
            logger.error('cron: failed to fetch status', data={'job_id': job_id, 'error': str(ex)})

    # Step 2: fetch and store results for all jobs that are now done.
    try:
        pending = jobs_service.get_processable_jobs()
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
            processed_result = speechmatics_api.parse_result(result)
            jobs_service.mark_processed(
                job_id=job_id,
                transcription=processed_result.get('transcription'),
                summary=processed_result.get('summary'),
                chapters=json.dumps(processed_result.get('chapters')),
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
