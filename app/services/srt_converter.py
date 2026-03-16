# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/srt_converter.py
#
#   Uses webvtt wrappers to do string with
#   subtitles in srt format into webvtt format
#

#from webvtt.parsers import SRTParser
#from webvtt.writers import WebVTTWriter
#from webvtt.errors import MalformedFileError


import io
import webvtt


def convert_srt(srt_content):
    try:
        # webvtt can read from a file-like object
        srt_file = io.StringIO(srt_content)

        vtt = webvtt.from_srt(srt_file)

        # return the VTT content as string
        return vtt.content

    except Exception as e:
        print("convert_srt: error", e)
        return ""






def _convert_srt(srt_content):
    try:
        parser = SRTStringParser().readstr(srt_content)
        captions = parser.captions
        webvtt_str = WebVTTWriter().webvtt_content(captions)

        return webvtt_str
    except MalformedFileError as e:
        print("convert_srt: error", e)
        return ""
