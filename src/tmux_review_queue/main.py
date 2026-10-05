"""Entry point: infrastructure CLI dispatch + composition root.

``main`` handles help/version/unknown output and dispatches the single ``add``
command to the app flow (``add_flow``) with a real ``FlowDeps`` built by
``default_deps``. Invoking the tool without a command is a usage error (exit
2); the only available command is ``add`` (no picker, no list/delete).
"""

from __future__ import annotations

import sys
from collections.abc import Sequence

from .app.flows import add_flow
from .app.ports import FlowDeps
from .infrastructure.messages import ConsoleMessageOutput
from .infrastructure.runner import MultiSessionizerRunner

USAGE = """\
usage: tmux-review-queue [-h] add ...

Register a review task as a multi-sessionizer group.

subcommands:
  add                     register a review task from a JSON document

options:
  -h, --help     show this help message and exit
"""

ADD_USAGE = """\
usage: tmux-review-queue add [-h] [--file PATH]

Register a review task as a multi-sessionizer group. The task document is read
from --file PATH or, with '-', from stdin.

options:
  -h, --help     show this help message and exit
  --file PATH    read the task document from this file ('-' reads stdin)
"""


def _error(msg: str) -> None:
    print(f"tmux-review-queue: error: {msg}", file=sys.stderr)
    print("Try 'tmux-review-queue --help' for more information.", file=sys.stderr)


def default_deps() -> FlowDeps:
    """Composition root: real runner and console message output."""
    return FlowDeps(
        runner=MultiSessionizerRunner(),
        messages=ConsoleMessageOutput(),
    )


def _add_dispatch(args: Sequence[str], deps: FlowDeps | None = None) -> int:
    deps = deps or default_deps()
    file_path: str | None = None
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in ("-h", "--help"):
            print(ADD_USAGE, end="")
            return 0
        if arg == "--file":
            index += 1
            if index >= len(args):
                _error("--file requires a PATH argument")
                return 2
            file_path = args[index]
        elif arg == "-":
            file_path = "-"
        else:
            _error(f"unexpected argument: {arg}")
            return 2
        index += 1
    return add_flow(file_path, deps)


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        _error("missing command")
        return 2
    if argv[0] in ("-h", "--help"):
        print(USAGE, end="")
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd != "add":
        _error(f"unknown command: {cmd}")
        return 2
    return _add_dispatch(rest)
