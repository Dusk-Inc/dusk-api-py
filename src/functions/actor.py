from fastapi import Request, Response

from contracts import ActorMiddlewareErrorResponse, ActorSource, RequestData


def get_header_value(value: str | list[str] | None) -> str | None:
    if isinstance(value, list):
        return value[0] if value else None
    return value


def read_actor_field(req: Request, field: str, source: ActorSource) -> str | None:
    if source == "header":
        return get_header_value(req.headers.get(field.lower()) or req.headers.get(field))

    request_data: RequestData | None = None
    if source == "query":
        request_data = dict(req.query_params)
    elif source == "body":
        body = getattr(req.state, "parsed_body", None)
        if isinstance(body, dict):
            request_data = body

    if not request_data:
        return None
    value = request_data.get(field)
    return value if isinstance(value, str) else None


def make_missing_actor_payload(code: str, message: str) -> ActorMiddlewareErrorResponse:
    return {"error": {"code": code, "message": message}}


def send_missing_actor(_req: Request, res: Response, payload: ActorMiddlewareErrorResponse, status_code: int) -> None:
    res.status_code = status_code
    res.body = str(payload).encode("utf-8")
