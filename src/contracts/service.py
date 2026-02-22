from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Literal

ServiceDecoratorPhase = Literal["encode", "decode"]


@dataclass
class ServiceDecoratorTransformErrorInput:
    phase: ServiceDecoratorPhase
    target: str
    message: str


@dataclass
class ServiceMapperContext:
    service_name: str
    method_name: str
    phase: ServiceDecoratorPhase


ServiceArgsMapper = Callable[[list[Any], ServiceMapperContext], list[Any] | Awaitable[list[Any]]]
ServiceResultMapper = Callable[[Any, ServiceMapperContext], Any | Awaitable[Any]]


@dataclass
class ServiceDecoratorRule:
    methods: list[str] | None = None
    map_args: ServiceArgsMapper | None = None
    map_result: ServiceResultMapper | None = None


@dataclass
class ServiceDecoratorConfig:
    service_name: str | None
    rules: list[ServiceDecoratorRule]
