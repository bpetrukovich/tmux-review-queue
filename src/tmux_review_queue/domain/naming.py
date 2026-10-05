"""Pure naming rules: slug generation, group name, and per-repo session name.

``slug`` preserves unicode letters (Cyrillic kept, no transliteration), replaces
whitespace and tmux-hostile characters (``/``, ``:``, ``\\``, ``"``, backtick,
quotes, and any other punctuation/space) with ``-``, collapses repeats, and
truncates to ~40 characters. Purely functional — no subprocess, filesystem, or
environment access.
"""

from __future__ import annotations

import re

from .models import Repo, Task

_KEEP = re.compile(r"[^\w·-]+", re.UNICODE)
_REPEATED_DASH = re.compile(r"-{2,}")

SEPARATOR = "·"


def slug(text: str, limit: int = 40) -> str:
    """Slug a description into a tmux-safe label."""
    s = _KEEP.sub("-", text)
    s = _REPEATED_DASH.sub("-", s)
    s = s.strip("-")
    if len(s) > limit:
        s = s[:limit].rstrip("-")
    return s


def group_name(task: Task) -> str:
    """The multi-sessionizer group name: ``<task_id>·<slug(description)>``."""
    return f"{task.id}{SEPARATOR}{slug(task.description)}"


def session_name(repo: Repo, task: Task) -> str:
    """The per-repo tmux session name: ``<task_id>·<repo_name>·<slug>``."""
    return f"{task.id}{SEPARATOR}{repo.name}{SEPARATOR}{slug(task.description)}"
