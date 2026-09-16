"""Dataset snapshot hashing."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DatasetSnapshot:
    snapshot_id: str
    record_count: int
    digest: str


def freeze_records(records: Iterable[dict], *, prefix: str = "snapshot") -> DatasetSnapshot:
    payloads = [json.dumps(record, sort_keys=True, separators=(",", ":")) for record in records]
    digest = hashlib.sha256()
    for payload in payloads:
        digest.update(payload.encode("utf-8"))
        digest.update(b"\n")
    hex_digest = digest.hexdigest()
    return DatasetSnapshot(snapshot_id=f"{prefix}_{hex_digest[:12]}", record_count=len(payloads), digest="sha256:" + hex_digest)
