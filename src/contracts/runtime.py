from dataclasses import dataclass
from typing import Any, Callable, Protocol


@dataclass
class RuntimePluginContext:
    logger: Any
    set_dependency: Callable[[str, Any], None]
    get_dependency: Callable[[str], Any | None]


class RuntimePlugin(Protocol):
    id: str

    def setup(self, context: RuntimePluginContext) -> None: ...
    def start(self, context: RuntimePluginContext) -> None: ...
    def stop(self, context: RuntimePluginContext) -> None: ...
