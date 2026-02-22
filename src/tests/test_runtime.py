import unittest

from modules.runtime_manager import RuntimeManager


class _FakePlugin:
    def __init__(self, plugin_id: str, events: list[str]) -> None:
        self.id = plugin_id
        self._events = events

    def start(self, _context) -> None:
        self._events.append(f"start:{self.id}")

    def stop(self, _context) -> None:
        self._events.append(f"stop:{self.id}")


class TestRuntime(unittest.IsolatedAsyncioTestCase):
    async def test_domain__runtime_manager__starts_and_stops_plugins_in_order(self) -> None:
        events: list[str] = []
        manager = RuntimeManager(logger=None)
        manager.use(_FakePlugin("one", events)).use(_FakePlugin("two", events))

        await manager.start()
        await manager.stop()

        self.assertEqual(events, ["start:one", "start:two", "stop:two", "stop:one"])

    async def test_boundary__runtime_manager__throws_for_duplicate_plugin_id(self) -> None:
        manager = RuntimeManager(logger=None)
        manager.use(_FakePlugin("duplicate", []))
        with self.assertRaisesRegex(ValueError, "Runtime plugin already registered: duplicate"):
            manager.use(_FakePlugin("duplicate", []))
