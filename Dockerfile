# Gebruik officiële Python image
FROM python:3.11-slim-bookworm

# Zet vereiste environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1 \
    CHROME_BIN=/usr/bin/chromium \
    CHROME_PATH=/usr/lib/chromium/ \
    PLAYWRIGHT_BROWSERS_PATH=/usr/bin/chromium

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
    # Schoon op na installatie
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installeer Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Configureer Poetry
RUN poetry config virtualenvs.create false

# Werkdirectory
WORKDIR /app

# Kopieer dependencies
COPY pyproject.toml poetry.lock* ./

# Installeer dependencies zonder het hoofdproject
RUN poetry install --only main --no-root --no-interaction --no-ansi

# Kopieer applicatiecode
COPY . .

# Start commando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9001"]
