from abc import ABC, abstractmethod
from typing import Protocol

from app.schemas.cuit import CuitResponse


class ScraperProtocol(Protocol):
    """Protocol for CUIT scraper implementations."""

    @abstractmethod
    async def scrape(self, numero: str) -> CuitResponse:
        """
        Scrape CUIT data for the given CUIT.

        Args:
            CUIT: The CUIT number to search for

        Returns:
            CuitResponse with success status and data or error
        """
        ...
