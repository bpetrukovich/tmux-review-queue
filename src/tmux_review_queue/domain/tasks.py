"""Pure task-document parsing and validation.

Turns the JSON document (a dict) into a :class:`Task` or a list of named
problems. Purely functional: no subprocess, filesystem, or environment access.

Validation rules (spec §Task payload validation): a task SHALL have a non-empty
``id``, a non-empty ``description``, and a non-empty ``repos`` array; each repo
SHALL have a non-empty ``name``, ``path``, ``ref``, and ``base``. ``ref`` and
``base`` accept any git revision string. An invalid document yields ``(None,
problems)`` — no partial data is ever produced.
"""

from __future__ import annotations

from typing import Any

from .models import Repo, Task

_REPO_FIELDS = ("name", "path", "ref", "base")


def _missing(field: str) -> str:
    return f"Task is missing a non-empty '{field}'."


def _validate_repo(repo: object, index: int) -> list[str]:
    label = f"repo #{index + 1}"
    if not isinstance(repo, dict):
        return [f"Task repo #{index + 1} must be an object."]
    problems: list[str] = []
    for field in _REPO_FIELDS:
        value = repo.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{label} is missing a non-empty '{field}'.")
    return problems


def parse_task(doc: Any) -> tuple[Task | None, list[str]]:
    """Validate a task document dict, returning ``(task, problems)``.

    A valid document yields ``(Task, [])``; an invalid one yields
    ``(None, problems)`` where ``problems`` names every violated rule, so
    nothing partial is ever registered.
    """
    if not isinstance(doc, dict):
        return None, ["Task document must be a JSON object."]

    problems: list[str] = []

    task_id = doc.get("id")
    if not isinstance(task_id, str) or not task_id.strip():
        problems.append(_missing("id"))

    description = doc.get("description")
    if not isinstance(description, str) or not description.strip():
        problems.append(_missing("description"))

    repos = doc.get("repos")
    if not isinstance(repos, list) or not repos:
        problems.append(_missing("repos"))
    else:
        for index, repo in enumerate(repos):
            problems.extend(_validate_repo(repo, index))

    if problems:
        return None, problems

    return (
        Task(
            id=task_id.strip(),
            description=description.strip(),
            repos=tuple(
                Repo(
                    name=repo["name"].strip(),
                    path=repo["path"].strip(),
                    ref=repo["ref"].strip(),
                    base=repo["base"].strip(),
                )
                for repo in repos
            ),
        ),
        [],
    )
