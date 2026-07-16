# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_authorization.py
#

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    # important to add the filter_headers here to avoid exposing credentials
    # in tests/cassettes!
    return {
        "record_mode": "once",
        "filter_headers": ["authorization"]
    }


@pytest.mark.vcr
def test_logout(client):
    res = client.get('/?slo')

    assert 'singleLogout' in res.data.decode()
    assert 'RelayState' in res.data.decode()


def test_legacy_login_page(client):
    res = client.get("/legacy_login", follow_redirects=True)

    assert res.status_code == 200
    assert 'Wachtwoord' in res.data.decode()


def test_wrong_credentials(client):
    res = client.post('/legacy_login', data=dict(
        username='avo-syncrator',
        password='wrong_pass',
    ), follow_redirects=True)

    assert 'Fout email of wachtwoord' in res.data.decode()


def test_right_credentials(client):
    res = client.post('/legacy_login', data=dict(
        username='admin',
        password='admin',
    ), follow_redirects=True)

    assert 'Fout email of wachtwoord' not in res.data.decode()
    assert 'Zoek een item op' in res.data.decode()
