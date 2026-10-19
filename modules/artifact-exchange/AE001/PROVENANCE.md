# AE001 Provenance

## Implementation identity

The architectural reference is modules/artifact-exchange/AEBS.py at repository commit 292c1c38b08b007592aab8fc14a97755367143e5. Its preserved source is source/reference/AEBS.py. The actual tested providers, issuance utilities, relay, association recorder, registry and laboratory keys are byte-identical MP003 copies under source/MP003/. Local copies matched the published Git blob identities and available live MP003 provider/relay files before AE001. Exact identities are in configs/AE001_SOURCE_MANIFEST.json and configs/AE001_RUN_MANIFEST.json.

AEBS.py's illustrative single-provider fixed token and printed boundary hashes were expanded by composing the already-tested MP003 provider-specific signed artifacts and authenticated boundary signaling. AE001 uses that existing protocol unchanged. It does not claim that the illustrative AEBS.py alone supplies these controls.

## Actual topology

| Role | Machine | Endpoint |
|---|---|---|
| Requester/scoring | Xer0trust, Windows | 192.168.1.102 |
| Relay | nuvl-relay, Raspberry Pi | 192.168.1.100:18080/nuvl |
| Association, separate process | nuvl-relay, Raspberry Pi | 192.168.1.100:19191/boundary |
| Provider A | Xer0trust-3, Linux | 192.168.1.118:19090/ingest |
| Provider B | Xer0trust2, Linux | 192.168.1.107:19090/ingest |

Providers used Python 3.12.3/cryptography 41.0.7. The Pi used Python 3.13.5/cryptography 43.0.0. Requesting/scoring used Python 3.12.14/cryptography 50.0.2. Deployments record runtime identity and file hashes. Per-role isolated remote roots are /home/seth/ARTIFACT_EXHANGE/RUN_ID. Canonical MP003 paths/state were not modified. Runtime state was explicitly initialized only in new AE001 run directories.

scripts/launch_role.py changes configuration globals for addresses, ports, run-state locations and adds an observational urllib audit hook on the relay. It does not replace provider evaluation, minting, persistence or boundary methods. The relay and association share a host but are separate processes; the AE001 Pi deployment contains only relay/association sources and public trust material. No process/host isolation or hostile-host resistance claim is made.

## Locked definition and evidence

configs/AE001_LOCK_SHA256SUMS.txt locks revision 1's contract, run manifest and copied-source inventory. The run manifest pins both campaign scripts and source bytes. Each run preserves the exact contract/manifest it used, input identities, per-case artifacts, raw signed packages, state/execution snapshots, relay delivery records, runtime consoles, final association log and checksum list. The scored directory is evidence/scored/AE001_SCORED_20261018_R1/. Its SHA256SUMS paths are relative to that run directory.

Preflight R1 failed before deployment due to the Windows command-line limit. Preflight R2 passed. Earlier harness versions under evidence/retained correspond to the preflight identities; the final harness's rejection/admission classification correction occurred before the scored freeze. Prior run files have not been rewritten. No extra negative case or changed expected reason was introduced after scoring.

Snapshot execution files may be zero-byte representations of an absent execution log; state_presence_and_hashes.json records actual presence. Provider B executed twice; Provider A never executed. Signature verification independently checks raw provider packages with their specific public keys. This run does not score association hash-chain consistency or cross-host chronology.

## Reproduction

Retain source and laboratory keys exactly as supplied. Prepare Python/cryptography at the documented role versions, three reachable SSH-managed Linux hosts with the expected /home/seth account layout, and a requesting Windows host. Adjust the host mapping in a new manifest revision if necessary and lock that revision before a new score. Provide your own SSH identity and known_hosts file externally; those access credentials are not included in the test package.

From the AE001 root, a preflight invocation is:

    python scripts/run_ae001.py --root . --identity PATH_TO_YOUR_SSH_KEY --known-hosts PATH_TO_YOUR_KNOWN_HOSTS --phase preflight --run-id AE001_PREFLIGHT_FRESH1

The local run directory and remote run roots must not exist. Do not reuse consumed authority or erase prior state. All selected sources and key bytes are supplied locally; their original MP003 installation was an inspection reference, while runtime deployment reads the local source tree. The harness checks canonical MP003 state hashes where present on the hosts and preserves matching before/after bookends. After a clean preflight and a suitable frozen revision, use --phase scored with a new run ID. Only the four defined cases execute. Per-run SHA256SUMS and the root publication SHA256SUMS identify exact bytes; neither is an external signature.

## Scope

This is technical evidence for the bounded AE001 exchange property. It is not a validation of every feature of a broader specification. It makes no physical-consequence, universal non-execution, secure-transport, provider-host-compromise, key-compromise, durability-under-fault, concurrency or global chronology claim. The recorder and relay do not gain provider authority. Provider-controlled software execution is the tested consequential step.
