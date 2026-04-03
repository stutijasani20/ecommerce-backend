import logging
from typing import Any, List, Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.response import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler for all HTTPExceptions (Starlette and FastAPI).
    """
    error_response = ErrorResponse(
        success=False,
        error=ErrorDetail(
            message=str(exc.detail),
            code=f"ERR_{exc.status_code}",
        )
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers=getattr(exc, "headers", None)
    )


async def validation_exception_handler(
    request: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handler for Pydantic validation errors (422).
    """
    error_response = ErrorResponse(
        success=False,
        error=ErrorDetail(
            message="Input validation failed",
            code="VALIDATION_ERROR",
            details=exc.errors()
        )
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for all unexpected server errors (500).
    """
    logger.exception(f"Unhandled exception: {str(exc)}")
    
    error_response = ErrorResponse(
        success=False,
        error=ErrorDetail(
            message="An unexpected server error occurred.",
            code="INTERNAL_SERVER_ERROR"
        )
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


def setup_exception_handlers(app: FastAPI) -> None:
    # Use StarletteHTTPException to catch both Starlette and FastAPI HTTPExceptions
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
