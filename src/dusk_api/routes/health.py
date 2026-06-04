from fastapi import APIRouter
from fastapi.responses import JSONResponse

from dusk_api.contracts import HealthRouterConfig
from dusk_api.tokens import health_routes


class HealthRouter:
    def __init__(self, config: HealthRouterConfig | None = None) -> None:
        self.router = APIRouter()
        resolved = config or HealthRouterConfig()
        readiness = resolved.readiness or (lambda: True)

        @self.router.get(health_routes["live"]["path"])
        async def health_live():
            return {"data": {"status": "ok"}}

        @self.router.get(health_routes["ready"]["path"])
        async def health_ready():
            ready = readiness()
            if ready:
                return {"data": {"status": "ok"}}
            return JSONResponse(status_code=503, content={"data": {"status": "unready"}})
