#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/ftp_uploader.py
#
#   FTP upload subtitle file and sidecar xml files.
#   as temporary workaround to get this working until
#   mh-api v2 solution is available.
#

import os
from viaa.configuration import ConfigParser
from viaa.observability import logging
from ftplib import FTP, error_perm, error_temp
import socket

logger = logging.get_logger(__name__, config=ConfigParser())


class FtpUploader:
    FTP_SERVER = os.environ.get(
        'FTP_SERVER',
        'ftp.localhost'
    )
    FTP_USER = os.environ.get('FTP_USER', 'anonymous')
    FTP_PASS = os.environ.get('FTP_PASS', '')
    FTP_DIR = os.environ.get('FTP_DIR', '/FTP_DIR/')

    def ftp_client(self, server):
        # We set a timout of max 7 seconds to be safe.
        # On localhost it works with timeout 3 also.
        ftp = FTP(server, timeout=7)
        return ftp

    def upload_subtitles(self, upload_folder, metadata, tp):
        try:
            # sends srt_file and xml_file to mediahaven
            srt_path = os.path.join(upload_folder, tp['srt_file'])
            xml_path = os.path.join(upload_folder, tp['xml_file'])

            logger.info(
                f"Uploading to {self.FTP_SERVER} in folder #{self.FTP_DIR}")

            ftp = self.ftp_client(self.FTP_SERVER)
            ftp.login(self.FTP_USER, self.FTP_PASS)

            # set pasv flag so we don't get timeouts
            # ftp.set_pasv(False)

            # change to correct ftp dir
            ftp.cwd(self.FTP_DIR)

            # upload srt file
            srt_result = ftp.storbinary(
                f"STOR {tp['srt_file']}",
                fp=open(srt_path, 'rb')
            )

            # upload xml sidecar file
            xml_result = ftp.storbinary(
                f"STOR {tp['xml_file']}",
                fp=open(xml_path, 'rb')
            )

            return {
                'srt_ftp_response': srt_result,
                'xml_ftp_response': xml_result
            }

        except error_temp as msg:
            print(f"FTP error_temp: {msg}", flush=True)
            return {'ftp_error': str(msg)}

        except error_perm as msg:
            print(f"FTP error_perm: {msg}", flush=True)
            return {'ftp_error': str(msg)}

        except (socket.error, socket.gaierror) as sock_err:
            print('FTP host="{}" error="{}"'.format(
                self.FTP_SERVER,
                sock_err
            ), flush=True)
            return {
                'ftp_error': f"FTP connect error, could not connect to {self.FTP_SERVER}"
            }
