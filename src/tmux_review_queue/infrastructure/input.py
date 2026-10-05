"""Input reading adapter: the task document from ``--file PATH`` or stdin."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO


class InputError(Exception):
    """Raised when no input can be read (missing file or empty stream)."""


def read_input(file_path: str | None, stdin: TextIO | None = None) -> str:
    """Read the raw task document text from a file or stdin.

    ``None`` or ``"-"`` selects stdin. Raises :class:`InputError` when the
    selected source yields no non-whitespace content or the file cannot be read.
    """
    source = stdin if stdin is not None else sys.stdin
    if file_path and file_path != "-":
        try:
            text = Path(file_path).read_text(encoding="utf-8")
        except OSError as exc:
            raise InputError(f"tmux-review-queue: error: cannot read '{file_path}': {exc}") from exc
    else:
        text = source.read()
    if not text.strip():
        raise InputError(
            "tmux-review-queue: error: no input: pass '--file PATH' or pipe a "
            "task document to stdin"
        )
    return text
