# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/fixtures.py
#
import json


def subtitle_sidecar():
    with open('tests/fixture_data/sidecar_v2.xml', 'r') as xmlfile:
        return xmlfile.read()


def sub_params():
    return {
        'pid': 'qsf7664p39',
        'subtitle_type': 'closed',
        'srt_file': 'qsf7664p39_closed.srt',
        'vtt_file': 'qsf7664p39.vtt',
        'mam_data': '{}',
        'replace_existing': None,
    }


def sub_meta():
    with open("tests/fixture_data/sub_metadata.json") as subtitle_metadata:
        return json.load(subtitle_metadata)
