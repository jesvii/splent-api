# Splent API

API en Flask para listar paquetes desde GitHub y leer su contrato en `pyproject.toml`.

## Requisitos

- Python 3.11+ (recomendado)
- Un token de GitHub (opcional, pero recomendado para evitar limites de rate limit)

## Configuracion

1. Crea tu archivo `.env` a partir de `.env.example`.
2. Ajusta al menos estas variables:

```env
GITHUB_ORG=splent-io
GITHUB_TOKEN=tu_token_aqui
```

## Ejecutar el proyecto

Instala dependencias:

```bash
pip install -r requirements.txt
```

Inicia la API:

```bash
python run.py
```

Por defecto Flask levanta en:

- http://127.0.0.1:5000

## Que abrir para ver paquetes

### 1) Ver todos los paquetes

Abre en navegador:

- http://127.0.0.1:5000/api/packages



### 2) Ver un paquete por nombre

Abre en navegador (ejemplo):

- http://127.0.0.1:5000/api/packages/splent_feature_auth


Si no existe, responde `404` con:

```json
{"error":"Package not found"}
```

## Endpoints

- `GET /api/packages`
- `GET /api/packages/<name>`
