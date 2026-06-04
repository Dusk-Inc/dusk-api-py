from fastapi import Request, Response

from dusk_api.contracts import ActorReader, ActorSource, MissingActorHandler
from dusk_api.functions import make_missing_actor_payload, read_actor_field, send_missing_actor
from dusk_api.tokens import (
    ACTOR_DEFAULT_MISSING_CODE,
    ACTOR_DEFAULT_MISSING_MESSAGE,
    ACTOR_DEFAULT_MISSING_STATUS_CODE,
    ACTOR_DEFAULT_REQUIRED,
    ACTOR_DEFAULT_SOURCE,
)


class ActorMiddleware:
    def __init__(
        self,
        field: str,
        source: ActorSource = ACTOR_DEFAULT_SOURCE,
        required: bool = ACTOR_DEFAULT_REQUIRED,
        missing_status_code: int = ACTOR_DEFAULT_MISSING_STATUS_CODE,
        missing_code: str = ACTOR_DEFAULT_MISSING_CODE,
        missing_message: str = ACTOR_DEFAULT_MISSING_MESSAGE,
        read_actor: ActorReader = read_actor_field,
        on_missing_actor: MissingActorHandler = send_missing_actor,
    ) -> None:
        self._field = field
        self._source = source
        self._required = required
        self._missing_status_code = missing_status_code
        self._missing_code = missing_code
        self._missing_message = missing_message
        self._read_actor = read_actor
        self._on_missing_actor = on_missing_actor

    def handler(self, req: Request, res: Response, next_fn) -> None:
        actor_id = self._read_actor(req, self._field, self._source)

        if not actor_id:
            req.state.actor_id = None
            if not self._required:
                next_fn()
                return

            payload = make_missing_actor_payload(self._missing_code, self._missing_message)
            self._on_missing_actor(req, res, payload, self._missing_status_code)
            return

        req.state.actor_id = actor_id
        next_fn()
