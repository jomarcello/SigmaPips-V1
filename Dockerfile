# Gebruik Python 3.11 als basis
FROM python:3.11-slim

# Zet omgevingsvariabelen
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONPATH=/app \
    CHROME_BIN=/usr/bin/chromium \
    CHROME_PATH=/usr/lib/chromium/

# Installeer alleen de essentiële packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Installeer Poetry
RUN pip install --upgrade pip && pip install poetry==1.7.1

# Stel werkdirectory in
WORKDIR /app

# Kopieer alleen dependency files
COPY pyproject.toml poetry.lock* /app/

# Installeer dependencies zonder dev dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction

# Kopieer code
COPY . /app/

# Start app
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9001"]
