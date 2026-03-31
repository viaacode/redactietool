FROM python:3.13-slim-bookworm

# Applications should run on port 8080 so NGINX can auto discover them.
EXPOSE 8080

# Make a new group and user so we don't run as root.
# RUN addgroup --system appgroup && adduser -u 1001 --system appuser --ingroup appgroup --home /app

WORKDIR /app

# Let the appuser own the files so he can rwx during runtime.
COPY --chown=1001:0 . .
RUN  apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev libxmlsec1-dev libxmlsec1-openssl libxslt1-dev zlib1g-dev
# Install gcc and pkg-config to compile uWSGI, xmlsec, and lxml (from source)
RUN set -ex; \
    apt-get install --no-install-recommends -y build-essential pkg-config &&\
    /usr/local/bin/python -m pip install --upgrade pip setuptools wheel ; \
    pip install uWSGI==2.0.31

# Install lxml from source and force it to link against the system libxml2
# (lxml >= 5.x bundles its own libxml2 by default; STATIC_DEPS=false overrides that)
# Then install xmlsec from source so it links against the same system libxml2.
# Both using the same libxml2 is what prevents the runtime 'version mismatch' error.
RUN STATIC_DEPS=false pip install lxml==6.0.2 --no-binary=lxml --no-cache-dir
RUN pip install xmlsec==1.3.17 --no-binary=xmlsec --no-cache-dir

# Verify the two libraries agree on libxml2 at build time
RUN python -c "from lxml import etree; import xmlsec; print('lxml libxml2:', etree.LIBXML_VERSION)"

# We install all our Python dependencies using internal pypi
RUN pip install -r requirements.txt \
    --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-internal/simple \
    --trusted-host do-prd-mvn-01.do.viaa.be \
    --no-cache-dir

RUN apt-get purge -y --auto-remove build-essential pkg-config && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH=/home/appuser/.local/bin:$PATH
# PLEASE use this only in the test keep main image clean
#    pip3 install -r requirements-test.txt && \
#    pip3 install flake8

#USER appuser

ENV SAML_ENV='saml/localhost'
ENV OAS_APPNAME='mediahaven'
ENV FLOWPLAYER_TOKEN='set_in_secrets'
ENV SECRET_KEY='set_in_secrets_for_meemoo_saml_cookie'
ENV OBJECT_STORE_URL='https://archief-media-qas.viaa.be/viaa/MOB'
ENV MEDIAHAVEN_API='https://archief-qas.viaa.be/mediahaven-rest-api'
ENV FTP_SERVER='ftp.viaa.be'
ENV FTP_DIR='/'
ENV TESTBEELD_PERM_ID='uuid_here'
ENV ONDERWIJS_PERM_ID='uuid2_here'
ENV ADMIN_PERM_ID='uuid3_here'
ENV FTP_USER='user'
ENV FTP_PASS='pass'
ENV MEDIAHAVEN_USER='user'
ENV MEDIAHAVEN_PASS='pass'
ENV KEYFRAME_EDITING_LINK='https://archief-qas.viaa.be/player?id='
ENV SPARQL_ENDPOINT='https://sparql_api_url'
ENV SPARQL_USER='user'
ENV SPARQL_PASS='pass'
ENV ES_SERVER='https://elasticsearch-ingest-qas-avo.private.cloud.meemoo.be'
ENV FLASK_ENV=production


# This command will be run when starting the container. It is the same one that
# can be used to run the application locally.
ENTRYPOINT [ "uwsgi", "-i", "uwsgi.ini"]
