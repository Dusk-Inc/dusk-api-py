from contextvars import ContextVar

from contracts import RequestContext

storage: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)


def get_correlation_id() -> str:
    value = storage.get()
    return value.correlation_id if value else "no-context"
