import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from contracts import DiscoveryModel, WellKnownRouterConfig
from modules.well_known import WellKnownRouter


class TestWellKnown(unittest.TestCase):
    def test_domain__openid_configuration__returns_expected_configuration(self) -> None:
        app = FastAPI()
        router = WellKnownRouter(
            WellKnownRouterConfig(
                issuer="https://issuer.example.com",
                public_key_set={"keys": []},
                available_models=[DiscoveryModel(id="model-1", caps=["chat"])],
            )
        )
        app.include_router(router.router)
        client = TestClient(app)

        response = client.get("/.well-known/openid-configuration")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["issuer"], "https://issuer.example.com")
