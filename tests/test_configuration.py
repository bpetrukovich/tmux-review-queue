"""Unit tests for the configuration DTO and errors."""

from __future__ import annotations

import pytest

from tmux_review_queue.app.configuration import ConfigError, ConfigNotFoundError, ReviewConfig


def test_review_config_field_access():
    config = ReviewConfig(command="git diff {base} {ref}")
    assert config.command == "git diff {base} {ref}"


def test_config_error_carries_problem_list():
    problems = ["first problem", "second problem"]
    exc = ConfigError(problems)
    assert exc.problems == problems
    assert "first problem" in str(exc)
    assert "second problem" in str(exc)


def test_config_not_found_is_distinct_error():
    assert issubclass(ConfigNotFoundError, Exception)
    assert not issubclass(ConfigNotFoundError, ConfigError)
    assert isinstance(ConfigNotFoundError("gone"), ConfigNotFoundError)


def test_review_config_is_frozen():
    config = ReviewConfig(command="x")
    with pytest.raises(AttributeError):
        config.command = "y"  # type: ignore[misc]
