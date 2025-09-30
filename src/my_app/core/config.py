"""Configuration management."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""

    app_name: str = "My App"
    debug: bool = False

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        return cls(
            app_name=os.getenv("APP_NAME", "My App"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )


config = Config.from_env()