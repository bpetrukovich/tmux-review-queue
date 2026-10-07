"""Unit tests for the CLI entry point (task 4.4).

``--help`` prints usage; a missing command, an unknown command, or a malformed
``add`` invocation exit 2 with a usage error.
"""

from __future__ import annotations

import io
import sys

from tmux_review_queue import main as main_module
from tmux_review_queue.app.configuration import ConfigError, ConfigNotFoundError, ReviewConfig
from tmux_review_queue.app.ports import MszResult

TEST_CONFIG = ReviewConfig(command="git diff {base} {ref}")


def test_help_prints_usage_and_exits_zero(capsys):
    assert main_module.main(["--help"]) == 0
    out = capsys.readouterr().out
    assert "usage: tmux-review-queue" in out
    assert "add" in out


def test_no_args_is_usage_error(capsys):
    assert main_module.main([]) == 2
    err = capsys.readouterr().err
    assert "missing command" in err


def test_unknown_command_is_usage_error(capsys):
    assert main_module.main(["switch"]) == 2
    assert "unknown command: switch" in capsys.readouterr().err


def test_add_help_prints_add_usage(capsys):
    assert main_module.main(["add", "--help"]) == 0
    out = capsys.readouterr().out
    assert "usage: tmux-review-queue add" in out
    assert "--file PATH" in out


def test_add_file_missing_argument_is_usage_error(capsys):
    assert main_module.main(["add", "--file"]) == 2
    assert "--file requires a PATH" in capsys.readouterr().err


def test_add_unexpected_argument_is_usage_error(capsys):
    assert main_module.main(["add", "task.json"]) == 2
    assert "unexpected argument: task.json" in capsys.readouterr().err


def test_add_with_file_runs_flow(tmp_path, monkeypatch, capsys):
    path = tmp_path / "task.json"
    path.write_text(
        '{"id": "rev-9", "description": "Проверка",'
        ' "repos": [{"name": "a", "path": "/a", "ref": "HEAD", "base": "main"}]}',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        main_module,
        "default_deps",
        lambda: main_module.FlowDeps(
            runner=FakeRunner(MszResult(stdout="added\n", stderr="", exit_code=0)),
            messages=main_module.ConsoleMessageOutput(),
            config=TEST_CONFIG,
        ),
    )
    assert main_module.main(["add", "--file", str(path)]) == 0
    out = capsys.readouterr().out
    assert "registered review group 'rev-9·Проверка'" in out


def test_add_dash_reads_stdin(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "stdin",
        io.StringIO(
            '{"id": "rev-9", "description": "Проверка",'
            ' "repos": [{"name": "a", "path": "/a", "ref": "HEAD", "base": "main"}]}'
        ),
    )
    monkeypatch.setattr(
        main_module,
        "default_deps",
        lambda: main_module.FlowDeps(
            runner=FakeRunner(MszResult(stdout="added\n", stderr="", exit_code=0)),
            messages=main_module.ConsoleMessageOutput(),
            config=TEST_CONFIG,
        ),
    )
    assert main_module.main(["add", "-"]) == 0
    assert "registered review group" in capsys.readouterr().out


class FakeRunner:
    def __init__(self, result):
        self.result = result

    def run(self, group_yaml):
        return self.result


# --- config errors (exit 1) ---------------------------------------------------


def test_add_missing_config_prints_skeleton_and_exits_one(monkeypatch, capsys):
    def missing(*args, **kwargs):
        raise ConfigNotFoundError("tmux-review-queue: error: config not found")

    monkeypatch.setattr(main_module, "default_deps", missing)
    assert main_module.main(["add"]) == 1
    err = capsys.readouterr().err
    assert "config not found" in err
    assert "[review]" in err
    assert "{base}" in err


def test_add_config_error_prints_problems_and_exits_one(monkeypatch, capsys):
    def broken(*args, **kwargs):
        raise ConfigError(["tmux-review-queue: error: bad placeholder"])

    monkeypatch.setattr(main_module, "default_deps", broken)
    assert main_module.main(["add"]) == 1
    assert "bad placeholder" in capsys.readouterr().err


def test_add_help_works_without_config(monkeypatch, capsys):
    def missing(*args, **kwargs):
        raise ConfigNotFoundError("tmux-review-queue: error: config not found")

    monkeypatch.setattr(main_module, "default_deps", missing)
    assert main_module.main(["add", "--help"]) == 0
    assert "usage: tmux-review-queue add" in capsys.readouterr().out
