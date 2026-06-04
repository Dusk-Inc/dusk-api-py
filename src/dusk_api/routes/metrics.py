from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

from dusk_api.contracts import MetricsRouterConfig
from dusk_api.tokens import metrics_routes


class MetricsRouter:
    def __init__(self, config: MetricsRouterConfig | None = None) -> None:
        self.router = APIRouter()
        resolved = config or MetricsRouterConfig()
        registry = resolved.registry or REGISTRY

        @self.router.get(metrics_routes["collect"]["path"])
        async def metrics_collect():
            metrics = generate_latest(registry)
            return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)
