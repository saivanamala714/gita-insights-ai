# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Make sure the script is executable
RUN chmod +x start.sh

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application using gunicorn with multiple workers
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 120 app:app
