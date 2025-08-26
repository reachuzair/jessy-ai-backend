#!/usr/bin/env python3
"""
Simple launcher script for the FastAPI backend.
Run this from anywhere to start the server.
"""

import uvicorn
import sys
import os

# Add the current directory to Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="localhost",
        port=8003,
        reload=True,
        log_level="info"
    )
