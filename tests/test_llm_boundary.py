from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest import mock

from loophole.errors import DependencyError, ProviderAuthError
from loophole.llm import LLMClient


class LLMBoundaryTests(unittest.TestCase):
    def test_llm_client_raises_clear_error_without_anthropic_dependency(self) -> None:
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "anthropic":
                raise ModuleNotFoundError("No module named 'anthropic'")
            return real_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=fake_import):
            with self.assertRaises(DependencyError) as exc_info:
                LLMClient()

        message = str(exc_info.exception)
        self.assertIn("uv sync", message)
        self.assertIn("python -m pip install -e .", message)

    def test_llm_client_translates_provider_auth_failure(self) -> None:
        class FakeAuthenticationError(Exception):
            pass

        client = LLMClient.__new__(LLMClient)
        client.anthropic = SimpleNamespace(AuthenticationError=FakeAuthenticationError)
        client.client = SimpleNamespace(
            messages=SimpleNamespace(
                create=mock.Mock(side_effect=FakeAuthenticationError("invalid x-api-key"))
            )
        )
        client.model = "test-model"
        client.max_tokens = 128

        with self.assertRaises(ProviderAuthError) as exc_info:
            client.call("system", "user")

        message = str(exc_info.exception)
        self.assertIn("authentication failed", message.lower())
        self.assertIn("LOOPHOLE_API_KEY", message)
