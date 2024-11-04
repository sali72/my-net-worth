from fastapi.responses import JSONResponse
from mongoengine.errors import DoesNotExist


async def does_not_exist_handler(request, exc: DoesNotExist):
    # Extract the model name from the exception message
    model_name = str(exc).split(" ")[0].split(".")[-1]

    return JSONResponse(
        status_code=404,
        content={"error": f"{model_name} not found."},
    )
