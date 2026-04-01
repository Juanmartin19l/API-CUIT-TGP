import asyncio
import re
import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.dependencies import ScraperDep, SemaphoreDep
from app.schemas.cuit import CuitResponse

logger = logging.getLogger(__name__)

router = APIRouter()

settings = get_settings()


@router.get("/{numero}", response_model=None)
async def get_cuit(
    numero: str,
    scraper: ScraperDep,
    semaphore: SemaphoreDep,
):
    """
    Busca un CUIT y devuelve la información correspondiente.

    El CUIT debe tener exactamente 11 dígitos.
    """
    if not re.match(r"^\d+$", numero):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El CUIT debe contener solo dígitos",
        )

    if len(numero) != 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El CUIT debe tener exactamente 11 dígitos",
        )

    result = CuitResponse(success=False, error="Error desconocido")

    for attempt in range(settings.SCRAPER_MAX_RETRIES):
        async with semaphore:
            result = await scraper.scrape(numero)

        if result.success:
            return result

        error_msg = str(result.error) if result.error else ""

        should_retry = (
            "Elemento no encontrado" in error_msg or "Timeout" in error_msg
        ) and attempt < settings.SCRAPER_MAX_RETRIES - 1

        if should_retry:
            delay = 2**attempt
            logger.warning(
                f"Intento {attempt + 1} falló: {error_msg}. Reintentando en {delay}s..."
            )
            await asyncio.sleep(delay)
            continue

        return JSONResponse(status_code=502, content=result.model_dump())

    return JSONResponse(status_code=502, content=result.model_dump())
