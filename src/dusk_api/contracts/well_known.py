from dataclasses import dataclass
from typing import Any

from .routes import RouteContract


@dataclass
class DiscoveryModel:
    id: str
    caps: list[str]


@dataclass
class WellKnownRouterConfig:
    issuer: str
    public_key_set: dict[str, Any]
    available_models: list[DiscoveryModel] | None = None


well_known_openid_configuration_contract = RouteContract(
    method="GET",
    path="/.well-known/openid-configuration",
    response=dict,
)

well_known_jwks_contract = RouteContract(
    method="GET",
    path="/.well-known/jwks.json",
    response=dict,
)

well_known_routes = {
    "openidConfiguration": well_known_openid_configuration_contract,
    "jwks": well_known_jwks_contract,
}
