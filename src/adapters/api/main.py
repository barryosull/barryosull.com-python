"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.api.rest.routes import router

# Create FastAPI application
app = FastAPI(
    title="Secret Hitler API",
    description="REST API for the Secret Hitler online game",
    version="0.1.0",
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint returning API information.

    Returns:
        Dictionary with API name and version.
    """
    return {"name": "Secret Hitler API", "version": "0.1.0"}


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dictionary with status.
    """
    return {"status": "ok"}


def run() -> None:
    """Run the FastAPI application with uvicorn.

    This function is used for development. In production, use uvicorn directly.
    """
    import uvicorn

    uvicorn.run("src.adapters.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
