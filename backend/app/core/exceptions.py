import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def error_response(status_code: int, code: str, message: str, details: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        if isinstance(exc.detail, dict):
            code = str(exc.detail.get("code", "http_error"))
            message = str(exc.detail.get("message", "Request failed"))
            details = {
                key: value
                for key, value in exc.detail.items()
                if key not in {"code", "message"}
            }
            return error_response(exc.status_code, code, message, details or None)

        detail = str(exc.detail)
        code = detail if detail.startswith(("AUTH_", "RATE_LIMITED")) else "http_error"
        message = "Request failed" if detail.startswith("AUTH_") else detail
        return error_response(exc.status_code, code, message)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        for item in errors:
            item.pop("ctx", None)
        return error_response(
            422,
            "validation_error",
            "Request validation failed",
            jsonable_encoder(errors),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error", exc_info=exc)
        return error_response(500, "internal_error", "An unexpected error occurred")
