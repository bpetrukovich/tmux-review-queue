"""Unit tests for the ``add`` flow exit-code paths (task 4.3/4.6)."""

from __future__ import annotations

import io

from tmux_review_queue.app.configuration import ReviewConfig
from tmux_review_queue.app.flows import DUPLICATE_HINT, add_flow
from tmux_review_queue.app.ports import FlowDeps, MszResult

VALID_DOC = """\
{
  "id": "rev-1",
  "description": "Review the parallel work",
  "repos": [
    {"name": "backend", "path": "/repos/backend", "ref": "feature/x", "base": "main"}
  ]
}
"""


class FakeRunner:
    def __init__(self, result: MszResult):
        self.result = result
        self.calls: list[str] = []

    def run(self, group_yaml: str) -> MszResult:
        self.calls.append(group_yaml)
        return self.result


class FakeMessages:
    def __init__(self):
        self.errors: list[str] = []
        self.registered_names: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def registered(self, group_name: str) -> None:
        self.registered_names.append(group_name)


def deps(result: MszResult):
    return FlowDeps(
        runner=FakeRunner(result),
        messages=FakeMessages(),
        config=ReviewConfig(command="git diff {base} {ref}"),
    )


def stdin_for(text: str):
    return io.StringIO(text)


# --- success -----------------------------------------------------------------


def test_add_flow_success_exits_zero_and_names_the_group():
    d = deps(MszResult(stdout="added\n", stderr="", exit_code=0))
    code = add_flow(None, d, stdin=stdin_for(VALID_DOC))
    assert code == 0
    assert d.messages.registered_names == ["rev-1·Review-the-parallel-work"]
    assert d.messages.errors == []
    assert len(d.runner.calls) == 1
    assert "name: rev-1·Review-the-parallel-work" in d.runner.calls[0]


# --- usage errors (exit 2) ---------------------------------------------------


def test_add_flow_no_input_is_usage_error():
    d = deps(MszResult(stdout="", stderr="", exit_code=0))
    code = add_flow(None, d, stdin=stdin_for("   \n"))
    assert code == 2
    assert any("no input" in e for e in d.messages.errors)
    assert d.runner.calls == []


def test_add_flow_missing_file_is_usage_error():
    d = deps(MszResult(stdout="", stderr="", exit_code=0))
    code = add_flow("/nonexistent/task.json", d)
    assert code == 2
    assert any("cannot read" in e for e in d.messages.errors)


# --- validation errors (exit 1) ----------------------------------------------


def test_add_flow_invalid_json_is_validation_error():
    d = deps(MszResult(stdout="", stderr="", exit_code=0))
    code = add_flow(None, d, stdin=stdin_for("not json"))
    assert code == 1
    assert any("invalid JSON" in e for e in d.messages.errors)
    assert d.runner.calls == []


def test_add_flow_validation_problems_exit_one_with_named_problem():
    d = deps(MszResult(stdout="", stderr="", exit_code=0))
    code = add_flow(None, d, stdin=stdin_for('{"description": "x", "repos": []}'))
    assert code == 1
    assert any("'id'" in e for e in d.messages.errors)
    assert any("'repos'" in e for e in d.messages.errors)
    assert d.runner.calls == []


# --- registration errors (exit 1) ---------------------------------------------


def test_add_flow_propagates_msz_error_as_exit_one():
    d = deps(MszResult(stdout="", stderr="backend blew up\n", exit_code=1))
    code = add_flow(None, d, stdin=stdin_for(VALID_DOC))
    assert code == 1
    assert any("backend blew up" in e for e in d.messages.errors)


def test_add_flow_duplicate_adds_hint_and_exits_one():
    d = deps(
        MszResult(
            stdout="",
            stderr="External entry already exists: rev-1·Review-the-parallel-work.\n",
            exit_code=1,
        )
    )
    code = add_flow(None, d, stdin=stdin_for(VALID_DOC))
    assert code == 1
    assert any("already exists" in e for e in d.messages.errors)
    assert any(DUPLICATE_HINT in e for e in d.messages.errors)


def test_add_flow_missing_runner_is_registration_error():
    d = deps(
        MszResult(stdout="", stderr="tmux-review-queue: error: cannot run 'msz': nope", exit_code=1)
    )
    code = add_flow(None, d, stdin=stdin_for(VALID_DOC))
    assert code == 1
    assert any("cannot run" in e for e in d.messages.errors)
