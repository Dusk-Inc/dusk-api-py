from dusk_api.contracts import WellKnownRouterConfig, well_known_routes


def make_openid_configuration(config: WellKnownRouterConfig) -> dict[str, object]:
    payload: dict[str, object] = {
        "issuer": config.issuer,
        "jwks_uri": f"{config.issuer}{well_known_routes['jwks'].path}",
        "authorization_endpoint": f"{config.issuer}/authorize",
        "token_endpoint": f"{config.issuer}/token",
        "userinfo_endpoint": f"{config.issuer}/userinfo",
        "ai_endpoint": f"{config.issuer}/ai/models",
        "id_token_signing_alg_values_supported": ["RS256"],
        "response_types_supported": ["code", "id_token"],
        "scopes_supported": ["openid", "profile", "email", "ai_access"],
    }

    if config.available_models is not None:
        payload["ai_models_supported"] = [model.__dict__ for model in config.available_models]

    return payload
