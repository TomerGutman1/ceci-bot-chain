FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common module
COPY common /app/common

# Copy bot code
COPY UNIFIED_INTENT_BOT_1 /app/UNIFIED_INTENT_BOT_1

# Set working directory to bot folder
WORKDIR /app/UNIFIED_INTENT_BOT_1

# Set Python path to include parent for common imports
ENV PYTHONPATH=/app:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8011/health').raise_for_status()"

# Run the bot
CMD ["python", "main.py"]