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
        username = os.environ["MEDIAHAVEN_USER"]
        password = os.environ.get('MEDIAHAVEN_PASS', 'password')
        client_id = os.environ["MEDIAHAVEN_CLIENT"]
        client_secret = os.environ["MEDIAHAVEN_SECRET"]
        grant = ROPCGrant(self.API_SERVER, client_id, client_secret)

        # Request a token
        try:
            grant.request_token(username, password)
        except RequestTokenError as e:
            logger.error(f"MediaHaven token error: {e}")

        self.client = MediaHaven(self.API_SERVER, grant)

    # TODO: check if this now works

    def delete_fragment(self, frag_id):
        # del_url = f"{self.API_SERVER}/resources/media/{frag_id}"
        # del_resp = self.session.delete(
        #     url=del_url,
        #     auth=(self.api_user(department), self.API_PASSWORD)
        # )
        del_url = f"delete_resource/{frag_id}"

        # what should we put for reason and event type here???
        del_resp = self.client.delete(
            del_url, Reason="reason", EventType="subtype")

        logger.info(
            "deleted old subtitle fragment",
            data={
                'fragment': frag_id,
                'del_response': del_resp
            }
        )

    def delete_old_subtitle(self, department, subtitle_file):
        items = self.client.records.search(
            q=f"+(originalFileName:{subtitle_file})")
        if items.total_nr_of_results >= 1:
            frag_id = items[0].Internal.FragmentId
            self.delete_fragment(frag_id)

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

    # TODO: convert call
    def send_subtitles(self, upload_folder, metadata, tp):
        # sends srt_file and xml_file to mediahaven
        send_url = f"{self.API_SERVER}/resources/media/"
        srt_path = os.path.join(upload_folder, tp['srt_file'])
        xml_path = os.path.join(upload_folder, tp['xml_file'])

        file_fields = {
            'file': (tp['srt_file'], open(srt_path, 'rb')),
            'metadata': (tp['xml_file'], open(xml_path, 'rb')),
            'externalId': ('', f"{metadata['externalId']}_{tp['subtitle_type']}"),
            'departmentId': ('', self.DEPARTMENT_ID),
            'autoPublish': ('', 'true')
        }

        logger.info("posting subtitles to mam", data=file_fields)
        response = self.session.post(
            url=send_url,
            auth=(self.api_user(tp['department']), self.API_PASSWORD),
            files=file_fields,
        )

        return response.json()

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

    # TODO: update call
    def update_metadata(self, department, fragment_id, external_id, xml_sidecar):
        send_url = f"{self.API_SERVER}/resources/media/{fragment_id}"
        # logger.info("syncing metadata to mediahaven...", data=xml_sidecar)
        logger.info(
            "Syncing fragment to mediahaven with sidecar post:", data=send_url)

        file_fields = {
            'metadata': ('metadata.xml', xml_sidecar),
            'externalId': ('', f"{external_id}"),
            'departmentId': ('', self.DEPARTMENT_ID),
            'autoPublish': ('', 'true')
        }

        response = self.session.post(
            url=send_url,
            auth=(self.api_user(department), self.API_PASSWORD),
            files=file_fields,
        )

        return response

    # below two methods are extra helpers only used by maintenance scripts
    # def get_object(self, object_id, department='testbeeld'):
    #     return self.get_proxy(department, f"/resources/media/{object_id}")

    # def list_videos(self, department='testbeeld'):
    #     matched_videos = self.list_objects(
    #         department, search=f"%2B(DepartmentName:{department})")
    #     return matched_videos
