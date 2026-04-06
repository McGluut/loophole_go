from __future__ import annotations


class LoopholeError(Exception):
    """Base exception for repo-specific runtime failures."""


class DependencyError(LoopholeError):
    """Raised when an optional runtime dependency is unavailable."""


class ProviderAuthError(LoopholeError):
    """Raised when the configured provider rejects the supplied credentials."""


class ProtocolError(LoopholeError):
    """Raised when an agent response breaks the expected contract."""
