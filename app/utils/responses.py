from typing import Any
from fastapi.responses import JSONResponse


def success_response(message: str, status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content={
            "message": message,
        },
    )


def error_response(message: str, status_code: int = 400, errors: Any | None = None):
    return JSONResponse(
        status_code=status_code,
        content={"message": message, "errors": errors},
    )
