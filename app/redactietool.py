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
import datetime
import json
import logging as stdlib_logging
import os

from flask import (Flask, Response, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)
from http import HTTPStatus
from flask_login import LoginManager, login_required  # current_user
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.config import flask_environment
from app.debug_login import legacy_login, legacy_login_submit
from app.saml import saml_login
from app.services.elastic_api import ElasticApi
from app.services.mediahaven_api import MediahavenApi
from app.services.meta_mapping import MetaMapping
from app.services.subtitle_files import (delete_files, get_vtt_subtitles,
                                         move_subtitle,
                                         save_sidecar_xml, save_subtitles)
from app.services.speechmatic_api import SpeechmaticsApi
from app.services.converter import ConverterService
from app.services.jobs import JobsService
from app.services.jobs_cron import start_scheduler
from app.services.suggest_api import SuggestApi
from app.services.user import User, check_saml_session
from app.services.validation import (pid_error, validate_input,
                                     validate_optional_subtitle_upload)

app = Flask(__name__)
config = ConfigParser()
logger = logging.get_logger(__name__, config=config)


class _SuppressStaticAndHealthLogs(stdlib_logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return '/static/' not in msg and '/health/' not in msg


stdlib_logging.getLogger('werkzeug').addFilter(_SuppressStaticAndHealthLogs())

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


# add routes to saml.py module for login/logout with saml
app.add_url_rule('/', view_func=saml_login, methods=['GET', 'POST'])

# Start background scheduler that polls Speechmatics for pending job results.
# In multi-worker deployments, enable this only in a single dedicated process
# by setting the REDACTIETOOL_ENABLE_SCHEDULER environment variable.
start_scheduler()

# add routes for legacy login (without saml) when testing or debugging
print("DEBUG legacy_login routes added")
app.add_url_rule('/legacy_login', view_func=legacy_login, methods=['GET'])
app.add_url_rule('/legacy_login', view_func=legacy_login_submit, methods=['POST'])


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


_IMMUTABLE_STATIC_PATHS = frozenset([
    '/static/avo-logo-i.svg',
    '/static/images/saml_login_background.jpg',
])

# Prefixes whose entire subtree is content-hashed (safe for immutable caching)
_IMMUTABLE_STATIC_PREFIXES = (
    '/static/vue/',
    '/static/bulma/fonts/',
)

# Vendored/minified third-party assets: stable but not content-hashed
_VENDOR_STATIC_PATHS = frozenset([
    '/static/flowplayer.min.js',
    '/static/flowplayer.css',
    '/static/quill.js',
    '/static/quill.snow.css',
    '/static/subtitles.min.js',
    '/static/turndown.js',
    '/static/bulma/bulma-tooltip.min.css',
    '/static/bulma/bundle.js',
    '/static/favicon.ico',
])

# App-specific assets without content hashes: cache briefly to allow quick rollouts
_APP_STATIC_PATHS = frozenset([
    '/static/redactietool_v2.js',
    '/static/style.css',
    '/static/bulma/overrides.css',
    '/static/bulma/core.css',
    '/static/bulma/modal_dialog.js',
])


@app.after_request
def set_static_cache_headers(response):
    path = request.path
    if path in _IMMUTABLE_STATIC_PATHS or any(path.startswith(p) for p in _IMMUTABLE_STATIC_PREFIXES):
        response.cache_control.public = True
        response.cache_control.max_age = 31536000
        response.cache_control.immutable = True
    elif path in _VENDOR_STATIC_PATHS:
        response.cache_control.public = True
        response.cache_control.max_age = 604800  # 1 week
    elif path in _APP_STATIC_PATHS:
        response.cache_control.public = True
        response.cache_control.max_age = 3600  # 1 hour
    return response


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
        logger.info('post_media, editing metadata', data={'pid': pid})
        return redirect(url_for('.edit_metadata', **locals()))


def upload_folder():
    path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    os.makedirs(path, exist_ok=True)
    return path


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
    jobs_service = JobsService()
    mam_data = mh_api.find_item_by_pid(department, pid)
    if not mam_data:
        return pid_error(pid, f"PID niet gevonden in {department}")

    try:
        speechmatics_data = jobs_service.get_job(department, pid)
    except Exception as ex:
        logger.error('edit_metadata: failed to fetch job data', data={'pid': pid, 'error': str(ex)})
        speechmatics_data = None
    mm = MetaMapping()
    template_vars = mm.mh_to_form(pid, department, mam_data, speechmatics_data, errors)

    # Restore POST result state passed via session (PRG pattern)
    post_result = session.pop('post_result', {})
    if post_result.get('mh_synced') is not None:
        template_vars['mh_synced'] = post_result['mh_synced']
    if post_result.get('mh_errors'):
        template_vars['mh_errors'] = post_result['mh_errors']
    if post_result.get('subtitle_synced'):
        template_vars['subtitle_synced'] = True
    if post_result.get('subtitle_synced_filename'):
        template_vars['subtitle_synced_filename'] = post_result['subtitle_synced_filename']
    if post_result.get('subtitle_error'):
        template_vars['subtitle_error'] = post_result['subtitle_error']

    # Fetch existing subtitle files from MediaHaven
    all_subs = mh_api.get_subtitles(department, pid)
    subtitle_files = []
    existing_subtitle_types = []
    for sub in all_subs:
        filename = sub.get('Descriptive', {}).get('OriginalFilename', '')
        fragment_id = sub.get('Internal', {}).get('FragmentId', '')
        subtitle_files.append({'filename': filename, 'fragment_id': fragment_id})
        if '_open.' in filename:
            existing_subtitle_types.append('open')
        if '_closed.' in filename:
            existing_subtitle_types.append('closed')
    template_vars['subtitle_files'] = subtitle_files
    template_vars['has_existing_subtitle'] = len(subtitle_files) > 0
    template_vars['existing_subtitle_types'] = existing_subtitle_types

    return render_template(
        'metadata/edit.html',
        **template_vars
    )


def _subtitle_upload_error(errors):
    """Return a human-readable subtitle upload error message.

    Detects EDUPLICATE responses and surfaces the conflicting record ID.
    """
    error_str = errors[0] if errors else ''
    if 'EDUPLICATE' in error_str:
        try:
            error_data = json.loads(error_str)
            record_ids = error_data.get('ExistingRecordIds', [])
            record_id = record_ids[0] if record_ids else '(onbekend)'
            return f'Dit ondertitel bestand is reeds in gebruik voor Record: {record_id}'
        except Exception:
            pass
    return 'Fout bij uploaden ondertitel: ' + error_str


@app.route('/edit_metadata', methods=['POST'])
@login_required
def save_item_metadata():
    pid = request.form.get('pid')
    department = request.form.get('department')

    mh_api = MediahavenApi()
    mam_data = mh_api.find_item_by_pid(department, pid)
    if not mam_data:
        return pid_error(pid, f"PID niet gevonden in {department}")

    # Check if a subtitle file was attached and validate it
    subtitle_validation_error = validate_optional_subtitle_upload(request.files)
    has_subtitle_file = (
        'subtitle_file' in request.files
        and request.files['subtitle_file'].filename != ''
    )
    uploaded_file = request.files.get('subtitle_file') if has_subtitle_file else None
    subtitle_type = request.form.get('subtitle_type', 'closed')

    # Phase 1 — Metadata save (unchanged logic)
    mm = MetaMapping()
    template_vars = mm.form_to_mh(request, mam_data)
    frag_id, ext_id, xml_sidecar = mm.xml_sidecar(mam_data, template_vars)
    response = mh_api.update_metadata(department, frag_id, ext_id, xml_sidecar)

    if response['status']:
        template_vars['mh_synced'] = True
    else:
        template_vars['mh_synced'] = False
        template_vars['mh_errors'] = response['errors']

    # Phase 2 — Subtitle handling
    replace_subtitle = request.form.get('replace_subtitle') == 'confirm'
    logger.info(
        'subtitle upload check',
        data={
            'pid': pid,
            'mh_synced': template_vars.get('mh_synced'),
            'has_subtitle_file': has_subtitle_file,
            'subtitle_validation_error': subtitle_validation_error,
            'replace_subtitle': replace_subtitle,
        }
    )
    if template_vars['mh_synced']:
        if has_subtitle_file and not subtitle_validation_error:
            # Upload subtitle directly via MediaHaven API
            try:
                tp = {
                    'pid': pid,
                    'department': department,
                    'subtitle_type': subtitle_type,
                }

                # If replacing, delete existing subtitle record from MH first
                if replace_subtitle:
                    existing_sub = mh_api.get_subtitle(department, pid, subtitle_type)
                    if existing_sub:
                        sub_fragment_id = existing_sub.get(
                            'Internal', {}).get('FragmentId')
                        if sub_fragment_id:
                            del_response = mh_api.delete_subtitle(
                                sub_fragment_id,
                                reason=f"Replacing subtitle for {pid}"
                            )
                            if not del_response['status']:
                                template_vars['subtitle_error'] = (
                                    'Fout bij verwijderen bestaand ondertitelbestand: '
                                    + ', '.join(del_response['errors'])
                                )

                if not template_vars.get('subtitle_error'):
                    tp['srt_file'], tp['vtt_file'] = save_subtitles(
                        upload_folder(), pid, uploaded_file)
                    if tp['srt_file']:
                        tp['srt_file'] = move_subtitle(upload_folder(), tp)
                        tp['xml_file'], xml_sidecar_data = save_sidecar_xml(
                            upload_folder(), mam_data, tp)

                        srt_path = os.path.join(upload_folder(), tp['srt_file'])
                        api_response = mh_api.upload_subtitle(
                            srt_path, tp['srt_file'], xml_sidecar_data)

                        delete_files(upload_folder(), tp)
                        if not api_response['status']:
                            template_vars['subtitle_error'] = _subtitle_upload_error(
                                api_response['errors'])
                        else:
                            template_vars['subtitle_synced'] = True
                            template_vars['subtitle_synced_filename'] = f"{pid}_{subtitle_type}.srt"
                    else:
                        template_vars['subtitle_error'] = 'Ondertitels moeten in SRT formaat'
            except Exception as e:
                logger.exception('subtitle upload failed', data={'pid': pid, 'error': str(e)})
                template_vars['subtitle_error'] = str(e)

        if subtitle_validation_error and has_subtitle_file:
            template_vars['subtitle_error'] = subtitle_validation_error

    # Re-fetch subtitle info for the template
    all_subs = mh_api.get_subtitles(department, pid)
    subtitle_files = []
    existing_subtitle_types = []
    for sub in all_subs:
        filename = sub.get('Descriptive', {}).get('OriginalFilename', '')
        fragment_id = sub.get('Internal', {}).get('FragmentId', '')
        subtitle_files.append({'filename': filename, 'fragment_id': fragment_id})
        if '_open.' in filename:
            existing_subtitle_types.append('open')
        if '_closed.' in filename:
            existing_subtitle_types.append('closed')
    template_vars['subtitle_files'] = subtitle_files
    template_vars['has_existing_subtitle'] = len(subtitle_files) > 0
    template_vars['existing_subtitle_types'] = existing_subtitle_types

    # Re-fetch speechmatics data so the AI section stays populated after save
    jobs_service = JobsService()
    try:
        speechmatics_data = jobs_service.get_job(department, pid)
    except Exception as ex:
        logger.error('save_item_metadata: failed to fetch job data', data={'pid': pid, 'error': str(ex)})
        speechmatics_data = None
    template_vars['sm_job_status'] = speechmatics_data.get('status') if speechmatics_data else None
    template_vars['sm_job_errors'] = speechmatics_data.get('errors') if speechmatics_data else None
    template_vars['sm_job_transcription'] = speechmatics_data.get('transcription') if speechmatics_data else None
    template_vars['sm_job_summary'] = speechmatics_data.get('summary') if speechmatics_data else None
    template_vars['sm_job_chapters'] = json.loads(speechmatics_data['chapters']) if speechmatics_data and isinstance(speechmatics_data.get('chapters'), str) else (speechmatics_data.get('chapters') if speechmatics_data else None)

    session['post_result'] = {
        'mh_synced': template_vars.get('mh_synced'),
        'mh_errors': template_vars.get('mh_errors'),
        'subtitle_synced': template_vars.get('subtitle_synced'),
        'subtitle_synced_filename': template_vars.get('subtitle_synced_filename'),
        'subtitle_error': template_vars.get('subtitle_error'),
    }

    return redirect(url_for('edit_metadata', pid=pid, department=department))


@app.route('/delete_subtitle', methods=['POST'])
@login_required
def delete_subtitle():
    data = request.get_json()
    fragment_id = data.get('fragment_id')
    pid = data.get('pid')

    mh_api = MediahavenApi()
    result = mh_api.delete_subtitle(fragment_id, reason=f"Deleted by editor for {pid}")

    return jsonify(result)


@app.route('/subtitle_files', methods=['GET'])
@login_required
def get_subtitle_files():
    pid = request.args.get('pid')
    department = request.args.get('department')

    mh_api = MediahavenApi()
    all_subs = mh_api.get_subtitles(department, pid)
    subtitle_files = []
    for sub in all_subs:
        filename = sub.get('Descriptive', {}).get('OriginalFilename', '')
        fragment_id = sub.get('Internal', {}).get('FragmentId', '')
        subtitle_files.append({'filename': filename, 'fragment_id': fragment_id})

    return jsonify(subtitle_files)


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

@app.route('/speechmatic/generate', methods=['POST'])
@login_required
def generate_transcript():
    json_data = request.json
    department = json_data.get('department')
    pid = json_data.get('pid')
    language = json_data.get('language') or 'nl'

    if not pid or not department:
        return {
            'error': 'pid and department are required in request body'
        }, HTTPStatus.BAD_REQUEST

    jobs_service = JobsService()
    mh_api = MediahavenApi()
    speechmatics_api = SpeechmaticsApi()

    try:
        mam_data = mh_api.find_item_by_pid(department, pid)
        if not mam_data:
            return {
                'error': f'PID not found: {pid}'
            }, HTTPStatus.NOT_FOUND
        
        job = jobs_service.get_job(department, pid)
        if job and job["status"] in ('created', 'running'):
            return {
                'error': f'Job already exists for pid: {pid} with status: {job["status"]}, but not processed yet'
            }, HTTPStatus.CONFLICT

        # If job does not exist, or is completed/rejected/deleted/expired, launch a new job

        video_url = mam_data.get('Internal', {}).get('PathToVideo')
        if not video_url:
            return {
                'error': f'No media url found for pid: {pid}'
            }, HTTPStatus.NOT_FOUND
        converter = ConverterService();
        temp_video_url = converter.get_media_url(video_url, '', '')
        if(not temp_video_url):
            return {
                'error': f'Failed to get temporary media url for pid: {pid}'
            }, HTTPStatus.INTERNAL_SERVER_ERROR
        logger.info(f"Launching transcription job for video url: {temp_video_url} with language: {language}")
        job_id = speechmatics_api.launch_job(temp_video_url, language=language)
        if(job is None):
            logger.info("Job is None, creating new job in database")
            jobs_service.create_job(department, pid, job_id)
        else:
            logger.info(f"Job already exists for pid: {pid}, updating with new job_id: {job_id} and resetting status")
            jobs_service.update_job(job["id"], speechmatic_job_id=job_id, status='created', processed_at=None)
        return {
            'department': department,
            'pid': pid,
            'job_id': job_id
        }, HTTPStatus.OK
    except Exception as ex:
        logger.exception('generate transcript failed', data={'pid': pid, 'error': str(ex)})
        return {
            'error': str(ex)
        }, HTTPStatus.INTERNAL_SERVER_ERROR
# Fetch status of a transcription job
@app.route('/<string:department>/<string:pid>/speechmatic/status', methods=['GET'])
@login_required
def transcription_status(department, pid):
    speechmatics_api = SpeechmaticsApi()
    jobs_service = JobsService()
    try:
        job = jobs_service.get_job(department, pid)
        if(not job):
            return {
                'job_id': None,
                'status': 'not found'
            }, HTTPStatus.NOT_FOUND
        if (job["processed_at"] is not None):
            status = job["status"]
            errors = []
        else:
            status, errors = speechmatics_api.get_job_status(job["speechmatic_job_id"])
            error_text = ' '.join(errors) if errors else None
            jobs_service.update_job(job["id"], status=status, errors=error_text)

            if status == 'done':
                logger.info('transcription_status: job done, fetching result immediately', data={'job_id': job["id"]})
                try:
                    result = speechmatics_api.get_job_result(job["speechmatic_job_id"])
                    processed_result = speechmatics_api.parse_result(result)
                    jobs_service.mark_processed(
                        job_id=job["id"],
                        transcription=processed_result.get('transcription'),
                        summary=processed_result.get('summary'),
                        chapters=json.dumps(processed_result.get('chapters')),
                        status='done',
                    )
                    logger.info('transcription_status: result stored', data={'job_id': job["id"]})
                except Exception as result_ex:
                    logger.exception('transcription_status: failed to fetch/store result', data={'job_id': job["id"], 'error': str(result_ex)})

        return {
            'job_id': job["id"],
            'status': status,
            'errors': errors,
        }, HTTPStatus.OK
    except Exception as ex:
        logger.exception(
            'fetching transcription status failed',
            data={
                'department': department,
                'pid': pid,
                'error': str(ex),
            },
        )
        return {
            'error': str(ex)
        }, HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/<string:department>/<string:pid>/speechmatic/result', methods=['GET'])
@login_required
def transcription_result(department, pid):
    jobs_service = JobsService()
    try:
        job = jobs_service.get_job(department, pid)
        if not job:
            return {'error': 'Job not found'}, HTTPStatus.NOT_FOUND

        if job['processed_at'] is not None:
            return {
                'job_id': job['id'],
                'status': job['status'],
                'transcript': job['transcription'],
                'summary': job['summary'],
                'chapters': job['chapters'],
            }, HTTPStatus.OK

        return {
            'job_id': job['id'],
            'status': job['status'],
            'message': 'Transcription not completed yet'
        }, HTTPStatus.OK
    except Exception as ex:
        logger.exception('fetching transcription result failed', data={'error': str(ex)})
        return {'error': str(ex)}, HTTPStatus.INTERNAL_SERVER_ERROR

# Ticket was moved to the backlog
# @app.route('/speechmatic/jobs', methods=['GET'])
# def list_jobs():
#     jobs_service = JobsService()
#     try:
#         jobs = jobs_service.list_jobs()
#         return {
#             'jobs': jobs
#         }, HTTPStatus.OK
#     except Exception as ex:
#         logger.exception('listing transcription jobs failed', data={'error': str(ex)})
#         return {
#             'error': str(ex)
#         }, HTTPStatus.INTERNAL_SERVER_ERROR

# =================== HEALTH CHECK ROUTES AND ERROR HANDLING ==================
@app.route("/health/live")
def liveness_check():
    return "OK", HTTPStatus.OK


@app.route('/404')
def not_found_errorpage():
    return render_template('404.html'), HTTPStatus.NOT_FOUND


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
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')), debug=False)
