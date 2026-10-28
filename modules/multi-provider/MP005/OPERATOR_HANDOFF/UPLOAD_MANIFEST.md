# Uploads — NOT READY for live use

Do not upload a draft as a locked file. Current preparation discussion needs only START_HERE.md, READINESS.json, ASSISTANT_HANDOFF.md and simulation_review/R3_SUMMARY.json. Final lock files below intentionally do not exist until R3 review and topology/config reconciliation. READINESS lists every missing file/blocker.

## Later authorized rehearsal — exact packet files

1. START_HERE.md
2. READINESS.json
3. ASSISTANT_HANDOFF.md
4. locked/MP005_CONTRACT.md
5. locked/MP005_RUN_MANIFEST.json
6. locked/MP005_IMPLEMENTATION_MANIFEST.json
7. locked/MP005_SOURCE_MANIFEST.json
8. locked/MP005_HARNESS_MANIFEST.json
9. locked/MP005_LOCK_SHA256SUMS.txt
10. MACHINE_MAP_TEMPLATE.md (filled verified copy, or initially unfilled only for separately authorized discovery)
11. PREFLIGHT_RUNBOOK.md
12. LIVE_COMMAND_TEMPLATES.md
13. R01_PROVIDER_A_RUNBOOK.md
14. R02_PROVIDER_B_RUNBOOK.md
15. STOP_CONDITIONS.md
16. simulation_review/R3_SUMMARY.json (actual reviewed results, not NOT_RUN placeholder)

Paste PROMPT_REHEARSAL.txt. SOURCE/HARNESS manifests and canonical inventory are needed to independently verify implementation/helper identities. LIVE_COMMAND_TEMPLATES supplies safe host-local/copy interfaces. READINESS prevents bypassing gates. Full R1/R2 trees and unrelated repository files are unnecessary unless a discrepancy needs investigation.

## Later scored run — exact packet files

Upload the same 16 files above, plus POST_RUN_AUDIT.md and the actual accepted rehearsal review, rehearsal case_results.json for R01 and R02, rehearsal SHA256SUMS.txt, and explicit scored-session authorization JSON. The exact external paths/filenames for these future artifacts cannot truthfully be named before the rehearsal/session exists; resolve them in this manifest before declaring the scored packet ready. Do not substitute synthetic placeholders.

Paste PROMPT_SCORED.txt. For post-run audit use PROMPT_POSTRUN_AUDIT.txt with actual scored artifacts and locked files. No need to upload private credentials, Wi-Fi passwords or SSH keys. Public reproducibility lab keys should be supplied only if genuinely required by reviewed locked material, not copied gratuitously.
