# Redactie tool

## Synopsis
Upload form for subtitles as collateral for mediaobject and editing metadata using calls
to knowledge graph. Searches by pid. Shows overview page with selection to either edit metadata
or upload new subtitle file. Shows flowplayer with subtitles after you upload a valid srt.
Subtitle srt is converted to webvtt for pre-viewing in flowplayer.
Finally submit to mediahaven (show confirmation dialog if a srt is already linked).
Allows basically to upload both closed and open srt files to videos for 'testbeeld' tenant
(tenant is now only one but can be easily extended for multiple tenants).

## Functional

### Server

| **Environment**     |  **Host**         |
| :----------------:  | :---------------: |
| INT                 | https://redactie-int.private.cloud.meemoo.be/  |
| QAS                 | https://redactie-qas.hetarchief.be  |
| PRD                 | https://redactie.hetarchief.be  |


### Prerequisites

* Git
* Docker
* Python 3.7+
* Linux (if you want to run it locally, uwsgi is not available on other platforms.)
* Access to the meemoo PyPi

### Usage

1. Clone this repository with:

    `$ git clone https://github.com/viaacode/redactietool.git`

2. Change into the new directory.

### Running locally

There is a Makefile included now. If you run make without arguments you can
see all available commands:

```
$ make

Available make commands:

  install               install packages and prepare environment
  clean                 remove all temporary files
  lint                  run the code linters
  format                reformat code
  test                  run all the tests
  coverage              run tests and generate coverage report
  server                start uvicorn development server and serve application locally
  debug                 start server in debugging mode for auto restarting after code changes etc.
  dockerrun             run docker image and serve web application in docker
                        (normally only needed if there are deploy issues)
  preview_bulma         Preview changed bulma styling before copying into flask
  precompile_bulma      re-compile bulma with custom styling and injecet into flask app/static folder
  vue_develop           Start Vue.js frontend server for developing Vue components
  vue_develop_api       Start mocking server to supply suggest json content with CORS for calling during vue_develop cycle
  precompile_assets     re-compile vue components for release and inject into flask app/static folder

```


1. Start by running make install which installs the pip packages and sets up the environment.
First make sure you can also fetch the VIAA/Meemoo specific packages.
This is done on macOS by editing the pip configuration file and then running make install:

macOS additional packages needed:
```
brew install libxml2 libxmlsec1 pkg-config
```

```
brew tap-new $USER/local
brew extract --version=1.2.37 libxmlsec1 $USER/local
brew uninstall libxmlsec1
brew install $USER/local/libxmlsec1@1.2.37
```
Now lxml works again. Later when lxml is fixed to work with newer libxmlsec1 again we can revert this like so:
```

# once python-xmlsec supports 1.3+ we can do following to undo it:
# brew uninstall $USER/local/libxmlsec1@1.2.37
# brew untap $USER/local
```

UPDATE for mac currently the libxmlsec1 installed with brew is a version that's incompatible with python package.
We need to use this until 

```
$ vi .config/pip/pip.conf

insert following:
[global]
index = http://meemoo_mvn_server:PORT/repository/pypi-all/pypi
index-url = http://meemoo_mvn_server:PORT/repository/pypi-all/simple
trusted-host = meemoo_mvn_server 


$ make install
```

This creates a virtual env and installs all packages.


2. Start the server in debug mode like so:

```
$ make debug
__________           .___              __  .__         ___________           .__   
\______   \ ____   __| _/____    _____/  |_|__| ____   \__    ___/___   ____ |  |  
 |       _// __ \ / __ |\__  \ _/ ___\   __\  |/ __ \    |    | /  _ \ /  _ \|  |  
 |    |   \  ___// /_/ | / __ \\  \___|  | |  \  ___/    |    |(  <_> |  <_> )  |__
 |____|_  /\___  >____ |(____  /\___  >__| |__|\___  >   |____| \____/ \____/|____/
        \/     \/     \/     \/     \/             \/                              

                 Develop mode, running on http://localhost:8080 


 * Serving Flask app "app.redactietool" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
{"message": " * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)"}
{"message": " * Restarting with stat"}
{"message": " * Debugger is active!"}

```


3. Run the tests with:

    `$ make test`

5. To run the web application in production mode use this make command :

   `$ make server`

The application is now serving requests on `localhost:8080`. Try it with:

    `$ curl -v -X GET http://127.0.0.1:8080/`

Or just visit this url in your browser http://127.0.0.1:8080

### Running using Docker

1. Build the container and run it:

   `$ make dockerrun`

### Helper scripts
To run the tests locally and also run flake8 linter/code checking:
```

$ make test    
===================================== test session starts ======================================
platform darwin -- Python 3.9.7, pytest-5.4.1, py-1.10.0, pluggy-0.13.1 -- /Users/wschrep/FreelanceWork/VIAA/subloader/python_env/bin/python
cachedir: .pytest_cache
rootdir: /Users/wschrep/FreelanceWork/VIAA/redactietool
plugins: recording-0.11.0, cov-2.8.1, mock-3.5.1
collected 29 items                                                                             

tests/test_app.py::test_home PASSED                                                      [  3%]
tests/test_app.py::test_liveness_check PASSED                                            [  6%]
tests/test_app.py::test_search_media_security PASSED                                     [ 10%]
tests/test_app.py::test_search_media PASSED                                              [ 13%]
tests/test_app.py::test_invalid_pid_entry PASSED                                         [ 17%]
tests/test_app.py::test_empty_pid PASSED                                                 [ 20%]
tests/test_app.py::test_wrong_pid_entry PASSED                                           [ 24%]
tests/test_app.py::test_working_pid_search PASSED                                        [ 27%]
tests/test_app.py::test_bad_srt_upload PASSED                                            [ 31%]
tests/test_app.py::test_invalid_upload PASSED                                            [ 34%]
tests/test_app.py::test_empty_upload PASSED                                              [ 37%]
tests/test_app.py::test_valid_subtitle PASSED                                            [ 41%]
tests/test_app.py::test_valid_subtitle_capitals PASSED                                   [ 44%]
tests/test_app.py::test_cancel_upload PASSED                                             [ 48%]
tests/test_app.py::test_subtitle_videoplayer_route PASSED                                [ 51%]
tests/test_app.py::test_subtitle_videoplayer_route_unknownfile PASSED                    [ 55%]
...

tests/test_sidecar.py::test_sidecar_v2 PASSED                                            [100%]
================================= 25 passed in 1.63s =================================
Running flake8 linter...
ALL OK
```
If you get flake8 warnings during development there's a scripts/autopep command you can run
that will auto-fix most styling issues (basically a python equivalent to rubocop -a used in ruby projects).


### Tests code coverage

Test coverage report can be generated with following coverage makefile command:

```
$ make coverage

...
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/__init__.py                       0      0   100%
app/config.py                        20      0   100%
app/redactietool.py                 339     58    83%
app/services/ftp_uploader.py         33     10    70%
app/services/input_escaping.py       35      0   100%
app/services/mediahaven_api.py      103     22    79%
app/services/meta_mapping.py         90      1    99%
app/services/mh_properties.py        70     18    74%
app/services/srt_converter.py        18      3    83%
app/services/subtitle_files.py       71      2    97%
app/services/suggest/Suggest.py      84     10    88%
app/services/suggest_api.py          40     10    75%
app/services/user.py                 18      1    94%
app/services/validation.py           38      3    92%
app/services/xml_sidecar.py         111      3    97%
debug.py                              3      3     0%
tests/__init__.py                     2      0   100%
tests/conftest.py                    10      0   100%
tests/fixtures.py                     7      0   100%
tests/test_app.py                   257      0   100%
tests/test_authorization.py          20      0   100%
tests/test_sidecar.py                10      0   100%
tests/test_srt_converter.py           5      0   100%
tests/test_suggest.py                42      0   100%
wsgi.py                               3      3     0%
-----------------------------------------------------
TOTAL                              1429    147    90%
Coverage HTML written to dir htmlcov
```

Then you can open the generated test coverage report here:
```
open htmlcov/index.html
```

### Environment variables

Best set following environment variables before running the server. This
allows login to work and also makes the mediahaven calls to upload the srt and lookup
metadata by pid functional:

```
export MEDIAHAVEN_API=https://archief-qas.viaa.be/mediahaven-rest-api
export MEDIAHAVEN_USER= lookup in team pass
export MEDIAHAVEN_PASS= lookup in team pass
export SAML_ENV 'saml/localhost' # or 'saml/prd' or...
export OAS_APPNAME 'mediahaven'  # or whatever the application access app name needs be
export SECRET_KEY 'set_in_secrets_for_meemoo_saml_cookie'
export OBJECT_STORE_URL 'https://archief-media-qas.viaa.be/viaa/MOB'
export FTP_SERVER '' # ftp url for uploading subtitles (internal vpn url)
export FTP_DIR '/'
export TESTBEELD_PERM_ID 'uuid_here'
export ONDERWIJS_PERM_ID 'uuid2_here'
export ADMIN_PERM_ID 'uuid3_here'
export FTP_USER 'user'
export FTP_PASS 'pass'
export KEYFRAME_EDITING_LINK 'https://archief-qas.viaa.be/player?id='
export SPARQL_ENDPOINT = 'https://sparql_api_url'
export SPARQL_USER = lookup in team pass
export SPARQL_PASS = lookup in team pass
export FLASK_ENV=PRODUCTION  
export FLOWPLAYER_TOKEN= lookup or ask Bart or Walter for this token
```

### Running the server locally:

To run a server on port 8080:

```
$ make server
```
The root page is now a login screen that both supports a form based login and a one button/saml authentication
which shares your login with other Meemoo applications.

following this link <a href="http://127.0.0.1:8080/">Redactietool localhost</a> after you have the server running.


During development you can autoformat and check linting errors like so:
```
$ make lint
```

Auto reformatting (a lot like rubocop but then with python):
```
$ make format
```


### Updating the bulma styling

To keep inline with most of our other web applications. A new makefile command called precompile_assets was added.
This recompiles the bulma sass files with your customized variables and then places this in the correct location in the
flask application static assets folder:

```
$ make precompile_bulma
re-compiling bulma components...

> bulma_latest_version@0.9.3 build frontend/bulma_styling 
> webpack --mode production

asset css/mystyles.css 169 KiB [compared for emit] (name: main)
asset js/bundle.js 349 bytes [compared for emit] [minimized] (name: main)
Entrypoint main 170 KiB = css/mystyles.css 169 KiB js/bundle.js 349 bytes
orphan modules 172 KiB (javascript) 937 bytes (runtime) [orphan] 7 modules
runtime modules 274 bytes 1 module
cacheable modules 79 bytes (javascript) 169 KiB (css/mini-extract)
  javascript modules 79 bytes
    ./src/index.js 29 bytes [built] [code generated]
    ./src/mystyles.scss 50 bytes [built] [code generated]
  css modules 169 KiB
    css ./node_modules/css-loader/dist/cjs.js!./node_modules/sass-loader/dist/cjs.js??ruleSet[1].rules[0].use[2]!./src/mystyles.scss 68 bytes [built] [code generated]
    css ./node_modules/css-loader/dist/cjs.js!./node_modules/sass-loader/dist/cjs.js??ruleSet[1].rules[0].use[2]!./src/mystyles.scss (1) 169 KiB [built] [code generated]
webpack 5.64.1 compiled successfully in 1236 ms
updating flask core css and overrides...
all done.
```


### Developing on the Vue.js components used in the metadata form

To easily work on the Vue.js frontend there's now a new makefile command:

```
$ make vue_develop
```

Then you just open a browser to port http://localhost:8081 and whenever you edit something in
frontend/redactietool_widgets/src folder this will auto reload and show your changes.


The frontend also needs some data to work on. To be able to work fully offline there is also a mocking server
that supplies data to the frontend to populate the dropdowns and vakken suggestions. To start it just use the
following make command in a seperate terminal window:

```
$ make vue_develop_api
```
That starts a seperate minimal flask server with some mocked data responses.

Once you are satisfied with the updates you can push it to flask and it will automatically appear inside the metadata
edit form. For making a new build of the vue components and auto inject into the flask jinja templates you use the following
makefile command:

```
$ make precompile_assets

 DONE  Compiled successfully in 2790ms

  File                                   Size                Gzipped

  dist/js/chunk-vendors.fd3d1052.js      138.53 KiB          46.88 KiB
  dist/js/app.e883cd90.js                18.34 KiB           4.84 KiB
  dist/modal_dialog.js                   2.06 KiB            0.67 KiB
  dist/bundle.js                         0.34 KiB            0.24 KiB
  dist/mystyles.css                      188.28 KiB          25.40 KiB
  dist/css/chunk-vendors.ac5b10c9.css    7.29 KiB            1.71 KiB
  dist/css/app.a5090ff4.css              1.23 KiB            0.45 KiB
  dist/overrides.css                     0.22 KiB            0.16 KiB

  Images and other types of assets omitted.

 DONE  Build complete. The dist directory is ready to be deployed.
 INFO  Check out deployment instructions at https://cli.vuejs.org/guide/deployment.html

Updating vue includes in flask app...done.
```

The benefit here is it auto generates a unique and minified app.xyz.js file so the users see the new vue application when visiting the site without the need to shift-reload and also we update the version (git tag) in the dropdown menu so we can see what version is deployed on the openshift server.
It also updates the flask base.html so that the new javascript and css imports point to the latest version.


### SAML authentication

Implementation was done using OneLogin's SAML Python Toolkit here https://github.com/onelogin/python3-saml.
To have a seperate settings.json file per environment we made the following structure:
```
app/saml
├── int
│   ├── advanced_settings.json
│   ├── certs
│   │   └── README
│   └── settings.json
├── localhost
│   ├── advanced_settings.json
│   ├── certs
│   │   └── README
│   └── settings.json
├── prd
│   ├── advanced_settings.json
│   ├── certs
│   │   └── README
│   └── settings.json
└── qas
    ├── advanced_settings.json
    ├── certs
    │   └── README
    └── settings.json
```

So for each environment a sp.key and sp.crt file is inserted using a volume mount that points to some openshift secrets defined in
redactietool-saml-qas and redactietool-saml-prd. They mount to /app/app/saml/qas/sp.key and /app/app/saml/prd/sp.key and sp.crt respectively.

Future work could involve instead of having a seperate settings.json and advanced_settings.json per environment to do parsing of the 
the xml response from the idp and then generating the settings.json upon application startup. Mind that we still would need a way to
correctly fill in the sp urls per environment also. The only real benefit would be that the public x509cert and the two urls singleSignOnService
and singleLogoutService would be refetched dynamically upon application startup (but if these are changed you still need to remember to restart all
related pods also).



### Dislaimer regarding pytest pyvcr recordings.
For integration tests with other services like Mediahaven API and oas server logins we use pytest-recording pip package.
If you want to rerecord the automated request responses used in some tests you can do so by deleting the yaml files in tests/cassettes.
If you write new tests be sure to also filter out the authorization headers. Before this was done/configured we accidentally exposed a basic auth header in all
generated yaml files (and this contains the pasword that is stored in normally an env var or secret because the header can be decoded).

To filter out headers in recorded api responses best use this snippet:
```
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "record_mode": "once",
        "filter_headers": ["authorization"]
    }
```
