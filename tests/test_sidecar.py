# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_sidecar.py
#

import pytest
from app.services.xml_sidecar import XMLSidecar
from .fixtures import sub_params, sub_meta, subtitle_sidecar

pytestmark = [pytest.mark.vcr(ignore_localhost=True)]


@pytest.fixture(scope="module")
def vcr_config():
    # important to add the filter_headers here to avoid exposing credentials
    # in tests/cassettes!
    return {
        "record_mode": "once",
        "filter_headers": ["authorization"]
    }


def test_sidecar_v2():
    xml_data = XMLSidecar().subtitle_sidecar(sub_meta(), sub_params())

    assert xml_data == subtitle_sidecar()
