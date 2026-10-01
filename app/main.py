from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router
from app.config import BASE_DIR, settings


app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="AI-powered comic and story creator",
    version="1.0.0",
)

static_dir = BASE_DIR / "static"
panels_dir = static_dir / "panels"
exports_dir = static_dir / "exports"

panels_dir.mkdir(parents=True, exist_ok=True)
exports_dir.mkdir(parents=True, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=str(static_dir)),
    name="static",
)

app.include_router(router)