import logging
import traceback

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from commons.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


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


def get_exception_name(exc: Exception) -> str:
    """Get the name of the exception."""
    return type(exc).__name__


def get_status_code(exception_name: str) -> int:
    """Get the status code based on the exception name."""
    return exception_status_map.get(exception_name, 500)


def extract_traceback_info(exc: Exception):
    """Extract file name and line number from the exception traceback."""
    tb = traceback.extract_tb(exc.__traceback__)
    if tb:
        last_trace = tb[-1]
        return last_trace.filename, last_trace.lineno
    return "Unknown", "Unknown"


def log_exception(exc: Exception, file_name: str, line_number: int):
    """Log the full exception information."""
    logging.error(
        "Exception occurred: %s\nFile: %s, Line: %d\nTraceback: %s",
        str(exc),
        file_name,
        line_number,
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )


async def base_exception_handler(request, exc: Exception):
    exception_name = get_exception_name(exc)
    status_code = get_status_code(exception_name)
    file_name, line_number = extract_traceback_info(exc)
    log_exception(exc, file_name, line_number)

    return JSONResponse(
        status_code=status_code,
        content={
            "exception_name": exception_name,
            "detail": str(exc),
        },
    )


async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "exception_name": "HTTPException",
            "detail": exc.detail,
        },
    )
