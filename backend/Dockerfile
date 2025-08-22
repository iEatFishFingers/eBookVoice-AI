# Use Python 3.11 slim image for smaller size and faster builds
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=8080 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimized settings
RUN pip install --no-cache-dir -r requirements.txt && \
    # Clean up any build artifacts
    find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} + || true

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p uploads audiobooks logs && \
    chmod 755 uploads audiobooks logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --system app && \
    chown -R app:app /app
USER app

# Health check with timeout optimization
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=2 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Expose port
EXPOSE 8080

# Run the application with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "300", "--max-requests", "1000", "--max-requests-jitter", "100", "app:app"]