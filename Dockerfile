# Use Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only dependency files first
COPY pyproject.toml poetry.lock ./

# Copy the app directory first
COPY ./app ./app/

# Copy the rest of the application code
COPY . .

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Expose port
EXPOSE 9001

# Command to run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9001"]
