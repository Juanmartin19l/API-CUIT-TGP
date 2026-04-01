from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    model_config = ConfigDict(env_file=".env")

    APP_NAME: str
    APP_VERSION: str
    APP_HOST: str
    APP_PORT: int
    SCRAPER_TIMEOUT: int
    SCRAPER_MAX_CONCURRENT: int
    SCRAPER_MAX_RETRIES: int
    BASE_URL: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()
