from fastapi.responses import JSONResponse
from fastapi import HTTPException

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

async def base_exception_handler(request, exc: Exception):
    exception_name = get_exception_name(exc)
    status_code = get_status_code(exception_name)

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