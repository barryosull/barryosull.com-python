"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from src.adapters.api.rest.routes import router
import os


# Configure logger
logging.basicConfig(
    filename=os.getenv("LOG_FILE", "/tmp/secret-hitler.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI application
app = FastAPI(
    title="Secret Hitler API",
    description="REST API for the Secret Hitler online game",
    version="0.1.0",
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include HTTP routes
app.include_router(router)
