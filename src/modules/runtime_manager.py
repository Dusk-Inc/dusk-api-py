import inspect

from contracts import RuntimePlugin, RuntimePluginContext


class RuntimeManager:
    def __init__(self, logger: object) -> None:
        self._logger = logger
        self._plugins: list[RuntimePlugin] = []
        self._started_plugin_ids: list[str] = []
        self._dependencies: dict[str, object] = {}
        self._started = False

    def use(self, plugin: RuntimePlugin) -> "RuntimeManager":
        if self._started:
            raise ValueError("Cannot register runtime plugin after startup.")

        if any(item.id == plugin.id for item in self._plugins):
            raise ValueError(f"Runtime plugin already registered: {plugin.id}")

        self._plugins.append(plugin)
        return self

    async def start(self) -> None:
        if self._started:
            return

        context = self._build_context()
        for plugin in self._plugins:
            setup = getattr(plugin, "setup", None)
            start = getattr(plugin, "start", None)
            if callable(setup):
                outcome = setup(context)
                if inspect.isawaitable(outcome):
                    await outcome
            if callable(start):
                outcome = start(context)
                if inspect.isawaitable(outcome):
                    await outcome
            self._started_plugin_ids.append(plugin.id)

        self._started = True

    async def stop(self) -> None:
        if not self._started:
            return

        context = self._build_context()
        for plugin_id in reversed(self._started_plugin_ids):
            plugin = next((item for item in self._plugins if item.id == plugin_id), None)
            if plugin is None:
                continue
            stop = getattr(plugin, "stop", None)
            if callable(stop):
                outcome = stop(context)
                if inspect.isawaitable(outcome):
                    await outcome

        self._started_plugin_ids.clear()
        self._started = False

    def get_dependency(self, key: str):
        return self._dependencies.get(key)

    def set_dependency(self, key: str, value: object) -> None:
        self._dependencies[key] = value

    def _build_context(self) -> RuntimePluginContext:
        return RuntimePluginContext(
            logger=self._logger,
            set_dependency=lambda key, value: self.set_dependency(key, value),
            get_dependency=lambda key: self.get_dependency(key),
        )
