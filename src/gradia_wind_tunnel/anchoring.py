"""Public anchoring: timestamped, non-equivocating evidence.

A hash chain the AUTHORS control is tamper-evident but cannot prove two things a
skeptical third party eventually asks for: that the chain shown is the ORIGINAL one
(not a wholesale regeneration), and that a commitment -- above all the preregistration
SHA and the hidden-vault hash -- existed BEFORE the results did. Both reduce to
existence-at-time and non-equivocation, and both are closed by anchoring a digest in
public infrastructure the authors do not control (Haber & Stornetta 1991; the same
mechanism Certificate Transparency uses for the web PKI and Sigstore/Rekor for the
software supply chain).

Mechanism here: build one canonical ANCHOR MANIFEST listing the preregistration SHA and
the sha256 of every key evidence artifact, then stamp that single file with
OpenTimestamps (`ots stamp` -> a .ots proof committing the digest to public calendar
servers, later upgraded to a Bitcoin block inclusion via `ots upgrade`). One stamp
covers every listed artifact by inclusion. Verification needs nothing from us:
recompute the listed sha256s, then `ots verify` the manifest against public
infrastructure.

Honesty rules, same as everywhere in this instrument: anchoring is best-effort and the
receipt states plainly whether a stamp happened; a missing `ots` binary or refused
network yields stamped=false with the reason -- never a fabricated proof. Anchoring
proves WHEN evidence existed, never that it is correct; correctness is what
verify_bundle and the oracle witness are for.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import write_canonical

ANCHOR_SCHEMA = "gradia-wind-tunnel-anchor.v1"

#: artifacts anchored when present (relative to the results dir's parent, i.e. repo root)
DEFAULT_ARTIFACTS = (
    "results/research-v1/research_report.json",
    "results/research-v1/index/index.json",
    "results/swe-merged/manifest.json",
)


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_attestations(root: str | Path = ".", extra: list[str] | None = None) -> list[dict]:
    """sha256 every present artifact from DEFAULT_ARTIFACTS + extras. Absent files are
    listed as absent rather than silently skipped -- the manifest says what it covers."""
    root = Path(root)
    out: list[dict] = []
    for rel in list(DEFAULT_ARTIFACTS) + list(extra or []):
        p = root / rel
        if p.exists():
            out.append({"path": rel, "sha256": sha256_file(p)})
        else:
            out.append({"path": rel, "absent": True})
    return out


def build_anchor_manifest(root: str | Path = ".", *, extra: list[str] | None = None,
                          created_utc: str | None = None) -> dict[str, Any]:
    return {
        "schema": ANCHOR_SCHEMA,
        "created_utc": created_utc or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "preregistration_sha256": os.environ.get("GRADIA_WT_PREREG_SHA256") or None,
        "artifacts": collect_attestations(root, extra),
        "claims": ("Anchoring this manifest proves the listed digests -- including the "
                   "preregistration SHA -- existed at or before the anchored time, and makes "
                   "equivocation (showing different histories to different parties) detectable. "
                   "It does NOT assert the artifacts are correct; recompute them with "
                   "verify_bundle / run_research.sh."),
    }


def _run(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # missing binary, timeout, ...
        return 127, f"{type(e).__name__}: {e}"


def stamp_file(path: str | Path, *, ots_bin: str | None = None) -> dict[str, Any]:
    """OpenTimestamps-stamp one file (best-effort, honest). Returns a receipt fragment."""
    ots = ots_bin or shutil.which("ots")
    p = Path(path)
    if not ots:
        return {"stamped": False, "reason": "ots (opentimestamps-client) not installed",
                "hint": "pip install opentimestamps-client"}
    proof = p.with_suffix(p.suffix + ".ots")
    if proof.exists():                       # already stamped: try to upgrade instead
        rc, out = _run([ots, "upgrade", str(proof)])
        return {"stamped": True, "ots_path": str(proof), "upgrade_attempted": True,
                "upgraded": rc == 0, "detail": out.strip()[-300:]}
    rc, out = _run([ots, "stamp", str(p)])
    if rc == 0 and proof.exists():
        return {"stamped": True, "ots_path": str(proof),
                "note": ("calendar attestation; run `ots upgrade` after ~a few hours to "
                         "attach the Bitcoin block inclusion proof"),
                "detail": out.strip()[-300:]}
    return {"stamped": False, "reason": f"ots stamp failed (rc={rc})", "detail": out.strip()[-300:]}


def verify_attestations(manifest: dict, root: str | Path = ".") -> dict[str, Any]:
    """Recompute every listed digest. (The .ots proof itself is verified with
    `ots verify`, against public infrastructure -- not by us.)"""
    root = Path(root)
    mismatches, missing, ok = [], [], 0
    for a in manifest.get("artifacts", []):
        if a.get("absent"):
            continue
        p = root / a["path"]
        if not p.exists():
            missing.append(a["path"]); continue
        if sha256_file(p) == a["sha256"]:
            ok += 1
        else:
            mismatches.append(a["path"])
    return {"ok": not mismatches and not missing, "matched": ok,
            "mismatched": mismatches, "missing": missing}


def anchor(root: str | Path = ".", *, out_dir: str = "results/anchors",
           extra: list[str] | None = None, ots_bin: str | None = None,
           created_utc: str | None = None) -> dict[str, Any]:
    """Build + write the anchor manifest, stamp it, upgrade any earlier proofs.
    Returns the full receipt (also written next to the manifest)."""
    root = Path(root)
    out = root / out_dir
    out.mkdir(parents=True, exist_ok=True)
    manifest = build_anchor_manifest(root, extra=extra, created_utc=created_utc)
    stamp_name = "anchor-" + manifest["created_utc"].replace(":", "").replace("-", "")
    mpath = out / f"{stamp_name}.json"
    write_canonical(mpath, manifest)
    receipt: dict[str, Any] = {
        "schema": ANCHOR_SCHEMA + ".receipt",
        "manifest_path": str(mpath.relative_to(root)),
        "manifest_sha256": sha256_file(mpath),
        "stamp": stamp_file(mpath, ots_bin=ots_bin),
        "upgrades": [],
    }
    ots = ots_bin or shutil.which("ots")
    if ots:                                   # upgrade every earlier proof, best-effort
        for old in sorted(out.glob("*.ots")):
            if old.name == mpath.name + ".ots":
                continue
            rc, _ = _run([ots, "upgrade", str(old)])
            receipt["upgrades"].append({"proof": old.name, "upgraded": rc == 0})
    write_canonical(out / f"{stamp_name}.receipt.json", receipt)
    return receipt
