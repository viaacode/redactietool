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

# issue this package does not install on our jenkens (nor in my docker)
# it does work locally:
# sparql-endpoint-fixture>=0.5.0
pytest_plugins = [
    #"sparql_endpoint_fixture.endpoint"
]

@pytest.fixture(scope="function")
def client():
    """Unauthenticated test client (default)."""
    app.config["TESTING"] = True
    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope="function")
def auth_client(client):
    """Authenticated test client."""
    with client.session_transaction() as sess:
        sess["samlUserdata"] = {
            "cn": ["Test user"],
            "apps": ["mediahaven"]
        }
    return client

