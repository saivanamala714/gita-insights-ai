"""
Main entry point for the Bhagavad Gita Q&A application.
This file ensures the FastAPI app is properly configured for production.
"""
import os
from app import app

# This file is used when running with Gunicorn
app = app  # This makes the app available to Gunicorn

if __name__ == "__main__":
    # This block is used when running with python main.py
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1
    )
