"""Unit tests for the domain models (task 2.1).

Frozen dataclasses must construct cleanly and raise ``TypeError`` on missing
fields (every field is required, no defaults).
"""

from __future__ import annotations

import pytest

from tmux_review_queue.domain.models import Repo, Task


def repo(**overrides):
    fields = {"name": "backend", "path": "/repos/backend", "ref": "feature/x", "base": "main"}
    fields.update(overrides)
    return Repo(**fields)


def test_task_constructs_with_full_fields():
    r1, r2 = repo(name="backend"), repo(name="frontend")
    task = Task("rev-1", "Review the parallel work", (r1, r2))
    assert task.id == "rev-1"
    assert task.description == "Review the parallel work"
    assert task.repos == (r1, r2)


def test_task_is_immutable():
    task = Task("rev-1", "Review", (repo(),))
    with pytest.raises(AttributeError):
        task.description = "changed"


def test_repo_constructs_with_all_fields():
    r = Repo(name="backend", path="/repos/backend", ref="HEAD", base="main")
    assert r.name == "backend"
    assert r.path == "/repos/backend"
    assert r.ref == "HEAD"
    assert r.base == "main"


def test_repo_is_immutable():
    r = repo()
    with pytest.raises(AttributeError):
        r.ref = "other"


def test_task_missing_repos_raises_type_error():
    with pytest.raises(TypeError):
        Task(id="rev-1", description="Review")


def test_task_missing_description_raises_type_error():
    with pytest.raises(TypeError):
        Task(id="rev-1", repos=(repo(),))


def test_repo_missing_ref_raises_type_error():
    with pytest.raises(TypeError):
        Repo(name="backend", path="/repos/backend", base="main")


def test_repo_missing_base_raises_type_error():
    with pytest.raises(TypeError):
        Repo(name="backend", path="/repos/backend", ref="HEAD")
