"""Infrastructure adapter: multi-sessionizer invoked as a black-box subprocess.

Runs ``multi-sessionizer external add "<group-yaml>"`` and surfaces
stdout/stderr and the exit code. The group document is passed as a single argv
element (quoted by the shell), exactly as the external CLI expects.
"""

from __future__ import annotations

import subprocess

from ..app.ports import MszResult


class MultiSessionizerRunner:
    """Object adapter satisfying the app ``MszRunner`` port."""

    def __init__(self, executable: str = "multi-sessionizer") -> None:
        self._executable = executable

    def run(self, group_yaml: str) -> MszResult:
        argv = [self._executable, "external", "add", group_yaml]
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            return MszResult(
                stdout="",
                stderr=(f"tmux-review-queue: error: cannot run '{self._executable}': {exc}"),
                exit_code=1,
            )
        return MszResult(stdout=proc.stdout, stderr=proc.stderr, exit_code=proc.returncode)
