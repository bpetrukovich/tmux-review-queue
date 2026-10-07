"""Infrastructure adapter: review configuration file loading.

Reads and validates the required TOML config following multi-sessionizer
conventions: ``~/.config/tmux-review-queue/config.toml`` by default, overridable
via ``TMUX_REVIEW_QUEUE_CONFIG``. A missing file raises
:class:`ConfigNotFoundError`; an invalid TOML or an invalid ``[review].command``
raises :class:`ConfigError` carrying the full problem list.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from ..app.configuration import ConfigError, ConfigNotFoundError, ReviewConfig
from ..domain.review_command import validate_command

DEFAULT_PATH = Path.home() / ".config" / "tmux-review-queue" / "config.toml"
ENV_OVERRIDE = "TMUX_REVIEW_QUEUE_CONFIG"


def _config_path() -> Path:
    override = os.environ.get(ENV_OVERRIDE)
    return Path(override).expanduser() if override else DEFAULT_PATH


def load_config(path: str | Path | None = None) -> ReviewConfig:
    """Load and validate the review configuration.

    ``path=None`` resolves the default path (env override respected). Raises
    :class:`ConfigNotFoundError` when the file is missing and
    :class:`ConfigError` when it does not parse or fails ``validate_command``.
    """
    target = Path(path).expanduser() if path is not None else _config_path()
    try:
        raw = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigNotFoundError(
            f"tmux-review-queue: error: config not found at '{target}': {exc}"
        ) from exc

    try:
        data = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError([f"tmux-review-queue: error: invalid TOML in '{target}': {exc}"]) from exc

    review = data.get("review")
    command = review.get("command") if isinstance(review, dict) else None
    if not isinstance(command, str) or not command.strip():
        raise ConfigError(
            [
                f"tmux-review-queue: error: config is missing a non-empty '[review].command' in '{target}'"
            ]
        )

    problems = validate_command(command)
    if problems:
        raise ConfigError([f"tmux-review-queue: error: {problem}" for problem in problems])

    return ReviewConfig(command=command)
