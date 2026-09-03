#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/services/mediahaven_api.py
#
#   Make api calls to hetarchief/mediahaven
#   find video and audio fragments used to lookup video by pid and tenant
#   upload_subtitle posts the srt file together with an xml sidecar
#   delete_subtitle used to replace existing srt with new upload
#

import os
import json
from urllib.parse import urlparse
from viaa.configuration import ConfigParser
from viaa.observability import logging
from mediahaven import MediaHaven
from mediahaven.mediahaven import DEFAULT_ACCEPT_FORMAT, MediaHavenException
from mediahaven.oauth2 import ROPCGrant, RequestTokenError

logger = logging.get_logger(__name__, config=ConfigParser())

def local_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


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

    def record_summary(self, record):
        # compact view of the fields that matter for subtitle ingest debugging
        descriptive = record.get('Descriptive', {})
        internal = record.get('Internal', {})
        dynamic = record.get('Dynamic', {})
        return {
            'original_filename': descriptive.get('OriginalFilename', ''),
            'fragment_id': internal.get('FragmentId', ''),
            'external_id': internal.get('ExternalId', ''),
            'archive_status': internal.get('ArchiveStatus', ''),
            'pid': dynamic.get('PID', ''),
            'is_verwant_aan': dynamic.get('dc_relations', {}).get('is_verwant_aan', ''),
        }

    def search_records(self, query, label, extra_data=None):
        # single place where we log what we asked mediahaven and what came back
        try:
            matched = self.client.records.search(q=query)
        except MediaHavenException as me:
            logger.error(
                f"{label} search failed",
                data={'query': query, 'error': str(me), **(extra_data or {})}
            )
            return []

        results = json.loads(matched.raw_response).get(
            'Results', []) if matched.total_nr_of_results else []

        logger.info(
            f"{label} search",
            data={
                'query': query,
                'total_nr_of_results': matched.total_nr_of_results,
                'records': [self.record_summary(r) for r in results],
                **(extra_data or {}),
            }
        )
        return results

    def get_subtitles(self, department, pid):
        sub_response = self.search_records(
            f"+(dc_relationsis_verwant_aan:{pid})",
            'get_subtitles',
            {'pid': pid}
        )
        return sub_response

    def subtitle_files(self, department, pid):
        # compact list used by the edit page and the polling endpoint.
        # a half ingested record (mediahaven wrote the row but the srt never
        # landed in the object store) has no Administrative.ExternalId, while
        # it still reports ArchiveStatus on_disk. Such a record cannot be
        # served as webvtt, so flag it instead of pretending it is there.
        files = []
        for sub in self.get_subtitles(department, pid):
            files.append({
                'filename': sub.get('Descriptive', {}).get('OriginalFilename', ''),
                'fragment_id': sub.get('Internal', {}).get('FragmentId', ''),
                'available': sub.get('Administrative', {}).get('ExternalId') is not None,
            })
        return files

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

    def subtitle_original_path(self, record_id):
        """Ask mediahaven where the srt of a subtitle record is stored.

        The record itself holds no url for it: a data record like an srt gets
        no browse, and its preview fields point at a keyframe image. The
        storage pools of the record do know the identifier and the filename of
        the original, so we read those instead of assuming the filename
        matches the media object id.

        The pool that holds the original has no ExternalBaseUrl of its own, so
        the caller combines this with the object store base url. Returns None
        when mediahaven has no stored original for us (yet).
        """
        try:
            pools = self.client._get(
                f"records/{record_id}/storage", DEFAULT_ACCEPT_FORMAT).json()
        except MediaHavenException as me:
            logger.error(
                'could not fetch subtitle storage pools',
                data={'record_id': record_id, 'error': str(me)}
            )
            return None

        original_pool = self.pick_original_pool(pools)
        logger.info(
            'subtitle storage pools',
            data={
                'record_id': record_id,
                'pools': [
                    {
                        'cluster_group': pool.get('ClusterGroup'),
                        'role': pool.get('Role'),
                        'online': pool.get('Online'),
                        'path_to_original': pool.get('PathToOriginal'),
                    }
                    for pool in pools
                ],
                'picked_role': original_pool.get(
                    'Role') if original_pool else None,
            }
        )
        if not original_pool:
            return None

        original = original_pool['PathToOriginal']
        return {
            'base_url': original.get('ExternalBaseUrl'),
            'identifier_path': original.get('IdentifierPath'),
            'file_path': original.get('FilePath'),
        }

    def pick_original_pool(self, pools):
        # an archived pool that is online is the one serving the file; a
        # subtitle whose ingest never completed only has a transient pool
        candidates = [
            pool for pool in pools
            if isinstance(pool, dict)
            and (pool.get('PathToOriginal') or {}).get('FilePath')
            and (pool.get('PathToOriginal') or {}).get('IdentifierPath')
        ]
        if not candidates:
            return None

        return sorted(
            candidates,
            key=lambda pool: (
                pool.get('Role') != 'ARCHIVE',
                not pool.get('Online'),
            )
        )[0]

    def essence_session(self, url):
        # a representation url served by the api itself needs our oauth
        # session, a signed object store url is fetched anonymously
        if urlparse(url).netloc != urlparse(self.API_SERVER).netloc:
            return None

        try:
            return self.client.grant._get_session()
        except Exception as e:
            logger.warning(
                'no authorized session for essence url',
                data={'url': url, 'error': str(e)}
            )
            return None

    def upload_subtitle(self, upload_folder, tp, xml_sidecar):
        """Create the subtitle record with a direct multipart upload.

        This replaces the old ftp watchfolder detour: mediahaven answers with
        the created record, so we know the fragment id right away instead of
        polling the search api until the ingest shows up.
        """
        srt_path = os.path.join(upload_folder, tp['srt_file'])
        form_data = {
            'title': tp['srt_file'],
            # requests would send a python bool as 'True'
            'publish': 'true',
            'departmentId': self.DEPARTMENT_ID,
            # the watchfolder ran the legacy ingest, and that is what makes
            # dc_relations/is_verwant_aan stick. Every subtitle lookup we do
            # searches on that relation, so keep using it.
            'workflow': 'Ingest-1.0',
            # no externalId on purpose: mediahaven computes it, and
            # subtitle_files() reads its presence as "the essence landed"
        }

        logger.info(
            "uploading subtitle to mediahaven...",
            data={
                'pid': tp['pid'],
                'subtitle_type': tp['subtitle_type'],
                'srt_file': tp['srt_file'],
                'srt_bytes': local_size(srt_path),
                'api_server': self.API_SERVER,
                **form_data,
            }
        )

        try:
            with open(srt_path, 'rb') as srt_file:
                record = self.client._post(
                    self.client.records._construct_path(),
                    files={
                        'file': (
                            tp['srt_file'], srt_file, 'application/x-subrip'),
                        # the sidecar only gets a content-type of its own when
                        # it is sent as a file part, and without that
                        # content-type mediahaven ignores the metadata
                        'metadata': (
                            'sidecar.xml',
                            xml_sidecar.encode('utf-8'),
                            'application/xml'),
                    },
                    **form_data
                )
        except MediaHavenException as me:
            return self.upload_failed(self.upload_error_message(me), tp, xml_sidecar, me)
        except OSError as oe:
            return self.upload_failed(
                'Ondertitelbestand kon niet gelezen worden', tp, xml_sidecar, oe)

        fragment_id = record.get('Internal', {}).get(
            'FragmentId', '') if isinstance(record, dict) else ''
        if not fragment_id:
            # a 2xx without a record body leaves us with nothing to address,
            # so don't report a synced subtitle we cannot show or delete
            return self.upload_failed(
                'Onverwacht antwoord van het MAM', tp, xml_sidecar, record)

        logger.info(
            'subtitle created in mediahaven',
            data={'pid': tp['pid'], 'record': self.record_summary(record)}
        )

        return {
            'status': True,
            'record': record,
            'fragment_id': fragment_id,
            'filename': record.get('Descriptive', {}).get(
                'OriginalFilename') or tp['srt_file'],
            # mediahaven only fills in the external id once the essence is
            # really there, see subtitle_files()
            'available': record.get(
                'Administrative', {}).get('ExternalId') is not None,
            'errors': [],
        }

    def upload_failed(self, message, tp, xml_sidecar, error):
        logger.error(
            'subtitle upload to mediahaven failed',
            data={
                'pid': tp['pid'],
                'subtitle_type': tp['subtitle_type'],
                'srt_file': tp['srt_file'],
                'error': str(error),
                # the sidecar decides whether the subtitle gets linked to the
                # video, so log it when something went wrong
                'xml_sidecar': xml_sidecar,
            }
        )
        return {
            'status': False,
            'record': None,
            'fragment_id': '',
            'filename': tp['srt_file'],
            'available': False,
            'errors': [message],
        }

    def upload_error_message(self, mh_exception):
        status_code = getattr(mh_exception, 'status_code', None)
        if status_code == 409:
            return 'Dit ondertitelbestand bestaat al in het MAM'
        if status_code == 403:
            return 'Geen rechten om dit ondertitelbestand op te laden in het MAM'
        return str(mh_exception)

    def delete_subtitle(self, fragment_id):
        try:
            logger.info("deleting subtitle from mediahaven...", data={'fragment_id': fragment_id})
            self.client.records.delete(fragment_id)
            return {
                'status': True,
                'errors': []
            }
        except MediaHavenException as me:
            return {
                'status': False,
                'errors': [str(me)]
            }

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
