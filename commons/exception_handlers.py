import logging
import traceback

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)

# Internal mapping - not exposed to clients
exception_status_map = {
    # Built-in Python exception
    "ValueError": 400,
    "KeyError": 404,
    # mongoengine.errors
    "ValidationError": 422,
    "DoesNotExist": 404,
    "NotUniqueError": 409,
    # bson.errors
    "InvalidId": 400,
}

# Generic error messages for clients
error_messages = {
    400: "Invalid request",
    404: "Resource not found",
    409: "Resource conflict",
    422: "Validation error",
    500: "Internal server error",
}


def get_status_code(exception_name: str) -> int:
    """Get the status code based on the exception name."""
    return exception_status_map.get(exception_name, 500)


def extract_traceback_info(exc: Exception) -> tuple[str, int]:
    """Extract file name and line number from the exception traceback."""
    tb = traceback.extract_tb(exc.__traceback__)
    if tb:
        last_trace = tb[-1]
        return last_trace.filename, last_trace.lineno
    return "Unknown", 0


def log_exception(exc: Exception, file_name: str, line_number: int):
    """Log the full exception information for internal use."""
    logging.error(
        "Exception %s occurred: %s\nFile: %s, Line: %d\nTraceback: %s",
        type(exc).__name__,
        str(exc),
        file_name,
        line_number,
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )


async def base_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with sanitized output."""
    exception_name = type(exc).__name__
    status_code = get_status_code(exception_name)

    # Log the full error details for debugging
    file_name, line_number = extract_traceback_info(exc)
    log_exception(exc, file_name, line_number)

    # Return sanitized response to client
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": error_messages.get(status_code, "An error occurred"),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with controlled output."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": (
                exc.detail
                if exc.detail
                else error_messages.get(exc.status_code, "An error occurred")
            ),
        },
    )
