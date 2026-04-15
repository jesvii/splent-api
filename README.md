# Splent API

A Flask API to list packages from GitHub and read their contract from `pyproject.toml`.

## Requirements

- Python 3.11+ (recommended)
- A GitHub token (optional, but recommended to avoid rate limits)

## Configuration

1. Create your `.env` file from `.env.example`.
2. Set at least these variables:

```env
GITHUB_ORG=splent-io
GITHUB_TOKEN=your_token_here
```

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

## What to open to view packages

### 1) View all packages

Open in your browser:

- http://127.0.0.1:5000/api/packages



### 2) View a package by name

Open in your browser (example):

- http://127.0.0.1:5000/api/packages/splent_feature_auth


If it does not exist, it returns `404` with:

```json
{"error":"Package not found"}
```

## Endpoints

- `GET /api/packages`
- `GET /api/packages/<name>`
