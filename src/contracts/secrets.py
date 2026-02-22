from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class SecretSnapshot:
    generation: int
    values: dict[str, str]


@dataclass(frozen=True)
class SecretRotation:
    generation: int
    previous_generation: int
    added_keys: list[str]
    removed_keys: list[str]
    updated_keys: list[str]
    unchanged_keys: list[str]


SecretLogger = object


@dataclass
class SecretManagerOptions:
    env: dict[str, str] | None = None
    logger: SecretLogger | None = None
    secret_path_env_var: str | None = None
    secret_path_default: str | None = None
    watch_debounce_ms: int | None = None
    require_read_only_file: bool | None = None


SecretRotationListener = Callable[[SecretRotation], None]
