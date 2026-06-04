import unittest

from fastapi.testclient import TestClient

from dusk_api.routes.health import HealthRouter
from fastapi import FastAPI


class TestHealth(unittest.TestCase):
    def test_domain__readiness_true__ready_returns_200(self) -> None:
        app = FastAPI()
        app.include_router(HealthRouter().router)
        client = TestClient(app)

        response = client.get("/health/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["status"], "ok")
