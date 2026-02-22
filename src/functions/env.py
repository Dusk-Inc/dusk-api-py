import os

from fastapi.responses import JSONResponse


def parse_env() -> dict[str, int | str]:
    host = os.environ.get("HOST", "0.0.0.0")
    port_raw = os.environ.get("PORT")
    if port_raw is None:
        raise ValueError("PORT is required")

    try:
        port = int(port_raw)
    except ValueError as error:
        raise ValueError("PORT must be a number") from error

    if port < 1 or port > 65535:
        raise ValueError("PORT must be in range 1..65535")

    return {"HOST": host, "PORT": port}


def send_not_implemented() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={
            "error": {
                "code": "NOT_IMPLEMENTED",
                "message": "Not implemented.",
            }
        },
    )
