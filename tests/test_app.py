# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_app.py
#

import pytest
import io
import os
import json

from unittest.mock import MagicMock
from http import HTTPStatus
from app.redactietool import app


@pytest.fixture(scope="module")
def setup():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'subtitle_uploads'
    yield setup


def decompress_response(response):
    import gzip
    import io

    body = response["body"]["string"]
    # Detect gzip magic header
    # Since we upgraded urllib3 from v1 to v2 responses are automatically decompressed,
    # but we use the python VCR library to record and store network calls, so the tests execute faster.
    # But those recordings were made with urllib3 v1 in compressed format.
    # So now we need to decompress them to match the urllib3 v2 format.
    if body.startswith(b"\x1f\x8b\x08"):
        try:
            response["body"]["string"] = gzip.decompress(body)
        except Exception:
            pass
    return response

@pytest.fixture(scope="module")
def vcr_config():
    # important to add the filter_headers here to avoid exposing credentials
    # in tests/cassettes!
    return {
        "before_record_response": decompress_response,
        "record_mode": "once",
        "preserve_exact_body_bytes": True,
        "filter_headers": ["authorization"]
    }


def test_home(client):
    res = client.get('/')
    assert res.status_code == HTTPStatus.OK
    assert b'Inloggen' in res.data


def test_liveness_check(client):
    res = client.get('/health/live')

    assert res.data == b'OK'
    assert res.status_code == HTTPStatus.OK


def test_search_media_security(client):
    res = client.get('/search_media')
    # assert res.status_code == 401  # unauthorized

    # with flask-login this auto redirects to login now with a 302
    assert res.status_code == HTTPStatus.FOUND  # redirects to login


def test_search_media(auth_client):
    with auth_client.session_transaction() as session:
        session['samlUserdata']['cn'] = ['Test user']
        session['samlUserdata']['apps'] = ['mediahaven']

    res = auth_client.get("/search_media")
    assert res.status_code == HTTPStatus.OK


def test_invalid_pid_entry(auth_client):
    res = auth_client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': 'abc123#'
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'PID formaat foutief' in res.data.decode()


def test_empty_pid(auth_client):
    res = auth_client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': ''
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'Geef een PID' in res.data.decode()


@pytest.mark.vcr
def test_wrong_pid_entry(auth_client):
    res = auth_client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': 'abc123'
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'PID niet gevonden in testbeeld' in res.data.decode()


@pytest.mark.skip(reason="requires PostgreSQL connection")
@pytest.mark.vcr
def test_working_pid_search(auth_client):
    res = auth_client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': 'qsxs5jbm5c',
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'Algemene metadata' in res.data.decode()


def test_invalid_long_pid_entry(auth_client):
    res = auth_client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': 'abc123'*40
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'PID te lang' in res.data.decode()


def test_invalid_department_entry(auth_client):
    res = auth_client.post("/search_media", data={
        'department': 'testbeeld%^',
        'pid': 'abc123'
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'Department formaat foutief' in res.data.decode()


def test_invalid_long_department(auth_client):
    res = auth_client.post("/search_media", data={
        'department': 'testbeeld_te_lang'*40,
        'pid': 'abc123'
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'department te lang' in res.data.decode()


@pytest.mark.skip(reason="returns 302 instead of 200")
@pytest.mark.vcr
def test_subtitle_videoplayer_route(auth_client):
    res = auth_client.get('/subtitles/qsxs5jbm5c.vtt')
    assert res.status_code == HTTPStatus.OK


@pytest.mark.vcr
def test_subtitle_videoplayer_route_unknownfile(client):
    res = client.get('/subtitles/someinvalidpath.vtt')
    assert res.status_code == HTTPStatus.FOUND  # redirects to 404 page


@pytest.mark.vcr
def test_edit_metadata_wrong_pid(auth_client):
    res = auth_client.get(
        "/edit_metadata?pid=somewrongpid&department=testbeeld",
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK
    assert 'Zoek een item op' in res.data.decode()
    assert 'niet gevonden' in res.data.decode()


@pytest.mark.skip(reason="requires PostgreSQL connection")
@pytest.mark.vcr
def test_edit_metadata_working_pid(auth_client):
    res = auth_client.get(
        "/edit_metadata?pid=qs5d8ncx8c&department=testbeeld",
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK
    assert 'Algemene metadata' in res.data.decode()


@pytest.mark.vcr
def test_subtitles_on_metadata_edit(auth_client):
    res = auth_client.get(
        "/item_subtitles/testbeeld/qs5d8ncx8c/closed",
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK


@pytest.mark.vcr
def test_onderwijsniveaus(auth_client):
    res = auth_client.get(
        "/onderwijsniveaus",
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK


@pytest.mark.vcr
def test_onderwijsgraden(auth_client):
    res = auth_client.get(
        "/onderwijsgraden",
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK


@pytest.mark.vcr
def test_themas(auth_client):
    res = auth_client.get(
        "/themas",
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK


@pytest.mark.vcr
def test_vakken(auth_client):
    res = auth_client.get(
        "/vakken",
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK


@pytest.mark.vcr
def test_keyword_search(auth_client):
    res = auth_client.post(
        "/keyword_search",
        json={'qry': 'zoek'},
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK
    search_results = json.loads(res.data)
    assert len(search_results) >= 4
    assert search_results[0]['text'] == 'zoekactie'


@pytest.mark.vcr
def test_vakken_suggesties(auth_client):
    graden_en_themas = {
        "graden": [
            {
                "id": "https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-1e-graad",
                "label": "lager 1e graad",
                "definition": "lager 1e graad",
                "child_count": 2,
                "parent_id": "https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-onderwijs"
            }
        ],
        "themas": [
            {
                "id": "https://data.hetarchief.be/id/onderwijs/thema/klassieke-talen",
                "label": "klassieke talen",
                "definition": "Taalkunde, exclusief literatuur, voor de klassieke talen"
            },
            {
                "id": "https://data.hetarchief.be/id/onderwijs/thema/media-en-communicatie",
                "label": "media en communicatie",
                "definition": "Alles over communicatie (verbaal, non-verbaal), communicatiemiddelen en de media"
            }
        ]
    }

    res = auth_client.post(
        "/vakken_suggest",
        json=graden_en_themas,
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK
    suggesties = json.loads(res.data)
    assert len(suggesties) == 3


@pytest.mark.vcr
def test_vakken_related(auth_client):
    graden_en_niveaus = {
        "graden": [
            {
                "id": "https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-1e-graad",
                "label": "lager 1e graad",
                "definition": "lager 1e graad",
                "child_count": 2,
                "parent_id": "https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-onderwijs"
            }
        ],
        "niveaus": [
            {
                "id": "https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-onderwijs",
                "label": "lager onderwijs",
                "definition": "lager onderwijs",
                "collection": "onderwijs subniveaus",
                "child_count": 3,
                "parent_id": "https://w3id.org/onderwijs-vlaanderen/id/structuur/basisonderwijs"
            }
        ]
    }
    res = auth_client.post(
        "/vakken_related",
        json=graden_en_niveaus,
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK
    overige_vakken = json.loads(res.data)
    assert len(overige_vakken) == 12


@pytest.mark.vcr
def test_publicatie_status(auth_client):
    res = auth_client.get(
        "/publicatie_status?pid=qs5d8ncx8c&department=testbeeld",
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK
    assert 'publish_item' in res.json.keys()


@pytest.mark.vcr
def test_publicatie_status_404(auth_client):
    res = auth_client.get(
        "/publicatie_status?pid=randompid&department=testbeeld",
        follow_redirects=True
    )

    assert res.status_code == HTTPStatus.OK
    assert 'publish_item' in res.json.keys()
    assert res.json['publish_item'] is False


@pytest.mark.skip(reason="requires TICKET_SERVICE_CERT environment variable")
@pytest.mark.vcr
def test_update_metadata(auth_client):
    with open('./tests/fixture_data/edit_mam_data.json', "r") as f:
        mam_data = json.loads(f.read())

    res = auth_client.post("/edit_metadata?pid=qsf7664p39&department=testbeeld", data={
        'pid': 'qsf7664p39',
        'department': 'testbeeld',
        'mam_data': json.dumps(mam_data),
        'sm_data': json.dumps({}),
        'serie': 'Serie veld test',
        'uitzenddatum': '2021-11-21',
        'ontsluitingstitel': 'Fietsstraten in centrum Gent',
        'prd_maker_attribute': 'Maker',
        'prd_maker_value': '',
        'prd_maker_attribute_1': 'Maker',
        'prd_maker_value_1': 'maker test',
        'prd_bijdrager_attribute': 'Aanwezig',
        'prd_bijdrager_value': '',
        'prd_bijdrager_attribute_1': 'Bijdrager',
        'prd_bijdrager_value_1': 'bijdrager test2',
        'prd_publisher_attribute': 'Distributeur',
        'prd_publisher_value': '',
        'prd_publisher_attribute_1': 'Distributeur',
        'prd_publisher_value_1': 'distributeur test',
        'avo_beschrijving': 'Beschrijving test 1234',
        'lom_type': '[{"name":"Video","code":"Video"}]',
        'lom1_beoogde_eindgebruiker': '[{"name":"Student","code":"Student"}]',
        'talen': '[{"name":"Nederlands","code":"nl"}]',
        'lom_onderwijs_combo': '[]',
        'lom1_onderwijsniveaus': """
          [
            {
              "id":"https://w3id.org/onderwijs-vlaanderen/id/structuur/hoger-onderwijs",
              "label":"hoger onderwijs",
              "definition":"hoger onderwijs",
              "collection":"onderwijsniveaus",
              "child_count":0
            },
            {
              "id":"https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-onderwijs",
              "label":"lager onderwijs",
              "definition":"lager onderwijs",
              "collection":"onderwijs subniveaus",
              "child_count":3,
              "parent_id":"https://w3id.org/onderwijs-vlaanderen/id/structuur/basisonderwijs"}
            ]
        """,
        'lom1_onderwijsgraden': """
          [{
                "id":"https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-1e-graad",
                "label":"lager 1e graad",
                "definition":"lager 1e graad",
                "child_count":2,
                "parent_id":"https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-onderwijs"
          }]""",
        'themas': """
          [
            {
                "id":"https://data.hetarchief.be/id/onderwijs/thema/sport-en-spel",
                "label":"sport en spel",
                "definition":"Alles over lichaamsbeweging, (top)sport, spellen en spelen"
            }
          ]""",
        'vakken': """
          [{
            "id":"https://w3id.org/onderwijs-vlaanderen/id/vak/ict",
            "label":"ICT",
            "definition":"ICT, computationeel denken"
          }]""",
        'trefwoorden': '[{"name":"Belgium","code":"Belgium"}]'
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'werden opgeslagen' in res.data.decode()


def test_random_404(client, setup):
    resp = client.delete('/somepage')
    assert resp.status_code == HTTPStatus.FOUND
    assert resp.location.endswith("/404")

    resp = client.get('/somepage')
    assert resp.status_code == HTTPStatus.FOUND
    assert resp.location.endswith("/404")

    resp = client.post('/somepage')
    assert resp.status_code == HTTPStatus.FOUND
    assert resp.location.endswith("/404")

    resp = client.put('/somepage')
    assert resp.status_code == HTTPStatus.FOUND
    assert resp.location.endswith("/404")


# =================== Combined metadata + subtitle tests =====================


@pytest.mark.skip(reason="requires VCR cassette recording against a live MediaHaven server")
@pytest.mark.vcr
def test_edit_metadata_with_subtitle_published(auth_client, mocker):
    """POST with a valid SRT file should save metadata then FTP-upload the subtitle."""
    with open('./tests/fixture_data/edit_mam_data.json', "r") as f:
        mam_data = json.loads(f.read())

    ftp_mock = MagicMock()

    def mock_ftp_client(self, server):
        ftp_mock.login.return_value = 'login ok'
        ftp_mock.cwd.return_value = 'dir changed'
        ftp_mock.storbinary.return_value = '226 Transfer complete.'
        return ftp_mock

    mocker.patch(
        'app.services.ftp_uploader.FtpUploader.ftp_client',
        mock_ftp_client
    )

    filepath = os.path.join('./tests/test_subs', 'testing_good.srt')
    res = auth_client.post("/edit_metadata?pid=qsf7664p39&department=testbeeld", data={
        'pid': 'qsf7664p39',
        'department': 'testbeeld',
        'mam_data': json.dumps(mam_data),
        'sm_data': json.dumps({}),
        'serie': 'Serie veld test',
        'uitzenddatum': '2021-11-21',
        'ontsluitingstitel': 'Fietsstraten in centrum Gent',
        'prd_maker_attribute': 'Maker',
        'prd_maker_value': '',
        'prd_bijdrager_attribute': 'Aanwezig',
        'prd_bijdrager_value': '',
        'prd_publisher_attribute': 'Distributeur',
        'prd_publisher_value': '',
        'avo_beschrijving': 'Beschrijving test',
        'lom_type': '[{"name":"Video","code":"Video"}]',
        'lom1_beoogde_eindgebruiker': '[{"name":"Student","code":"Student"}]',
        'talen': '[{"name":"Nederlands","code":"nl"}]',
        'lom_onderwijs_combo': '[]',
        'lom1_onderwijsniveaus': '[]',
        'lom1_onderwijsgraden': '[]',
        'themas': '[]',
        'vakken': '[]',
        'trefwoorden': '[]',
        'publicatiestatus_checked': 'on',
        'subtitle_type': 'closed',
        'subtitle_file': (open(filepath, 'rb'), 'testing_good.srt'),
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'werden opgeslagen' in res.data.decode()
    assert 'succesvol opgeladen' in res.data.decode()
    assert ftp_mock.login.called


@pytest.mark.skip(reason="requires VCR cassette recording against a live MediaHaven server")
@pytest.mark.vcr
def test_edit_metadata_without_subtitle(auth_client, mocker):
    """POST without subtitle file should only save metadata."""
    with open('./tests/fixture_data/edit_mam_data.json', "r") as f:
        mam_data = json.loads(f.read())

    res = auth_client.post("/edit_metadata?pid=qsf7664p39&department=testbeeld", data={
        'pid': 'qsf7664p39',
        'department': 'testbeeld',
        'mam_data': json.dumps(mam_data),
        'sm_data': json.dumps({}),
        'serie': 'Serie veld test',
        'uitzenddatum': '2021-11-21',
        'ontsluitingstitel': 'Fietsstraten in centrum Gent',
        'prd_maker_attribute': 'Maker',
        'prd_maker_value': '',
        'prd_bijdrager_attribute': 'Aanwezig',
        'prd_bijdrager_value': '',
        'prd_publisher_attribute': 'Distributeur',
        'prd_publisher_value': '',
        'avo_beschrijving': 'Beschrijving test',
        'lom_type': '[{"name":"Video","code":"Video"}]',
        'lom1_beoogde_eindgebruiker': '[{"name":"Student","code":"Student"}]',
        'talen': '[{"name":"Nederlands","code":"nl"}]',
        'lom_onderwijs_combo': '[]',
        'lom1_onderwijsniveaus': '[]',
        'lom1_onderwijsgraden': '[]',
        'themas': '[]',
        'vakken': '[]',
        'trefwoorden': '[]',
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'werden opgeslagen' in res.data.decode()
    body = res.data.decode()
    assert 'succesvol opgeladen' not in body
    assert 'automatisch opgeladen' not in body


@pytest.mark.skip(reason="requires VCR cassette recording against a live MediaHaven server")
@pytest.mark.vcr
def test_edit_metadata_with_invalid_srt(auth_client, mocker):
    """POST with a non-SRT file should show a subtitle validation error."""
    with open('./tests/fixture_data/edit_mam_data.json', "r") as f:
        mam_data = json.loads(f.read())

    res = auth_client.post("/edit_metadata?pid=qsf7664p39&department=testbeeld", data={
        'pid': 'qsf7664p39',
        'department': 'testbeeld',
        'mam_data': json.dumps(mam_data),
        'sm_data': json.dumps({}),
        'serie': 'Serie veld test',
        'uitzenddatum': '2021-11-21',
        'ontsluitingstitel': 'Fietsstraten in centrum Gent',
        'prd_maker_attribute': 'Maker',
        'prd_maker_value': '',
        'prd_bijdrager_attribute': 'Aanwezig',
        'prd_bijdrager_value': '',
        'prd_publisher_attribute': 'Distributeur',
        'prd_publisher_value': '',
        'avo_beschrijving': 'Beschrijving test',
        'lom_type': '[{"name":"Video","code":"Video"}]',
        'lom1_beoogde_eindgebruiker': '[{"name":"Student","code":"Student"}]',
        'talen': '[{"name":"Nederlands","code":"nl"}]',
        'lom_onderwijs_combo': '[]',
        'lom1_onderwijsniveaus': '[]',
        'lom1_onderwijsgraden': '[]',
        'themas': '[]',
        'vakken': '[]',
        'trefwoorden': '[]',
        'publicatiestatus_checked': 'on',
        'subtitle_type': 'closed',
        'subtitle_file': (io.BytesIO(b"not a subtitle"), 'badfile.png'),
    }, follow_redirects=True)

    assert res.status_code == HTTPStatus.OK
    assert 'werden opgeslagen' in res.data.decode()
    assert '.srt extensie' in res.data.decode()


# security check without session routes redirect to login:
@pytest.mark.vcr
def test_subtitle_videoplayer_route_without_session(client):
    with client.session_transaction() as session:
        session.clear()
    res = client.get(
        '/subtitles/qsxs5jbm5c.vtt',
        follow_redirects=True
    )
    assert res.status_code == HTTPStatus.OK
    assert 'Log in om gebruik te maken' in res.data.decode()


@pytest.mark.vcr
def test_publicatie_status_protected(client):
    with client.session_transaction() as session:
        session.clear()

    res = client.get(
        "/publicatie_status?pid=qs5d8ncx8c&department=testbeeld",
        follow_redirects=True
    )
    assert res.status_code == HTTPStatus.OK
    assert 'Log in om gebruik te maken' in res.data.decode()


# static file cache header tests

def test_cache_immutable_existing_paths(client):
    for path in ['/static/avo-logo-i.svg', '/static/images/saml_login_background.jpg']:
        res = client.get(path)
        assert res.cache_control.public is True
        assert res.cache_control.max_age == 31536000
        assert res.cache_control.immutable is True


def test_cache_immutable_vue_bundles(client):
    for path in [
        '/static/vue/js/app.3c43299f.js',
        '/static/vue/js/chunk-vendors.84d9dc4d.js',
        '/static/vue/css/app.b7f7662c.css',
        '/static/vue/css/chunk-vendors.a902fd7e.css',
    ]:
        res = client.get(path)
        assert res.cache_control.public is True
        assert res.cache_control.max_age == 31536000
        assert res.cache_control.immutable is True


def test_cache_immutable_fonts(client):
    for path in [
        '/static/bulma/fonts/slick.woff',
        '/static/bulma/fonts/slick.ttf',
    ]:
        res = client.get(path)
        assert res.cache_control.public is True
        assert res.cache_control.max_age == 31536000
        assert res.cache_control.immutable is True


def test_cache_vendor_libs(client):
    for path in [
        '/static/flowplayer.min.js',
        '/static/flowplayer.css',
        '/static/quill.js',
        '/static/quill.snow.css',
        '/static/subtitles.min.js',
        '/static/turndown.js',
        '/static/bulma/bulma-tooltip.min.css',
        '/static/bulma/bundle.js',
        '/static/favicon.ico',
    ]:
        res = client.get(path)
        assert res.cache_control.public is True
        assert res.cache_control.max_age == 604800
        assert not res.cache_control.immutable


def test_cache_app_assets(client):
    for path in [
        '/static/redactietool_v2.js',
        '/static/style.css',
        '/static/bulma/overrides.css',
        '/static/bulma/core.css',
        '/static/bulma/modal_dialog.js',
    ]:
        res = client.get(path)
        assert res.cache_control.public is True
        assert res.cache_control.max_age == 3600
        assert not res.cache_control.immutable
