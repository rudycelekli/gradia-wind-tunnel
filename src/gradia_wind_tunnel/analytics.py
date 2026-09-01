"""Analytics sink — stream the evidence frames into a warehouse or Gradia analytics.

`frames.ndjson` is already one row per attack; this module streams those rows to
a sink so exploit density, cost, and slice trends are queryable as the study runs.
`LocalJsonlSink` is offline (a file/warehouse landing zone). `GradiaAnalyticsSink`
posts batches to Gradia's analytics ingestion (dependency-free; transport seam so
it is testable without network). Streaming is additive: the canonical frames stay
the authoritative, self-verifying record; analytics is a downstream view.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class AnalyticsSink(Protocol):
    name: str
    def emit(self, rows: list[dict[str, Any]]) -> int: ...


@dataclass
class LocalJsonlSink:
    """Append rows to a local JSONL landing zone (a warehouse stage)."""
    path: Path
    name: str = "local_jsonl"
    written: int = 0

    def emit(self, rows: list[dict[str, Any]]) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + "\n")
        self.written += len(rows)
        return len(rows)


class GradiaAnalyticsSink:
    """POST batches to Gradia analytics ingestion (stub; transport-testable).

    Reads the ingestion token from the environment; routes through the Gradia
    analytics endpoint. Never carries provider keys or raw content — frames are
    digest-only rows.
    """

    name = "gradia_analytics"

    def __init__(self, base_url: str, token_env: str = "GRADIA_ANALYTICS_TOKEN",
                 dataset: str = "wind_tunnel_frames", transport=None) -> None:
        self.base_url = base_url.rstrip("/")
        self.dataset = dataset
        self.token = os.environ.get(token_env)
        self._transport = transport or self._urllib_transport
        self.written = 0

    def _urllib_transport(self, url: str, headers: dict, body: dict) -> dict:  # pragma: no cover
        import urllib.request
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def emit(self, rows: list[dict[str, Any]]) -> int:
        if not self.token:
            raise RuntimeError("GRADIA_ANALYTICS_TOKEN unset; cannot post to Gradia analytics.")
        url = f"{self.base_url}/analytics/ingest"
        headers = {"content-type": "application/json", "authorization": f"Bearer {self.token}"}
        self._transport(url, headers, {"dataset": self.dataset, "rows": rows})
        self.written += len(rows)
        return len(rows)


def stream_frames(frames_path: Path, sink: AnalyticsSink, batch: int = 200) -> int:
    """Read frames.ndjson and emit rows to the sink in batches; return count."""
    rows: list[dict[str, Any]] = []
    total = 0
    for line in Path(frames_path).read_text().splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
        if len(rows) >= batch:
            total += sink.emit(rows)
            rows = []
    if rows:
        total += sink.emit(rows)
    return total
