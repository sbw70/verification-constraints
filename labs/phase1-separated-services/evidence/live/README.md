# Live Instance

**Endpoint:** https://lab.xer0trust.com/

A continuously running request path comparison: a conventional gateway→app→database path and a provider-first verification boundary, side by side, receiving identical adversarial traffic. Live telemetry, 1-second refresh.

The claim under test: in the provider-first path, denial happens at the boundary **before any downstream execution** — no database touch, no application activation, prior to rejection.

## Steady-state behavior

Tens of millions of adversarial requests processed to date. Zero valid credentials presented. Zero false authorizations.

| | Conventional | Provider-First |
|---|---|---|
| Requests touching the database before denial | ~100% | **0%** |
| Provider sees the request | ~12 ms | ~5 ms |
| Rejection latency (avg) | ~16 ms | ~13 ms |
| Rejection latency (p99) | ~74 ms | ~58 ms |
| Timeouts | 0 | 0 |

Both paths plus shared services run in roughly 340 MB RAM at around a third of one CPU on a low-cost cloud instance.

Exact live values are on the dashboard.

## What to look at

- **Data exposure.** The conventional path touches the database on every denied request. The provider-first path touches it on none. Same traffic, same denial outcome — the difference is what activates before the "no."
- **Provider visibility timing.** The provider sees the request roughly 2.5x earlier in the provider-first path.
- **Consistency.** These ratios have held across the full run, not a curated window.

Everything running on the instance is in this repository — same services, same request shapes. The test is reproducible from this lab directory.

## Notes

- The dashboard retains compact rolling samples only; full per-request payloads are not retained.
- This is an observability test of request ordering only. 

