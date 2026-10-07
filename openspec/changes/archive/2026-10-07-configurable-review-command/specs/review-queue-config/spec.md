# Spec Delta

## Purpose

Configures the review command template used to build each review workspace, loaded from a required TOML file following multi-sessionizer conventions.

## ADDED Requirements

### Requirement: Required configuration file
The system SHALL load its configuration from `~/.config/tmux-review-queue/config.toml`, with the path overridable via the `TMUX_REVIEW_QUEUE_CONFIG` environment variable. When the file is missing, unreadable, or contains invalid TOML, the system SHALL print an example configuration skeleton to stderr and SHALL NOT register anything.

#### Scenario: Config file missing
- **WHEN** the user runs `add` and no config file exists at the default or environment-overridden path
- **THEN** the command prints an example configuration skeleton and exits with a non-zero status without registering anything

#### Scenario: Config path overridden by environment
- **WHEN** `TMUX_REVIEW_QUEUE_CONFIG` points to a valid config file
- **THEN** the command reads that file instead of the default path

#### Scenario: Config file is invalid TOML
- **WHEN** the config file exists but does not parse as TOML
- **THEN** the command prints the parse error and exits with a non-zero status without registering anything

### Requirement: Review command template validation
The system SHALL require the config to define `[review].command` as a non-empty string containing both the `{base}` and `{ref}` placeholders and no other `{...}` placeholder. A config violating this SHALL be rejected with every problem listed, and the command SHALL exit with a non-zero status without registering anything.

#### Scenario: Missing command
- **WHEN** the config lacks `[review].command` or it is empty
- **THEN** the command prints an error naming the missing key and exits with a non-zero status without registering anything

#### Scenario: Missing placeholder
- **WHEN** the configured command contains only one of the `{base}` or `{ref}` placeholders, or neither
- **THEN** the command prints an error naming the missing placeholder and exits with a non-zero status without registering anything

#### Scenario: Unknown placeholder
- **WHEN** the configured command contains a placeholder other than `{base}` or `{ref}`
- **THEN** the command prints an error naming the unknown placeholder and exits with a non-zero status without registering anything