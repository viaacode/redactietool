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
		self.base_url = os.environ.get('SPEECHMATIC_BASE_URL', '')
		if not self.base_url:
			raise ValueError("SPEECHMATIC_BASE_URL environment variable is not set")
		self.api_key = os.environ.get('SPEECHMATIC_API_KEY', '')
		if not self.api_key:
			raise ValueError("SPEECHMATIC_API_KEY environment variable is not set")
		
	def _headers(self) -> dict:
		return {"Authorization": f"Bearer {self.api_key}"}

	# ------------------------------------------------------------------
	# Public API
	# ------------------------------------------------------------------

	def launch_job(self, audio_path: str, language: str = "nl") -> str:
		"""Submit a transcription job to Speechmatics and return the job id."""
		if(audio_path is None):
			logger.error("Audio path is required to launch a transcription job")
			raise ValueError("Audio path is required to launch a transcription job")
		config = {
			"type": "transcription",
			"fetch_data": {
				"url": audio_path
			},
			"transcription_config": {
				"language": language,
    			"diarization": "speaker",
				"operating_point": "enhanced",
				# "enable_entities": True
			},
			"summarization_config": {
				"summary_length": "brief",
				"content_type": "conversational"
			},
			"auto_chapters_config": {}
		}
		try:
			logger.info(f"Submitting transcription job for media file: {audio_path} with language: {language}: {json.dumps(config)}")
			response = requests.post(
				f"{self.base_url}/v2/jobs",
				headers=self._headers(),
				files={"config": (None, json.dumps(config), "application/json")},
			)
			logger.info(f"Speechmatics launch_job response: status={response.status_code} body={response.text}")
			response.raise_for_status()
			job_id = response.json()["id"]
			logger.info(f"Speechmatics job created: {job_id}")
			return job_id
		except requests.HTTPError as e:
			logger.exception(f"Error launching transcription job for audio {audio_path}: status={e.response.status_code} body={e.response.text}")
			raise

	def get_job_status(self, job_id: str) -> tuple[str, list]:
		"""Return (status, errors) for the transcription job *job_id*."""
		if (job_id is None):
			logger.error("Job ID is required to fetch job result")
			raise ValueError("Job ID is required to fetch job result")
		try:
			response = requests.get(
				f"{self.base_url}/v2/jobs/{job_id}",
				headers=self._headers(),
			)
			logger.info(f"Speechmatics get_job_status response: job={job_id} status={response.status_code} body={response.text}")
			response.raise_for_status()
			responseData = response.json()
			job = responseData["job"]
			errors = [e.get("message", "") for e in job.get("errors", [])]
			return job["status"], errors
		except requests.HTTPError as e:
			logger.exception(f"Error fetching job status for job {job_id}: status={e.response.status_code} body={e.response.text}")
			raise

	def get_job_result(self, job_id: str) -> dict:
		"""Return the transcript result for a completed transcription job."""
		if(job_id is None):
			logger.error("Job ID is required to fetch job result")
			raise ValueError("Job ID is required to fetch job result")
		try:
			response = requests.get(
				f"{self.base_url}/v2/jobs/{job_id}/transcript",
				headers=self._headers(),
			)
			logger.info(f"Speechmatics get_job_result response: job={job_id} status={response.status_code}")
			response.raise_for_status()
			response_json = response.json()
			logger.info(f"Successfully fetched job result from Speechmatics for job {job_id}: {json.dumps(response_json)}")
			return response_json
		except requests.HTTPError as e:
			error_body = e.response.text if e.response is not None else str(e)
			logger.exception(f"Error fetching job result for job {job_id}: status={e.response.status_code if e.response is not None else 'N/A'} body={error_body}")
			raise

	def list_jobs(self) -> list:
		"""Return all jobs currently known to the Speechmatics API."""
		try:
			response = requests.get(
				f"{self.base_url}/v2/jobs",
				headers=self._headers(),
			)
			response.raise_for_status()
			return response.json().get("jobs", [])
		except requests.HTTPError as e:
			logger.exception(f"Error listing jobs from Speechmatics: {e.response.text}")
			raise

	def delete_job(self, job_id: str) -> None:
		"""Delete a job from Speechmatics by its job id."""
		try:
			response = requests.delete(
				f"{self.base_url}/v2/jobs/{job_id}",
				headers=self._headers(),
			)
			response.raise_for_status()
			logger.info(f"Deleted job {job_id} from Speechmatics")
		except requests.HTTPError as e:
			logger.exception(f"Error deleting job {job_id} from Speechmatics: {e.response.text}")
			raise

	@staticmethod
	def parse_result(raw: dict) -> dict:
		"""Parse a raw Speechmatics transcript response into structured fields.

		Returns a dict with:
		  - transcription: plain-text transcript with chapter timestamps interleaved
		  - summary:       bullet-point summary string
		  - chapters:      list of {title, summary, start_time, end_time}
		"""
		transcription = SpeechmaticsApi.build_transcript(raw.get("results") or []) \
			or "Het antwoord van Speechmatics bevatte geen transcritpie. Gelieve opnieuw te proberen."

		summary = (raw.get("summary") or {}).get("content") \
			or "Het antwoord van Speechmatics bevatte geen samenvatting. Gelieve opnieuw te proberen."

		chapters = [
			{
				"title": ch.get("title") or "Het antwoord van Speechmatics bevatte geen hoofdstukken. Gelieve opnieuw te proberen.",
				"summary": ch.get("summary") or "",
				"start_time": ch.get("start_time"),
				"end_time": ch.get("end_time"),
			}
			for ch in (raw.get("chapters") or [])
		]

		transcription = SpeechmaticsApi.build_transcript(raw.get("results", []), chapters=chapters)

		summary = raw.get("summary", {}).get("content", "")

		return {
			"transcription": transcription,
			"summary": summary,
			"chapters": chapters,
		}

	@staticmethod
	def build_transcript(events: list, chapters: list = None) -> str:
		result_lines = []

		current_speaker = None
		current_sentence = []
		current_start_time = None

		sorted_chapters = sorted(chapters or [], key=lambda c: c["start_time"])
		next_chapter_idx = 0

		def format_time(seconds: float) -> str:
			total_seconds = int(seconds)
			h = total_seconds // 3600
			m = (total_seconds % 3600) // 60
			s = total_seconds % 60
			return f"{h:02d}:{m:02d}:{s:02d}"

		def flush():
			"""Flush current sentence into result_lines, inserting chapter timestamps as needed."""
			nonlocal current_sentence, current_speaker, next_chapter_idx, current_start_time
			if current_speaker and current_sentence:
				sentence = "".join(current_sentence).strip()
				# Insert any chapter timestamps whose boundary has been reached
				while (next_chapter_idx < len(sorted_chapters) and
						current_start_time is not None and
						sorted_chapters[next_chapter_idx]["start_time"] <= current_start_time):
					if result_lines:
						result_lines.append("")
					result_lines.append(format_time(sorted_chapters[next_chapter_idx]["start_time"]))
					next_chapter_idx += 1
				result_lines.append(f"{current_speaker}: {sentence}")
			current_sentence = []
			current_start_time = None

		for event in events:
			if not event.get("alternatives"):
				continue

			alt = event["alternatives"][0]
			content = alt.get("content", "")
			speaker = alt.get("speaker", "UNKNOWN")
			event_type = event.get("type")

			# Speaker change → flush current sentence
			if current_speaker is None:
				current_speaker = speaker
			elif speaker != current_speaker:
				flush()
				current_speaker = speaker

			if event_type == "word":
				# Capture start time of first word in the segment for chapter boundary checks
				if current_start_time is None:
					current_start_time = event.get("start_time")
				# Add space before word if needed
				if current_sentence:
					current_sentence.append(" ")
				current_sentence.append(content)

			elif event_type == "punctuation":
				# Attach punctuation directly (no preceding space)
				current_sentence.append(content)

				# If end of sentence but speaker continues, want to merge the sentences.
				# End-of-sentence → flush
				# if event.get("is_eos"):
				# 	flush()
				# 	current_speaker = None  # force new line even if same speaker continues

		# Flush any remaining text
		flush()

		return "\n".join(result_lines)
