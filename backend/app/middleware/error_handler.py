from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import AppException
from app.core.logging import logger


async def app_exception_handler(request: Request, exc: AppException):
    """Handles all custom domain and application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Translates Pydantic validation errors into the standardized error format."""
    details = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", []) if loc != "body"])
        details.append({
            "field": field,
            "message": err.get("msg", "Validation error"),
            "type": err.get("type", "value_error")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The supplied data failed validation rules.",
                "details": details
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Standardizes FastAPI/Starlette HTTP exceptions."""
    # Derive an appropriate error code based on status code
    code_map = {
        400: "BAD_REQUEST",
        401: "AUTHENTICATION_FAILED",
        403: "PERMISSION_DENIED",
        404: "RESOURCE_NOT_FOUND",
        409: "RESOURCE_CONFLICT",
        422: "VALIDATION_ERROR",
        423: "RESOURCE_LOCKED",
        500: "INTERNAL_SERVER_ERROR"
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")

    # If detail is already a dict, check if it fits the schema
    message = str(exc.detail) if exc.detail else "An error occurred."
    details = []

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details
            }
        },
        headers=getattr(exc, "headers", None)
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catches any unexpected internal exception without leaking stack traces or secrets."""
    logger.exception(f"Unhandled exception during request {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "details": []
            }
        }
    )
