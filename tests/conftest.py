# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/conftest.py
#
#   shared fixtures and basic setup, (also look at __init__.py)
#

import pytest
from app.redactietool import app

pytest_plugins = [
    "sparql_endpoint_fixture.endpoint"
]

@pytest.fixture(scope='module')
def client():
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()
