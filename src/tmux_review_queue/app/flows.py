"""App flow: the single ``add`` pipeline.

Reads the task document (file/stdin), parses and validates it, builds the group
document, registers it with multi-sessionizer, and maps results to exit codes:
``0`` success, ``1`` validation/registration error (including a duplicate group
name, wrapped with an AI-friendly hint), ``2`` usage error (missing input).
No business rules or raw process/filesystem/terminal calls live here — the
pipeline threads values between the injected ``FlowDeps`` adapters and the pure
domain.
"""

from __future__ import annotations

import json
from typing import TextIO

from ..domain.naming import group_name
from ..domain.tasks import parse_task
from ..domain.workspaces import group_yaml
from ..infrastructure.input import InputError, read_input
from .ports import FlowDeps

DUPLICATE_HINT = "change the `id` or `description` so the group name differs, then retry"


def add_flow(file_path: str | None, deps: FlowDeps, stdin: TextIO | None = None) -> int:
    try:
        raw = read_input(file_path, stdin)
    except InputError as exc:
        deps.messages.error(str(exc))
        return 2

    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        deps.messages.error(f"tmux-review-queue: error: invalid JSON: {exc}")
        return 1

    task, problems = parse_task(doc)
    if task is None:
        for problem in problems:
            deps.messages.error(f"tmux-review-queue: error: {problem}")
        return 1

    result = deps.runner.run(group_yaml(task))
    if result.exit_code == 0:
        deps.messages.registered(group_name(task))
        return 0

    combined = "\n".join(line for line in (result.stdout, result.stderr) if line)
    if "already exists" in combined:
        deps.messages.error(combined)
        deps.messages.error(f"tmux-review-queue: error: {DUPLICATE_HINT}")
        return 1

    deps.messages.error(
        combined or f"tmux-review-queue: error: multi-sessionizer failed (exit {result.exit_code})"
    )
    return 1
