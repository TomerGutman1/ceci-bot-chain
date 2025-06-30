FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy common modules first
COPY common/ /app/common/
COPY schemas/ /app/schemas/

# Copy service files
COPY MAIN_INTENT_BOT_1/ /app/MAIN_INTENT_BOT_1/

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    openai==0.28.1 \
    requests==2.31.0 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    pyyaml==6.0.1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LAYER_NAME=MAIN_INTENT_BOT_1

# Expose port
EXPOSE 8011

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8011/health || exit 1

# Run the service
CMD ["python", "MAIN_INTENT_BOT_1/main.py"]