# MD001 — Multi-Domain Stateless Verification: Results

Xer0trust LLC. Publication reconciliation: November 25, 2026.

The retained physical records support the operator-recorded B01 PASS, N01 PASS,
and B02 PASS dispositions within the conditions below. This document consolidates
existing records. No experiment, signature test, runtime probe, packet reconstruction,
or physical-host operation was repeated during publication reconciliation.

## Physical scored cases

The original collection labels use November 19, 2026; the recorded case responses
use November 20 UTC. Folder timestamps and host clocks are preserved as recorded;
they are not an independently synchronized cross-host chronology.

| Case | Recorded result | Main observations | Original files retained |
|---|---|---|---:|
| B01 | PASS | HTTP 200, accepted=true, reason=accepted, signature_checks=1; original artifact bytes agree across producer, Pi observations, and HP verifier ingress | 31 |
| N01 | PASS | Downstream event.outcome mutation; HTTP 422, accepted=false, reason=invalid_signature, signature_checks=1 | 34 |
| B02 | PASS | Original B01 artifact accepted by a fresh HP verifier process after recorded producer shutdown/unavailability; HTTP 200 and signature_checks=1 | 45 |

All 110 scored files match the available originals by file size and SHA-256.
Repeated relay/verifier snapshots inside different collection boundaries are
intentional historical evidence and have not been deduplicated.

## B01 — Valid signed assertion through the application relay

Dell performed LOCAL_SORT_V1 with input [9,1,4,2] and observed [1,2,4,9], then
produced and sent the signed assertion. Pi ran the mechanical application relay.
HP's pass ingress forwarded the body to its loopback verifier.

The sender's [result.json](evidence/B01_SCORED_20261119_223940/B01_sender_20261120T033737Z_18481/result.json)
records HTTP 200, accepted=true, one signature check, verifier PID 99396, and
process instance f6e33415a02649fbbdad70a0b27d4323.
The [operation record](evidence/B01_SCORED_20261119_223940/B01_sender_20261120T033737Z_18481/operation.json)
and original signed bytes remain separate observations.

The original [B01 byte comparison](evidence/B01_SCORED_20261119_223940/B01_BYTE_COMPARISON.json) records
four equal 332-byte observations: producer, Pi ingress, Pi egress, and verifier
ingress. Reconciliation recomputed all four file hashes and compared the original
collection to its staged copy. It did not redo capture reconstruction.

Artifact SHA-256: `61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a`.

Independent wire-analysis inputs remain in the collection: PCAP, tool version,
TCP conversation and packet-analysis exports, both reconstructed stream exports,
and the two extracted Pi artifact bodies. Relay diagnostic body hashes alone are
not received-wire proof.

## N01 — Downstream signed-field mutation

The original valid artifact passed through Pi unchanged. HP's explicitly selected
tampering ingress changed event.outcome from SUCCESS to FAILURE downstream of
the relay and retained the original signature. The modified bytes reached the
same verifier process used by B01.

The [mutation record](evidence/N01_SCORED_20261119_224654/N01_ingress_20261120T034412Z_99441/bbc4944fa9294ca2bb2ff346c1967d26-mutation.json)
records signature_replaced=false. The original and modified envelopes are retained.
The [sender result](evidence/N01_SCORED_20261119_224654/N01_sender_20261120T034533Z_18525/result.json)
records HTTP 422, invalid_signature, and one signature check.

Original/Pi artifact SHA-256: `61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a`.

Modified downstream artifact SHA-256: `bae4f84d46d91e3b805890d8e683d9800798c4927343f4d266670824a9b21594`.

The original UTF-16 PowerShell [artifact hash comparison](evidence/N01_SCORED_20261119_224654/ARTIFACT_HASH_COMPARISON.txt)
contains six identities. All six were recomputed against their available original
files without rewriting the comparison record. N01 does not require equality
between the Pi body and the intentionally modified verifier ingress body.

## B02 — Producer unavailable and independent re-verification

The original [shutdown record](evidence/B02_SCORED_20261119_225126/PRODUCER_SHUTDOWN_RECORD.txt) records shutdown
initiation at 2026-11-19 22:52:33 EST, operator confirmation that the plug was pulled,
and an observation at 22:55:07 EST. The separate
[offline check](evidence/B02_SCORED_20261119_225126/PRODUCER_OFFLINE_CHECK.txt) records failed controller-to-Dell
TCP port 22 and ping checks. These are preserved operator/controller observations;
this reconciliation did not observe power state directly.

The new [verifier process](evidence/B02_SCORED_20261119_225126/B02_verifier_20261120T035716Z_99481/process.json)
records PID 99481, instance e701195478694a8eabfff8ce7c5e95ae, and start time
2026-11-20T03:57:16.720931+00:00. These differ from B01's verifier identity.
The [resubmission result](evidence/B02_SCORED_20261119_225126/B02_submit_20261120T035635Z_5534/result.json)
records accepted=true, reason=accepted, and one signature check.

The [B02 byte comparison](evidence/B02_SCORED_20261119_225126/B02_BYTE_COMPARISON.json) binds the original B01
artifact to both B02 Pi observation bodies and the new verifier's ingress body.
All four referenced files match `61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a`. The B02 submission artifact
also matches the original B01 artifact byte for byte.

The retained verification implementation does not use prior artifact history or a
producer service to decide acceptance. Evidence output is observational. A process
restart and a failed connection alone would not establish the case; the retained
acceptance, body identities, source/configuration identity, and operator records
must be considered together.

## Supporting validation and failures

These are supporting records, not additional physical scored cases:

| Original local adapter collection under validation/ | Recorded passed/failed |
|---|---|
| 20261118T035131Z_82147bd7 | 0 / 1 |
| 20261118T035153Z_9edc3256 | 0 / 1 |
| 20261118T035245Z_eef5c4c2 | 9 / 1 |
| 20261118T035328Z_c2e46f14 | 12 / 0 |
| 20261118T035639Z_b8352e18 | 6 / 0 synthetic stream checks |

The initial desktop loopback infrastructure failure and final 21-pass/0-fail
source-snapshotted offline run are retained under desktop/MULTI_DOMAIN_001/evidence/offline/.
The intermediate earlier successful desktop run was deliberately excluded during
November 21 staging; its exclusion is documented in PROVENANCE.md.

Saved Linux runtime probes record 20/20 checks on each of Dell, Pi, and HP.
Saved desktop runtime probes record 18/18. They do not substitute for physical
case evidence. Positive/negative preflight collections and the support export
remain under evidence/support/.

## Scope and limits

MD001 concerns independently checking signed assertions after application relay
conveyance. It does not establish that a signature proves the underlying event
truth, gives execution authority, or causes physical actuation. No ESP witness or
physical non-execution result is claimed. X01 remains an unscored disclosure
inventory, not a fourth scored PASS.

Transport is plaintext and exposes artifact fields and network metadata. The
experiment does not establish confidentiality, hostile-host resistance, protection
against a holder of the intentionally published laboratory private key, arbitrary
fault tolerance, synchronized chronology, or production readiness.

The publication manifest proves byte consistency of the proposed package relative
to its November 25 inventory. It does not create collection-time attestations or
repair historical provenance gaps. See [PROVENANCE.md](PROVENANCE.md) for the
original hash scopes, exclusions, missing historical source revision, and runtime
identity limitations.
