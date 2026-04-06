from __future__ import annotations

import unittest
from unittest import mock

from loophole.errors import DependencyError
from loophole.llm import LLMClient


class LLMBoundaryTests(unittest.TestCase):
    def test_llm_client_raises_clear_error_without_anthropic_dependency(self) -> None:
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "anthropic":
                raise ModuleNotFoundError("No module named 'anthropic'")
            return real_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=fake_import):
            with self.assertRaises(DependencyError):
                LLMClient()
