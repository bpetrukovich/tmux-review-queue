# Spec Delta

## Purpose

Accepts an AI-reported review task (id, description, list of repositories with git revisions) and registers it as a named group of review workspaces in multi-sessionizer, so its interactive picker can launch one tmux session per repository with a diff view open.

## ADDED Requirements

### Requirement: Task intake via CLI
The system SHALL accept a review task as a JSON document through the `add` command, reading the document either from a file path (`--file PATH`) or from stdin. Invoking the command without any input SHALL fail with a usage error and register nothing.

#### Scenario: Add a task from a file
- **WHEN** the user runs `tmux-review-queue add --file task.json` with a valid task document
- **THEN** the task is validated and registered, and the command exits with status 0

#### Scenario: Add a task from stdin
- **WHEN** the user pipes a valid task document into `tmux-review-queue add -`
- **THEN** the task is validated and registered, and the command exits with status 0

#### Scenario: Missing input
- **WHEN** the user runs `tmux-review-queue add` without a file argument and stdin is empty
- **THEN** the command prints a usage error, exits with a non-zero status, and registers nothing

### Requirement: Task payload validation
The system SHALL validate the task document before registering anything. A task SHALL have a non-empty `id`, a non-empty `description`, and a non-empty `repos` array; each repo SHALL have a non-empty `name`, `path`, `ref`, and `base`. The `ref` and `base` fields SHALL accept any git revision string (branch name, tag, commit hash, or `HEAD`). An invalid document SHALL be rejected with an error message naming the problem and SHALL NOT register any partial data.

#### Scenario: Valid task accepted
- **WHEN** the document contains `id`, `description`, and at least one fully-populated repo
- **THEN** the task is accepted and registered

#### Scenario: Missing id
- **WHEN** the document has an empty or absent `id`
- **THEN** the command rejects it with an error naming the missing `id`, exits non-zero, and registers nothing

#### Scenario: Repo missing a ref
- **WHEN** a repo entry lacks `ref` or `base`
- **THEN** the command rejects the document with an error naming the incomplete repo, exits non-zero, and registers nothing

### Requirement: Registration as a multi-sessionizer group
The system SHALL register each accepted task with multi-sessionizer as a named external group whose name is `<task_id>·<slug(description)>` and whose members are one inline tmuxp workspace per repository. The system SHALL call multi-sessionizer's public CLI as a black box and SHALL NOT modify its code, config, or data store directly.

#### Scenario: Task registered as a named group
- **WHEN** a valid task is added
- **THEN** multi-sessionizer's external store contains a group named `<task_id>·<slug(description)>` with one workspace member per repo

#### Scenario: Group appears in the picker
- **WHEN** the user later opens multi-sessionizer's interactive picker
- **THEN** the registered task is listed under `[group] <task_id>·<slug(description)>` and selecting it provisions the review sessions

### Requirement: Review workspace generation
The system SHALL generate one inline tmuxp workspace per repository with `start_directory` set to the repository path, a single window named `diff` running `nvim +'DiffviewOpen <base>..<ref>'`, and a `session_name` that includes the task id, the repository name, and a slug of the description. The system SHALL NOT run any git checkout or branch-switching command.

#### Scenario: Workspace generated per repository
- **WHEN** a task contains two repositories
- **THEN** the registered group contains two workspace members, each targeting its own repository path and diff range

#### Scenario: No branch switching
- **WHEN** a task is registered
- **THEN** no git checkout or switch command is issued for any repository

### Requirement: Duplicate task handling
When a task's group name already exists in the multi-sessionizer external store, the system SHALL report multi-sessionizer's existing-entry error together with guidance to change the `id` or `description` so the group name differs and then retry, and SHALL exit with a non-zero status without crashing or corrupting existing entries.

#### Scenario: Re-adding the same task
- **WHEN** the user adds a task whose group name already exists
- **THEN** the command prints the existing-entry error and a hint to change `id` or `description` and retry, exits non-zero, and existing entries are unchanged

### Requirement: No interactive picker in the tool
The system SHALL NOT implement an interactive selector (fzf) or a session-launching command. Session selection and provisioning SHALL be delegated entirely to multi-sessionizer's interactive mode.

#### Scenario: Tool has a single command
- **WHEN** the user inspects the tool's usage
- **THEN** the only available command is `add`; there is no picker, no review-launch, and no list/delete command