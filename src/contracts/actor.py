from typing import Any, Callable, Literal, TypedDict

from fastapi import Request, Response

ActorSource = Literal["header", "query", "body"]
RequestData = dict[str, Any]


class ActorMiddlewareErrorResponse(TypedDict):
    error: dict[str, str]


ActorReader = Callable[[Request, str, ActorSource], str | None]
MissingActorHandler = Callable[[Request, Response, ActorMiddlewareErrorResponse, int], None]
