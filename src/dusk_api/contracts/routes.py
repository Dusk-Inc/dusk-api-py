from dataclasses import dataclass
from typing import Any, Literal

RouteMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


@dataclass
class RouteContract:
    method: RouteMethod
    path: str
    request: Any | None = None
    response: Any | None = None
