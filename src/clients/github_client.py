import base64
import requests
from flask import current_app
import time

GITHUB_API_URL = "https://api.github.com"

def check_rate_limit():
    headers = _build_headers()
    response = requests.get(f"{GITHUB_API_URL}/rate_limit", headers=headers)

    if response.status_code == 200:
        data = response.json()
        remaining = data['resources']['core']['remaining']  # Peticiones restantes
        reset_time = data['resources']['core']['reset']     # Hora de reinicio
        
        # Si no quedan peticiones, esperamos hasta el siguiente ciclo
        if remaining == 0:
            reset_timestamp = reset_time
            current_time = int(time.time())
            wait_time = reset_timestamp - current_time + 10  # Esperamos 10 segundos después del reset
            print(f"Rate limit alcanzado. Esperando {wait_time} segundos...")
            time.sleep(wait_time)  # Esperamos hasta que el rate limit se reinicie
        else:
            print(f"Peticiones restantes: {remaining}")
    else:
        print("Error al verificar el rate limit")

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