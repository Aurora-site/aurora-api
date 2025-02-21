import hashlib
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from internal.settings import ADMIN_PASS, ADMIN_SALT, ADMIN_USER

security = HTTPBasic()

SecDep = Annotated[HTTPBasicCredentials, Depends(security)]


def check_credentials(credentials: SecDep) -> bool:
    correct_username = secrets.compare_digest(
        credentials.username,
        ADMIN_USER,
    )
    correct_password = secrets.compare_digest(
        bytes.fromhex(ADMIN_PASS),
        hashlib.pbkdf2_hmac(
            "sha256",
            credentials.password.encode(),
            bytes.fromhex(ADMIN_SALT),
            100_000,
        ),
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True
