from dataclasses import dataclass
from typing import Any, Callable

from fastapi import FastAPI

ReadinessCheck = Callable[[], bool]


@dataclass
class AppManagerConfig:
    service_name: str
    log_level: str | None = None
    logger: Any | None = None
    readiness: ReadinessCheck | None = None


@dataclass
class AppManagerModel:
    app: FastAPI
    logger: Any


AppConfig = AppManagerConfig
AppModel = AppManagerModel
