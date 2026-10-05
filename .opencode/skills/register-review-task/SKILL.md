---
name: register-review-task
description: Register a review request for completed work across one or more repositories. Use when the user asks to review what was done, to open a review of parallel work, or to queue a code review.
---

Register a review request so the user can review the work in one go. Use this
whenever you finished parallel work across several branches or repositories and
the user wants it reviewed — for example "please review this", "open a review
of the changes", or "queue a review for the work I just landed".

## How to register a review

Compose the request from the work itself (the repositories touched and the
revisions involved), write it to a file (a file is far less likely to be mangled
by shell quoting than inline JSON), and submit it:

```bash
tmux-review-queue add --file /tmp/review-request.json
# or from stdin:
cat /tmp/review-request.json | tmux-review-queue add -
```

### Request schema

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

- `id` — required, non-empty. A stable identifier for the review; use it as the identity of the request.
- `description` — required, non-empty. The human label; a slug of it is embedded in the generated names.
- `repos` — required, non-empty. One entry per repository, each requiring a non-empty `name`, `path`, `ref`, and `base`.
- `ref` is the revision **under review** (what the user is asked to look at); `base` is the comparison base (what it is compared against). Both accept **any git revision string**: a branch, a tag, a commit hash, or `HEAD`.
- `path` must be the absolute path of a local clone of the repository.

The tool does not validate that the revisions exist and never changes any
working tree. Make sure each repository already has the reviewed revision
available; the diff range is resolved when the review is opened.

## Naming rules

- The review request is shown under the name `<id>·<slug(description)>`.
- Each repository inside the request is named `<id>·<repo_name>·<slug(description)>`.

The slug keeps unicode letters — **Cyrillic is preserved, no transliteration** —
replaces whitespace and hostile characters with `-`, collapses repeats, and
truncates to ~40 chars. The separator is the middle dot `·`.

## Exit codes

- `0` — request registered.
- `1` — validation or registration error (including a duplicate name).
- `2` — usage error (no input, bad arguments).

## Duplicate behavior

Submitting the same `id` + `description` again (the generated name already
exists) is an **error**: the command prints the existing-entry message, appends
the hint *"change the `id` or `description` so the name differs, then retry"*,
and exits 1. Existing requests are never replaced or deleted.

To re-register a review (e.g. with an updated diff range), **change the `id` or
the `description`** so the generated name differs, then submit again.

## Worked example

Registering a two-repository review of a backend `feature/x` branch and a
frontend change on `HEAD`:

```bash
cat > /tmp/review-request.json <<'EOF'
{
  "id": "rev-42",
  "description": "Review the parallel work",
  "repos": [
    { "name": "backend", "path": "/home/u/work/backend", "ref": "feature/x", "base": "main" },
    { "name": "frontend", "path": "/home/u/work/frontend", "ref": "HEAD", "base": "main" }
  ]
}
EOF
tmux-review-queue add --file /tmp/review-request.json
```

Expected output:

```
tmux-review-queue: registered review group 'rev-42·Review-the-parallel-work'
```

The user then reviews the work by opening the generated review. If that name
already exists, the command reports the duplicate and tells you to change `id`
or `description` and retry.

## Requirements

- `tmux-review-queue` available on `PATH` (installed globally).