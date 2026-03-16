# --- STAGE 1: BUILDER ---
FROM python:3.13-slim-bookworm AS builder

# Install build dependencies for xmlsec and lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    git \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1 \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .

# 1. Upgrade pip
# 2. Install everything to /install prefix
# 3. Force lxml/xmlsec to build from source to match system libs
RUN pip install --upgrade pip && \
    pip install --prefix=/install gunicorn && \
    pip install --prefix=/install -r requirements.txt && \
    pip install --prefix=/install git+https://github.com/viaacode/mediahaven-python.git@v0.8.1 && \
    pip install --prefix=/install  git+https://github.com/viaacode/chassis.py.git@v0.2.0 && \

    pip install --prefix=/install --no-binary lxml,xmlsec lxml xmlsec

# --- STAGE 2: RUNNER ---
FROM python:3.13-slim-bookworm

WORKDIR /app

# Install runtime libraries for xmlsec and SAML
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxmlsec1 \
    libxmlsec1-openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the pre-compiled packages from builder
COPY --from=builder /install /usr/local
# Copy application code
COPY --chown=1001:0 . .

# Set environment paths correctly
ENV PATH="/usr/local/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# Meemoo Security Standard
USER 1001

# --- GUNICORN CONFIGURATION ---
# 1. Bind to 0.0.0.0 so Kubernetes/Openshift can reach it
# 2. Use 'app.redactietool:app' (file:variable)
# 3. Use 'gthread' worker for better performance with I/O (SAML/API calls)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "--worker-class", "gthread", "wsgi:app"]
