#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers and integrated
#           code from python-saml3 flask demo for SAML authorization
#
#           Thanks to 'suggest library' from Miel Vander Sande that will
#           be used to populate the dropdowns in the metadata
#           form's LOM sections. Suggest is part of the KnowledeGraph project.
#
#  app/redactietool.py
#
#   Application to upload srt file and push into mediahaven.
#   It stores and converts an uploaded srt file to webvtt format,
#   shows preview with flowplayer and subtitles.
#   Metadata is fetched with mediahaven_api using a pid.
#   Authorization is refactored to use SAML.
#   We also use calls to the thesaurus tool using the suggest library
#   from Miel.
#
import json
import os

from flask import (Flask, Response, redirect, render_template, request,
                   send_from_directory, session, url_for)
from flask_api import status
from flask_login import LoginManager, login_required  # current_user
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.config import flask_environment
from app.saml import saml_login
from app.services.elastic_api import ElasticApi
from app.services.ftp_uploader import FtpUploader
from app.services.mediahaven_api import MediahavenApi
from app.services.meta_mapping import MetaMapping
from app.services.subtitle_files import (delete_files, get_vtt_subtitles,
                                         move_subtitle, not_deleted,
                                         save_sidecar_xml, save_subtitles)
from app.services.suggest_api import SuggestApi
from app.services.user import OAS_APPNAME, User, check_saml_session
from app.services.validation import (pid_error, upload_error,
                                     validate_conversion, validate_input,
                                     validate_upload)

app = Flask(__name__)
config = ConfigParser()
logger = logging.get_logger(__name__, config=config)

app.config.from_object(flask_environment())

# session cookie secret key
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'meemoo_saml_secret_to_be_set_using_configmap_or_secrets'
)

# subtitles object store url
app.config['OBJECT_STORE_URL'] = os.environ.get(
    'OBJECT_STORE_URL', 'https://archief-media-qas.viaa.be/viaa/MOB'
)

app.config['SAML_PATH'] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.environ.get('SAML_ENV', 'saml/localhost')
)


# @app.route('/', methods=['GET', 'POST'])
app.add_url_rule('/', view_func=saml_login, methods=['GET', 'POST'])

# optionally session expiry can be set like so if wanted:
# app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=9)
# sesson.permanent = True

# mixin/model for current_user method of flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'saml_login'


@login_manager.request_loader
def load_user_from_request(request):
    user = User()
    if check_saml_session():
        user.save_saml_username(session.get('samlUserdata'))
        return user
    else:
        session.clear()  # clear bad or timed out session


# ====================== Development LOGIN RELATED ROUTES ==========================
@app.route('/legacy_login', methods=['GET'])
def legacy_login():
    return render_template('legacy_login.html')


@app.route('/legacy_login', methods=['POST'])
def login():
    if app.config['DEBUG'] is True or app.config['TESTING']:
        username = request.form.get('username')
        password = request.form.get('password')

        logger.info("POST login =", dictionary={
            'username': username,
            'password': '[FILTERED]'
        })

        if username == 'admin' and password == 'admin':
            session['samlUserdata'] = {}
            session['samlUserdata']['cn'] = [username]
            session['samlUserdata']['apps'] = [OAS_APPNAME]
            return redirect(
                url_for('.search_media')
            )
        else:
            session.clear()  # clear bad or timed out session
            return render_template('legacy_login.html', validation_errors='Fout email of wachtwoord')

    else:
        return render_template('legacy_login.html', validation_errors='Development login disabled')


# ======================== SUBLOADER RELATED ROUTES ===========================
@app.route('/search_media', methods=['GET'])
@login_required
def search_media():
    if 'samlUserdata' in session:
        if len(session['samlUserdata']) > 0:
            attributes = session['samlUserdata'].items()

    SHOW_DEBUG_PIDS = app.config['DEBUG'] is True
    return render_template('search_media.html', **locals())


@app.route('/search_media', methods=['POST'])
@login_required
def post_media():
    pid = request.form.get('pid')
    department = request.form.get('department')

    if not pid:
        return pid_error(pid, 'Geef een PID')
    else:
        if request.form.get('redirect_subtitles') == 'yes':
            logger.info('post_media, editing subtitles', data={'pid': pid})
            return redirect(url_for('.get_upload', **locals()))
        else:
            logger.info('post_media, editing metadata', data={'pid': pid})
            return redirect(url_for('.edit_metadata', **locals()))


@app.route('/upload', methods=['GET'])
@login_required
def get_upload():
    logger.info('get_upload')

    pid = request.args.get('pid').strip()
    department = request.args.get('department')

    validation_error = validate_input(pid, department)
    if validation_error:
        return pid_error(pid, validation_error)

    mh_api = MediahavenApi()
    mam_data = mh_api.find_item_by_pid(department, pid)
    if not mam_data:
        return pid_error(pid, f"PID niet gevonden in {department}")

    # subtitle files already uploaded:
    all_subs = mh_api.get_subtitles(department, pid)
    subfiles = []
    for sub in all_subs:
        subfiles.append(sub.get('Descriptive').get('OriginalFilename'))

    return render_template(
        'subtitles/upload.html',
        pid=pid,
        department=department,
        mam_data=json.dumps(mam_data),
        subtitle_files=subfiles,
        title=mam_data.get('Descriptive').get('Title'),
        description=mam_data.get('Descriptive').get('Description'),
        created=mam_data.get('Descriptive').get('CreationDate'),
        archived=mam_data.get('Descriptive').get('ArchiveDate'),
        original_cp=mam_data.get('Dynamic').get('Original_CP'),
        video_url=mam_data.get('Internal').get('PathToVideo'),
        keyframe=mam_data.get('Internal').get('PathToKeyframe'),
        flowplayer_token=os.environ.get('FLOWPLAYER_TOKEN', 'set_in_secrets')
    )


@app.route('/upload', methods=['POST'])
@login_required
def post_upload():
    tp = {
        'pid': request.form.get('pid'),
        'department': request.form.get('department'),
        'mam_data': request.form.get('mam_data'),
        'video_url': request.form.get('video_url'),
        'subtitle_type': request.form.get('subtitle_type')
    }

    validation_error, uploaded_file = validate_upload(tp, request.files)
    if validation_error:
        return upload_error(tp, validation_error)

    tp['subtitle_file'], tp['vtt_file'] = save_subtitles(
        upload_folder(), tp['pid'], uploaded_file)

    conversion_error = validate_conversion(tp)
    if conversion_error:
        return upload_error(tp, conversion_error)

    logger.info('subtitles/preview', data={
        'pid': tp['pid'],
        'file': tp['subtitle_file']
    })

    video_data = json.loads(tp['mam_data'])
    tp['title'] = video_data.get('Descriptive').get('Title')
    tp['description'] = video_data.get('description')
    tp['keyframe'] = video_data.get('Internal').get('PathToKeyframe')
    tp['created'] = video_data.get('Descriptive').get('CreationDate')
    tp['archived'] = video_data.get('Descriptive').get('ArchiveDate')
    tp['original_cp'] = video_data.get('Dynamic').get('Original_CP')
    tp['flowplayer_token'] = os.environ.get(
        'FLOWPLAYER_TOKEN', 'set_in_secrets')

    return render_template('subtitles/preview.html', **tp)


def upload_folder():
    return os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])


@app.route('/cancel_upload')
@login_required
def cancel_upload():
    pid = request.args.get('pid')
    department = request.args.get('department')
    vtt_file = request.args.get('vtt_file')
    srt_file = request.args.get('srt_file')

    delete_files(upload_folder(), {
        'srt_file': srt_file,
        'vtt_file': vtt_file
    })

    return redirect(url_for('.get_upload', pid=pid, department=department))


@app.route('/send_to_mam', methods=['POST'])
@login_required
def send_subtitles_to_mam():

    tp = {
        'pid': request.form.get('pid'),
        'department': request.form.get('department'),
        'video_url': request.form.get('video_url'),
        'subtitle_type': request.form.get('subtitle_type'),
        'srt_file': request.form.get('subtitle_file'),
        'vtt_file': request.form.get('vtt_file'),
        'xml_file': request.form.get('xml_file'),
        'xml_sidecar': request.form.get('xml_sidecar'),
        'mh_response': request.form.get('mh_response'),
        'mam_data': request.form.get('mam_data'),
        'replace_existing': request.form.get('replace_existing'),
    }

    video_data = json.loads(tp['mam_data'])
    tp['title'] = video_data.get('Descriptive').get('Title')
    tp['keyframe'] = video_data.get('previewImagePath')
    tp['flowplayer_token'] = os.environ.get(
        'FLOWPLAYER_TOKEN', 'set_in_secrets')

    if tp['replace_existing'] == 'cancel':
        # abort and remove temporary files
        delete_files(upload_folder(), tp)

    # extra check to avoid re-sending if user refreshes page
    if not_deleted(upload_folder(), tp['srt_file']):
        metadata = json.loads(tp['mam_data'])
        if not tp['replace_existing']:
            # first request, generate xml_file
            tp['srt_file'] = move_subtitle(upload_folder(), tp)

            tp['xml_file'], tp['xml_sidecar'] = save_sidecar_xml(
                upload_folder(), metadata, tp)

        # upload subtitle and xml sidecar with ftp
        ftp_uploader = FtpUploader()
        ftp_response = ftp_uploader.upload_subtitles(
            upload_folder(), metadata, tp)
        tp['mh_response'] = json.dumps(ftp_response)
        if 'ftp_error' in ftp_response:
            tp['mh_error'] = True

        # cleanup temp files and show final page with mh request results
        delete_files(upload_folder(), tp)
        return render_template('subtitles/sent.html', **tp)
    else:
        # user refreshed page (tempfiles already deleted),
        # or user chose 'cancel' above. in both cases show
        # subtitles already sent
        tp['upload_cancelled'] = True
        return render_template('subtitles/sent.html', **tp)


# for subtitles files we need to switch of caching so we get the latest content
@app.route('/item_subtitles/<string:department>/<string:pid>/<string:subtype>', methods=['GET'])
@login_required
def get_subtitle_by_type(department, pid, subtype):
    mh_api = MediahavenApi()
    sub_response = mh_api.get_subtitle(department, pid, subtype)

    if not sub_response:
        return ""

    object_store_url = app.config.get('OBJECT_STORE_URL')
    object_id = sub_response.get('Internal').get('MediaObjectId', '')
    org_name = sub_response.get('Administrative').get(
        'OrganisationName').upper()
    srt_url = f"{object_store_url}/{org_name}/{object_id}/{object_id}.srt"
    print("SRT LINK:", srt_url)

    response = Response(get_vtt_subtitles(srt_url))
    response.cache_control.max_age = 0
    response.headers.add('Last-Modified', datetime.datetime.now())
    response.headers.add(
        'Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    response.headers.add('Pragma', 'no-cache')
    return response


@app.route('/subtitles/<filename>')
@login_required
def uploaded_subtitles(filename):
    response = send_from_directory(upload_folder(), filename)
    response.cache_control.max_age = 0
    response.headers.add('Last-Modified', datetime.datetime.now())
    response.headers.add(
        'Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    response.headers.add('Pragma', 'no-cache')

    return response


# ====================== Redactietool metadata ROUTES =========================
@app.route('/edit_metadata', methods=['GET'])
@login_required
def edit_metadata():
    pid = request.args.get('pid').strip()
    department = request.args.get('department')
    errors = request.args.get('validation_errors')

    logger.info(f'GET item_metadata pid={pid}')

    validation_error = validate_input(pid, department)
    if validation_error:
        return pid_error(pid, validation_error)

    mh_api = MediahavenApi()
    mam_data = mh_api.find_item_by_pid(department, pid)
    if not mam_data:
        return pid_error(pid, f"PID niet gevonden in {department}")

    mm = MetaMapping()
    template_vars = mm.mh_to_form(pid, department, mam_data, errors)

    return render_template(
        'metadata/edit.html',
        **template_vars
    )


@app.route('/edit_metadata', methods=['POST'])
@login_required
def save_item_metadata():
    pid = request.form.get('pid')
    department = request.form.get('department')

    mh_api = MediahavenApi()
    mam_data = mh_api.find_item_by_pid(department, pid)
    if not mam_data:
        return pid_error(pid, f"PID niet gevonden in {department}")

    mm = MetaMapping()
    template_vars = mm.form_to_mh(request, mam_data)
    frag_id, ext_id, xml_sidecar = mm.xml_sidecar(mam_data, template_vars)
    response = mh_api.update_metadata(department, frag_id, ext_id, xml_sidecar)

    if response['status']:
        template_vars['mh_synced'] = True
    else:
        template_vars['mh_synced'] = False
        template_vars['mh_errors'] = response['errors']

    # we can even do another GET call here to validate the changed modified timestamp

    return render_template(
        'metadata/edit.html',
        **template_vars
    )


@app.route('/publicatie_status', methods=['GET'])
@login_required
def publicatie_status():
    pid = request.args.get('pid')
    department = request.args.get('department')

    # extra request necessary in order to fetch rightsmanagement/permissions
    # can be deprecated if we move to v2
    mh_api = MediahavenApi()
    return {
        'publish_item': mh_api.get_publicatiestatus(department, pid)
    }


@app.route('/onderwijsniveaus', methods=['GET'])
@login_required
def get_onderwijsniveaus():
    suggest_api = SuggestApi()
    return suggest_api.get_onderwijsniveaus()


@app.route('/onderwijsgraden', methods=['GET'])
@login_required
def get_onderwijsgraden():
    suggest_api = SuggestApi()
    return suggest_api.get_onderwijsgraden()


@app.route('/themas', methods=['GET'])
@login_required
def get_themas():
    suggest_api = SuggestApi()
    return suggest_api.get_themas()


@app.route('/vakken', methods=['GET'])
@login_required
def get_vakken():
    suggest_api = SuggestApi()
    return suggest_api.get_vakken()


@app.route('/vakken_suggest', methods=['POST'])
@login_required
def vakken_suggest():
    json_data = request.json
    suggest_api = SuggestApi()
    result = suggest_api.get_vakken_suggesties(
        json_data['graden'], json_data['themas'])
    return result


@app.route('/vakken_related', methods=['POST'])
@login_required
def vakken_related():
    json_data = request.json
    suggest_api = SuggestApi()
    result = suggest_api.get_vakken_related(
        json_data['graden'], json_data['niveaus'])
    return result


@app.route('/keyword_search', methods=['POST'])
@login_required
def keyword_search():
    json_data = request.json
    es_api = ElasticApi()
    return es_api.search_keyword(json_data['qry'])


# =================== HEALTH CHECK ROUTES AND ERROR HANDLING ==================
@app.route("/health/live")
def liveness_check():
    return "OK", status.HTTP_200_OK


@app.route('/404')
def not_found_errorpage():
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized(e):
    # return "<h1>401</h1><p>Unauthorized</p>", 401
    return redirect(url_for('.saml_login'))


@app.errorhandler(404)
def page_not_found(e):
    # return "<h1>404</h1><p>Page not found</p>", 404
    return redirect(url_for('.not_found_errorpage'))


# =============== Main application startup without debug mode ================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)
