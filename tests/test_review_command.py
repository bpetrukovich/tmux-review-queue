"""Unit tests for review command validation and rendering."""

from __future__ import annotations

from tmux_review_queue.domain.models import Repo
from tmux_review_queue.domain.review_command import render_command, validate_command


def make_repo(base: str = "main", ref: str = "feature/x") -> Repo:
    return Repo(name="backend", path="/repos/backend", ref=ref, base=base)


# --- validate_command ---------------------------------------------------------


def test_validate_accepts_template_with_both_placeholders():
    assert validate_command("nvim +'DiffviewOpen {base}..{ref}'") == []


def test_validate_flags_missing_base():
    problems = validate_command("diff {ref}")
    assert any("{base}" in p for p in problems)


def test_validate_flags_missing_ref():
    problems = validate_command("diff {base}")
    assert any("{ref}" in p for p in problems)


def test_validate_flags_missing_both():
    problems = validate_command("nvim +'DiffviewOpen'")
    assert any("{base}" in p for p in problems)
    assert any("{ref}" in p for p in problems)


def test_validate_flags_unknown_placeholder():
    problems = validate_command("diff {base} {ref} {repo}")
    assert any("{repo}" in p for p in problems)
    assert not any("{base}" in p for p in problems)


def test_validate_requires_non_empty_template():
    assert validate_command("") != []
    assert validate_command("   ") != []


def test_validate_leaves_empty_braces_alone():
    problems = validate_command("diff {base} {ref} {}")
    assert problems == []


# --- render_command -----------------------------------------------------------


def test_render_substitutes_per_repo():
    repo = make_repo(base="release/1.0", ref="HEAD")
    assert render_command("git diff {base} {ref}", repo) == "git diff release/1.0 HEAD"


def test_render_no_double_substitution():
    repo = make_repo(base="ref", ref="base")
    assert render_command("diff {base} {ref}", repo) == "diff ref base"


def test_render_preserves_template_surroundings():
    repo = make_repo()
    assert render_command("nvim +'DiffviewOpen {base}..{ref}'", repo) == (
        "nvim +'DiffviewOpen main..feature/x'"
    )
