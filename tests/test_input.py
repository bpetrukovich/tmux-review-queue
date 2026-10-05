"""Unit tests for input reading (task 4.1).

Covers file source, stdin source, and the empty-input error.
"""

from __future__ import annotations

import io

import pytest

from tmux_review_queue.infrastructure.input import InputError, read_input

TASK_JSON = '{"id": "rev-1"}'


def test_read_from_file(tmp_path):
    path = tmp_path / "task.json"
    path.write_text(TASK_JSON, encoding="utf-8")
    assert read_input(str(path)) == TASK_JSON


def test_read_from_stdin():
    assert read_input(None, stdin=io.StringIO(TASK_JSON)) == TASK_JSON


def test_dash_reads_from_stdin():
    assert read_input("-", stdin=io.StringIO(TASK_JSON)) == TASK_JSON


def test_empty_stdin_raises_input_error():
    with pytest.raises(InputError) as exc:
        read_input(None, stdin=io.StringIO("   \n"))
    assert "no input" in str(exc.value)


def test_missing_file_raises_input_error():
    with pytest.raises(InputError) as exc:
        read_input("/nonexistent/task.json")
    assert "cannot read" in str(exc.value)
