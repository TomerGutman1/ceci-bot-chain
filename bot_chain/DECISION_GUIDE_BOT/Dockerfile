FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY ./DECISION_GUIDE_BOT/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code
COPY ./DECISION_GUIDE_BOT/main.py .

# Copy common modules
COPY ./common ./common

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8018

# Expose the port
EXPOSE 8018

# Run the application
CMD ["python", "main.py"]