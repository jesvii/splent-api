import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
    GITHUB_ORG = os.getenv("GITHUB_ORG", "splent-io")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    SPLENT_API_TOKEN = os.getenv("SPLENT_API_TOKEN")
    PACKAGES_FILE = os.getenv("PACKAGES_FILE", "packages.json")
