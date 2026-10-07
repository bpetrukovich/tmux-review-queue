"""Unit tests for the TOML config loader."""

from __future__ import annotations

import pytest

from tmux_review_queue.app.configuration import ConfigError, ConfigNotFoundError
from tmux_review_queue.infrastructure.config_loader import (
    ENV_OVERRIDE,
    load_config,
)


def test_load_config_default_path(tmp_path, monkeypatch):
    target = tmp_path / "config.toml"
    target.write_text('[review]\ncommand = "git diff {base} {ref}"\n', encoding="utf-8")
    monkeypatch.delenv(ENV_OVERRIDE, raising=False)
    config = load_config(path=target)
    assert config.command == "git diff {base} {ref}"


def test_load_config_ignores_default_when_path_given(tmp_path, monkeypatch):
    target = tmp_path / "config.toml"
    target.write_text('[review]\ncommand = "git diff {base} {ref}"\n', encoding="utf-8")
    monkeypatch.delenv(ENV_OVERRIDE, raising=False)
    assert load_config(path=target).command == "git diff {base} {ref}"


def test_load_config_env_override_is_used(tmp_path, monkeypatch):
    target = tmp_path / "override.toml"
    target.write_text('[review]\ncommand = "git diff {base} {ref}"\n', encoding="utf-8")
    monkeypatch.setenv(ENV_OVERRIDE, str(target))
    assert load_config().command == "git diff {base} {ref}"


def test_load_config_missing_file_raises_not_found(tmp_path, monkeypatch):
    monkeypatch.delenv(ENV_OVERRIDE, raising=False)
    with pytest.raises(ConfigNotFoundError):
        load_config(path=tmp_path / "nope.toml")


def test_load_config_invalid_toml_raises_config_error(tmp_path):
    target = tmp_path / "config.toml"
    target.write_text("this is [not toml\n", encoding="utf-8")
    with pytest.raises(ConfigError) as excinfo:
        load_config(path=target)
    assert any("invalid TOML" in p for p in excinfo.value.problems)


def test_load_config_missing_command_raises(tmp_path):
    target = tmp_path / "config.toml"
    target.write_text("[review]\n", encoding="utf-8")
    with pytest.raises(ConfigError) as excinfo:
        load_config(path=target)
    assert any("[review].command" in p for p in excinfo.value.problems)


def test_load_config_missing_placeholder_raises(tmp_path):
    target = tmp_path / "config.toml"
    target.write_text('[review]\ncommand = "git diff {base}"\n', encoding="utf-8")
    with pytest.raises(ConfigError) as excinfo:
        load_config(path=target)
    assert any("{ref}" in p for p in excinfo.value.problems)


def test_load_config_unknown_placeholder_raises(tmp_path):
    target = tmp_path / "config.toml"
    target.write_text('[review]\ncommand = "git diff {base} {ref} {repo}"\n', encoding="utf-8")
    with pytest.raises(ConfigError) as excinfo:
        load_config(path=target)
    assert any("{repo}" in p for p in excinfo.value.problems)


def test_load_config_valid_file(tmp_path):
    target = tmp_path / "config.toml"
    target.write_text('[review]\ncommand = "git diff {base} {ref}"\n', encoding="utf-8")
    config = load_config(path=target)
    assert config.command == "git diff {base} {ref}"
