"""Canonical serialization and digest helpers.

Byte-identical to the scheme used across the Gradia program (gradia_universes,
Gradia Guard): sorted keys, compact separators, integer-normalized numbers,
NaN/Inf refused. Evidence signed in Python must verify unchanged in the Gradia
Explorer / Guard verifier, so the spelling must not drift across runtimes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def normalize_numbers(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize_numbers(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_numbers(item) for item in value]
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        normalize_numbers(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    """sha256 of the canonical encoding of ``value``."""
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def write_canonical(path: Path, value: Any) -> str:
    """Write ``value`` canonically (newline-terminated); return its digest."""
    data = canonical_bytes(value)
    path.write_bytes(data + b"\n")
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
