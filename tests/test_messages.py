"""Unit tests for the console message output (task 4.5)."""

from __future__ import annotations

import tomllib

from tmux_review_queue.domain.review_command import validate_command
from tmux_review_queue.infrastructure.messages import CONFIG_EXAMPLE, ConsoleMessageOutput


def test_registered_names_the_group_on_stdout(capsys):
    ConsoleMessageOutput().registered("rev-1·Review-the-work")
    assert (
        capsys.readouterr().out
        == "tmux-review-queue: registered review group 'rev-1·Review-the-work'\n"
    )


def test_error_goes_to_stderr(capsys):
    ConsoleMessageOutput().error("boom")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "boom\n"


def test_config_example_command_passes_validation():
    data = tomllib.loads(CONFIG_EXAMPLE)
    assert validate_command(data["review"]["command"]) == []
    assert "{base}" in data["review"]["command"]
    assert "{ref}" in data["review"]["command"]
