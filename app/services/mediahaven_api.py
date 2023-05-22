#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/services/mediahaven_api.py
#
#   Make api calls to hetarchief/mediahaven
#   find video and audio fragments used to lookup video by pid and tenant
#   send_subtitles saves the srt file together with an xml sidecar
#   delete_old_subtitle used to replace existing srt with new upload
#

import os
import json
from viaa.configuration import ConfigParser
from viaa.observability import logging
from mediahaven import MediaHaven
from mediahaven.mediahaven import MediaHavenException
from mediahaven.oauth2 import ROPCGrant, RequestTokenError

logger = logging.get_logger(__name__, config=ConfigParser())


class MediahavenApi:
    API_SERVER = os.environ.get(
        'MEDIAHAVEN_API',
        'https://archief-qas.viaa.be/mediahaven-rest-api/v2'
    )

    DEPARTMENT_ID = os.environ.get(
        'DEPARTMENT_ID',
        'dd111b7a-efd0-44e3-8816-0905572421da'
    )

    # ONDERWIJS_PERM_ID is enkel voor de publicatiestatus flag
    ONDERWIJS_PERM_ID = os.environ.get(
        'ONDERWIJS_PERM_ID', 'config_onderwijs_uuid')

    def __init__(self, session=None):
        # Create a ROPC grant

        # API_USER_PREFIX = os.environ.get('MEDIAHAVEN_USER_PREFIX', 'viaa@')
        username = os.environ.get('MEDIAHAVEN_USER', 'user')
        password = os.environ.get('MEDIAHAVEN_PASS', 'password')
        client_id = os.environ.get('MEDIAHAVEN_CLIENT', 'client_id')
        client_secret = os.environ.get('MEDIAHAVEN_SECRET', 'client_secret')
        grant = ROPCGrant(self.API_SERVER, client_id, client_secret)

        # Request a token
        try:
            grant.request_token(username, password)
        except RequestTokenError as e:
            logger.error(f"MediaHaven token error: {e}")

        self.client = MediaHaven(self.API_SERVER, grant)

    def find_item_by_pid(self, department, pid):
        records = self.client.records.search(q=f"+(ExternalId:{pid})")

        if not records.total_nr_of_results > 0:
            return None

        if records.total_nr_of_results == 1:
            return json.loads(records.raw_response).get('Results', [{}])[0]
        elif records.total_nr_of_results > 1:
            # future todo, iterate them and pick a certain one to return?
            return json.loads(records.raw_response).get('Results', [{}])[1]
        else:
            return None

    def get_publicatiestatus(self, department, pid):
        records = self.client.records.search(q=f"+(ExternalId:{pid})")
        if records.total_nr_of_results < 1:
            return False

        permissions = records[0].RightsManagement.Permissions.Read
        return self.ONDERWIJS_PERM_ID in permissions

    def get_subtitles(self, department, pid):
        matched_subs = self.client.records.search(
            q=f"+(dc_relationsis_verwant_aan:{pid})")
        if not matched_subs.total_nr_of_results:
            return []

        sub_response = json.loads(
            matched_subs.raw_response).get('Results', [{}])
        return sub_response

    def get_subtitle(self, department, pid, subtype):
        matched_subs = self.client.records.search(
            q=f"+(dc_relationsis_verwant_aan:{pid})")
        if not matched_subs.total_nr_of_results:
            return False

        if matched_subs.total_nr_of_results == 1:
            return json.loads(matched_subs.raw_response).get('Results', [{}])[0]
        elif matched_subs.total_nr_of_results > 1:
            all_subs = json.loads(
                matched_subs.raw_response).get('Results', [{}])
            for sub in all_subs:
                if subtype in sub.get('Descriptive').get('OriginalFilename'):
                    return sub
        else:
            return False

    def update_metadata(self, department, fragment_id, external_id, xml_sidecar):
        try:
            logger.info("syncing metadata to mediahaven...")
            return {
                'status': self.client.records.update(record_id=fragment_id, xml=xml_sidecar),
                'errors': []
            }
        except MediaHavenException as me:
            return {
                'status': False,
                'errors': [str(me)]
            }
