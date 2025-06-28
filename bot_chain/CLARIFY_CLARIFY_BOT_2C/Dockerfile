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
COPY CLARIFY_CLARIFY_BOT_2C/ ./CLARIFY_CLARIFY_BOT_2C/

# Set Python path
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8015/health || exit 1

# Run the application
CMD ["python", "CLARIFY_CLARIFY_BOT_2C/main.py"]