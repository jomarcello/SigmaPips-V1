# Gebruik Python 3.11 als basis
FROM python:3.11-slim

# Zet omgevingsvariabelen om caching en logs te optimaliseren
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Installeer Chrome en andere dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Installeer Poetry op een betrouwbare manier
RUN pip install --upgrade pip && pip install poetry==1.7.1

# Stel de werkdirectory in
WORKDIR /app

# Kopieer en installeer alleen de dependencies
COPY pyproject.toml poetry.lock* /app/

# Zorg ervoor dat Poetry geen virtuele omgevingen maakt
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Kopieer de rest van de bestanden
COPY . /app/

# Start de applicatie via Uvicorn
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9001"]
