"""Configuration management for the application."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""

    # API settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    # Application settings
    APP_NAME: str = "AI Writing Assistant"

    # Frontend serving (for prod)
    # Set SERVE_FRONTEND=true to serve built frontend files from backend
    # In development, leave this false to use Vite dev server
    SERVE_FRONTEND: bool = (
        os.getenv("SERVE_FRONTEND", "false").lower() == "true"
    )
    FRONTEND_DIR: str = os.getenv("FRONTEND_DIR", "../frontend/dist")

    def validate(self):
        """Validate required settings."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")


settings = Settings()
