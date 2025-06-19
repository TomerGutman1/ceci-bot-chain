# PandasAI Service Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_pandasai.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_pandasai.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p /app/cache && chmod 777 /app/cache

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Run the application
CMD ["python", "-u", "pandasai_service.py"]
