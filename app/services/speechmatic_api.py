#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  app/services/speechmatic_api.py
#
#   Service class to interact with the Speechmatics Batch API.
#   Reads the API key from the SPEECHMATIC_API_KEY environment variable.
#

import json
import os
from viaa.configuration import ConfigParser
from viaa.observability import logging

import requests

config = ConfigParser()
logger = logging.get_logger(__name__, config=config)


class SpeechmaticsApi:

	def __init__(self):
		self.api_key = os.environ.get('SPEECHMATIC_API_KEY', '')
		self.base_url = os.environ.get('SPEECHMATIC_BASE_URL', 'https://eu1.asr.api.speechmatics.com')
		
	def _headers(self) -> dict:
		return {"Authorization": f"Bearer {self.api_key}"}

	# ------------------------------------------------------------------
	# Public API
	# ------------------------------------------------------------------

	def launch_job(self, audio_path: str, language: str = "nl") -> str:
		"""Submit a transcription job to Speechmatics and return the job id."""
		config = {
			"type": "transcription",
			"fetch_data": {
				"url": audio_path
			},
			"transcription_config": {
				"language": language,
				# "operating_point": "enhanced",
				# "enable_entities": True
			},
			"summarization_config": {
				"summary_length": "brief",
				"content_type": "conversational"
			},
			"auto_chapters_config": {}
		}
		try:
			logger.info(f"Submitting transcription job for audio file: {audio_path} with language: {language}")
			response = requests.post(
				f"{self.base_url}/v2/jobs",
				headers=self._headers(),
				files={"config": (None, json.dumps(config), "application/json")},
			)
			# response.raise_for_status()
			job_id = response.json()["id"]
			logger.info(f"Received response from Speechmatics, job {job_id}")
			return job_id
		except requests.HTTPError as e:
			logger.exception(f"Error launching transcription job for audio {audio_path}: {e.response.text}")
			raise

	def get_job_status(self, job_id: str) -> str:
		"""Return the current status string of the transcription job *job_id*."""
		try:
			response = requests.get(
				f"{self.base_url}/v2/jobs/{job_id}",
				headers=self._headers(),
			)
			logger.info(f"Fetched job status from Speechmatics for job {job_id}")
			responseData = response.json()
			return responseData["job"]["status"]
		except requests.HTTPError as e:
			logger.exception(f"Error fetching job status for job {job_id}: {e.response.text}")
			raise

	def get_job_result(self, job_id: str) -> dict:
		"""Return the transcript result for a completed transcription job."""
		try:
			response = requests.get(
				f"{self.base_url}/v2/jobs/{job_id}/transcript",
				headers=self._headers(),
			)

			logger.info(f"Successfully fetched job result from Speechmatics for job {job_id}")
			return response.json()
		except requests.HTTPError as e:
			logger.exception(f"Error fetching job result for job {job_id}: {e.response.text}")
			raise
