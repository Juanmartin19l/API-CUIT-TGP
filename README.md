# API CUIT TGP

API REST para consulta de CUIT basada en FastAPI con Selenium para web scraping.

## Descripcion

Esta API permite consultar informacion de CUIT del sitio cuitonline.com. El usuario ingresa un numero de CUIT de 11 digitos y la API devuelve los datos correspondientes: denominacion, CUIT, tipo de persona, condicion frente al Impuesto a las Ganancias, condicion frente al IVA y condicion como empleador.

## Requisitos

- Python 3.12+
- Google Chrome (para Selenium)
- Docker (opcional)

## Configuracion

La aplicacion utiliza variables de entorno definidas en el archivo `.env`. Copie el archivo `.env.example` a `.env` y configure los valores segun sea necesario.

```env
APP_NAME=API CUIT TGP
APP_VERSION=0.1.0
APP_HOST=0.0.0.0
APP_PORT=8000
SCRAPER_TIMEOUT=3
SCRAPER_MAX_CONCURRENT=5
SCRAPER_MAX_RETRIES=3
BASE_URL=URL
```

### Variables de Entorno

| Variable | Descripcion | Valor Predeterminado |
|----------|-------------|---------------------|
| APP_NAME | Nombre de la aplicacion | API CUIT TGP |
| APP_VERSION | Version de la aplicacion | 0.1.0 |
| APP_HOST | Host donde corre la API | 0.0.0.0 |
| APP_PORT | Puerto de la API | 8000 |
| SCRAPER_TIMEOUT | Timeout del scraper en segundos | 3 |
| SCRAPER_MAX_CONCURRENT | Maximo de scrapers simultaneos | 5 |
| SCRAPER_MAX_RETRIES | Maximo de reintentos | 3 |
| BASE_URL | URL base del sitio a scrapear | https://www.cuitonline.com/search |

## Instalacion

### Con UV

```bash
# Instalar dependencias
uv sync

# Ejecutar la aplicacion
uv run uvicorn app.main:app --reload
```

### Con Docker

```bash
# Build de la imagen
docker build -t api-cuit .

# Ejecucion
docker run -p 8000:8000 api-cuit
```

O usando docker-compose:

```bash
docker-compose up --build
```

## Uso

### Endpoint

```
GET /api/v1/cuit/{numero}
```

### Ejemplo de Request

```bash
curl http://localhost:8000/api/v1/cuit/30675428081
```

### Respuesta Exitosa

```json
{
  "success": true,
  "data": {
    "denominacion": "JUAN PEREZ",
    "cuit": "30-67542808-1",
    "tipo_persona": "Persona Fisica",
    "condicion_ganancias": "Responsable Inscripto",
    "condicion_iva": "Responsable Inscripto",
    "condicion_empleador": "No registra"
  }
}
```

### Respuesta de Error

```json
{
  "success": false,
  "error": "Error al procesar la solicitud"
}
```

## Manejo de Errores

La API implementa las siguientes estrategias de manejo de errores:

- **Elemento no encontrado / Timeout**: Reintenta automaticamente hasta 3 veces con backoff exponencial (1s, 2s).
- **Validacion**: El CUIT debe contener exactamente 11 digitos. De lo contrario, devuelve un error 400.

## Pruebas

```bash
# Ejecutar pruebas
python -m pytest
```

## Arquitectura

```
app/
├── api/v1/
│   └── endpoints/
│       └── cuit.py          # Endpoint de consulta de CUIT
├── core/
│   ├── config.py            # Configuracion centralizada
│   ├── dependencies.py      # Inyeccion de dependencias
│   ├── scraper.py           # Protocolo del scraper
│   └── scraper_impl.py      # Implementacion con Selenium
├── schemas/
│   └── cuit.py              # Modelos Pydantic
└── main.py                  # Aplicacion FastAPI
```

## Tech Stack

- **FastAPI**: Framework web asincronico
- **Selenium**: Automatizacion del navegador para scraping
- **Pydantic**: Validacion de datos
- **UV**: Gestor de paquetes

## Licencia

