"""Web application entry point."""

from fastapi import FastAPI
from my_app.api.routes import router
from my_app import __version__

app = FastAPI(
    title="My App",
    description="A Python app with web and CLI interfaces",
    version=__version__,
)

app.include_router(router)


def run():
    """Run the web server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()