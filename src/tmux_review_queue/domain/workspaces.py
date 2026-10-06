"""Pure review-workspace generation.

Builds the inline tmuxp workspace document for one repository and the
multi-sessionizer group document for a whole task. The generated command is
``nvim +'DiffviewOpen <base>..<ref>'`` — no git checkout or branch switching is
ever issued. Purely functional (PyYAML is the only non-stdlib facility).
"""

from __future__ import annotations

import yaml

from .models import Repo, Task
from .naming import group_name, session_name


def workspace_yaml(repo: Repo, task: Task) -> str:
    """Inline tmuxp workspace for a single repository, as a YAML string."""
    workspace = {
        "session_name": session_name(repo, task),
        "start_directory": repo.path,
        "windows": [
            {
                "window_name": "diff",
                "panes": [
                    {"shell_command": f"nvim +'DiffviewOpen {repo.base}..{repo.ref}'"}
                ],
            }
        ],
    }
    return yaml.safe_dump(workspace, sort_keys=False, allow_unicode=True, width=1000)


def group_yaml(task: Task) -> str:
    """Group document ``{name, tags, sessions: [workspace-yaml...]}`` as YAML.

    The ``sessions`` list holds one inline tmuxp workspace per repository, which
    is how multi-sessionizer stores named group members. ``tags`` carries the
    task id so the picker renders it as ``[external] [<id>] <name>``.
    """
    group = {
        "name": group_name(task),
        "tags": [task.id],
        "sessions": [workspace_yaml(repo, task) for repo in task.repos],
    }
    return yaml.safe_dump(group, sort_keys=False, allow_unicode=True, width=1000)
