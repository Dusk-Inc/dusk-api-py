import os
from pathlib import Path
import time

from contracts import SecretManagerOptions, SecretRotation, SecretSnapshot
from functions.secrets import (
    are_secret_maps_equal,
    build_rotation,
    is_missing_file_error,
    is_permission_denied_error,
    merge_with_process_env,
    parse_secrets_file,
    resolve_secret_path,
)
from tokens import DEFAULT_SECRET_PATH, DEFAULT_SECRET_PATH_ENV_VAR, DEFAULT_WATCH_DEBOUNCE_MS

SecretRotationListener = callable


class SecretManager:
    def __init__(self, options: SecretManagerOptions | None = None) -> None:
        resolved = options or SecretManagerOptions()
        self._env = resolved.env or dict(os.environ)
        self._logger = resolved.logger
        self._secret_path_env_var = resolved.secret_path_env_var or DEFAULT_SECRET_PATH_ENV_VAR
        self._secret_path_default = resolved.secret_path_default or DEFAULT_SECRET_PATH
        self._watch_debounce_ms = resolved.watch_debounce_ms or DEFAULT_WATCH_DEBOUNCE_MS
        self._require_read_only_file = True if resolved.require_read_only_file is None else resolved.require_read_only_file
        self._listeners: set = set()
        self._snapshot = SecretSnapshot(generation=0, values={})

    def get_snapshot(self) -> SecretSnapshot:
        return self._snapshot

    def get_secret(self, key: str) -> str | None:
        return self._snapshot.values.get(key)

    def get_required_secret(self, key: str) -> str:
        value = self.get_secret(key)
        if not value:
            raise ValueError(f"Required secret is missing: {key}.")
        return value

    def get_all_secrets(self) -> dict[str, str]:
        return dict(self._snapshot.values)

    def on_rotate(self, listener):
        self._listeners.add(listener)

        def unsubscribe() -> None:
            self._listeners.discard(listener)

        return unsubscribe

    async def load_secrets(self) -> SecretSnapshot:
        return await self.refresh_secrets()

    async def ensure_fresh_secrets_file(self) -> None:
        snapshot = self._snapshot if self._snapshot.generation > 0 else await self.load_secrets()
        secrets = snapshot.values
        require_file = secrets.get("DUSK_SECRETS_REQUIRE_FILE", "true").lower() == "true"
        if not require_file:
            return

        secret_path = resolve_secret_path(self._env, self._secret_path_env_var, self._secret_path_default)
        path_value = Path(secret_path)
        if not path_value.exists():
            raise ValueError(f"Required secrets file is missing: {secret_path}.")

        parsed_max_age = int(secrets.get("DUSK_SECRETS_MAX_AGE_SEC", "300"))
        max_age_sec = parsed_max_age if parsed_max_age > 0 else 300
        age_sec = int(time.time() - path_value.stat().st_mtime)
        if age_sec > max_age_sec:
            raise ValueError(f"Secrets file is stale ({age_sec}s old): {secret_path}.")

    async def refresh_secrets(self) -> SecretSnapshot:
        values = await self._collect_secrets()
        previous_values = dict(self._snapshot.values)
        if are_secret_maps_equal(previous_values, values):
            return self._snapshot

        generation = self._snapshot.generation + 1
        self._snapshot = SecretSnapshot(generation=generation, values=dict(values))

        if generation > 1:
            rotation = build_rotation(previous_values, values, generation - 1, generation)
            for listener in list(self._listeners):
                listener(rotation)

        return self._snapshot

    async def start_watching(self) -> None:
        return None

    def stop_watching(self) -> None:
        return None

    async def _collect_secrets(self) -> dict[str, str]:
        secret_path = resolve_secret_path(self._env, self._secret_path_env_var, self._secret_path_default)
        file_secrets: dict[str, str] = {}

        try:
            if self._require_read_only_file:
                self._ensure_read_only(secret_path)
            with open(secret_path, "r", encoding="utf-8") as handle:
                content = handle.read()
            file_secrets = parse_secrets_file(content)
        except Exception as error:
            if not is_missing_file_error(error):
                raise

        return merge_with_process_env(file_secrets, self._env)

    def _ensure_read_only(self, secret_path: str) -> None:
        try:
            if os.access(secret_path, os.W_OK):
                raise ValueError(
                    f"Secrets file is writable by the current process: {secret_path}. Expected read-only."
                )
        except Exception as error:
            if is_missing_file_error(error) or is_permission_denied_error(error):
                return
            raise
