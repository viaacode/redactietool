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

    def local_size(self, path):
        try:
            return os.path.getsize(path)
        except OSError as e:
            return f"unavailable ({e})"

    def remote_size(self, ftp, filename):
        # SIZE right after STOR tells us if the bytes really landed on the
        # watchfolder. A 550 here means the file is gone again, which normally
        # means the mediahaven watchfolder already picked it up for ingest.
        try:
            return str(ftp.size(filename))
        except (error_perm, error_temp, OSError) as e:
            return f"unavailable ({e})"

    def check_uploaded_files(self, filenames):
        # Diagnostic used while waiting for the ingest: files that are still in
        # the watchfolder mean mediahaven did not pick them up at all, files
        # that are gone mean it did and the ingest itself went wrong.
        ftp = None
        try:
            ftp = self.ftp_client(self.FTP_SERVER)
            ftp.login(self.FTP_USER, self.FTP_PASS)
            ftp.cwd(self.FTP_DIR)

            still_present = {
                filename: self.remote_size(ftp, filename)
                for filename in filenames
            }
            logger.info(
                'watchfolder check',
                data={
                    'ftp_server': self.FTP_SERVER,
                    'ftp_dir': self.FTP_DIR,
                    'files': still_present,
                }
            )
            return still_present

        except (error_temp, error_perm, socket.error, socket.gaierror) as e:
            logger.error(
                'watchfolder check failed',
                data={'error': str(e), 'ftp_server': self.FTP_SERVER}
            )
            return {}

        finally:
            if ftp is not None:
                try:
                    ftp.quit()
                except Exception as quit_err:
                    logger.info(f"FTP quit failed: {quit_err}")

    def upload_subtitles(self, upload_folder, metadata, tp):
        ftp = None
        try:
            # sends srt_file and xml_file to mediahaven
            srt_path = os.path.join(upload_folder, tp['srt_file'])
            xml_path = os.path.join(upload_folder, tp['xml_file'])

            logger.info(
                f"Uploading to {self.FTP_SERVER} in folder #{self.FTP_DIR}",
                data={
                    'ftp_server': self.FTP_SERVER,
                    'ftp_dir': self.FTP_DIR,
                    'ftp_user': self.FTP_USER,
                    'srt_file': tp['srt_file'],
                    'xml_file': tp['xml_file'],
                    'srt_local_bytes': self.local_size(srt_path),
                    'xml_local_bytes': self.local_size(xml_path),
                    # the sidecar decides how mediahaven links the subtitle to
                    # the video, so log it in full when ingest goes wrong
                    'xml_sidecar': tp.get('xml_sidecar'),
                }
            )

            ftp = self.ftp_client(self.FTP_SERVER)
            login_response = ftp.login(self.FTP_USER, self.FTP_PASS)

            # change to correct ftp dir
            cwd_response = ftp.cwd(self.FTP_DIR)
            logger.info(
                'FTP connected',
                data={
                    'login_response': str(login_response),
                    'cwd_response': str(cwd_response),
                    'pwd': str(ftp.pwd()),
                }
            )

            # upload srt file
            with open(srt_path, 'rb') as srt_fp:
                srt_result = ftp.storbinary(f"STOR {tp['srt_file']}", fp=srt_fp)
            srt_remote_size = self.remote_size(ftp, tp['srt_file'])

            # upload xml sidecar file. mediahaven triggers the ingest on this
            # one, so it has to go last.
            with open(xml_path, 'rb') as xml_fp:
                xml_result = ftp.storbinary(f"STOR {tp['xml_file']}", fp=xml_fp)
            xml_remote_size = self.remote_size(ftp, tp['xml_file'])

            logger.info(
                'FTP upload completed',
                data={
                    'srt_file': tp['srt_file'],
                    'xml_file': tp['xml_file'],
                    'srt_ftp_response': srt_result,
                    'xml_ftp_response': xml_result,
                    'srt_local_bytes': self.local_size(srt_path),
                    'xml_local_bytes': self.local_size(xml_path),
                    'srt_remote_bytes': srt_remote_size,
                    'xml_remote_bytes': xml_remote_size,
                    'ftp_server': self.FTP_SERVER,
                    'ftp_dir': self.FTP_DIR,
                }
            )

            return {
                'srt_ftp_response': srt_result,
                'xml_ftp_response': xml_result
            }

        except error_temp as msg:
            logger.error(
                'FTP error_temp',
                data={
                    'error': str(msg),
                    'ftp_server': self.FTP_SERVER,
                    'ftp_dir': self.FTP_DIR,
                    'srt_file': tp.get('srt_file'),
                    'xml_file': tp.get('xml_file'),
                }
            )
            return {'ftp_error': str(msg)}

        except error_perm as msg:
            logger.error(
                'FTP error_perm',
                data={
                    'error': str(msg),
                    'ftp_server': self.FTP_SERVER,
                    'ftp_dir': self.FTP_DIR,
                    'srt_file': tp.get('srt_file'),
                    'xml_file': tp.get('xml_file'),
                }
            )
            return {'ftp_error': str(msg)}

        except (socket.error, socket.gaierror) as sock_err:
            logger.error(
                'FTP connect error',
                data={
                    'error': str(sock_err),
                    'ftp_server': self.FTP_SERVER,
                }
            )
            return {
                'ftp_error': f"FTP connect error, could not connect to {self.FTP_SERVER}"
            }

        finally:
            # without a QUIT the control connection stays open until the
            # garbage collector kicks in
            if ftp is not None:
                try:
                    ftp.quit()
                except Exception as quit_err:
                    logger.info(f"FTP quit failed: {quit_err}")
