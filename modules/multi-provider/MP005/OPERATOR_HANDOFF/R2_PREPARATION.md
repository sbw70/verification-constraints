# Historical R2 preparation — R2 is now completed and reviewed

Do not repeat these preparation steps or overwrite existing evidence. See simulation_review/R2_SUMMARY.json for actual independently reviewed results and the snapshot-semantics blocker. The prior instructions below are retained as historical preparation only.

# Next permitted execution: LOCAL Linux R2 only

R2 is NOT_RUN. No SSH from this preparation task is needed or performed. Pavilion is xer0trust-4, local simulation-only. Its reported Linux Mint 22.3 / Python 3.12.3 / ext4 / existing cryptography 50.0.2 satisfy the candidate requirements if confirmed on the machine.

Transfer the CURRENT v2 portable ZIP to the Pavilion with the operator's established password-based method. Extract into a NEW directory, leaving /home/seth/MULTI_PROVIDER_005 and its R1 tree unchanged. Do not overlay an earlier candidate. Do not reuse an R2 evidence directory. Archive digest and verified file list accompany the ZIP. Its top folder is MP005_HARDENED_R2_OPERATOR_PREP.

Pavilion â€” local simulation shell: activate the existing Linux venv, change into the new candidate root, confirm hostname and pwd one command at a time. No Windows venv. Then ONE command:

```sh
python3 -B simulation/run.py --session MP005_SIMULATED_SMOKE_R2
```

Expected: eight case results, Provider A/B S00â€“S03, then STOP_FOR_OPERATOR_REVIEW. Never retry into the same directory. Preserve errors and the entire evidence tree even if the run stops early. No live topology endpoints are permitted; the harness enforces loopback.

Copy complete evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R2 back into a NEW local evidence directory under the Windows root. Verify its inventory and the unchanged R1 inventory. Review raw ledgers, snapshots, process identities, signed boundaries and all assertions, not just PASS labels. Retain any anomalies. Update simulation_review/R2_SUMMARY.json with actual evidence paths/hashes only after independent review. If S03 re-enables X, replay changes ledger/execution, fresh authority advances incorrectly, or any case is ambiguous: STOP, no freeze.

After a successful review, stop for operator review before live work. The draft final claim must be narrowed to R01/R02 restart durability, while local S03 is supporting characterization. Resolve live topology, evidence transfer and authorization inputs during a separately authorized preflight, then finalize/freeze before rehearsal operations. Never invent a lock now.
