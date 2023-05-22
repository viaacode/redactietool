# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_sidecar.py
#

import pytest
from app.services.subtitle_files import save_sidecar_xml
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
    xml_filename, xml_data = save_sidecar_xml(
        "./tests/test_subs", sub_meta(), sub_params())

    print(xml_data)
    assert xml_data == subtitle_sidecar()
