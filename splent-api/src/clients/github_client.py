import requests
from flask import current_app

GITHUB_API_URL = "https://api.github.com"


def fetch_org_repos():
    org = current_app.config["GITHUB_ORG"]
    token = current_app.config.get("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        f"{GITHUB_API_URL}/orgs/{org}/repos",
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    return response.json()