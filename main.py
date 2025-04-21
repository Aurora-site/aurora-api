import logging
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
from typing import Annotated, AsyncGenerator

import structlog
import tortoise
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from internal.auth import check_credentials
from internal.db.config import register_orm
from internal.jobs import job_router
from internal.jobs.job_router import scheduler_lifespan
from internal.logger import setup_logging, setup_uvicorn_logging
from internal.routers import admin_router, api_router, proxy_router, user_router
from internal.settings import (
    ALLOWED_ORIGINS,
    IGNORE_CORS,
    LOG_JSON,
    LOG_LEVEL,
    MEDIA_FOLDER,
)

logging.getLogger("hishel.controller").setLevel(logging.WARNING)
setup_logging(
    json_logs=LOG_JSON,
    log_level=LOG_LEVEL,
)
access_logger = structlog.stdlib.get_logger("api.access")
log = structlog.stdlib.get_logger(__name__)

# Create data folder for db files
(Path(".") / "data").mkdir(parents=True, exist_ok=True)
# Create folder for media files
(Path(".") / MEDIA_FOLDER).mkdir(parents=True, exist_ok=True)


def app_lifespan(lifespans: list):
    @asynccontextmanager
    async def _lifespan_manager(app: FastAPI):
        exit_stack = AsyncExitStack()
        async with exit_stack:
            for lifespan in lifespans:
                await exit_stack.enter_async_context(lifespan(app))
            yield

    return _lifespan_manager


@asynccontextmanager
async def db_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with register_orm(app):
        yield


app = FastAPI(
    lifespan=app_lifespan([db_lifespan, scheduler_lifespan]),
    swagger_ui_parameters={"syntaxHighlight": False},
    docs_url=None,
    redoc_url=None,
)
setup_uvicorn_logging(app, access_logger)


@app.get("/health", status_code=200, include_in_schema=False)
async def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def redirect_docs():
    return RedirectResponse(url="/docs")


AdminAuth = Annotated[HTTPBasicCredentials, Depends(check_credentials)]


@app.get("/docs", tags=["Docs"])
async def get_documentation(credentials: AdminAuth):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


app.mount("/media", StaticFiles(directory=MEDIA_FOLDER))
app.include_router(api_router.router)
app.include_router(user_router.router)
app.include_router(admin_router.router)
app.include_router(proxy_router.router)
app.include_router(job_router.router)


@app.exception_handler(tortoise.exceptions.ValidationError)
async def validation_exception_handler(request, exc):
    log.error(str(exc.args[0]))
    return JSONResponse(status_code=422, content={"detail": exc.args[0]})


@app.exception_handler(tortoise.exceptions.IntegrityError)
async def integrity_exception_handler(request, exc):
    log.error(str(exc.args[0]))
    return JSONResponse(status_code=409, content={"detail": str(exc.args[0])})


@app.exception_handler(tortoise.exceptions.OperationalError)
async def operational_exception_handler(request, exc):
    log.error(exc, exc_info=True, stack_info=True)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


if IGNORE_CORS:
    app.add_middleware(  # type: ignore
        CORSMiddleware,  # type: ignore
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
else:
    app.add_middleware(  # type: ignore
        CORSMiddleware,  # type: ignore
        allow_origins=ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
