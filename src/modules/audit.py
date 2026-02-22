from fastapi import Request


def _read_trace_id(request: Request) -> str | None:
    correlation_id = request.headers.get("x-correlation-id")
    if correlation_id:
        return correlation_id
    trace_id = request.headers.get("x-trace-id")
    return trace_id if trace_id else None


async def audit_middleware(request: Request, call_next):
    trace_id = _read_trace_id(request)
    request.state.trace_id = trace_id

    def log_audit(level: str, payload: dict[str, object]) -> None:
        payload_with_trace = dict(payload)
        if trace_id:
            payload_with_trace["trace_id"] = trace_id

        logger = getattr(request.state, "logger", None)
        if logger is None:
            return

        if level == "info" and hasattr(logger, "info"):
            logger.info(payload_with_trace)
            return
        if hasattr(logger, "error"):
            logger.error(payload_with_trace)

    request.state.log_audit = log_audit
    return await call_next(request)


def read_trace_id(request: Request) -> str | None:
    return _read_trace_id(request)
