"""Docker sandbox adapter boundary for Paper 1 infrastructure work."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DockerSandboxConfig:
    image: str
    network: str = "none"
    cpu_quota: float | None = None
    memory: str | None = None


class DockerSandboxUnavailable(RuntimeError):
    pass


class DockerSandbox:
    def __init__(self, config: DockerSandboxConfig) -> None:
        self.config = config

    def start(self) -> None:
        raise DockerSandboxUnavailable(
            "Docker execution is a deployment adapter; use LocalWorkspaceSandbox for local tests or implement the Docker runner."
        )
