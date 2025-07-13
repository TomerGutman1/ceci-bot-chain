FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY UNIFIED_INTENT_BOT_1/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code to working directory
COPY . .

# Set Python path for imports
ENV PYTHONPATH=/app:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8011/health').raise_for_status()"

# Run the bot
CMD ["python", "UNIFIED_INTENT_BOT_1/main.py"]