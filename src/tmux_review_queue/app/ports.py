"""App ports: the adapter contracts the ``add`` flow depends on."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .configuration import ReviewConfig


@dataclass(frozen=True)
class MszResult:
    """Outcome of invoking multi-sessionizer as a black-box subprocess."""

    stdout: str
    stderr: str
    exit_code: int


class MszRunner(Protocol):
    def run(self, group_yaml: str) -> MszResult: ...


class MessageOutput(Protocol):
    def error(self, msg: str) -> None: ...

    def registered(self, group_name: str) -> None: ...


@dataclass(frozen=True)
class FlowDeps:
    runner: MszRunner
    messages: MessageOutput
    config: ReviewConfig
