"""MessageOutput adapter: all user-facing stderr/stdout text."""

from __future__ import annotations

import sys


class ConsoleMessageOutput:
    def error(self, msg: str) -> None:
        print(msg, file=sys.stderr)

    def registered(self, group_name: str) -> None:
        print(f"tmux-review-queue: registered review group '{group_name}'")
