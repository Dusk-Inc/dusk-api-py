from dataclasses import dataclass
from typing import Callable

ReadinessCheck = Callable[[], bool]


@dataclass
class HealthRouterConfig:
    readiness: ReadinessCheck | None = None
