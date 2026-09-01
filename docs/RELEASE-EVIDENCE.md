# Release evidence — v1.0.0

Published record: [10.5281/zenodo.22233638](https://doi.org/10.5281/zenodo.22233638)

This file distinguishes what a clean checkout can recompute from what remains a
claim boundary.

## Required release gates

```bash
python -m pip install -e '.[dev]'
make test
python -m pytest -q
make lint typecheck
make verify-release
```

At release, the expected outcomes are:

- 165 property/control checks pass.
- 6 pytest contracts pass.
- Ruff and Mypy pass on the released source boundary.
- Every committed directory containing both `frames.ndjson` and `manifest.json`
  replays successfully; the v1.0.0 release contains 26 such Proof Packs.
- The live SWE-bench Verified merged bundle contains 1,800 grader-level frames
  across 100 control-clean instances, with 89 oracle-witnessed exploits.

CI repeats these gates on Python 3.11, 3.12, and 3.13.

## Historical manifest normalization

Two pre-release manifests represented their receipt-derived cost total one ten-thousandth
away from the released verifier because their floating-point accumulation was rounded by
a different path. Their raw `frames.ndjson` bytes and `frames_chain_head` values were not
changed. `scripts/normalize_release_manifests.py` is allowlisted to the two prior manifest
digests, changes only `totals.total_cost_usd`, records old/new values and the prior digest
inside each manifest, recomputes the manifest self-digest, and refuses any broader change.

This is a derivative-aggregate normalization, not a rewritten outcome.

## Claim boundary

These gates establish deterministic instrument behavior, evidence integrity, and
recomputability of the committed aggregates. They do not establish model-training lift,
universal benchmark quality, or causal claims outside the frozen cells named in the paper.
