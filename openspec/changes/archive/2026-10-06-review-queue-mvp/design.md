# Design

## Context

`tmux-review-queue` is a sibling of `multi-sessionizer` in this repo. multi-sessionizer is Python 3.12 / uv / PyYAML with a layered layout: pure `domain/`, `app/` flows, and `infrastructure/` (subprocess, config, sqlite). Its public CLI exposes `multi-sessionizer external add <yaml-string>`, which accepts a **named group** (`name` + `tags` + `sessions`) whose members are inline tmuxp workspaces; such groups surface in its interactive fzf as `[external] [<task-id>] <name>` and are provisioned via tmuxp when selected. See proposal.md for the motivation.

## Goals / Non-Goals

**Goals:**
- A thin, AI-friendly intake CLI that turns a task document into a registered multi-sessionizer group.
- Reuse multi-sessionizer's picker and provisioning entirely — zero fzf, zero tmux logic in this project.
- Zero changes to multi-sessionizer; it is invoked only through its public CLI.
- Mirror multi-sessionizer's stack and layer boundaries for testability.
- Ship an opencode skill teaching the AI how to register tasks (payload, naming, duplicate behavior).

**Non-Goals:**
- Own queue store or `tasks.json`; task status/update/delete; own fzf or launch command.
- MCP server (natural follow-up adapter over the same intake core).
- Configurable tmuxp review template (hardcoded in MVP).
- Git branch switching, worktree management, or any tmux/tmuxp execution here.

## Decisions

### 1. No own queue store — multi-sessionizer external store is the queue
The tool only registers groups; the "queue" and the "select" step both live in multi-sessionizer (its external store + its interactive picker).
*Alternative considered:* `tasks.json` as source of truth plus an own fzf. Rejected — duplicates multi-sessionizer's picker, adds state that must be kept in sync, and contradicts "fzf is multi-sessionizer's responsibility".

### 2. Invoke multi-sessionizer via its public CLI as a black box
The infrastructure adapter runs `multi-sessionizer external add "<group-yaml>"` and surfaces stdout/stderr and exit code.
*Alternative considered:* writing directly to multi-sessionizer's sqlite external store. Rejected — couples to internals and violates the "don't touch multi-sessionizer" constraint.

### 3. Naming
- **Group name** (what the human sees in fzf): `<task_id>·<slug(description)>`. The task id is the stable, predictable prefix (repeat-handling identity); the slug is the human label, which gives `description` its purpose.
- **Per-repo tmux session names**: `<task_id>·<repo_name>·<slug(description)>` — description stays visible in `tmux list-sessions`; the repo name keeps sessions unique within a task, so tmuxp never collides on two workspaces declaring the same name.
- **Slug**: keeps unicode letters (Cyrillic preserved — no transliteration), replaces whitespace and shell/tmux-hostile characters with `-`, collapses repeats, truncates to ~40 chars.

### 4. Intake input format
`add --file PATH` or `add -` (stdin). JSON is read from a file or stdin, never from argv — the AI is far less likely to mangle a document it writes to a file than JSON embedded in a shell command.

### 5. Layer boundaries mirror multi-sessionizer
- `domain/` (pure): task document parsing and validation, slug generation, tmuxp workspace building, group YAML building.
- `app/`: the single `add` flow wiring domain + adapters.
- `infrastructure/`: reading input (file/stdin), running the `multi-sessionizer` subprocess (injected runner, mocked in tests), console output.
- Because we never run tmux ourselves, tests fake the multi-sessionizer subprocess instead of needing a tmux sandbox.

### 6. Exit-code convention
`0` success, `1` validation/registration error, `2` usage error — matching multi-sessionizer's convention.

### 7. `ref` / `base` accept any git revision
The payload's `ref` is the revision under review (right side of the diff) and `base` is the left side; both accept any git-rev-parse-able string — branch, tag, commit hash, or `HEAD`. The tool does not validate their existence and does not check out anything: Diffview resolves them at selection time. The generated command is `nvim +'DiffviewOpen <base>..<ref>'`.

### 8. Duplicate handling — error with an AI-friendly hint
The tool never pre-reads multi-sessionizer's store (it stays a black box). When multi-sessionizer reports an existing entry (`UNIQUE(name)` in its external store), the adapter detects that message and wraps it with guidance: change `id` or `description` so the group name differs, then retry. Exit code 1. Multi-sessionizer never replaces or deletes on duplicate — rejection is its own behavior.

## Risks / Trade-offs

- **Dependence on multi-sessionizer CLI contract** → isolated in the infrastructure adapter; if the CLI changes, only that adapter is affected.
- **Duplicate group names rejected by multi-sessionizer** (`UNIQUE(name)`) → reported as an error with an AI-facing hint to change `id`/`description`; an update/delete flow is a post-MVP follow-up.
- **Repo not on the review branch** → Diffview fails at open time, since we never check out by design. Documented in `--help`; responsibility of the agent that registered the task.
- **Slug truncation could theoretically collide across tasks** → task ids are assumed unique (agent responsibility); exact duplicates are surfaced by multi-sessionizer anyway.
- **Long/unicode names in tmux** → `·` and Cyrillic are safe in YAML/tmux names; truncation keeps them sane.

## Migration Plan

New standalone project — nothing to migrate. multi-sessionizer, tmux, tmuxp, nvim, and Diffview must be present at runtime; the tool reports a clear error if the `multi-sessionizer` CLI cannot be executed. The AI-usage skill ships in `.opencode/skills/`; README documents copying it to `~/.config/opencode/skills/` so any agent can load it.

## Open Questions

- None.