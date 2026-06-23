# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/subtitle_files.py
#
#   methods to create temporary srt, vtt and xml files
#   used for sending to mediahaven and streaming in the flowplayer preview.html
#   we also save the subtitle xml sidecar here for ftp uploading
#

import os
import webvtt
import requests

from app.services.srt_converter import convert_srt
from app.services.xml_sidecar import XMLSidecar
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


def get_vtt_subtitles(srt_url):
    srt_content = requests.get(srt_url).text
    return convert_srt(srt_content)


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

    if tp.get('xml_file'):
        delete_file(upload_folder, tp['xml_file'])


def move_subtitle(upload_folder, tp):
    # moving it from somename.srt into <pid>_open/closed.srt
    new_filename = f"{tp['pid']}_{tp['subtitle_type']}.srt"
    orig_path = os.path.join(upload_folder, tp['srt_file'])
    new_path = os.path.join(upload_folder, new_filename)

    if not os.path.exists(new_path):
        os.rename(orig_path, new_path)
    return new_filename


def save_sidecar_xml(upload_folder, metadata, tp):
    # now write data to correct filename
    xml_pid = f"{tp['pid']}_{tp['subtitle_type']}"
    xml_filename = f"{xml_pid}.xml"
    xml_data = XMLSidecar().subtitle_sidecar(metadata, tp)
    sf = open(os.path.join(upload_folder, xml_filename), 'w')
    sf.write(xml_data)
    sf.close()

    return xml_filename, xml_data
