# MP005 — Provider restart durability

Phase 1 local build only. No provider has run under MP005. S00–S03, live rehearsal and scored campaign are NOT_RUN. The live contract is a draft; no final lock exists.

The planned question is whether already-consumed authority remains spent after a forced idle provider-process restart with the same durable state, while fresh authority remains usable. R01 covers A, R02 covers B. Only the target restarts; relay, recorder and non-target remain running. Source is unchanged MP003. See configs/MP005_CONTRACT.md and notes/MP005_IMPLEMENTATION_INSPECTION.md.

On a later approved LOCAL Linux environment, copy this entire tree preserving file bytes, install requirements.txt and run from its root:

    python3 simulation/run.py --session MP005_SIMULATED_SMOKE_R1

The session directory must be new. This runs separate S00/S01/S02/S03 cases per provider on numeric loopback addresses only, preserving disposable state/evidence. The non-Linux guard refuses before provider import/start; no Windows persistence emulation is supplied. Actual Linux execution has not been validated yet. Stop after simulation for review; it is not MP005 proof or live preflight.

The frozen sources/lab keys are in provider_a/, provider_b/, intermediary/ and association/. MP005-only tools are in harness/ and simulation/. Candidate manifests distinguish them. operator/LIVE_RUNBOOK.md describes future gated manual phases and source checks; it does not authorize execution. notes/ contains source inspection. CHECK_ME preserves earlier issues and their disposition. Do not overwrite old runs or canonical MP003/MP004 state. No final results or publication staging exist.
