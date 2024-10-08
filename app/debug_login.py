from flask import current_app as app
from flask import redirect, render_template, request, session, url_for
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.services.user import OAS_APPNAME

config = ConfigParser()
logger = logging.get_logger(__name__, config=config)


# link to this route is only shown when DEBUG = True or env == TESTING
# we also double check in submit if this is the case and else show error that iss disabled

# method GET /legacy_login
def legacy_login():
    return render_template('legacy_login.html')


# method POST /legacy_login
def legacy_login_submit():
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

