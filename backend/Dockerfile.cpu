# Lightweight CPU-only Dockerfile for free hosting
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for free tier)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libssl-dev \
    espeak-ng \
    espeak-ng-data \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.cpu.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads chapters audiobooks logs temp

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=8080

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port (use $PORT for cloud platforms)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Use gunicorn for production
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 "app:create_app()"