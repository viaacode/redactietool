# -*- coding: utf-8 -*-
#
#  tests/test_mediahaven_upload.py
#
#   the subtitle upload posts the srt and its xml sidecar straight to the
#   mediahaven records endpoint. These tests pin down the multipart request we
#   send and how we read the created record back.
#

import pytest

from unittest.mock import MagicMock
from mediahaven.mediahaven import MediaHavenException

from app.services.mediahaven_api import MediahavenApi
from tests import fixtures


@pytest.fixture
def api(mocker):
    mocker.patch(
        'app.services.mediahaven_api.MediahavenApi.__init__',
        lambda self, session=None: None
    )
    mh_api = MediahavenApi()
    mh_api.client = MagicMock()
    mh_api.client.records._construct_path.return_value = 'records'
    return mh_api


@pytest.fixture
def tp(tmp_path):
    params = fixtures.sub_params()
    (tmp_path / params['srt_file']).write_text(
        '1\n00:00:00,000 --> 00:00:01,000\nhallo\n', encoding='utf-8')
    return params


def created_record(external_id=None):
    return {
        'Descriptive': {'OriginalFilename': 'qsf7664p39_closed.srt'},
        'Internal': {
            'FragmentId': 'f' * 96,
            'MediaObjectId': 'f' * 64,
            'ArchiveStatus': 'in_progress',
        },
        'Administrative': {
            'OrganisationName': 'testbeeld',
            'ExternalId': external_id,
        },
        'Dynamic': {'PID': 'qsf7664p39_closed'},
    }


def test_upload_subtitle_posts_srt_and_sidecar(api, tp, tmp_path):
    api.client._post.return_value = created_record()
    sidecar = fixtures.subtitle_sidecar()

    result = api.upload_subtitle(str(tmp_path), tp, sidecar)

    assert result['status'] is True
    assert result['fragment_id'] == 'f' * 96
    assert result['filename'] == 'qsf7664p39_closed.srt'
    # mediahaven only fills in the external id once the essence is really
    # there, so a fresh upload is not available for the player yet
    assert result['available'] is False
    assert result['errors'] == []

    args, kwargs = api.client._post.call_args
    assert args == ('records',)

    files = kwargs['files']
    assert set(files) == {'file', 'metadata'}

    srt_name, srt_file, srt_content_type = files['file']
    assert srt_name == 'qsf7664p39_closed.srt'
    assert srt_content_type == 'application/x-subrip'
    # the file is streamed from disk, so the handle must not outlive the call
    assert srt_file.closed

    _, metadata, metadata_content_type = files['metadata']
    # without an explicit content-type mediahaven ignores the sidecar
    assert metadata_content_type == 'application/xml'
    assert metadata == sidecar.encode('utf-8')

    assert kwargs['title'] == 'qsf7664p39_closed.srt'
    # a python bool would reach mediahaven as 'True'
    assert kwargs['publish'] == 'true'
    assert kwargs['departmentId'] == api.DEPARTMENT_ID
    # the legacy ingest is what makes dc_relations/is_verwant_aan stick
    assert kwargs['workflow'] == 'Ingest-1.0'
    # mediahaven computes the external id; sending one would make every fresh
    # upload look available before its essence landed
    assert 'externalId' not in kwargs
    assert 'ingestSpaceId' not in kwargs
    assert 'zone' not in kwargs


def test_upload_subtitle_available_once_essence_landed(api, tp, tmp_path):
    api.client._post.return_value = created_record(
        external_id='qsf7664p39_closed')

    result = api.upload_subtitle(
        str(tmp_path), tp, fixtures.subtitle_sidecar())

    assert result['available'] is True


def test_upload_subtitle_duplicate_file(api, tp, tmp_path):
    api.client._post.side_effect = MediaHavenException(
        {'message': 'file already present'}, status_code=409)

    result = api.upload_subtitle(
        str(tmp_path), tp, fixtures.subtitle_sidecar())

    assert result['status'] is False
    assert result['errors'] == ['Dit ondertitelbestand bestaat al in het MAM']


def test_upload_subtitle_without_publish_rights(api, tp, tmp_path):
    api.client._post.side_effect = MediaHavenException(
        {'message': 'forbidden'}, status_code=403)

    result = api.upload_subtitle(
        str(tmp_path), tp, fixtures.subtitle_sidecar())

    assert result['status'] is False
    assert 'Geen rechten' in result['errors'][0]


def test_upload_subtitle_other_api_error(api, tp, tmp_path):
    api.client._post.side_effect = MediaHavenException(
        {'message': 'invalid sidecar'}, status_code=400)

    result = api.upload_subtitle(
        str(tmp_path), tp, fixtures.subtitle_sidecar())

    assert result['status'] is False
    assert 'invalid sidecar' in result['errors'][0]


def test_upload_subtitle_missing_srt(api, tp, tmp_path):
    (tmp_path / tp['srt_file']).unlink()

    result = api.upload_subtitle(
        str(tmp_path), tp, fixtures.subtitle_sidecar())

    assert result['status'] is False
    assert result['errors'] == ['Ondertitelbestand kon niet gelezen worden']
    assert not api.client._post.called


def test_upload_subtitle_response_without_record(api, tp, tmp_path):
    # a 2xx without a record body leaves us nothing to show or delete
    api.client._post.return_value = True

    result = api.upload_subtitle(
        str(tmp_path), tp, fixtures.subtitle_sidecar())

    assert result['status'] is False
    assert result['errors'] == ['Onverwacht antwoord van het MAM']


# ===================== srt url lookup via the api ===========================


def pool(role='ARCHIVE', online=True, original=None, cluster_group='mob_castor'):
    return {
        'ClusterGroup': cluster_group,
        'Role': role,
        'Online': online,
        'PathToPreview': None,
        'PathToOriginal': original,
    }


def path_to_original(base_url=None, identifier='a' * 64):
    return {
        'IdentifierPath': identifier,
        'FilePath': f"{identifier}.srt",
        'ExternalBaseUrl': base_url,
    }


def test_subtitle_original_path_from_storage_pools(api):
    api.client._get.return_value = MagicMock(
        json=MagicMock(return_value=[
            # the browse pool only carries a keyframe
            pool(original=None, cluster_group='browse'),
            pool(original=path_to_original()),
        ])
    )

    location = api.subtitle_original_path('f' * 96)

    assert location == {
        'base_url': None,
        'identifier_path': 'a' * 64,
        'file_path': f"{'a' * 64}.srt",
    }
    path, _accept_format = api.client._get.call_args[0]
    assert path == f"records/{'f' * 96}/storage"


def test_subtitle_original_path_prefers_archived_pool(api):
    api.client._get.return_value = MagicMock(
        json=MagicMock(return_value=[
            pool(role='TRANSIENT', original=path_to_original(
                identifier='t' * 64), cluster_group='mob'),
            pool(role='ARCHIVE', original=path_to_original(
                identifier='a' * 64)),
        ])
    )

    assert api.subtitle_original_path(
        'f' * 96)['identifier_path'] == 'a' * 64


def test_subtitle_original_path_uses_external_base_url(api):
    api.client._get.return_value = MagicMock(
        json=MagicMock(return_value=[
            pool(original=path_to_original(
                base_url='https://media.example/viaa/ORG/')),
        ])
    )

    assert api.subtitle_original_path(
        'f' * 96)['base_url'] == 'https://media.example/viaa/ORG/'


def test_subtitle_original_path_without_stored_original(api):
    # a subtitle whose ingest never completed has no original anywhere
    api.client._get.return_value = MagicMock(
        json=MagicMock(return_value=[pool(original=None)]))

    assert api.subtitle_original_path('f' * 96) is None


def test_subtitle_original_path_api_error(api):
    # mediahaven answers 400 for record types it has no storage view on
    api.client._get.side_effect = MediaHavenException(
        {'Message': 'Record is not a data object'}, status_code=400)

    assert api.subtitle_original_path('f' * 96) is None


# ============ only a mediahaven url needs our authorized session ============


def test_essence_session_for_api_url(api):
    api.client.grant._get_session.return_value = 'oauth-session'

    assert api.essence_session(
        f"{api.API_SERVER}/records/x/representations") == 'oauth-session'


def test_essence_session_for_object_store_url(api):
    assert api.essence_session(
        'https://archief-media-qas.viaa.be/viaa/ORG/abc/abc.srt') is None
    assert not api.client.grant._get_session.called
