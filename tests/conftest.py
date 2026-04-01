import pytest
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.dependencies import set_scraper, reset_scraper


class MockScraper:
    """Mock scraper for testing."""

    def __init__(self, response):
        self.response = response

    async def scrape(self, numero: str):
        return self.response


@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture
def sample_cuit_data():
    from app.schemas.cuit import CuitData

    return CuitData(
        denominacion="JOHN DOE",
        cuit="30-67542808-1",
        tipo_persona="Persona Física",
        condicion_ganancias="Responsable Inscripto",
        condicion_iva="Responsable Inscripto",
        condicion_empleador="No registra",
    )


@pytest.fixture
def sample_cuit_response(sample_cuit_data):
    from app.schemas.cuit import CuitResponse

    return CuitResponse(success=True, data=sample_cuit_data)


@pytest.fixture
def mock_scraper(sample_cuit_response):
    return MockScraper(sample_cuit_response)


@pytest.fixture
def mock_error_scraper():
    from app.schemas.cuit import CuitResponse

    return MockScraper(CuitResponse(success=False, error="Timeout"))


@pytest.fixture(autouse=True)
def cleanup_scraper():
    yield
    reset_scraper()
