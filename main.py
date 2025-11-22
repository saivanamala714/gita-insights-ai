"""
Main entry point for the Bhagavad Gita Q&A application.
This file ensures the FastAPI app is properly configured for production.
"""
from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
