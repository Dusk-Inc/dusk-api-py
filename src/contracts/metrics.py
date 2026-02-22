from dataclasses import dataclass
from typing import Any


@dataclass
class MetricsRouterConfig:
    registry: Any | None = None
