"""MessageOutput adapter: all user-facing stderr/stdout text."""

from __future__ import annotations

import sys

CONFIG_EXAMPLE = """\
# tmux-review-queue configuration
# Copy to ~/.config/tmux-review-queue/config.toml (or the path in
# $TMUX_REVIEW_QUEUE_CONFIG) and adjust the review command.

[review]
command = "nvim +'DiffviewOpen {base}..{ref}'"
"""


class ConsoleMessageOutput:
    def error(self, msg: str) -> None:
        print(msg, file=sys.stderr)

    def registered(self, group_name: str) -> None:
        print(f"tmux-review-queue: registered review group '{group_name}'")
