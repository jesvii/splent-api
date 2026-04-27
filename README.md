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

## How to test the new functionality

### 1) Make sure the API is running

Start it with:

```bash
python run.py
```

### 2) Test the read endpoints

Open these links in the browser:

- http://127.0.0.1:5000/api/packages
- http://127.0.0.1:5000/api/packages/splent_feature_auth

### 3) Test package publishing

Use Postman, Thunder Client, Insomnia, or any API client to send a `POST` request to:

- http://127.0.0.1:5000/api/packages

Send a JSON body with:

- `name`
- `description`
- `provides`
- `requires`
- `private` (optional, defaults to `false`)

Expected result:

- The repo is created in GitHub
- A `pyproject.toml` file is added with the contract
- The API returns the package data

### 4) Test package updating

Send a `PUT` request to:

- http://127.0.0.1:5000/api/packages/<name>

Update one or more of these fields:

- `description`
- `provides`
- `requires`

Expected result:

- The existing repo is updated
- The `pyproject.toml` contract is refreshed
- The API returns the updated package data

## Endpoints

- `GET /api/packages` - List all packages
- `GET /api/packages/<name>` - Get a specific package  
- `POST /api/packages` - Publish a new package
- `PUT /api/packages/<name>` - Update an existing package
