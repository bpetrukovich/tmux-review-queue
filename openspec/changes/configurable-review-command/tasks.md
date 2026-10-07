# Tasks

## 1. Domain: review command rules

- [x] 1.1 Implement `validate_command(template) -> list[str]` in new `domain/review_command.py` (pure, regex over `{...}`; requires both `{base}` and `{ref}`, flags unknown placeholders); verify `tests/test_review_command.py` covers missing base, missing ref, both missing, unknown placeholder, and a valid template
- [x] 1.2 Implement `render_command(template, repo) -> str` with single-pass `re.sub(r"\{base\}|\{ref\}", ...)`; verify tests cover per-repo substitution and no double-substitution when a value contains the other placeholder's text
- [x] 1.3 Change `workspace_yaml(repo, task, command)` and `group_yaml(task, command)` to render the configured command per repo; verify updated `tests/test_workspaces.py` passes with configured-command assertions and no hardcoded `DiffviewOpen`/`CodeDiff` string remains in tests

## 2. App layer plumbing

- [x] 2.1 Add `ReviewConfig(command: str)` plus `ConfigError` (carries a problem list) and `ConfigNotFoundError` in new `app/configuration.py`; verify `tests/test_configuration.py` covers field access and problem-list formatting
- [x] 2.2 Extend `FlowDeps` with `config: ReviewConfig` in `app/ports.py` and make `add_flow` pass `deps.config.command` into `group_yaml`; verify updated `tests/test_flows.py` (fakes now supply a config) passes

## 3. Infrastructure: config file loading

- [x] 3.1 Implement `load_config(path=None) -> ReviewConfig` in new `infrastructure/config_loader.py` (tomllib; `TMUX_REVIEW_QUEUE_CONFIG` env override of `~/.config/tmux-review-queue/config.toml`; missing file → `ConfigNotFoundError`, invalid TOML → `ConfigError`, then domain `validate_command`); verify `tests/test_config_loader.py` covers default path, env override, missing file, invalid TOML, each validation failure, and a valid file
- [x] 3.2 Add `CONFIG_EXAMPLE` skeleton (with a `[review].command` containing both placeholders) to `infrastructure/messages.py`; verify it passes `validate_command` in `tests/test_messages.py`
- [x] 3.3 Wire config loading into `main.py` `_add_dispatch`/`default_deps`: missing config → skeleton + exit 1, config error → problems + exit 1, `--help` works without a config; verify updated `tests/test_main.py` covers all three
- [ ] 3.4 Document the config file, env override, and placeholder rules in README.md; verify the documented example passes `validate_command`

## 4. Integration verification

- [ ] 4.1 Run `.venv/bin/python -m pytest -q`, `.venv/bin/ruff check .`, and `.venv/bin/ruff format . --check`; verify the whole suite and linters are green