# Splent API

A Flask API used by the Splent marketplace and CLI to publish and list feature packages.
Feature code lives in GitHub repositories. The API reads official packages from GitHub and stores marketplace registrations sent by the CLI.

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

`GITHUB_ORG` is the default organization used when no owner is provided. By default this is `splent-io`.

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
- http://127.0.0.1:5000/api/packages?owner=splent-io



### 2) View a package by name

Open in your browser (example):

- http://127.0.0.1:5000/api/packages/splent_feature_auth
- http://127.0.0.1:5000/api/packages/splent-io/splent_feature_auth


If it does not exist, it returns `404` with:

```json
{"error":"Package not found"}
```

## How to test the API

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
- `owner`
- `repo_url` or `repository_url`
- `metadata` (optional)

Expected result:

- The package registration is stored in the marketplace API
- The GitHub repository remains maintained by its owner
- The API returns the package data

### 4) Test package updating

Send a `PUT` request to:

- http://127.0.0.1:5000/api/packages/<name>

Update one or more of these fields:

- `description`
- `provides`
- `requires`

Expected result:

- The marketplace registration is updated
- The API returns the updated package data

## Endpoints

- `GET /api/packages` - List all packages
- `GET /api/packages/<name>` - Get a specific package  
- `POST /api/packages` - Publish a new package
- `PUT /api/packages/<name>` - Update an existing package
