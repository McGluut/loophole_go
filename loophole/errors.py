from __future__ import annotations


class LoopholeError(Exception):
    """Base exception for repo-specific runtime failures."""


class DependencyError(LoopholeError):
    """Raised when an optional runtime dependency is unavailable."""


class ProtocolError(LoopholeError):
    """Raised when an agent response breaks the expected contract."""
