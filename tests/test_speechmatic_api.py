# -*- coding: utf-8 -*-
#
#  tests/test_speechmatic_api.py
#
#   Unit tests for SpeechmaticsApi. All HTTP calls are mocked.
#

from unittest.mock import MagicMock, patch

from app.services.speechmatic_api import SpeechmaticsApi


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_api(monkeypatch, api_key='test-key', base_url='https://eu1.asr.api.speechmatics.com'):
    monkeypatch.setenv('SPEECHMATIC_API_KEY', api_key)
    monkeypatch.setenv('SPEECHMATIC_BASE_URL', base_url)
    return SpeechmaticsApi()


def _mock_response(json_data, raise_for_status=False):
    resp = MagicMock()
    resp.json.return_value = json_data
    if raise_for_status:
        resp.raise_for_status.side_effect = Exception('HTTP Error')
    return resp


# ---------------------------------------------------------------------------
# _headers
# ---------------------------------------------------------------------------

class TestHeaders:
    def test_returns_bearer_authorization(self, monkeypatch):
        api = _make_api(monkeypatch, api_key='secret-key')
        assert api._headers() == {'Authorization': 'Bearer secret-key'}

    def test_empty_key_gives_empty_bearer(self, monkeypatch):
        api = _make_api(monkeypatch, api_key='')
        assert api._headers() == {'Authorization': 'Bearer '}


# ---------------------------------------------------------------------------
# launch_job
# ---------------------------------------------------------------------------

class TestLaunchJob:
    def test_returns_job_id_from_response(self, monkeypatch):
        api = _make_api(monkeypatch)
        resp = _mock_response({'id': 'job-abc-123'})
        with patch('app.services.speechmatic_api.requests.post', return_value=resp):
            job_id = api.launch_job('https://media.example.com/video.mp4', language='nl')
        assert job_id == 'job-abc-123'

    def test_posts_to_correct_url(self, monkeypatch):
        api = _make_api(monkeypatch, base_url='https://eu1.asr.api.speechmatics.com')
        resp = _mock_response({'id': 'job-1'})
        with patch('app.services.speechmatic_api.requests.post', return_value=resp) as mock_post:
            api.launch_job('https://media.example.com/video.mp4')
        assert mock_post.call_args[0][0] == 'https://eu1.asr.api.speechmatics.com/v2/jobs'

    def test_default_language_is_nl(self, monkeypatch):
        api = _make_api(monkeypatch)
        resp = _mock_response({'id': 'job-1'})
        import json as _json
        with patch('app.services.speechmatic_api.requests.post', return_value=resp) as mock_post:
            api.launch_job('https://media.example.com/video.mp4')
        # The config is sent as a multipart file field
        files_arg = mock_post.call_args[1].get('files') or mock_post.call_args[0][1] if len(mock_post.call_args[0]) > 1 else mock_post.call_args[1]['files']
        config_json = files_arg['config'][1]
        config = _json.loads(config_json)
        assert config['transcription_config']['language'] == 'nl'

    def test_custom_language_is_forwarded(self, monkeypatch):
        api = _make_api(monkeypatch)
        resp = _mock_response({'id': 'job-en'})
        import json as _json
        with patch('app.services.speechmatic_api.requests.post', return_value=resp) as mock_post:
            api.launch_job('https://media.example.com/video.mp4', language='en')
        files_arg = mock_post.call_args[1]['files']
        config = _json.loads(files_arg['config'][1])
        assert config['transcription_config']['language'] == 'en'


# ---------------------------------------------------------------------------
# get_job_status
# ---------------------------------------------------------------------------

class TestGetJobStatus:
    def test_returns_status_string(self, monkeypatch):
        api = _make_api(monkeypatch)
        resp = _mock_response({'job': {'status': 'running'}})
        with patch('app.services.speechmatic_api.requests.get', return_value=resp):
            status = api.get_job_status('job-xyz')
        assert status == 'running'

    def test_calls_correct_url(self, monkeypatch):
        api = _make_api(monkeypatch, base_url='https://eu1.asr.api.speechmatics.com')
        resp = _mock_response({'job': {'status': 'done'}})
        with patch('app.services.speechmatic_api.requests.get', return_value=resp) as mock_get:
            api.get_job_status('my-job-id')
        assert mock_get.call_args[0][0] == 'https://eu1.asr.api.speechmatics.com/v2/jobs/my-job-id'

    def test_done_status(self, monkeypatch):
        api = _make_api(monkeypatch)
        resp = _mock_response({'job': {'status': 'done'}})
        with patch('app.services.speechmatic_api.requests.get', return_value=resp):
            assert api.get_job_status('j') == 'done'


# ---------------------------------------------------------------------------
# get_job_result
# ---------------------------------------------------------------------------

class TestGetJobResult:
    def test_returns_full_response(self, monkeypatch):
        api = _make_api(monkeypatch)
        expected = {'results': [], 'summary': {'content': 'test'}, 'chapters': []}
        resp = _mock_response(expected)
        with patch('app.services.speechmatic_api.requests.get', return_value=resp):
            result = api.get_job_result('job-abc')
        assert result == expected

    def test_calls_transcript_endpoint(self, monkeypatch):
        api = _make_api(monkeypatch, base_url='https://eu1.asr.api.speechmatics.com')
        resp = _mock_response({})
        with patch('app.services.speechmatic_api.requests.get', return_value=resp) as mock_get:
            api.get_job_result('job-abc')
        assert mock_get.call_args[0][0] == 'https://eu1.asr.api.speechmatics.com/v2/jobs/job-abc/transcript'

    def test_deleted_job_raises_http_error(self, monkeypatch):
        """Real API returns 404 {"code":404,"detail":"Job deleted by user","error":"Job not found"}."""
        import requests as req
        api = _make_api(monkeypatch)
        mock_response = MagicMock()
        mock_response.text = '{"code":404,"detail":"Job deleted by user","error":"Job not found"}'
        resp = MagicMock()
        resp.raise_for_status.side_effect = req.HTTPError('404', response=mock_response)
        with patch('app.services.speechmatic_api.requests.get', return_value=resp):
            try:
                api.get_job_result('deleted-job')
                assert False, 'Expected HTTPError'
            except req.HTTPError:
                pass

    def test_path_not_found_raises_http_error(self, monkeypatch):
        """Real API returns 404 {"code":404,"error":"Path not found"} for unknown job ids."""
        import requests as req
        api = _make_api(monkeypatch)
        mock_response = MagicMock()
        mock_response.text = '{"code":404,"error":"Path not found"}'
        resp = MagicMock()
        resp.raise_for_status.side_effect = req.HTTPError('404', response=mock_response)
        with patch('app.services.speechmatic_api.requests.get', return_value=resp):
            try:
                api.get_job_result('unknown-job')
                assert False, 'Expected HTTPError'
            except req.HTTPError:
                pass


# ---------------------------------------------------------------------------
# list_jobs
# ---------------------------------------------------------------------------

class TestListJobs:
    def test_returns_list_of_jobs(self, monkeypatch):
        api = _make_api(monkeypatch)
        resp = _mock_response({'jobs': [{'id': 'j1'}, {'id': 'j2'}]})
        with patch('app.services.speechmatic_api.requests.get', return_value=resp):
            jobs = api.list_jobs()
        assert len(jobs) == 2
        assert jobs[0]['id'] == 'j1'

    def test_returns_empty_list_when_no_jobs(self, monkeypatch):
        api = _make_api(monkeypatch)
        resp = _mock_response({'jobs': []})
        with patch('app.services.speechmatic_api.requests.get', return_value=resp):
            assert api.list_jobs() == []


# ---------------------------------------------------------------------------
# delete_job
# ---------------------------------------------------------------------------

class TestDeleteJob:
    def test_calls_delete_endpoint(self, monkeypatch):
        api = _make_api(monkeypatch, base_url='https://eu1.asr.api.speechmatics.com')
        resp = MagicMock()
        with patch('app.services.speechmatic_api.requests.delete', return_value=resp) as mock_del:
            api.delete_job('job-to-delete')
        assert mock_del.call_args[0][0] == 'https://eu1.asr.api.speechmatics.com/v2/jobs/job-to-delete'

    def test_raises_for_http_error(self, monkeypatch):
        import requests as req
        api = _make_api(monkeypatch)
        mock_response = MagicMock()
        mock_response.text = '{"code":404,"detail":"Job deleted by user","error":"Job not found"}'
        resp = MagicMock()
        resp.raise_for_status.side_effect = req.HTTPError('404', response=mock_response)
        resp.text = 'Not found'
        with patch('app.services.speechmatic_api.requests.delete', return_value=resp):
            try:
                api.delete_job('missing-job')
            except req.HTTPError:
                pass  # expected


# ---------------------------------------------------------------------------
# parse_result (static, no mocking needed)
# ---------------------------------------------------------------------------

class TestParseResult:
    def test_extracts_summary(self):
        raw = {'results': [], 'summary': {'content': 'A brief summary.'}, 'chapters': []}
        result = SpeechmaticsApi.parse_result(raw)
        assert result['summary'] == 'A brief summary.'

    def test_extracts_chapters_with_all_fields(self):
        raw = {
            'results': [],
            'summary': {'content': ''},
            'chapters': [
                {'title': 'Intro', 'summary': 'Opening', 'start_time': 0.0, 'end_time': 120.0},
                {'title': 'Main', 'summary': 'Main part', 'start_time': 120.0, 'end_time': 600.0},
            ],
        }
        result = SpeechmaticsApi.parse_result(raw)
        assert len(result['chapters']) == 2
        assert result['chapters'][0] == {'title': 'Intro', 'summary': 'Opening', 'start_time': 0.0, 'end_time': 120.0}
        assert result['chapters'][1]['start_time'] == 120.0

    def test_missing_summary_key_returns_empty_string(self):
        raw = {'results': [], 'chapters': []}
        result = SpeechmaticsApi.parse_result(raw)
        assert result['summary'] == ''

    def test_missing_chapters_key_returns_empty_list(self):
        raw = {'results': [], 'summary': {'content': 'x'}}
        result = SpeechmaticsApi.parse_result(raw)
        assert result['chapters'] == []

    def test_transcription_key_present(self):
        raw = {'results': [], 'summary': {'content': ''}, 'chapters': []}
        result = SpeechmaticsApi.parse_result(raw)
        assert 'transcription' in result


# ---------------------------------------------------------------------------
# build_transcript (static, no mocking needed)
# ---------------------------------------------------------------------------

class TestBuildTranscript:
    def _word(self, content, speaker='S1'):
        return {'type': 'word', 'alternatives': [{'content': content, 'speaker': speaker}]}

    def _punct(self, content, speaker='S1'):
        return {'type': 'punctuation', 'alternatives': [{'content': content, 'speaker': speaker}]}

    def test_empty_events_returns_empty_string(self):
        assert SpeechmaticsApi.build_transcript([]) == ''

    def test_single_speaker_words(self):
        events = [self._word('Hello'), self._word('world')]
        transcript = SpeechmaticsApi.build_transcript(events)
        assert 'S1: Hello world' in transcript

    def test_punctuation_attached_without_space(self):
        events = [self._word('Hello'), self._punct('.')]
        transcript = SpeechmaticsApi.build_transcript(events)
        assert 'Hello.' in transcript

    def test_speaker_change_creates_new_line(self):
        events = [self._word('Yes', 'S1'), self._word('No', 'S2')]
        lines = SpeechmaticsApi.build_transcript(events).splitlines()
        assert len(lines) == 2
        assert lines[0].startswith('S1:')
        assert lines[1].startswith('S2:')

    def test_multiple_words_same_speaker(self):
        events = [self._word('One'), self._word('two'), self._word('three')]
        transcript = SpeechmaticsApi.build_transcript(events)
        assert transcript == 'S1: One two three'

    def test_realistic_multispeaker_snippet(self):
        """Snippet taken from a real Speechmatics API response (job s3kabc1hln)."""
        def w(content, speaker):
            return {'type': 'word', 'alternatives': [{'content': content, 'speaker': speaker}]}

        def p(content, speaker):
            return {'type': 'punctuation', 'alternatives': [{'content': content, 'speaker': speaker}]}

        events = [
            # S1: "Bij Albert."
            w('Bij', 'S1'), w('Albert', 'S1'), p('.', 'S1'),
            # S3: "Stoor ik?"
            w('Stoor', 'S3'), w('ik', 'S3'), p('?', 'S3'),
            # S2: "Nee, nee nee nee."
            w('Nee', 'S2'), p(',', 'S2'), w('nee', 'S2'), w('nee', 'S2'), w('nee', 'S2'), p('.', 'S2'),
            # S3: "Kom binnen Albert, het gaat druk worden als we van boord komen."
            w('Kom', 'S3'), w('binnen', 'S3'), w('Albert', 'S3'), p(',', 'S3'),
            w('het', 'S3'), w('gaat', 'S3'), w('druk', 'S3'), w('worden', 'S3'),
            w('als', 'S3'), w('we', 'S3'), w('van', 'S3'), w('boord', 'S3'), w('komen', 'S3'), p('.', 'S3'),
        ]
        lines = SpeechmaticsApi.build_transcript(events).splitlines()
        assert lines[0] == 'S1: Bij Albert.'
        assert lines[1] == 'S3: Stoor ik?'
        assert lines[2] == 'S2: Nee, nee nee nee.'
        assert lines[3] == 'S3: Kom binnen Albert, het gaat druk worden als we van boord komen.'
