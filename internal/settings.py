import os
import sys

from dotenv import load_dotenv

load_dotenv()

IGNORE_CORS = bool(os.getenv("IGNORE_CORS", False))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
LOG_JSON = bool(os.getenv("LOG_JSON", not sys.stderr.isatty()))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DB_URL = os.getenv("DB_URL", "sqlite://data/db.sqlite3")
MEDIA_FOLDER = os.getenv("MEDIA_FOLDER", "media")

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv(
    "ADMIN_PASS",
    "59061d0505246e53f61023ec2bcffbd3b2a4b391370408a623a07a4c0c2e9899",
)
ADMIN_SALT = os.getenv("ADMIN_SALT", "a1e8fd5c6c18537ae7b93f08825a4327")
ADMIN_TEST_PASS = "admin"  # only for tests

# OpenWeatherMap API key
OW_API_KEY = os.environ["OW_API_KEY"]
