"""PostgreSQL adapter boundary.

The Paper 1 local runtime uses JSONL by default. This module marks the future
PostgreSQL storage interface without pretending a production schema migration
has been completed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PostgresConfig:
    dsn: str


class PostgresStoreUnavailable(RuntimeError):
    pass


class PostgresEventStore:
    def __init__(self, config: PostgresConfig) -> None:
        self.config = config

    def append(self, event: dict) -> None:
        raise PostgresStoreUnavailable("PostgreSQL persistence is a deployment adapter; JSONLEventStore is active.")
