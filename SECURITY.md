# Security & responsible-use policy

## Provider credentials
This project never stores provider API keys in the repository. Real-model runs
read keys from the environment only, and every model call is routed through
Gradia Guard so it becomes a hash-chained receipt. Never place a key in an
actor identifier, a preregistration, a CLI argument, a run log, or an issue.

## Responsible disclosure of benchmark exploits
This is a defensive tool. When it finds that a **named public benchmark's
scoring pipeline** can be gamed, we disclose responsibly before publishing:

1. Privately notify the benchmark's maintainers with oracle-witnessed examples,
   the causal-slice finding, and a **suggested patch**.
2. Offer a reasonable embargo window (default 45 days).
3. Report maintainer responses in the paper; credit them if they wish.
4. Release the *repair loop and hidden-suite protocol* prominently — not a
   turnkey "fool any benchmark" script. The naturalness constraint limits
   surfaced failures to plausible ones, not injection payloads.

## What we never publish
Live credentials, raw provider traces, real personal or clinical records
(universe clinical items are synthetic), or a hidden regression suite before its
committed reveal.

## Reporting a vulnerability in this tool
Use the private "Report a vulnerability" flow on the GitHub repository. Do not
open a public issue for a credential or data-exposure report.
