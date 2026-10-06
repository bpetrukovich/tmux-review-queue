# tmux-review-queue

Register AI-reported review tasks as named groups of review workspaces in
[multi-sessionizer](https://github.com/xxx/multi-sessionizer) — one tmux
session per repository with a diff view open, launched by multi-sessionizer's
interactive picker.

When an AI agent finishes parallel work across several branches, `add` turns a
small JSON document (task id + description + per-repo git revisions) into a
ready-to-review tmux setup in a single step. The tool is a thin intake CLI
only: it never runs tmux, tmuxp, nvim, or git itself, and it calls
multi-sessionizer strictly as a black box.

## Install

Requires Python ≥ 3.12, [uv](https://docs.astral.sh/uv/), and the
`multi-sessionizer` CLI on `PATH`.

```bash
uv tool install .
```

At runtime the tool shells out to `multi-sessionizer external add`; the
provisioned sessions need `tmux`, `tmuxp`, and `nvim` with the
[Diffview](https://github.com/sindrets/diffview.nvim) plugin.

## Usage

```bash
tmux-review-queue add --file task.json
cat task.json | tmux-review-queue add -
```

`add` reads a single JSON task document from `--file PATH` or, with `-`, from
stdin. The document is validated before anything is registered — an invalid
document registers nothing and exits 1. Invoking the command without any input
is a usage error (exit 2).

### Payload schema (AI-facing)

```json
{
  "id": "rev-1",
  "description": "Review the parallel work",
  "repos": [
    { "name": "backend", "path": "/home/u/work/backend", "ref": "feature/x", "base": "main" },
    { "name": "frontend", "path": "/home/u/work/frontend", "ref": "HEAD", "base": "release/1.0" }
  ]
}
```

- `id` (required, non-empty): stable task identifier.
- `description` (required, non-empty): human label; a slug of it appears in the
  group and session names.
- `repos` (required, non-empty): one or more repositories. Each repo requires a
  non-empty `name`, `path`, `ref`, and `base`.
- `ref` is the revision under review (right side of the diff); `base` is the
  comparison base (left side). Both accept **any git revision string** — a
  branch, a tag, a commit hash, or `HEAD`. The tool does not validate that the
  revisions exist and never checks anything out: Diffview resolves the range at
  selection time. The repo is assumed to already have the reviewed revision
  available (e.g. it is checked out on the review branch).

### Naming scheme

- **Group name** (shown in the picker): `<id>·<slug(description)>`.
- **Per-repo tmux session name**: `<id>·<repo_name>·<slug(description)>`.

The slug keeps unicode letters (Cyrillic is preserved, no transliteration),
replaces whitespace and tmux-hostile characters with `-`, collapses repeats,
and truncates to ~40 chars. The `·` separator keeps the label readable.

### What happens

Each repo becomes one inline tmuxp workspace: a single `diff` window running
`nvim +'DiffviewOpen <base>..<ref>'` with `start_directory` set to the repo
path. The workspaces are registered with multi-sessionizer as a named group;
multi-sessionizer's interactive picker then lists it as
`[external] [<id>] <name>` (the task id as a picker tag) and, when selected,
provisions the tmux sessions. No git
checkout or branch-switching command is ever issued.

### Duplicate group names

If the group name already exists in multi-sessionizer's external store, the
command prints multi-sessionizer's error plus a hint to change the `id` or
`description` so the group name differs, and exits 1. Existing entries are
left unchanged.

### Exit codes

- `0` — task registered.
- `1` — validation or registration error (including a duplicate group name).
- `2` — usage error (no input, bad arguments).

## The AI skill

The opencode skill that teaches an agent how to register review requests lives in
[`.opencode/skills/register-review-task/`](.opencode/skills/register-review-task/SKILL.md).

To install it for every agent, copy it to the user-level skills directory:

```bash
cp -r .opencode/skills/register-review-task ~/.config/opencode/skills/
```

## Development

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format . --check
```