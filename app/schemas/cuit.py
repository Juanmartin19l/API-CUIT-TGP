from pydantic import BaseModel
from typing import Optional


class CuitData(BaseModel):
    """Datos extraídos del scraper."""

    denominacion: str
    cuit: str
    tipo_persona: str
    condicion_ganancias: str
    condicion_iva: str
    condicion_empleador: str


class CuitResponse(BaseModel):
    """Respuesta del endpoint."""

    success: bool
    data: Optional[CuitData] = None
    error: Optional[str] = None
