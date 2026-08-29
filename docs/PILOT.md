# Wind Tunnel — pilot harness

A self-contained, **offline, zero-API-key** proof that the core loop of the
Reward-Hacking Wind Tunnel works. Pure Python stdlib. Nothing here touches a
network.

```bash
python -m pilot.demo      # end-to-end demonstration (findings below)
python -m pilot.tests     # 16 property tests, all green
python -m pilot.verify pilot/sample_run.json   # recompute density + chain head
```

## What it demonstrates

On procedurally generated GSM8K-style math with an **exact numeric oracle**
(so truth needs no human):

1. **L1 exploit finding.** A reference-free `KeywordGamingJudge` — which
   reproduces the documented "scores plausibility, not correctness" failure
   mode — is gamed by a `keyword_inflation` attack: a **wrong** answer dressed
   in judge-favored phrasing scores PASS while the oracle says WRONG. Every
   exploit is `judge=PASS ∧ oracle=WRONG`, confirmed automatically.
2. **Controls.** `final_answer_corruption` and `authoritative_wrong` (wrong, but
   no favored phrasing) do **not** exploit the judge — isolating *what* is being
   gamed.
3. **Causal slice.** The factorial screen recovers the interaction
   *keyword_inflation ∧ steps≥3* (steps=2 → 0/1000; steps≥3 → 1000/1000),
   a true factorial cell because the factor was generated exactly.
4. **Whack-a-mole (H2).** Blacklisting the exploited phrase closes that family
   (→ 0) but the adversary relocates to another favored phrase (→ 666/1000):
   the patch is specific, not general.
5. **Autoimmunity (H3).** The same patch now wrongly rejects **correct** answers
   that used the phrase (0% → 100% false-rejection on steps≥3): hardening the
   scorer attacks healthy tissue.
6. **Self-commitment (H4).** A judge that commits to its own answer first
   collapses reference-free gaming to zero — structural defense helps.
7. **Reproducibility.** A deterministic run-log chain head; `verify` recomputes
   it and detects tamper (exit 1 on drift).

## Going to Phase 0 (real numbers, your budget)

Swap `KeywordGamingJudge` for `RealModelJudge` in `judges.py`: wire your
provider SDK into `.score(...)`, keep the `Verdict` shape, and route every judge
call through Gradia Guard so each is a hash-chained receipt. Point `items.py` at
a real named benchmark's items + oracle. The loop, slice screen, metrics, and
verifier are unchanged.

## Honesty note

The `KeywordGamingJudge` is an illustrative mock that *reproduces* a documented
failure mode so the pipeline runs offline; the numbers above are a
demonstration of the machinery, **not** an empirical finding about any real
model. Real findings come from Phase 0 with `RealModelJudge`.

## Files

| file | role |
|------|------|
| `items.py` | procedural item generator + exact oracle + declared factors |
| `transforms.py` | typed wrong-by-construction transforms + oracle-checked witnesses |
| `judges.py` | `Judge` interface, `KeywordGamingJudge` (mock), `SelfCommitmentJudge`, `RealModelJudge` (stub) |
| `windtunnel.py` | attack loop, exploit density, slice screen, autoimmunity, chain head |
| `verify.py` | recompute density + chain head from a run log; detect tamper |
| `demo.py` | the end-to-end narrated run |
| `tests.py` | 16 property tests |
