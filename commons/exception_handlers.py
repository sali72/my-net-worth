from fastapi.responses import JSONResponse
import traceback


async def base_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "exception_name": type(exc).__name__,
            "message": str(exc),
        },
    )
