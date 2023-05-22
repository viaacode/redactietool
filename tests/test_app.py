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
from flask_api import status
from app.redactietool import app


@pytest.fixture(scope="module")
def setup():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'subtitle_uploads'
    yield setup


@pytest.fixture(scope="module")
def vcr_config():
    # important to add the filter_headers here to avoid exposing credentials
    # in tests/cassettes!
    return {
        "record_mode": "once",
        "filter_headers": ["authorization"]
    }


def test_home(client):
    res = client.get('/')
    assert res.status_code == status.HTTP_200_OK
    assert b'Inloggen' in res.data


def test_liveness_check(client):
    res = client.get('/health/live')

    assert res.data == b'OK'
    assert res.status_code == status.HTTP_200_OK


def test_search_media_security(client):
    res = client.get('/search_media')
    # assert res.status_code == 401  # unauthorized

    # with flask-login this auto redirects to login now with a 302
    assert res.status_code == 302  # redirects to login


def test_search_media(client):
    with client.session_transaction() as session:
        session['samlUserdata'] = {}
        session['samlUserdata']['cn'] = ['Test user']
        session['samlUserdata']['apps'] = ['mediahaven']

    res = client.get("/search_media")
    assert res.status_code == 200


def test_invalid_pid_entry(client):
    res = client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': 'abc123#'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'PID formaat foutief' in res.data.decode()


def test_empty_pid(client):
    res = client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': ''
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Geef een PID' in res.data.decode()


@pytest.mark.vcr
def test_wrong_pid_entry(client):
    res = client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': 'abc123'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'PID niet gevonden in testbeeld' in res.data.decode()


@pytest.mark.vcr
def test_working_pid_search(client):
    res = client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': 'qsxs5jbm5c',
        'redirect_subtitles': 'yes'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Kies ondertitelbestand' in res.data.decode()


def test_invalid_long_pid_entry(client):
    res = client.post("/search_media", data={
        'department': 'testbeeld',
        'pid': 'abc123'*40
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'PID te lang' in res.data.decode()


def test_invalid_department_entry(client):
    res = client.post("/search_media", data={
        'department': 'testbeeld%^',
        'pid': 'abc123'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Department formaat foutief' in res.data.decode()


def test_invalid_long_department(client):
    res = client.post("/search_media", data={
        'department': 'testbeeld_te_lang'*40,
        'pid': 'abc123'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'department te lang' in res.data.decode()


@pytest.mark.vcr
def test_bad_srt_upload(client):
    filename = 'subtitles.srt'

    res = client.post("/upload", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'mam_data': '',
        'video_url': 'http://somevideopath',
        'subtitle_type': 'closed',
        'subtitle_file': (io.BytesIO(b"some initial data"), filename)
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Ondertitels moeten in SRT formaat' in res.data.decode()


@pytest.mark.vcr
def test_invalid_upload(client):
    filename = 'somefile.png'

    res = client.post("/upload", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'mam_data': '',
        'video_url': 'http://somevideopath',
        'subtitle_type': 'closed',
        'subtitle_file': (io.BytesIO(b"some initial data"), filename)
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Ondertitels moeten in SRT formaat' in res.data.decode()


@pytest.mark.vcr
def test_empty_upload(client):
    res = client.post("/upload", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'mam_data': '',
        'video_url': 'http://somevideopath',
        'subtitle_type': 'closed',
        'subtitle_file': None
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Geen ondertitels bestand' in res.data.decode()


@pytest.mark.vcr
def test_valid_subtitle(client):
    filename = 'testing_good.srt'
    filepath = os.path.join('./tests/test_subs', filename)

    with open('./tests/test_subs/mam_data.json') as mam_json_file:
        mam_data = json.load(mam_json_file)

    res = client.post("/upload", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'mam_data': json.dumps(mam_data),
        'video_url': 'http://somevideopath',
        'subtitle_type': 'closed',
        'subtitle_file': (open(filepath, 'rb'), filename)
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Ondertitelbestand' in res.data.decode()
    assert 'PID' in res.data.decode()
    assert 'qsxs5jbm5c' in res.data.decode()
    assert 'qsxs5jbm5c.srt' in res.data.decode()
    assert 'Toevoegen' in res.data.decode()
    assert 'Wissen' in res.data.decode()


@pytest.mark.vcr
def test_valid_subtitle_capitals(client):
    filename = 'test_good2.SRT'
    filepath = os.path.join('./tests/test_subs', filename)

    with open('./tests/test_subs/mam_data.json') as mam_json_file:
        mam_data = json.load(mam_json_file)

    res = client.post("/upload", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'mam_data': json.dumps(mam_data),
        'video_url': 'http://somevideopath',
        'subtitle_type': 'closed',
        'subtitle_file': (open(filepath, 'rb'), filename)
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Ondertitelbestand' in res.data.decode()
    assert 'PID' in res.data.decode()
    assert 'qsxs5jbm5c' in res.data.decode()
    assert 'qsxs5jbm5c.srt' in res.data.decode()
    assert 'Toevoegen' in res.data.decode()
    assert 'Wissen' in res.data.decode()


@pytest.mark.vcr
def test_cancel_upload(client):
    data = {
        'pid': 'abc',
        'department': 'testbeeld',
        'srt_file': 'somefile.srt',
        'vtt_file': 'somefile.vtt',
    }
    res = client.get(
        "/cancel_upload",
        query_string=data,
        follow_redirects=True)
    assert res.status_code == 200
    assert 'PID niet gevonden in testbeeld' in res.data.decode()


@pytest.mark.vcr
def test_subtitle_videoplayer_route(client):
    res = client.get('/subtitles/qsxs5jbm5c.vtt')
    assert res.status_code == 200


@pytest.mark.vcr
def test_subtitle_videoplayer_route_unknownfile(client):
    res = client.get('/subtitles/someinvalidpath.vtt')
    assert res.status_code == 302  # redirects to 404 page


@pytest.mark.vcr
def test_send_to_mam_shows_confirmation(client):
    with open('./tests/test_subs/mam_data.json') as mam_json_file:
        mam_data = json.load(mam_json_file)

    res = client.post("/send_to_mam", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'subtitle_type': 'closed',
        'subtitle_file': 'qsxs5jbm5c.srt',
        'vtt_file': 'qsxs5jbm5c.vtt',
        'transfer_method': 'api',
        'mam_data': json.dumps(mam_data)
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Ondertitelbestand bestaat al voor deze video' in res.data.decode()
    assert 'bestaande ondertitelbestand qsxs5jbm5c_closed.srt. Wil je het vervangen?' in res.data.decode()


@pytest.mark.vcr
def test_send_to_mam_confirm_works(client):
    with open('./tests/test_subs/mam_data.json') as mam_json_file:
        mam_data = json.load(mam_json_file)

    # replace existing subtitle now
    res = client.post("/send_to_mam", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'subtitle_type': 'closed',
        'subtitle_file': 'qsxs5jbm5c_closed.srt',
        'xml_file': 'qsxs5jbm5c_closed.xml',
        'mam_data': json.dumps(mam_data),
        'transfer_method': 'api',
        'replace_existing': 'confirm'
    }, follow_redirects=True)

    assert res.status_code == 200
    print(res.data.decode(), flush=True)
    assert 'De ondertitels werden succesvol opgeladen' in res.data.decode()


@pytest.mark.vcr
def test_send_to_mam_cancel_works(client):
    with open('./tests/test_subs/mam_data.json') as mam_json_file:
        mam_data = json.load(mam_json_file)

    # replace existing subtitle now
    res = client.post("/send_to_mam", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'subtitle_type': 'closed',
        'subtitle_file': 'qsxs5jbm5c_closed.srt',
        'vtt_file': 'qsxs5jbm5c.vtt',
        'xml_file': 'qsxs5jbm5c_closed.xml',
        'mam_data': json.dumps(mam_data),
        'replace_existing': 'cancel'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'Bestaande ondertitels werden behouden' in res.data.decode()


@pytest.mark.vcr
def test_edit_metadata_wrong_pid(client):
    res = client.get(
        "/edit_metadata?pid=somewrongpid&department=testbeeld",
        follow_redirects=True
    )

    assert res.status_code == 200
    assert 'Zoek een item op' in res.data.decode()
    assert 'niet gevonden' in res.data.decode()


@pytest.mark.vcr
def test_edit_metadata_working_pid(client):
    res = client.get(
        "/edit_metadata?pid=qs5d8ncx8c&department=testbeeld",
        follow_redirects=True
    )

    assert res.status_code == 200
    assert 'Algemene metadata' in res.data.decode()


@pytest.mark.vcr
def test_subtitles_on_metadata_edit(client):
    res = client.get(
        "/item_subtitles/testbeeld/qs5d8ncx8c/closed",
        follow_redirects=True
    )

    assert res.status_code == 200


@pytest.mark.vcr
def test_onderwijsniveaus(client):
    res = client.get(
        "/onderwijsniveaus",
        follow_redirects=True
    )

    assert res.status_code == 200


@pytest.mark.vcr
def test_onderwijsgraden(client):
    res = client.get(
        "/onderwijsgraden",
        follow_redirects=True
    )

    assert res.status_code == 200


@pytest.mark.vcr
def test_themas(client):
    res = client.get(
        "/themas",
        follow_redirects=True
    )

    assert res.status_code == 200


@pytest.mark.vcr
def test_vakken(client):
    res = client.get(
        "/vakken",
        follow_redirects=True
    )

    assert res.status_code == 200


@pytest.mark.vcr
def test_keyword_search(client):
    res = client.post(
        "/keyword_search",
        json={'qry': 'zoek'},
        follow_redirects=True
    )

    assert res.status_code == 200
    search_results = json.loads(res.data)
    assert len(search_results) >= 4
    assert search_results[0]['text'] == 'zoekactie'


@pytest.mark.vcr
def test_vakken_suggesties(client):
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

    res = client.post(
        "/vakken_suggest",
        json=graden_en_themas,
        follow_redirects=True
    )

    assert res.status_code == 200
    suggesties = json.loads(res.data)
    assert len(suggesties) == 3


@pytest.mark.vcr
def test_vakken_related(client):
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
    res = client.post(
        "/vakken_related",
        json=graden_en_niveaus,
        follow_redirects=True
    )

    assert res.status_code == 200
    overige_vakken = json.loads(res.data)
    assert len(overige_vakken) == 12


@pytest.mark.vcr
def test_publicatie_status(client):
    res = client.get(
        "/publicatie_status?pid=qs5d8ncx8c&department=testbeeld",
        follow_redirects=True
    )

    assert res.status_code == 200
    assert 'publish_item' in res.json.keys()


@pytest.mark.vcr
def test_publicatie_status_404(client):
    res = client.get(
        "/publicatie_status?pid=randompid&department=testbeeld",
        follow_redirects=True
    )

    assert res.status_code == 200
    assert 'publish_item' in res.json.keys()
    assert res.json['publish_item'] is False


@pytest.mark.vcr
def test_update_metadata(client):
    with open('./tests/fixture_data/edit_mam_data.json', "r") as f:
        mam_data = json.loads(f.read())

    res = client.post("/edit_metadata?pid=qsf7664p39&department=testbeeld", data={
        'pid': 'qsf7664p39',
        'department': 'testbeeld',
        'mam_data': json.dumps(mam_data),
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

    assert res.status_code == 200
    assert 'werden opgeslagen' in res.data.decode()


def test_random_404(client, setup):
    resp = client.delete('/somepage')
    assert resp.status_code == 302
    assert resp.location == 'http://localhost/404'

    resp = client.get('/somepage')
    assert resp.status_code == 302
    assert resp.location == 'http://localhost/404'

    resp = client.post('/somepage')
    assert resp.status_code == 302
    assert resp.location == 'http://localhost/404'

    resp = client.put('/somepage')
    assert resp.status_code == 302
    assert resp.location == 'http://localhost/404'


@pytest.mark.vcr
def test_valid_subtitle_for_ftp(client):
    filename = 'testing_good.srt'
    filepath = os.path.join('./tests/test_subs', filename)

    with open('./tests/test_subs/mam_data.json') as mam_json_file:
        mam_data = json.load(mam_json_file)

    res = client.post("/upload", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'mam_data': json.dumps(mam_data),
        'video_url': 'http://somevideopath',
        'subtitle_type': 'closed',
        'subtitle_file': (open(filepath, 'rb'), filename)
    }, follow_redirects=True)

    assert res.status_code == 200
    assert 'PID' in res.data.decode()
    assert 'Ondertitelbestand' in res.data.decode()
    assert 'qsxs5jbm5c' in res.data.decode()
    assert 'qsxs5jbm5c.srt' in res.data.decode()
    assert 'Toevoegen' in res.data.decode()
    assert 'Wissen' in res.data.decode()


@pytest.mark.vcr
def test_subtitle_ftp_upload(client, mocker):
    with open('./tests/test_subs/mam_data.json') as mam_json_file:
        mam_data = json.load(mam_json_file)

    # mock ftp calls
    ftp_mock = MagicMock()

    def mock_ftp_client(self, server):
        assert server == 'ftp.localhost'
        ftp_mock.login.return_value = 'login ok'
        ftp_mock.cwd.return_value = 'dir changed'
        ftp_mock.storbinary.return_value = '226 Transfer complete.'

        return ftp_mock

    mocker.patch(
        'app.services.ftp_uploader.FtpUploader.ftp_client',
        mock_ftp_client
    )

    # replace existing subtitle now
    res = client.post("/send_to_mam", data={
        'pid': 'qsxs5jbm5c',
        'department': 'testbeeld',
        'subtitle_type': 'closed',
        'subtitle_file': 'qsxs5jbm5c.srt',
        'xml_file': 'qsxs5jbm5c.xml',
        'mam_data': json.dumps(mam_data),
        'transfer_method': 'ftp'

    }, follow_redirects=True)

    assert ftp_mock.login.called
    assert ftp_mock.cwd.called
    ftp_mock.cwd.assert_called_with('/FTP_DIR/')
    assert ftp_mock.storbinary.called_twice

    assert res.status_code == 200
    print(res.data.decode(), flush=True)
    assert 'De ondertitels werden succesvol opgeladen' in res.data.decode()
    assert '226 Transfer complete' in res.data.decode()


# security check without session routes redirect to login:
@pytest.mark.vcr
def test_subtitle_videoplayer_route_without_session(client):
    with client.session_transaction() as session:
        session.clear()
    res = client.get(
        '/subtitles/qsxs5jbm5c.vtt',
        follow_redirects=True
    )
    assert res.status_code == 200
    assert 'Log in om gebruik te maken' in res.data.decode()


@pytest.mark.vcr
def test_publicatie_status_protected(client):
    with client.session_transaction() as session:
        session.clear()

    res = client.get(
        "/publicatie_status?pid=qs5d8ncx8c&department=testbeeld",
        follow_redirects=True
    )
    assert res.status_code == 200
    assert 'Log in om gebruik te maken' in res.data.decode()
