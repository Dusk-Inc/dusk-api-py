from uuid import uuid4

from fastapi import Request

from contracts import RequestContext
from functions.context import storage


async def trace_middleware(request: Request, call_next):
    header_id = request.headers.get("x-correlation-id")
    correlation_id = header_id if isinstance(header_id, str) and header_id else str(uuid4())

    token = storage.set(RequestContext(correlation_id=correlation_id))
    try:
        response = await call_next(request)
    finally:
        storage.reset(token)

    response.headers["x-correlation-id"] = correlation_id
    return response
