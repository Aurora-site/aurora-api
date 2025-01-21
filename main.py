from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import structlog
import tortoise
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from internal.db.config import register_orm
from internal.logger import setup_logging, setup_uvicorn_logging
from internal.routers import admin_router, api_router, user_router
from internal.settings import IGNORE_CORS, LOG_JSON, LOG_LEVEL, MEDIA_FOLDER

setup_logging(
    json_logs=LOG_JSON,
    log_level=LOG_LEVEL,
)
access_logger = structlog.stdlib.get_logger("api.access")
# log = structlog.stdlib.get_logger(__name__)

# Create data folder for db files
(Path(".") / "data").mkdir(parents=True, exist_ok=True)
# Create folder for media files
(Path(".") / MEDIA_FOLDER).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # if getattr(app.state, "testing", None):
    #     async with lifespan_test(app) as _:
    #         yield
    # else:
    # app startup
    async with register_orm(app):
        yield


app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"syntaxHighlight": False},
)
setup_uvicorn_logging(app, access_logger)


@app.get("/health", status_code=200, include_in_schema=False)
async def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def redirect_docs():
    return RedirectResponse(url="/docs")


app.mount("/media", StaticFiles(directory=MEDIA_FOLDER))
app.include_router(api_router.router)
app.include_router(user_router.router)
app.include_router(admin_router.router)


@app.exception_handler(tortoise.exceptions.ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.args[0]})


@app.exception_handler(tortoise.exceptions.IntegrityError)
async def integrity_exception_handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": str(exc.args[0])})


if IGNORE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
