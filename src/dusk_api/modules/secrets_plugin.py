from dusk_api.contracts import RuntimePluginContext, SecretManagerOptions
from dusk_api.modules.secrets import SecretManager
from dusk_api.tokens import (
    RUNTIME_DEPENDENCY_SECRETS_ENV,
    RUNTIME_DEPENDENCY_SECRETS_MANAGER,
    RUNTIME_DEPENDENCY_SECRETS_SNAPSHOT,
    RUNTIME_PLUGIN_SECRETS,
)


class SecretsPlugin:
    id = RUNTIME_PLUGIN_SECRETS

    def __init__(self, config: SecretManagerOptions | None = None) -> None:
        self._config = config or SecretManagerOptions()
        self._manager: SecretManager | None = None
        self._unsubscribe = None

    async def start(self, context: RuntimePluginContext) -> None:
        self._manager = SecretManager(self._config)
        snapshot = await self._manager.load_secrets()

        context.set_dependency(RUNTIME_DEPENDENCY_SECRETS_MANAGER, self._manager)
        context.set_dependency(RUNTIME_DEPENDENCY_SECRETS_SNAPSHOT, snapshot)
        context.set_dependency(RUNTIME_DEPENDENCY_SECRETS_ENV, dict(snapshot.values))

        def on_rotate(_rotation):
            if not self._manager:
                return
            latest = self._manager.get_snapshot()
            context.set_dependency(RUNTIME_DEPENDENCY_SECRETS_SNAPSHOT, latest)
            context.set_dependency(RUNTIME_DEPENDENCY_SECRETS_ENV, dict(latest.values))

        self._unsubscribe = self._manager.on_rotate(on_rotate)
        await self._manager.start_watching()

    async def stop(self, _context: RuntimePluginContext | None = None) -> None:
        if callable(self._unsubscribe):
            self._unsubscribe()
        if self._manager:
            self._manager.stop_watching()
        self._manager = None
