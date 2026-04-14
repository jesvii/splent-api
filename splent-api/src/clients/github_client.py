import base64
import requests
from flask import current_app

GITHUB_API_URL = "https://api.github.com"


def _build_headers():
    token = current_app.config.get("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def fetch_org_repos():
    org = current_app.config["GITHUB_ORG"]

    response = requests.get(
        f"{GITHUB_API_URL}/orgs/{org}/repos",
        headers=_build_headers(),
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def fetch_repo_file(repo_name, path):
    org = current_app.config["GITHUB_ORG"]

    response = requests.get(
        f"{GITHUB_API_URL}/repos/{org}/{repo_name}/contents/{path}",
        headers=_build_headers(),
        timeout=10
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    data = response.json()

    content = data.get("content")
    encoding = data.get("encoding")

    if not content or encoding != "base64":
        return None

    decoded = base64.b64decode(content).decode("utf-8")
    return decoded