# Tasks

## 1. Project scaffolding

- [x] 1.1 Initialize a `uv` Python package `tmux-review-queue` at the repo root with `pyproject.toml` (Python >=3.12, `PyYAML`, dev extras `pytest`/`ruff`, `[project.scripts] tmux-review-queue = "tmux_review_queue.main:main"`, `[tool.uv] package = true`) and verify `uv run tmux-review-queue --help` prints usage
- [x] 1.2 Add `src/tmux_review_queue/` package skeleton (`domain/`, `app/`, `infrastructure/` subpackages with `__init__.py`) and verify `uv run python -c "import tmux_review_queue"` succeeds
- [x] 1.3 Add `AGENTS.md` with test/quality commands (`.venv/bin/python -m pytest -q`, `.venv/bin/ruff check .`, `.venv/bin/ruff format . --check`) and the note that the tool never runs tmux itself and calls `multi-sessionizer` as a black box; verify the commands listed run clean on the empty package
- [x] 1.4 Add `.gitignore` for `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`; verify `uv sync` works and ignores apply

## 2. Domain: task model and validation

- [x] 2.1 Implement frozen dataclasses `Task(id, description, repos)` and `Repo(name, path, ref, base)` in `domain/models.py`; verify unit tests construct both and fail on missing fields
- [x] 2.2 Implement task-document parsing/validation from a dict (non-empty `id`, non-empty `description`, non-empty `repos`; each repo with non-empty `name`/`path`/`ref`/`base`, where `ref` and `base` accept any git revision string such as a branch, tag, commit hash, or `HEAD`) returning a `Task` or a list of named problems; verify tests cover the spec scenarios "valid accepted", "missing id", "repo missing a ref" and assert no partial data is produced

## 3. Domain: naming and workspace generation

- [x] 3.1 Implement `slug()` that preserves unicode letters (Cyrillic kept, no transliteration), replaces whitespace and `/:\\"\`'` plus other tmux-hostile chars with `-`, collapses repeats, and truncates to ~40 chars; verify tests cover Cyrillic preservation, hostile-char replacement, collapse, and truncation
- [x] 3.2 Implement `group_name(task)` returning `f"{task.id}·{slug(task.description)}"` and `session_name(repo, task)` returning `f"{task.id}·{repo.name}·{slug(task.description)}"`; verify unit tests assert the exact expected strings including the `·` separator
- [x] 3.3 Implement `workspace_yaml(repo, task)` producing an inline tmuxp workspace (session_name, start_directory = repo path, single window `diff` running `nvim +'DiffviewOpen <base>..<ref>'`) as a YAML string; verify tests assert the parsed YAML fields and that no `git checkout`/`git switch` command appears anywhere
- [x] 3.4 Implement `group_yaml(task)` producing the `{name, tags: [<task_id>], sessions: [workspace-yaml...]}` group document YAML with one workspace member per repo; verify a test round-trips it through `yaml.safe_load` and asserts the group name, the task-id tag, and member count

## 4. Infrastructure and app flow

- [x] 4.1 Implement input reading in `infrastructure/input.py` (from `--file PATH` or stdin) returning the raw text; verify tests cover file source, stdin source, and empty-input error
- [x] 4.2 Implement `MultiSessionizerRunner` in `infrastructure/` that invokes `multi-sessionizer external add "<group-yaml>"` as a subprocess and returns stdout/stderr/exit code; verify a test runs it with a fake executable or mocked subprocess and asserts the exact argv
- [x] 4.3 Implement the `add` flow in `app/flows.py` (read input → parse/validate → build group yaml → call runner → map results: success exit 0, validation errors exit 1, msz existing-entry error propagated as exit 1, usage errors exit 2); verify tests cover each exit-code path
- [x] 4.4 Implement the CLI entry point in `main.py` with `--help` documenting the single `add` command, `--file PATH`, and `-` for stdin; verify `uv run tmux-review-queue --help` prints usage and `uv run tmux-review-queue` without args exits 2 with a usage error
- [x] 4.5 Add `infrastructure/messages.py` console output (success line naming the registered group, validation problems, propagated msz errors) and verify tests assert the printed messages
- [x] 4.6 Implement duplicate-hint wrapping: when the msz runner output reports an existing entry, append the guidance "change the `id` or `description` so the group name differs, then retry" and exit 1; verify a test covers a duplicated-name run and asserts the hint text is present

## 5. Integration and documentation

- [x] 5.1 Write `README.md` with install (`uv tool install .`), usage, the AI-facing payload JSON schema (`ref`/`base` accept any git revision), the naming scheme, and the assumption that repos already have the reviewed revision available (Diffview resolves at selection time); verify the documented commands run as written
- [x] 5.2 Verify end-to-end with a real multi-sessionizer install: run `add` with a sample two-repo task using `ref`/`base`, confirm the group appears in `multi-sessionizer external list`, and confirm selecting it in the interactive picker provisions tmux sessions (using a throwaway task id); verify against the spec scenarios
- [x] 5.3 Write `.opencode/skills/register-review-task/SKILL.md` teaching the AI how to register a task: when to use it, the payload schema with `ref`/`base` semantics, the naming rules (group and per-repo session names, Cyrillic slug), duplicate behavior (error → change `id`/`description` and retry), and a worked example; add the install instruction (copy to `~/.config/opencode/skills/`) to README; verify the skill loads and the documented `add` invocation runs as written