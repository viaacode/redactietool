from flask import current_app as app
from flask import redirect, render_template, request, session
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from app.services.user import OAS_APPNAME, User, check_saml_session


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


def saml_login():
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


