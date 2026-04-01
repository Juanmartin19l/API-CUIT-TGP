import asyncio
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager

from app.core.config import get_settings
from app.core.scraper import ScraperProtocol
from app.schemas.cuit import CuitData, CuitResponse

logger = logging.getLogger(__name__)

settings = get_settings()


def create_driver() -> webdriver.Chrome:
    """Create and configure Chrome driver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(settings.SCRAPER_TIMEOUT)

    return driver


def _scrape_cuit(numero: str) -> CuitResponse:
    """Scrape CUIT data from cuitonline.com."""
    url = f"{settings.BASE_URL}/{numero}"
    driver = None

    try:
        logger.info(f"Scraping URL: {url}")
        driver = create_driver()
        driver.get(url)

        wait = WebDriverWait(driver, settings.SCRAPER_TIMEOUT)

        no_results = driver.find_elements(
            By.CSS_SELECTOR, "div.left-pane h1.title-no-results"
        )
        if no_results:
            logger.warning(f"CUIT no encontrado: {numero}")
            return CuitResponse(
                success=False, error="CUIT no válido: El CUIT ingresado no existe"
            )

        hit_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hit")))

        denominacion_a = hit_div.find_element(
            By.CSS_SELECTOR, "div.denominacion > a.denominacion"
        )
        denominacion = denominacion_a.find_element(By.TAG_NAME, "h2").text.strip()

        doc_facets = hit_div.find_element(By.CLASS_NAME, "doc-facets")

        linea_cuit_persona = doc_facets.find_element(
            By.CLASS_NAME, "linea-cuit-persona"
        )
        cuit_span = linea_cuit_persona.find_element(By.CLASS_NAME, "cuit").text.strip()

        bullet_spans = doc_facets.find_elements(By.CSS_SELECTOR, "span.bullet")

        field_values = []
        for span in bullet_spans:
            text = driver.execute_script(
                "return arguments[0].nextSibling.textContent;", span
            )
            if text:
                text = text.replace("\xa0", " ").replace("&nbsp;", " ").strip()
            else:
                text = ""
            field_values.append(text)

        while len(field_values) < 4:
            field_values.append("")

        data = CuitData(
            denominacion=denominacion,
            cuit=cuit_span,
            tipo_persona=field_values[0],
            condicion_ganancias=field_values[1],
            condicion_iva=field_values[2],
            condicion_empleador=field_values[3],
        )

        logger.info(f"Successfully scraped CUIT: {cuit_span}")
        return CuitResponse(success=True, data=data)

    except TimeoutException:
        logger.error(f"Timeout esperando elementos en {url}")
        return CuitResponse(
            success=False, error="Elemento no encontrado: Timeout al cargar la página"
        )

    except NoSuchElementException as e:
        logger.error(f"Elemento no encontrado: {e}")
        return CuitResponse(
            success=False,
            error="Elemento no encontrado: Estructura de datos no encontrada en la página",
        )

    except WebDriverException as e:
        logger.error(f"Error de WebDriver: {e}")
        return CuitResponse(success=False, error=f"Error de WebDriver: {str(e)}")

    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return CuitResponse(success=False, error=f"Error inesperado: {str(e)}")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")


class SeleniumScraper(ScraperProtocol):
    """Selenium-based scraper implementation for CUIT data."""

    async def scrape(self, numero: str) -> CuitResponse:
        """Scrape CUIT data using Selenium."""
        return await asyncio.to_thread(_scrape_cuit, numero)
