FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy common modules first
COPY common/ /app/common/

# Copy service files
COPY MAIN_REWRITE_BOT_0/ /app/MAIN_REWRITE_BOT_0/

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    openai==0.28.1 \
    pydantic==2.5.0 \
    python-multipart==0.0.6

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LAYER_NAME=MAIN_REWRITE_BOT_0

# Expose port
EXPOSE 8010

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8010/health || exit 1

# Run the service
CMD ["python", "MAIN_REWRITE_BOT_0/main.py"]