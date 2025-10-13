"""Main entry point for the AI Writing Assistant backend."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routes import rephrase

settings.validate()

app = FastAPI(title=settings.APP_NAME)

app.include_router(rephrase.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": f"{settings.APP_NAME} Backend"}


# Conditionally serve frontend static files (for production)
# In development: SERVE_FRONTEND=false (default) - use Vite dev server
# In production: SERVE_FRONTEND=true - backend serves built frontend
if settings.SERVE_FRONTEND:
    # Navigate to project root: backend/app/main.py -> backend/app -> backend -> project_root
    project_root = Path(__file__).parent.parent.parent
    # Remove leading "../" from FRONTEND_DIR and join with project root
    frontend_path = project_root / settings.FRONTEND_DIR.lstrip("../")

    if frontend_path.exists():
        # Mount frontend static files (MUST be last route!)
        app.mount(
            "/",
            StaticFiles(directory=str(frontend_path), html=True),
            name="static",
        )
        print(f"Serving frontend from: {frontend_path}")
    else:
        print(
            f"Warning: SERVE_FRONTEND=true but {frontend_path} doesn't exist"
        )
        print(
            f"Run 'npm run build' in frontend directory to create dist folder"
        )
