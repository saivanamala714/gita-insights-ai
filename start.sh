#!/bin/bash

# Set the port
export PORT=${PORT:-8080}

# Run the FastAPI application
uvicorn app:app --host 0.0.0.0 --port $PORT --reload
