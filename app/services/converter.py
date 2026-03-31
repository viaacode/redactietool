#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  app/services/converter.py
#
#   Service that exchanges a media path for a temporary playback URL (ticket)
#   via the meemoo ticket service. Used to generate short-lived URLs that are
#   then passed to the Speechmatics API for transcription.
#
# Required environment variables:
#   TICKET_SERVICE_URL          - Base URL of the ticket service
#                                 e.g. https://ticket-service.hetarchief.be
#   TICKET_SERVICE_CERT         - Path to the client certificate PEM file
#                                 e.g. /app/certs/client.crt.pem
#   TICKET_SERVICE_KEY_PATH     - Path to the (encrypted) private key PEM file
#                                 e.g. /app/certs/client.key.pem
#   TICKET_SERVICE_PASSPHRASE   - Passphrase protecting the private key
#   TICKET_SERVICE_MAX_AGE      - Token validity in seconds (default: 3600)
#   TICKET_SERVICE_HOST         - Default referer/host when none is provided
#                                 by the caller
#

import os
import ssl

import requests
from requests.adapters import HTTPAdapter
from viaa.configuration import ConfigParser
from viaa.observability import logging

config = ConfigParser()
logger = logging.get_logger(__name__, config=config)

_LOCALHOST_IPS = {'::1', '::ffff:127.0.0.1', '127.0.0.1'}


def _resolve_public_ip() -> str:
    """Return the machine's public IPv4 address, used when the client IP is localhost."""
    try:
        return requests.get('https://api.ipify.org', timeout=5).text.strip()
    except Exception:
        return '127.0.0.1'


class _MtlsAdapter(HTTPAdapter):
    """HTTPAdapter that injects a pre-built SSLContext for mutual TLS."""

    def __init__(self, ssl_context: ssl.SSLContext, **kwargs):
        self._ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self._ssl_context
        super().init_poolmanager(*args, **kwargs)


class ConverterService:

    def __init__(self):
        self.base_url = os.environ.get('TICKET_SERVICE_URL', '').rstrip('/')
        self.cert_path = os.environ.get('TICKET_SERVICE_CERT_PATH', '')
        self.key_path = os.environ.get('TICKET_SERVICE_KEY_PATH', '')
        self.passphrase = os.environ.get('TICKET_SERVICE_PASSPHRASE') or None
        self.max_age = int(os.environ.get('TICKET_SERVICE_MAX_AGE', '3600'))
        self.host = os.environ.get('TICKET_SERVICE_HOST', '').rstrip('/')

    def _build_session(self) -> requests.Session:
        """Create a requests.Session configured with mutual TLS."""
        ssl_context = ssl.create_default_context()
        ssl_context.load_cert_chain(
            certfile=self.cert_path,
            keyfile=self.key_path,
            password=self.passphrase,
        )
        # check if files exists
        if not os.path.isfile(self.cert_path):
            logger.error(f"Certificate file not found at {self.cert_path}")
            raise FileNotFoundError(f"Certificate file not found at {self.cert_path}")
        if not os.path.isfile(self.key_path):
            logger.error(f"Key file not found at {self.key_path}")
            raise FileNotFoundError(f"Key file not found at {self.key_path}")
        session = requests.Session()
        session.mount('https://', _MtlsAdapter(ssl_context))
        return session

    def get_ticket(self, path: str, referer: str = '', ip: str = '127.0.0.1') -> dict:
        """
        Request a temporary playback ticket for *path* from the ticket service.

        :param path:    Media path to generate a ticket for.
        :param referer: Domain of the client allowed to play the media.
                        Falls back to TICKET_SERVICE_HOST when empty.
        :param ip:      IP address of the client allowed to play the media.
                        Localhost addresses are automatically resolved to the
                        machine's public IP.
        :returns:       The ticket payload (dict) returned by the service.
        :raises requests.HTTPError: When the ticket service returns a non-2xx response.
        """
        resolved_referer = (referer or self.host).rstrip('/')

# archief-media-qas.viaa.be 
# viaa.be
# redactietool.meemoo.be
        params = {
            'app': 'hetarchief.be',
            'client': '',
            'referer': '',#resolved_referer,
            'maxage': self.max_age,
        }

        logger.info('converter: requesting ticket', data={'path': path, 'referer': resolved_referer})
        print(f"self: {self.base_url}")
        session = self._build_session()
        response = session.get(
            f'{self.base_url}/{path}',
            params=params,
            headers={'Accept': '*/*'},
            timeout=10,
        )
        response.raise_for_status()

        logger.info('converter: ticket response', data={
            'status': response.status_code,
            'url': response.url,
            'content_type': response.headers.get('Content-Type', ''),
            'body': response.text[:500],
        })
        ticket = response.json()
        logger.info('converter: ticket received', data={'path': path})
        return ticket

    def get_media_url(self, path: str, referer: str = '', ip: str = '127.0.0.1') -> str:
        """
        Returns a playback URL constructed from the ticket service base URL,
        the relative path, and the jwt token from get_ticket.

        :param path: Full media URL (https://archief-media...) or a relative path.
        :returns: URL string in the form base_url/relative_path?token=<jwt>
        """
        from urllib.parse import urlparse
        print(f"Original path: {path}")
        
        prefix_strip = os.environ.get('TICKET_SERVICE_VIDEO_PREFIX_STRIP', self.base_url).rstrip('/')
        if path.startswith(prefix_strip):
            relative_path = path.lstrip(prefix_strip).lstrip('/')
        else:
            # If the path doesn't start with the expected prefix, attempt to extract the relative path
            parsed_url = urlparse(path)
            relative_path = parsed_url.path.lstrip('/')
            
        logger.info('converter: get_media_url', data={'relative_path': relative_path})
        logger.info(f"Resolved relative ip: {ip}")
        print(f"Resolved relative path: {relative_path}")
        ticket = self.get_ticket(relative_path, referer=referer, ip=ip)
        serviceUrl = os.environ.get('MEDIA_SERVICE_URL', self.base_url).rstrip('/')
        return f"{serviceUrl}/{relative_path}?token={ticket.get('jwt', '')}"
