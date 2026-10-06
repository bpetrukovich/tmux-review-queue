"""Unit tests for workspace and group YAML generation (task 3.3-3.4).

Asserts the parsed YAML fields and that no ``git checkout``/``git switch``
command ever appears.
"""

from __future__ import annotations

import yaml

from tmux_review_queue.domain.models import Repo, Task
from tmux_review_queue.domain.naming import group_name, session_name
from tmux_review_queue.domain.workspaces import group_yaml, workspace_yaml


def two_repo_task():
    repos = (
        Repo(name="backend", path="/repos/backend", ref="feature/x", base="main"),
        Repo(name="frontend", path="/repos/frontend", ref="HEAD", base="release/1.0"),
    )
    return Task(id="rev-3", description="Review the parallel work", repos=repos)


# --- workspace_yaml ----------------------------------------------------------


def test_workspace_yaml_fields():
    task = two_repo_task()
    repo = task.repos[0]
    data = yaml.safe_load(workspace_yaml(repo, task))
    assert data["session_name"] == session_name(repo, task)
    assert data["start_directory"] == "/repos/backend"
    assert [w["window_name"] for w in data["windows"]] == ["diff"]
    assert data["windows"][0]["panes"][0]["shell_command"] == "nvim +'DiffviewOpen main..feature/x'"


def test_workspace_yaml_uses_repo_specific_diff_range():
    task = two_repo_task()
    repo = task.repos[1]
    data = yaml.safe_load(workspace_yaml(repo, task))
    assert data["start_directory"] == "/repos/frontend"
    assert data["windows"][0]["panes"][0]["shell_command"] == "nvim +'DiffviewOpen release/1.0..HEAD'"


def test_workspace_yaml_never_checks_out_or_switches():
    task = two_repo_task()
    for repo in task.repos:
        text = workspace_yaml(repo, task)
        assert "git checkout" not in text
        assert "git switch" not in text


def test_workspace_yaml_is_valid_yaml_and_is_a_mapping():
    task = two_repo_task()
    data = yaml.safe_load(workspace_yaml(task.repos[0], task))
    assert isinstance(data, dict)


# --- group_yaml --------------------------------------------------------------


def test_group_yaml_round_trips_name_and_member_count():
    task = two_repo_task()
    data = yaml.safe_load(group_yaml(task))
    assert data["name"] == group_name(task)
    assert isinstance(data["sessions"], list)
    assert len(data["sessions"]) == 2


def test_group_yaml_tags_carries_task_id():
    task = two_repo_task()
    data = yaml.safe_load(group_yaml(task))
    assert data["tags"] == ["rev-3"]


def test_group_yaml_members_are_workspace_documents():
    task = two_repo_task()
    data = yaml.safe_load(group_yaml(task))
    for member in data["sessions"]:
        ws = yaml.safe_load(member)
        assert isinstance(ws, dict)
        assert ws["windows"][0]["window_name"] == "diff"
        assert ws["windows"][0]["panes"][0]["shell_command"].startswith("nvim +'DiffviewOpen ")


def test_group_yaml_one_member_per_repo():
    task = two_repo_task()
    data = yaml.safe_load(group_yaml(task))
    assert len(data["sessions"]) == len(task.repos)


def test_group_yaml_never_contains_checkout_or_switch():
    assert "git checkout" not in group_yaml(two_repo_task())
    assert "git switch" not in group_yaml(two_repo_task())


def test_group_yaml_members_parse_as_multi_sessionizer_workspace_strings():
    task = two_repo_task()
    data = yaml.safe_load(group_yaml(task))
    for member in data["sessions"]:
        assert isinstance(member, str)
