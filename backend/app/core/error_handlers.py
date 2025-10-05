"""
Centralized error handling and logging for FastAPI
"""

import logging
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger("psychnow")


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    trace_id = str(uuid.uuid4())
    logger.warning(
        "HTTPException",
        extra={
            "trace_id": trace_id,
            "path": request.url.path,
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "trace_id": trace_id},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    trace_id = str(uuid.uuid4())
    logger.warning(
        "ValidationError",
        extra={
            "trace_id": trace_id,
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "trace_id": trace_id},
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    trace_id = str(uuid.uuid4())
    logger.exception(
        "UnhandledException",
        extra={
            "trace_id": trace_id,
            "path": request.url.path,
        },
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "trace_id": trace_id},
    )


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    # Reduce noisy loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


