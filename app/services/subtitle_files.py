# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/subtitle_files.py
#
#   description: methods to create temporary srt, vtt and xml files
#   used for sending to mediahaven and streaming in the flowplayer preview.html
#   get_property is easy helper method to iterate mdProperties inside
#   returned data from find_item_by_pid call.
#

import os
import webvtt
import requests

from app.services.srt_converter import convert_srt
from app.services.meta_sidecar import get_property, sidecar_root
from werkzeug.utils import secure_filename
from viaa.configuration import ConfigParser
from viaa.observability import logging
from lxml import etree

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

            # convert <br> into newlines
            fsrt = open(srt_path, 'rt')
            content = fsrt.read()
            content = content.replace('<br>', '\n')
            content = content.replace('<br/>', '\n')
            content = content.replace('<br />', '\n')
            fsrt.close()
            fsrt = open(srt_path, 'wt')
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
    TESTBEELD_PERM_ID = os.environ.get(
        'TESTBEELD_PERM_ID', 'config_testbeeld_uuid')
    ONDERWIJS_PERM_ID = os.environ.get(
        'ONDERWIJS_PERM_ID', 'config_onderwijs_uuid')
    ADMIN_PERM_ID = os.environ.get('ADMIN_PERM_ID', 'config_admin_uuid')

    cp_id = get_property(metadata, 'CP_id')
    cp = get_property(metadata, 'CP')
    xml_pid = f"{tp['pid']}_{tp['subtitle_type']}"

    root, MH_NS, MHS_NS, XSI_NS = sidecar_root()

    descriptive = etree.SubElement(root, '{%s}Descriptive' % MHS_NS)
    etree.SubElement(descriptive, '{%s}Title' % MH_NS).text = tp['srt_file']
    description = f"Subtitles for item {tp['pid']}"
    etree.SubElement(descriptive, '{%s}Description' % MH_NS).text = description

    rights = etree.SubElement(
        root, '{%s}RightsManagement' % MHS_NS)  # of Structural?
    permissions = etree.SubElement(rights, '{%s}Permissions' % MH_NS)
    etree.SubElement(permissions, '{%s}Read' % MH_NS).text = TESTBEELD_PERM_ID
    etree.SubElement(permissions, '{%s}Read' % MH_NS).text = ONDERWIJS_PERM_ID
    etree.SubElement(permissions, '{%s}Read' % MH_NS).text = ADMIN_PERM_ID
    etree.SubElement(permissions, '{%s}Write' % MH_NS).text = TESTBEELD_PERM_ID
    etree.SubElement(permissions, '{%s}Write' % MH_NS).text = ADMIN_PERM_ID
    etree.SubElement(permissions, '{%s}Export' %
                     MH_NS).text = TESTBEELD_PERM_ID
    etree.SubElement(permissions, '{%s}Export' % MH_NS).text = ADMIN_PERM_ID

    mdprops = etree.SubElement(root, "{%s}Dynamic" % MHS_NS)

    # set is_verwant_aan needs overwrite strategy and is needed for new items
    relations = etree.SubElement(mdprops, "dc_relations")
    relations.set('strategy', 'OVERWRITE')
    etree.SubElement(relations, "is_verwant_aan").text = tp['pid']

    etree.SubElement(mdprops, "CP_id").text = cp_id
    # mediahaven computes external_id for us.
    # etree.SubElement(mdprops, "external_id").text = xml_pid
    etree.SubElement(mdprops, "PID").text = xml_pid
    etree.SubElement(mdprops, "CP").text = cp
    etree.SubElement(mdprops, "sp_name").text = 'borndigital'

    xml_data = etree.tostring(
        root, pretty_print=True, encoding="UTF-8", xml_declaration=True
    ).decode()

    # now write data to correct filename
    xml_filename = f"{xml_pid}.xml"
    sf = open(os.path.join(upload_folder, xml_filename), 'w')
    sf.write(xml_data)
    sf.close()

    return xml_filename, xml_data
