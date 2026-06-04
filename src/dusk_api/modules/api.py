import logging

from fastapi import FastAPI

from dusk_api.contracts import AppManagerConfig, HealthRouterConfig, RuntimePlugin, SecretManagerOptions
from dusk_api.functions import get_correlation_id, trace_middleware
from dusk_api.modules.audit import audit_middleware
from dusk_api.modules.runtime_manager import RuntimeManager
from dusk_api.modules.secrets_plugin import SecretsPlugin
from dusk_api.routes.health import HealthRouter
from dusk_api.routes.metrics import MetricsRouter
from dusk_api.tokens import (
    RUNTIME_DEPENDENCY_SECRETS_ENV,
    RUNTIME_DEPENDENCY_SECRETS_MANAGER,
    RUNTIME_DEPENDENCY_SECRETS_SNAPSHOT,
)


class AppManager:
    def __init__(self, config: AppManagerConfig) -> None:
        self.app = FastAPI()
        self.logger = config.logger or logging.getLogger(config.service_name)
        if config.log_level:
            self.logger.setLevel(config.log_level.upper())

        self.runtime = RuntimeManager(self.logger)

        self.app.middleware("http")(trace_middleware)
        self.app.middleware("http")(audit_middleware)
        self.app.include_router(HealthRouter(HealthRouterConfig(readiness=config.readiness)).router)
        self.app.include_router(MetricsRouter().router)

        self.secrets = _SecretsFacade(self)

    def use(self, plugin: RuntimePlugin) -> "AppManager":
        self.runtime.use(plugin)
        return self

    def get_dependency(self, key: str):
        return self.runtime.get_dependency(key)

    async def start_runtime(self) -> None:
        await self.runtime.start()

    async def stop_runtime(self) -> None:
        await self.runtime.stop()


class _SecretsFacade:
    def __init__(self, app_manager: AppManager) -> None:
        self._app_manager = app_manager

    def use(self, config: SecretManagerOptions | None = None) -> AppManager:
        self._app_manager.runtime.use(SecretsPlugin(config))
        return self._app_manager

    def get_manager(self):
        return self._app_manager.runtime.get_dependency(RUNTIME_DEPENDENCY_SECRETS_MANAGER)

    def get_snapshot(self):
        return self._app_manager.runtime.get_dependency(RUNTIME_DEPENDENCY_SECRETS_SNAPSHOT)

    def get_env(self):
        return self._app_manager.runtime.get_dependency(RUNTIME_DEPENDENCY_SECRETS_ENV)
