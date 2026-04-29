# -*- coding: utf-8 -*-
#
#  tests/test_converter.py
#
#   Unit tests for ConverterService.get_media_url.
#   get_ticket (which requires real TLS certs) is mocked via patch.object.
#

import pytest
from unittest.mock import patch

from app.services.converter import ConverterService


def _make_service(monkeypatch, base_url='https://ticket.example.com', media_service_url=None, prefix_strip=None):
    monkeypatch.setenv('TICKET_SERVICE_URL', base_url)
    monkeypatch.setenv('TICKET_SERVICE_CERT_PATH', '/fake/cert.pem')
    monkeypatch.setenv('TICKET_SERVICE_KEY_PATH', '/fake/key.pem')
    monkeypatch.delenv('TICKET_SERVICE_PASSPHRASE', raising=False)
    if media_service_url:
        monkeypatch.setenv('MEDIA_SERVICE_URL', media_service_url)
    else:
        monkeypatch.delenv('MEDIA_SERVICE_URL', raising=False)
    if prefix_strip:
        monkeypatch.setenv('TICKET_SERVICE_VIDEO_PREFIX_STRIP', prefix_strip)
    else:
        monkeypatch.delenv('TICKET_SERVICE_VIDEO_PREFIX_STRIP', raising=False)
    return ConverterService()


class TestGetMediaUrl:
    def test_returned_url_contains_jwt_token(self, monkeypatch):
        service = _make_service(monkeypatch, media_service_url='https://media.example.com')
        with patch.object(service, 'get_ticket', return_value={'jwt': 'my-jwt-token'}):
            url = service.get_media_url('https://other.host.com/viaa/path/video.mp4')
        assert 'token=my-jwt-token' in url

    def test_returned_url_uses_media_service_url(self, monkeypatch):
        service = _make_service(monkeypatch, media_service_url='https://media.example.com')
        with patch.object(service, 'get_ticket', return_value={'jwt': 'tok'}):
            url = service.get_media_url('https://other.host.com/path/video.mp4')
        assert url.startswith('https://media.example.com/')

    def test_strips_configured_prefix_from_path(self, monkeypatch):
        base = 'https://ticket.example.com'
        service = _make_service(monkeypatch, base_url=base, prefix_strip=base)
        with patch.object(service, 'get_ticket', return_value={'jwt': 'tok'}) as mock_ticket:
            service.get_media_url(f'{base}/path/to/video.mp4')
            
        called_path = mock_ticket.call_args[0][0]
        assert called_path == 'path/to/video.mp4'

    def test_falls_back_to_url_path_when_prefix_not_matched(self, monkeypatch):
        service = _make_service(
            monkeypatch,
            base_url='https://ticket.example.com',
            prefix_strip='https://ticket.example.com',
        )
        with patch.object(service, 'get_ticket', return_value={'jwt': 'tok'}) as mock_ticket:
            service.get_media_url('https://archief-media.viaa.be/viaa/TESTBEELD/video.mp4')
        called_path = mock_ticket.call_args[0][0]
        # The relative path should be extracted from the URL path
        assert 'viaa/TESTBEELD/video.mp4' in called_path

    def test_empty_jwt_produces_empty_token_param(self, monkeypatch):
        service = _make_service(monkeypatch, media_service_url='https://media.example.com')
        with patch.object(service, 'get_ticket', return_value={}):
            url = service.get_media_url('https://other.com/path/video.mp4')
        assert 'token=' in url

    def test_get_ticket_receives_relative_path(self, monkeypatch):
        """get_ticket should never receive absolute URLs — only relative paths."""
        service = _make_service(
            monkeypatch,
            base_url='https://ticket.example.com',
            prefix_strip='https://ticket.example.com',
        )
        with patch.object(service, 'get_ticket', return_value={'jwt': 'tok'}) as mock_ticket:
            service.get_media_url('https://ticket.example.com/media/clip.mp4')
        called_path = mock_ticket.call_args[0][0]
        assert not called_path.startswith('http')
