FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared libraries first
COPY common/ ./common/

# Copy application code
COPY QUERY_RANKER_BOT_3Q/ ./QUERY_RANKER_BOT_3Q/

# Set Python path
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8016/health || exit 1

# Run the application
CMD ["python", "QUERY_RANKER_BOT_3Q/main.py"]