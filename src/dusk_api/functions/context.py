from contextvars import ContextVar

from dusk_api.contracts import RequestContext

storage: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)


def get_correlation_id() -> str:
    value = storage.get()
    return value.correlation_id if value else "no-context"
