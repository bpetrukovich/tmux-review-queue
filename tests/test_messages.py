"""Unit tests for the console message output (task 4.5)."""

from __future__ import annotations

from tmux_review_queue.infrastructure.messages import ConsoleMessageOutput


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
