# Splent API

A Flask API used by the Splent marketplace and CLI to publish and list feature packages.
Feature code lives in GitHub repositories. The API reads official packages from GitHub and stores marketplace registrations sent by the CLI.

## Requirements

- Python 3.11+ (recommended)
- A GitHub token (optional, but recommended to avoid rate limits)
- Docker and Docker Compose for deployment

## Configuration

1. Create your `.env` file from `.env.example`.
2. Set at least these variables:

```env
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=change-me
SPLENT_API_TOKEN=change-me
PACKAGES_FILE=/data/packages.json
GITHUB_ORG=splent-io
GITHUB_TOKEN=
```

`GITHUB_ORG` is the default organization used when no owner is provided. By default this is `splent-io`.

`SPLENT_API_TOKEN` is used by the CLI and marketplace as a Bearer token:

```http
Authorization: Bearer <token>
```

Do not commit the real `.env` file.

## Run the project

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
python run.py
```

By default, Flask runs on:

- http://127.0.0.1:5000

## Docker deployment

The domain points to port `80`, so Docker Compose exposes the API on port `80`.

Start or rebuild the service:

```bash
docker compose up -d --build
```

Check the service:

```bash
docker compose ps
docker compose logs -f splent-api
```

Restart the service:

```bash
docker compose restart splent-api
```

Stop the service:

```bash
docker compose down
```

The container uses `restart: always` in `docker-compose.yml`.

The marketplace registry file is stored in:

```text
./data/packages.json
```

inside the VM, mounted in the container as `/data/packages.json`.

## What to open to view packages

### 1) View all packages

Use the Bearer token if `SPLENT_API_TOKEN` is configured:

```bash
curl -H "Authorization: Bearer $SPLENT_API_TOKEN" \
  http://127.0.0.1/api/packages
```

Local development URL:

- http://127.0.0.1:5000/api/packages
- http://127.0.0.1:5000/api/packages?owner=splent-io

Production URL inside the VM:

- http://127.0.0.1/api/packages
- http://127.0.0.1/api/packages?owner=splent-io

### 2) View a package by name

Open in your browser or call with curl:

- http://127.0.0.1:5000/api/packages/splent_feature_auth
- http://127.0.0.1:5000/api/packages/splent-io/splent_feature_auth

If it does not exist, it returns `404` with:

```json
{"error":"Package not found"}
```

## Health check

This endpoint does not require authentication:

```bash
curl http://127.0.0.1/health
```

Expected response:

```json
{"status":"ok"}
```

## How to test the API

### 1) Make sure the API is running

Start it locally:

```bash
python run.py
```

Or with Docker:

```bash
docker compose up -d --build
```

### 2) Test the read endpoints

Open these links in the browser or call them with curl:

- http://127.0.0.1:5000/api/packages
- http://127.0.0.1:5000/api/packages/splent_feature_auth

### 3) Test package publishing

Use Postman, Thunder Client, Insomnia, curl, or any API client to send a `POST` request to:

- http://127.0.0.1:5000/api/packages

Send a JSON body with:

- `full_name`
- `name`
- `owner`
- `repository`
- `repo_url`
- `contract`
- `metadata` (optional)

Example:

```json
{
  "full_name": "jesvii/splent_feature_orcid@v1.0.0",
  "owner": "jesvii",
  "name": "splent_feature_orcid",
  "repository": "jesvii/splent_feature_orcid",
  "repo_url": "https://github.com/jesvii/splent_feature_orcid",
  "contract": {
    "description": "ORCID feature",
    "provides": {},
    "requires": {}
  },
  "metadata": {
    "source": "splent-cli",
    "feature_version": "v1.0.0"
  }
}
```

Expected result:

- The package registration is stored in the marketplace API
- The GitHub repository remains maintained by its owner
- The API returns the package data

### 4) Test package updating

Send a `PUT` request to:

- http://127.0.0.1:5000/api/packages/<name>

Update one or more of these fields:

- `contract`
- `metadata`
- `repo_url`

Expected result:

- The marketplace registration is updated
- The API returns the updated package data

## Endpoints

- `GET /health` - Health check
- `GET /api/packages` - List all packages
- `GET /api/packages/<name>` - Get a specific package
- `POST /api/packages` - Publish a new package
- `PUT /api/packages/<name>` - Update an existing package
