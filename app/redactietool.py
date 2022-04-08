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
import os
import json
import datetime

from flask import (Flask, request, render_template, session,
                   redirect, url_for, send_from_directory, Response)

from flask_api import status
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.config import flask_environment
from app.services.mediahaven_api import MediahavenApi
from app.services.elastic_api import ElasticApi
from app.services.suggest_api import SuggestApi
from app.services.ftp_uploader import FtpUploader
from app.services.subtitle_files import (
    save_subtitles, delete_files, save_sidecar_xml,
    move_subtitle, not_deleted, get_vtt_subtitles
)
from app.services.mh_properties import get_property
from app.services.validation import (pid_error, upload_error, validate_input,
                                     validate_upload, validate_conversion)

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from flask_login import LoginManager, login_required  # current_user
from app.services.meta_mapping import MetaMapping
from app.services.user import User, check_saml_session, OAS_APPNAME


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

# optionally session expiry can be set like so if wanted:
# app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=9)
# sesson.permanent = True

# mixin/model for current_user method of flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'


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
            session['samlUserdata']['apps'] = ['broken'+OAS_APPNAME]
            print(">>>>>>>> redirect to search_media")
            return redirect(
                url_for('.search_media')
            )
        else:
            session.clear()  # clear bad or timed out session
            return render_template('legacy_login.html', validation_errors='Fout email of wachtwoord')

    else:
        return render_template('legacy_login.html', validation_errors='Development login disabled')


# ========================== SAML Authentication ==============================
def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=app.config['SAML_PATH'])

    # this is a possible replacement for settings.json to be tested (not sure how certs will load with this) :
    # idp_data = OneLogin_Saml2_IdPMetadataParser.parse_remote(https://example.com/metadatas, entity_id='idp_entity_id')
    # idp_data = OneLogin_Saml2_IdPMetadataParser.parse_remote('https://example.com/auth/saml2/idp/metadata', timeout=5)
    # auth = OneLogin_Saml2_Auth(req, old_settings=idp_data)
    return auth


def prepare_flask_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy()
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    errors = []
    error_reason = None
    not_auth_warn = False
    success_slo = False
    attributes = False
    legacy_login_enabled = app.config['DEBUG'] is True or app.config['TESTING']

    if 'sso' in request.args:
        # If AuthNRequest ID need to be stored in
        # order to later validate it, do instead
        sso_built_url = auth.login()
        session['AuthNRequestID'] = auth.get_last_request_id()
        return redirect(sso_built_url)
    elif 'slo' in request.args:
        name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
        if 'samlNameId' in session:
            name_id = session['samlNameId']
        if 'samlSessionIndex' in session:
            session_index = session['samlSessionIndex']
        if 'samlNameIdFormat' in session:
            name_id_format = session['samlNameIdFormat']
        if 'samlNameIdNameQualifier' in session:
            name_id_nq = session['samlNameIdNameQualifier']
        if 'samlNameIdSPNameQualifier' in session:
            name_id_spnq = session['samlNameIdSPNameQualifier']

        return redirect(
            auth.logout(
                name_id=name_id,
                session_index=session_index,
                nq=name_id_nq,
                name_id_format=name_id_format,
                spnq=name_id_spnq
            )
        )
    elif 'acs' in request.args:
        request_id = None
        if 'AuthNRequestID' in session:
            request_id = session['AuthNRequestID']

        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()
        if len(errors) == 0:
            if 'AuthNRequestID' in session:
                del session['AuthNRequestID']
            session['samlUserdata'] = auth.get_attributes()
            session['samlNameId'] = auth.get_nameid()
            session['samlNameIdFormat'] = auth.get_nameid_format()
            session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
            session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
            session['samlSessionIndex'] = auth.get_session_index()
            self_url = OneLogin_Saml2_Utils.get_self_url(req)
            if 'RelayState' in request.form and self_url != request.form['RelayState']:
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the request.form['RelayState'] is a trusted URL.
                return redirect(
                    auth.redirect_to(
                        request.form['RelayState']
                    )
                )
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()
    elif 'sls' in request.args:
        request_id = None
        if 'LogoutRequestID' in session:
            request_id = session.get(
                'LogoutRequestID', 'empty_logout_request_id')

        def dscb(): return session.clear()

        # HOTFIX so that the POST_DATA is put in GET_DATA and we properly
        # respond to the sls request from our idp
        req['get_data'] = req['post_data']

        # re-init auth with hotfixed request object
        auth = init_saml_auth(req)

        url = auth.process_slo(request_id=request_id, delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the url is a trusted URL.
                return redirect(url)
            else:
                success_slo = True
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()

    if check_saml_session():
        return redirect('/search_media')
    else:
        return render_template(
            'index.html',
            errors=errors,
            error_reason=error_reason,
            not_auth_warn=not_auth_warn,
            success_slo=success_slo,
            attributes=attributes,
            legacy_login_enabled=legacy_login_enabled,
            # validation_errors=f'Invalid login or no access to {OAS_APPNAME}'
        )


# ======================== SUBLOADER RELATED ROUTES ===========================
@app.route('/search_media', methods=['GET'])
@login_required
def search_media():
    if 'samlUserdata' in session:
        if len(session['samlUserdata']) > 0:
            attributes = session['samlUserdata'].items()

    logger.info('search_media')
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
        title=mam_data.get('title'),
        keyframe=mam_data.get('previewImagePath'),
        description=mam_data.get('description'),
        created=get_property(mam_data, 'CreationDate'),
        archived=get_property(mam_data, 'created_on'),
        original_cp=get_property(mam_data, 'Original_CP'),
        # for v2 mam_data['Internal']['PathToVideo']
        video_url=mam_data.get('videoPath'),
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
    tp['title'] = video_data.get('title')
    tp['description'] = video_data.get('description')
    tp['keyframe'] = video_data.get('previewImagePath')
    tp['created'] = get_property(video_data, 'CreationDate')
    tp['archived'] = get_property(video_data, 'created_on')
    tp['original_cp'] = get_property(video_data, 'Original_CP')
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
        'transfer_method': request.form.get('transfer_method')
    }

    video_data = json.loads(tp['mam_data'])
    tp['title'] = video_data.get('title')
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

        if tp['transfer_method'] == 'api':
            mh_api = MediahavenApi()
            if tp['replace_existing'] == 'confirm':
                mh_api.delete_old_subtitle(tp['department'], tp['srt_file'])

            mh_response = mh_api.send_subtitles(upload_folder(), metadata, tp)
            logger.info('send_to_mam', data=mh_response)
            tp['mh_response'] = json.dumps(mh_response)

            if not tp['replace_existing'] and (
                (mh_response.get('status') == 409)
                or
                (mh_response.get('status') == 400)
            ):  # duplicate error can give 409 or 400, show dialog
                return render_template('subtitles/confirm_replace.html', **tp)
        else:
            # upload subtitle and xml sidecar with ftp instead
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

    if response.status_code >= 200 and response.status_code < 300:
        print("Mediahaven save ok, status code=", response.status_code)
        template_vars['mh_synced'] = True
    else:
        template_vars['mh_synced'] = False
        template_vars['mh_errors'] = [response.json()['message']]
        print("Mediahaven ERRORS= ", response.json())

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
    return redirect(url_for('.index'))


@app.errorhandler(404)
def page_not_found(e):
    # return "<h1>404</h1><p>Page not found</p>", 404
    return redirect(url_for('.not_found_errorpage'))


# =============== Main application startup without debug mode ================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)
