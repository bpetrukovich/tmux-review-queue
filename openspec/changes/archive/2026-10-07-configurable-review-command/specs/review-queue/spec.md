# Spec Delta

## MODIFIED Requirements

### Requirement: Review workspace generation
The system SHALL generate one inline tmuxp workspace per repository with `start_directory` set to the repository path, a single window named `diff` running the review command configured in the required config file, with the repository's `base` and `ref` substituted into the `{base}` and `{ref}` placeholders, and a `session_name` that includes the task id, the repository name, and a slug of the description. The system SHALL NOT run any git checkout or branch-switching command.

#### Scenario: Workspace generated per repository
- **WHEN** a task contains two repositories
- **THEN** the registered group contains two workspace members, each targeting its own repository path and diff range

#### Scenario: Configured command per repository
- **WHEN** the configured command is `git diff {base} {ref}` and a repository has `base` `main` and `ref` `feature/x`
- **THEN** the generated workspace runs `git diff main feature/x` in that repository

#### Scenario: No branch switching
- **WHEN** a task is registered
- **THEN** no git checkout or switch command is issued for any repository