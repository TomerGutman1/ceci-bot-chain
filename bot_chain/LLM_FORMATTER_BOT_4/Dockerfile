FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common module
COPY common /app/common

# Copy bot code
COPY LLM_FORMATTER_BOT_4 /app/LLM_FORMATTER_BOT_4

# Set working directory to bot folder
WORKDIR /app/LLM_FORMATTER_BOT_4

# Set Python path to include parent for common imports
ENV PYTHONPATH=/app:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8017/health').raise_for_status()"

# Run the bot
CMD ["python", "main.py"]