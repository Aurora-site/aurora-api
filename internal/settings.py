import base64
import os
import sys

from dotenv import load_dotenv

load_dotenv()

_true_values = (
    "True",
    "true",
    "1",
)

IGNORE_CORS = os.getenv("IGNORE_CORS", "False") in _true_values
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
LOG_JSON = os.getenv("LOG_JSON", str(not sys.stderr.isatty())) in _true_values
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
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "True") in _true_values

# https://github.com/DenverCoder1/jct-discord-bot/blob/67af73fa05afda73973d8843c1a66c6bacc5ceaf/config.py#L44
FCM_PROJECT_ID = os.getenv("FCM_PROJECT_ID", "")
# fmt: off
FCM_SETTINGS = {
    "type": "service_account",
    "project_id": FCM_PROJECT_ID,
    "private_key_id": os.getenv("FCM_PRIVATE_KEY_ID", ""),
    "private_key": base64.b64decode(os.getenv("FCM_PRIVATE_KEY", "")).decode(),
    "client_email": f"firebase-adminsdk-fbsvc@{FCM_PROJECT_ID}"
        f".iam.gserviceaccount.com",
    "client_id": os.getenv("FCM_CLIENT_ID", ""),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/"
        f"firebase-adminsdk-fbsvc%40{FCM_PROJECT_ID}.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}
# fmt: on
FCM_DRY_RUN = os.getenv("FCM_DRY_RUN", "True") in _true_values
ENV_NAME = os.getenv("ENV_NAME", "dev")
