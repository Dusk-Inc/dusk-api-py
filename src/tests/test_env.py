import os
import unittest

from functions.env import parse_env


class TestEnv(unittest.TestCase):
    def test_domain__valid_env__parses_port_and_host(self) -> None:
        original = dict(os.environ)
        try:
            os.environ["HOST"] = "127.0.0.1"
            os.environ["PORT"] = "3000"
            result = parse_env()
            self.assertEqual(result, {"HOST": "127.0.0.1", "PORT": 3000})
        finally:
            os.environ.clear()
            os.environ.update(original)

    def test_complement__port_out_of_range__throws_validation_error(self) -> None:
        original = dict(os.environ)
        try:
            os.environ["HOST"] = "127.0.0.1"
            os.environ["PORT"] = "0"
            with self.assertRaises(ValueError):
                parse_env()
        finally:
            os.environ.clear()
            os.environ.update(original)
