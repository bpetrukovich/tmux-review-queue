"""App DTOs and errors for the review configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewConfig:
    """Validated review configuration consumed by the ``add`` flow."""

    command: str


class ConfigError(Exception):
    """The configuration exists but is invalid; carries the problem list."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = problems


class ConfigNotFoundError(Exception):
    """No config file exists at the expected path."""
