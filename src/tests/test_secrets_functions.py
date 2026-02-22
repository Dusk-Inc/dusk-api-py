import unittest

from functions.secrets import (
    build_rotation,
    merge_with_process_env,
    parse_secret_line,
    parse_secrets_file,
)


class TestSecretsFunctions(unittest.TestCase):
    def test_domain__parse_secret_line__reads_export(self) -> None:
        self.assertEqual(parse_secret_line("export DB_USER=file-user"), ("DB_USER", "file-user"))

    def test_boundary__parse_secret_line__comment_returns_none(self) -> None:
        self.assertIsNone(parse_secret_line("# comment"))

    def test_domain__parse_secrets_file__parses_values(self) -> None:
        parsed = parse_secrets_file("DB_USER=file-user\nDB_PASS=file-pass")
        self.assertEqual(parsed, {"DB_USER": "file-user", "DB_PASS": "file-pass"})

    def test_domain__merge_with_process_env__env_wins(self) -> None:
        merged = merge_with_process_env({"DB_PASS": "file"}, {"DB_PASS": "env"})
        self.assertEqual(merged["DB_PASS"], "env")

    def test_domain__build_rotation__produces_deltas(self) -> None:
        rotation = build_rotation({"A": "1", "B": "2"}, {"B": "2", "C": "3"}, 1, 2)
        self.assertEqual(rotation.generation, 2)
        self.assertEqual(rotation.previous_generation, 1)
        self.assertEqual(rotation.added_keys, ["C"])
        self.assertEqual(rotation.removed_keys, ["A"])
        self.assertEqual(rotation.updated_keys, [])
        self.assertEqual(rotation.unchanged_keys, ["B"])
