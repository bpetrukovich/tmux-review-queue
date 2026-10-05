"""Domain DTOs: the review task and its repositories.

Frozen dataclasses so instances are immutable value objects; omitting a field
raises ``TypeError`` because every field is required.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Repo:
    """A single repository under review.

    ``ref`` is the revision under review (right side of the diff); ``base`` is
    the comparison base (left side). Both accept any git revision string — a
    branch, a tag, a commit hash, or ``HEAD``. Existence is never validated:
    Diffview resolves the range at selection time.
    """

    name: str
    path: str
    ref: str
    base: str


@dataclass(frozen=True)
class Task:
    """A review task: a stable id, a human description, and one or more repos."""

    id: str
    description: str
    repos: tuple[Repo, ...]
