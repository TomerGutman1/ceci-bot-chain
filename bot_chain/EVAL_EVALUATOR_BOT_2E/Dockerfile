FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common libraries
COPY common/ ./common/

# Copy bot-specific code
COPY EVAL_EVALUATOR_BOT_2E/ ./EVAL_EVALUATOR_BOT_2E/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8014/health || exit 1

# Run the application
CMD ["python", "EVAL_EVALUATOR_BOT_2E/main.py"]