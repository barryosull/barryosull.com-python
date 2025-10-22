"""Main FastAPI application."""

import src.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from src.adapters.api.rest.routes import router
import os
from pathlib import Path


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
        "http://localhost:8000",
        "http://localhost:8080",
    ],  # React dev servers and production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if src.config.IS_PRODUCTION:
    app.add_middleware(HTTPSRedirectMiddleware)

# Include API routes first (before static files)
app.include_router(router)

# Serve static assets from the dist folder
frontend_dist_dir = Path(src.config.FRONTEND_DIR) / "dist"
if frontend_dist_dir.exists():
    # Mount assets directory for CSS, JS, images, etc.
    app.mount(
        "/assets",
        StaticFiles(directory=frontend_dist_dir / "assets"),
        name="assets"
    )

    # Serve HTML files and SPA support
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve HTML files or the React SPA for all non-API routes."""
        # Check if a specific HTML file is requested
        if full_path.endswith('.html'):
            html_file = frontend_dist_dir / full_path
            if html_file.exists():
                return FileResponse(html_file)

        # Default to index.html for SPA routing
        index_file = frontend_dist_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Frontend not found"}
