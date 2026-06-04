from typing import Any, Literal, Protocol

AuditLevel = Literal["info", "error"]
AuditPayload = dict[str, Any]


class RequestLogger(Protocol):
    def info(self, arg: Any) -> None: ...
    def error(self, arg: Any) -> None: ...
