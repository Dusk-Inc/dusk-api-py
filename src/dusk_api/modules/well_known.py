from fastapi import APIRouter

from dusk_api.contracts import WellKnownRouterConfig, well_known_routes
from dusk_api.functions import make_openid_configuration


class WellKnownRouter:
    def __init__(self, config: WellKnownRouterConfig) -> None:
        self.router = APIRouter()

        @self.router.get(well_known_routes["openidConfiguration"].path)
        def openid_configuration():
            return make_openid_configuration(config)

        @self.router.get(well_known_routes["jwks"].path)
        def jwks():
            return config.public_key_set
