FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    chromium \
    libglvnd \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Environment variabele voor de port
ENV PORT=8080

# Start de main applicatie (niet de test service)
CMD ["python", "-m", "uvicorn", "trading_bot.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
