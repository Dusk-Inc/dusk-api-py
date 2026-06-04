from dataclasses import dataclass


@dataclass
class RequestContext:
    correlation_id: str
