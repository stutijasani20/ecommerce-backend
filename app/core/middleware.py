import json
from typing import Any, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.schemas.response import SuccessResponse

_DEFAULT_MESSAGES = {
    ("GET",    200): "Fetched successfully",
    ("POST",   200): "Created successfully",
    ("POST",   201): "Created successfully",
    ("PUT",    200): "Updated successfully",
    ("PATCH",  200): "Updated successfully",
    ("DELETE", 200): "Deleted successfully",
    ("DELETE", 204): "Deleted successfully",
}


class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip wrapping for documentation, health, and static files
        path = request.url.path
        if any(
            path.startswith(p)
            for p in [
                "/docs", 
                "/redoc", 
                f"{settings.API_V1_STR}/openapi.json", 
                "/openapi.json",
                f"{settings.API_V1_STR}/auth/login"
            ]
        ) or path == "/health":
            return await call_next(request)

        response = await call_next(request)

        # Only wrap if it's a successful JSON response
        if (
            response.status_code < 400 
            and "application/json" in response.headers.get("content-type", "")
        ):
            try:
                # Capture the body
                body = [section async for section in response.body_iterator]
                data = None
                if body:
                    data = json.loads(b"".join(body))

                # If the data is already wrapped, return it as is
                if isinstance(data, dict) and "success" in data:
                    async def body_iterator():
                        for section in body:
                            yield section
                    response.body_iterator = body_iterator()
                    return response

                # Determine message: endpoint-supplied header takes priority,
                # otherwise fall back to method-based default.
                headers = dict(response.headers)
                message = headers.pop("x-response-message", None) or \
                    _DEFAULT_MESSAGES.get((request.method, response.status_code))

                # Wrap the data in SuccessResponse
                wrapped_response = SuccessResponse(
                    success=True,
                    message=message,
                    data=data,
                )

                # Remove content-length to let JSONResponse recalculate it
                headers.pop("content-length", None)

                return JSONResponse(
                    content=wrapped_response.model_dump(),
                    status_code=response.status_code,
                    headers=headers,
                )
            except Exception as e:
                # If something fails, try to restore the body and return original
                async def body_iterator():
                    for section in body:
                        yield section
                response.body_iterator = body_iterator()
                return response

        return response
