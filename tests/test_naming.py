"""Unit tests for naming rules (task 3.1-3.2).

Covers slug Cyrillic preservation, hostile-char replacement, collapse,
truncation, and the exact group/session name strings including the ``·``
separator.
"""

from __future__ import annotations

from tmux_review_queue.domain.models import Repo, Task
from tmux_review_queue.domain.naming import SEPARATOR, group_name, session_name, slug


def task(**overrides):
    repo = Repo(name="backend", path="/repos/backend", ref="feature/x", base="main")
    fields = {"id": "rev-1", "description": "Review the parallel work", "repos": (repo,)}
    fields.update(overrides)
    return Task(**fields)


# --- slug --------------------------------------------------------------------


def test_slug_preserves_cyrillic_letters():
    assert slug("Проверка ветки ревью") == "Проверка-ветки-ревью"


def test_slug_replaces_hostile_chars():
    assert slug('a/b:c\\d"e`f') == "a-b-c-d-e-f"


def test_slug_replaces_quotes_and_apostrophes():
    assert slug("it's a 'bug'") == "it-s-a-bug"


def test_slug_collapses_repeated_separators():
    assert slug("a   b") == "a-b"
    assert slug("a -- b") == "a-b"
    assert slug("a  /  b") == "a-b"


def test_slug_strips_leading_and_trailing_dashes():
    assert slug("  hello  ") == "hello"
    assert slug("/hello/") == "hello"


def test_slug_truncates_to_about_40_chars():
    result = slug("x" * 50)
    assert len(result) == 40
    assert result == "x" * 40


def test_slug_truncation_strips_a_trailing_dash():
    result = slug("a" * 39 + " " + "b")
    assert result == "a" * 39
    assert not result.endswith("-")


def test_slug_keeps_underscores_and_hyphens():
    assert slug("feature_branch-v2") == "feature_branch-v2"


# --- group_name / session_name -----------------------------------------------


def test_group_name_is_id_separator_slug():
    t = task(description="Review the parallel work")
    assert group_name(t) == f"rev-1{SEPARATOR}Review-the-parallel-work"


def test_group_name_uses_cyrillic_slug():
    t = task(description="Проверка параллельной работы")
    assert group_name(t) == f"rev-1{SEPARATOR}Проверка-параллельной-работы"


def test_session_name_includes_id_repo_and_slug():
    t = task(description="Review the parallel work")
    r = t.repos[0]
    assert session_name(r, t) == f"rev-1{SEPARATOR}backend{SEPARATOR}Review-the-parallel-work"


def test_session_name_exact_string_with_separator():
    t = task(id="T-42", description="Проверка")
    r = Repo(name="frontend", path="/repos/frontend", ref="HEAD", base="main")
    assert session_name(r, t) == "T-42·frontend·Проверка"


def test_group_and_session_names_share_the_slug_suffix():
    t = task(id="rev-9", description="Проверка диффов")
    r = t.repos[0]
    suffix = f"{SEPARATOR}{slug(t.description)}"
    assert group_name(t).endswith(suffix)
    assert session_name(r, t).endswith(suffix)
