# Gebruik officiële Python image
FROM python:3.11-slim-bookworm

# Zet vereiste environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1 \
    CHROME_BIN=/usr/bin/chromium \
    CHROME_PATH=/usr/lib/chromium/ \
    PLAYWRIGHT_BROWSERS_PATH=/usr/bin/chromium \
    POETRY_VIRTUALENVS_CREATE=false \
    # Voeg debug logging toe
    POETRY_VERBOSE=1 \
    PYTHONVERBOSE=1

# Installeer system dependencies voor Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    chromium \
    chromium-driver \
    # Benodigde libraries voor Chromium
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgtk-3-0 \
    libgbm1 \
    # Debug tools
    procps \
    # Schoon op na installatie
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installeer Poetry met specifieke versie check
RUN pip install "poetry==$POETRY_VERSION" && \
    poetry --version

# Debug: Toon werkdirectory
WORKDIR /app
RUN pwd && ls -la

# Kopieer alleen de app directory en poetry files
COPY app/ ./app/
COPY pyproject.toml poetry.lock ./

# Debug: Toon poetry files en valideer
RUN ls -la && \
    cat pyproject.toml && \
    poetry check --no-interaction || true

# Installeer dependencies zonder het hoofdproject
RUN poetry install --only main --no-root --no-interaction --verbose

# Debug: Toon finale structuur
RUN ls -la

# Start commando zonder reload (dat kan problemen veroorzaken in productie)
CMD ["poetry", "run", "start"]
