import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    hf_api_key: str = os.getenv("HF_API_KEY", "")

    gemini_outline_model: str = "gemini-2.5-flash"

    gemini_story_model: str = "gemini-2.5-pro"

    hf_image_model: str = "runwayml/stable-diffusion-v1-5"

    image_provider: str = "huggingface"

    use_demo_fallback: bool = True

    panel_count: int = 5

    app_name: str = "ComicCraft"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()