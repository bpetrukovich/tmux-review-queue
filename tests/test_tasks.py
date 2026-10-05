"""Unit tests for task-document parsing/validation (task 2.2).

Covers the spec scenarios: "valid accepted", "missing id", "repo missing a
ref", plus the no-partial-data guarantee.
"""

from __future__ import annotations

from tmux_review_queue.domain.models import Repo, Task
from tmux_review_queue.domain.tasks import parse_task


def doc(**overrides):
    base = {
        "id": "rev-7",
        "description": "Review parallel backend work",
        "repos": [
            {"name": "backend", "path": "/repos/backend", "ref": "feature/x", "base": "main"}
        ],
    }
    base.update(overrides)
    return base


def test_valid_task_accepted():
    task, problems = parse_task(doc())
    assert problems == []
    assert isinstance(task, Task)
    assert task.id == "rev-7"
    assert task.repos[0] == Repo(
        name="backend", path="/repos/backend", ref="feature/x", base="main"
    )


def test_valid_task_accepts_any_git_revision_strings():
    task, problems = parse_task(
        doc(
            repos=[
                {"name": "a", "path": "/a", "ref": "main", "base": "HEAD"},
                {"name": "b", "path": "/b", "ref": "v1.2.3", "base": "abc123def"},
            ]
        )
    )
    assert problems == []
    assert task.repos[0].ref == "main"
    assert task.repos[0].base == "HEAD"
    assert task.repos[1].ref == "v1.2.3"
    assert task.repos[1].base == "abc123def"


def test_missing_id_rejected():
    task, problems = parse_task(doc(id=""))
    assert task is None
    assert any("'id'" in p for p in problems)


def test_absent_id_rejected():
    task, problems = parse_task(doc(id=None))
    assert task is None
    assert any("'id'" in p for p in problems)


def test_missing_description_rejected():
    task, problems = parse_task(doc(description=""))
    assert task is None
    assert any("'description'" in p for p in problems)


def test_missing_repos_rejected():
    task, problems = parse_task(doc(repos=[]))
    assert task is None
    assert any("'repos'" in p for p in problems)


def test_repo_missing_ref_rejected():
    task, problems = parse_task(
        doc(repos=[{"name": "backend", "path": "/repos/backend", "ref": "", "base": "main"}])
    )
    assert task is None
    assert any("'ref'" in p for p in problems)
    assert "repo #1" in problems[0]


def test_repo_missing_base_rejected():
    task, problems = parse_task(
        doc(repos=[{"name": "backend", "path": "/repos/backend", "ref": "HEAD", "base": ""}])
    )
    assert task is None
    assert any("'base'" in p for p in problems)


def test_repo_missing_name_and_path_rejected():
    task, problems = parse_task(doc(repos=[{"ref": "HEAD", "base": "main"}]))
    assert task is None
    assert any("'name'" in p for p in problems)
    assert any("'path'" in p for p in problems)


def test_invalid_repo_entry_rejected():
    task, problems = parse_task(doc(repos=["not-an-object"]))
    assert task is None
    assert any("must be an object" in p for p in problems)


def test_non_object_document_rejected():
    task, problems = parse_task(["rev-7"])
    assert task is None
    assert problems == ["Task document must be a JSON object."]


def test_no_partial_data_when_second_repo_invalid():
    task, problems = parse_task(
        doc(
            repos=[
                {"name": "backend", "path": "/repos/backend", "ref": "HEAD", "base": "main"},
                {"name": "frontend", "path": "/repos/frontend"},
            ]
        )
    )
    assert task is None
    assert any("repo #2" in p and "'ref'" in p for p in problems)
    assert any("repo #2" in p and "'base'" in p for p in problems)
    # the valid first repo must not leak through as a partial result
    assert "repo #1" not in "\n".join(problems)
