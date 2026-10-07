# tmux-review-queue — agent & contributor notes

## Test & quality commands

`uv run pytest` may fail to spawn pytest (permission denied) — use:

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format . --check
```

## Tool boundaries

This tool never runs tmux, tmuxp, or nvim itself. It builds tmuxp workspace
documents and registers them with `multi-sessionizer` (the local CLI) as a
named group of external entries; `multi-sessionizer` is called strictly as a
black box through `multi-sessionizer external add "<group-yaml>"` and its code,
config, and data store are never modified or read directly.

Domain (`src/tmux_review_queue/domain/`) must stay free of subprocess,
filesystem, and environment access.

## Acceptance criteria

Please ensure user has always installed the latest version of this tool in path
