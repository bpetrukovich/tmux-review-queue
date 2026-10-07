"""Pure review-command template validation and rendering.

The configured ``[review].command`` is a shell template with exactly the
``{base}`` and ``{ref}`` placeholders. Purely functional — no subprocess,
filesystem, or environment access.
"""

from __future__ import annotations

import re

from .models import Repo

_PLACEHOLDER = re.compile(r"\{([^{}]+)\}")
_RENDER = re.compile(r"\{base\}|\{ref\}")


def validate_command(template: str) -> list[str]:
    """Return the list of problems for an invalid review command template.

    A valid template is a non-empty string containing both ``{base}`` and
    ``{ref}`` and no other ``{...}`` placeholder. Empty ``{}`` sequences do not
    match and are left untouched.
    """
    if not template or not template.strip():
        return ["review command must be a non-empty string"]
    placeholders = {match for match in _PLACEHOLDER.findall(template)}
    problems: list[str] = []
    for required in ("base", "ref"):
        if required not in placeholders:
            problems.append(f"review command is missing the {{{required}}} placeholder")
    for unknown in sorted(placeholders - {"base", "ref"}):
        problems.append(f"review command has an unknown placeholder {{{unknown}}}")
    return problems


def render_command(template: str, repo: Repo) -> str:
    """Render a review command template with a repository's base/ref.

    Single-pass substitution so a value that itself contains the other
    placeholder's text is never substituted again.
    """
    values = {"base": repo.base, "ref": repo.ref}
    return _RENDER.sub(lambda match: values[match.group(0)[1:-1]], template)
