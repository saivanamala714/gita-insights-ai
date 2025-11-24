FROM python:3.12-slim

# System deps for heavy packages (chromadb, playwright, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# If you use playwright/chroma
# RUN playwright install-deps && playwright install chromium || true

COPY . .

ENV PORT=8080

# This line is golden
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1