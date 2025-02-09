# Gebruik een lichtere basis image
FROM python:3.11-slim-bookworm

# Zet omgevingsvariabelen
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    CHROME_BIN=/usr/bin/chromium \
    CHROME_PATH=/usr/lib/chromium/

# Installeer alleen noodzakelijke system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    chromium \
    chromium-driver \
    # Clean up apt cache
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installeer Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Configureer Poetry om geen virtuele omgeving te maken
RUN poetry config virtualenvs.create false

# Stel werkdirectory in
WORKDIR /app

# Kopieer dependency files
COPY pyproject.toml poetry.lock* ./

# Installeer dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Kopieer applicatiecode
COPY . .

# Start commando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9001"]
