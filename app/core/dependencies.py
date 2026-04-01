import asyncio
from typing import Annotated

from fastapi import Depends

from app.core.config import get_settings
from app.core.scraper import ScraperProtocol
from app.core.scraper_impl import SeleniumScraper

settings = get_settings()

_semaphore: asyncio.Semaphore | None = None


def get_semaphore() -> asyncio.Semaphore:
    """Get or create the semaphore for limiting concurrent scrapers."""
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(settings.SCRAPER_MAX_CONCURRENT)
    return _semaphore


_scraper_instance: ScraperProtocol | None = None


def get_scraper() -> ScraperProtocol:
    """Get or create the scraper instance."""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = SeleniumScraper()
    return _scraper_instance


def set_scraper(scraper: ScraperProtocol) -> None:
    """Set the scraper instance (useful for testing)."""
    global _scraper_instance
    _scraper_instance = scraper


def reset_scraper() -> None:
    """Reset the scraper instance (useful for testing)."""
    global _scraper_instance
    _scraper_instance = None


ScraperDep = Annotated[ScraperProtocol, Depends(get_scraper)]
SemaphoreDep = Annotated[asyncio.Semaphore, Depends(get_semaphore)]
