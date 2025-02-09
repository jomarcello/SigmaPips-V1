# Gebruik officiële Python image
FROM python:3.11-slim-bookworm

# Zet vereiste environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Debug: Toon werkdirectory
WORKDIR /app

# Kopieer alleen de benodigde files
COPY app/ ./app/
COPY requirements.txt .

# Installeer dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8080

# Use environment variables
ENV PORT=8080

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]


