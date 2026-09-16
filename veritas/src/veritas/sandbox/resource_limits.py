"""Sandbox resource limit configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceLimits:
    timeout_seconds: float = 10.0
    max_output_bytes: int = 200_000
    network: str = "deny"
