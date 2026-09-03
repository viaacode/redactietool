# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/subtitle_files.py
#
#   methods to create temporary srt and vtt files
#   used for sending to mediahaven and streaming in the flowplayer preview.html
#

import os
import webvtt
import requests

from app.services.srt_converter import convert_srt
from werkzeug.utils import secure_filename
from viaa.configuration import ConfigParser
from viaa.observability import logging

logger = logging.get_logger(__name__, config=ConfigParser())


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['srt', 'SRT']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_subtitles(upload_folder, pid, uploaded_file):
    try:
        if uploaded_file and allowed_file(
                secure_filename(uploaded_file.filename)):
            srt_filename = pid + '.srt'
            vtt_filename = pid + '.vtt'

            # save srt and converted vtt file in uploads folder
            srt_path = os.path.join(upload_folder, srt_filename)
            uploaded_file.save(srt_path)

            # convert <br> into newlines; use utf-8-sig to handle UTF-8 BOM
            fsrt = open(srt_path, 'rt', encoding='utf-8-sig')
            content = fsrt.read()
            content = content.replace('<br>', '\n')
            content = content.replace('<br/>', '\n')
            content = content.replace('<br />', '\n')
            fsrt.close()
            fsrt = open(srt_path, 'wt', encoding='utf-8')
            fsrt.write(content)
            fsrt.close()

            # create vtt file
            vtt_file = webvtt.from_srt(srt_path)
            vtt_file.save()

            return srt_filename, vtt_filename
    except webvtt.errors.MalformedFileError as we:
        logger.info(f"Parse error in srt {we}")
    except webvtt.errors.MalformedCaptionError as we:
        logger.info(f"Parse error in srt {we}")

    return None, None


def get_vtt_subtitles(srt_url, session=None):
    # a subtitle url that mediahaven serves itself needs the authorized
    # session of the api client, an object store url does not
    srt_response = (session or requests).get(srt_url)
    # the object store serves srt as text/plain without a charset, so requests
    # falls back to ISO-8859-1 and utf-8 accents come out as mojibake (Ã©).
    # utf-8-sig also strips a BOM when the uploaded file has one.
    srt_response.encoding = 'utf-8-sig'
    srt_content = srt_response.text
    vtt_content = convert_srt(srt_content)

    if not vtt_content:
        # convert_srt swallows parse errors, so log what we actually fetched:
        # a 404 page, a wrong encoding or a BOM all end up as an empty result
        logger.warning(
            'could not convert srt from object store',
            data={
                'srt_url': srt_url,
                'authorized': session is not None,
                'status_code': srt_response.status_code,
                'content_type': srt_response.headers.get('Content-Type'),
                'encoding': srt_response.encoding,
                'content_length': len(srt_content),
                'first_line': repr(srt_content.split('\n')[0][:80]),
            }
        )

    return vtt_content


def not_deleted(upload_folder, f):
    return os.path.exists(os.path.join(upload_folder, f))


def delete_file(upload_folder, f):
    try:
        if f and len(f) > 3:
            sub_tempfile_path = os.path.join(upload_folder, f)
            os.unlink(sub_tempfile_path)
    except FileNotFoundError:
        logger.info(f"Warning file not found for deletion {f}")
        pass


def delete_files(upload_folder, tp):
    if tp.get('srt_file'):
        delete_file(upload_folder, tp['srt_file'])

    if tp.get('vtt_file'):
        delete_file(upload_folder, tp['vtt_file'])


def move_subtitle(upload_folder, tp):
    # moving it from somename.srt into <pid>_open/closed.srt
    new_filename = f"{tp['pid']}_{tp['subtitle_type']}.srt"
    orig_path = os.path.join(upload_folder, tp['srt_file'])
    new_path = os.path.join(upload_folder, new_filename)

    if not os.path.exists(new_path):
        os.rename(orig_path, new_path)
    return new_filename
