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
COPY QUERY_SQL_GEN_BOT_2Q/ /app/QUERY_SQL_GEN_BOT_2Q/

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    openai==0.28.1 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    sqlparse==0.4.4 \
    psycopg2-binary==2.9.9

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LAYER_NAME=QUERY_SQL_GEN_BOT_2Q

# Expose port
EXPOSE 8012

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8012/health || exit 1

# Run the service
CMD ["python", "QUERY_SQL_GEN_BOT_2Q/main.py"]