"""Unit tests for the multi-sessionizer runner (task 4.2).

Asserts the exact argv passed to the subprocess and the returned
stdout/stderr/exit code.
"""

from __future__ import annotations

import subprocess

from tmux_review_queue.infrastructure.runner import MultiSessionizerRunner

GROUP_YAML = "name: rev-1·Review-the-work\nsessions:\n  - |-\n    session_name: rev-1\n"


def test_run_builds_exact_argv(monkeypatch):
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout="added\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = MultiSessionizerRunner().run(GROUP_YAML)

    assert captured["argv"] == ["multi-sessionizer", "external", "add", GROUP_YAML]
    assert captured["kwargs"]["check"] is False
    assert captured["kwargs"]["capture_output"] is True
    assert captured["kwargs"]["text"] is True
    assert result.exit_code == 0
    assert result.stdout == "added\n"
    assert result.stderr == ""


def test_run_uses_custom_executable(monkeypatch):
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    MultiSessionizerRunner(executable="fake-msz").run(GROUP_YAML)
    assert captured["argv"][0] == "fake-msz"


def test_run_surfaces_nonzero_exit(monkeypatch):
    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(
            argv, 1, "", "External entry already exists: rev-1·Review-the-work.\n"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = MultiSessionizerRunner().run(GROUP_YAML)
    assert result.exit_code == 1
    assert "already exists" in result.stderr


def test_run_handles_missing_executable(monkeypatch):
    def fake_run(argv, **kwargs):
        raise FileNotFoundError("No such file or directory")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = MultiSessionizerRunner().run(GROUP_YAML)
    assert result.exit_code == 1
    assert "cannot run" in result.stderr
