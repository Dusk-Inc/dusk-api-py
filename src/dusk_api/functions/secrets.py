import os
from pathlib import Path

from dusk_api.contracts import SecretRotation


def parse_secret_line(line: str) -> tuple[str, str] | None:
    trimmed = line.strip()
    if len(trimmed) == 0 or trimmed.startswith("#"):
        return None

    normalized = trimmed[len("export ") :] if trimmed.startswith("export ") else trimmed
    separator = normalized.find("=")
    if separator <= 0:
        return None

    key = normalized[:separator].strip()
    if not key.replace("_", "A").isalnum() or key[0].isdigit():
        return None

    raw_value = normalized[separator + 1 :].strip()
    if len(raw_value) == 0:
        return key, ""

    if raw_value.startswith('"') and raw_value.endswith('"') and len(raw_value) >= 2:
        unquoted = raw_value[1:-1]
        value = (
            unquoted.replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\\\", "\\")
        )
        return key, value

    if raw_value.startswith("'") and raw_value.endswith("'") and len(raw_value) >= 2:
        unquoted = raw_value[1:-1]
        return key, unquoted.replace("\\'", "'").replace("\\\\", "\\")

    return key, raw_value


def parse_secrets_file(content: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in content.splitlines():
        entry = parse_secret_line(line)
        if entry is None:
            continue
        key, value = entry
        parsed[key] = value
    return parsed


def merge_with_process_env(file_secrets: dict[str, str], env: dict[str, str]) -> dict[str, str]:
    merged = dict(file_secrets)
    for key, value in env.items():
        if isinstance(value, str):
            merged[key] = value
    return merged


def are_secret_maps_equal(left: dict[str, str], right: dict[str, str]) -> bool:
    return left == right


def build_rotation(
    previous_values: dict[str, str],
    current_values: dict[str, str],
    previous_generation: int,
    generation: int,
) -> SecretRotation:
    previous_keys = set(previous_values.keys())
    current_keys = set(current_values.keys())

    added_keys = sorted([key for key in current_keys if key not in previous_keys])
    removed_keys = sorted([key for key in previous_keys if key not in current_keys])
    shared_keys = [key for key in current_keys if key in previous_keys]
    updated_keys = sorted([key for key in shared_keys if previous_values[key] != current_values[key]])
    unchanged_keys = sorted([key for key in shared_keys if previous_values[key] == current_values[key]])

    return SecretRotation(
        generation=generation,
        previous_generation=previous_generation,
        added_keys=added_keys,
        removed_keys=removed_keys,
        updated_keys=updated_keys,
        unchanged_keys=unchanged_keys,
    )


def resolve_secret_path(env: dict[str, str], secret_path_env_var: str, secret_path_default: str) -> str:
    configured_path = env.get(secret_path_env_var) or secret_path_default
    return str(Path(configured_path).resolve())


def is_missing_file_error(error: object) -> bool:
    return isinstance(error, FileNotFoundError)


def is_permission_denied_error(error: object) -> bool:
    return isinstance(error, PermissionError)
