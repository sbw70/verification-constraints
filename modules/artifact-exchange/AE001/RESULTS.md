# AE001 — Provider-Controlled Artifact Exchange: Results

A request-bound provider-issued artifact traversed the relay while the target provider retained artifact evaluation, software execution and authenticated boundary signaling.

Scored run: **AE001_SCORED_20261018_R1 — PASS**.

| Case | Provider B result | Outcome |
|---|---|---|
| B01 | START, one software execution, COMPLETE | PASS |
| N01 | DENY auth_bad_sig; state/execution unchanged | PASS |
| N02 | DENY auth_provider_mismatch; state/execution unchanged | PASS |
| B02 | START, one software execution, COMPLETE | PASS |

The requester submitted operation bytes and a B-header artifact to the Pi relay. The unchanged relay mechanically derived request representation/binding and forwarded the header value without decoding provider authorization. Providers sent their signed events directly to a separate association-recorder process. Relay HTTP 204 carried no provider decision.

The full session contains ten authenticated provider submissions: four background Provider A auth_missing denials and six Provider B events. Final A state: zero spent/executions. Final B state: two spent/executions. Negatives preserved B state and execution bytes. Exact request, binding, operation and authorization identities correlate relay delivery records, raw signed packages and provider state. The recorder's verification fields were not used as the boundary-signature oracle. Canonical MP003 state hashes matched before/after AE001.

Preflight R1 was INCOMPLETE before deployment because the source-transfer command exceeded Windows command-line length. R2 passed after transport changed to SSH stdin. Their outputs and relevant original harness versions are retained. Before freeze, the harness was also corrected to classify authenticated unexpected admission as FAIL even if it produces excess boundary events. No provider/relay implementation or expected case outcome changed. The scored run used the subsequently locked harness.

Limitations: software execution evidence only; no physical witness or mechanical result. The relay audit records outbound request construction attempts, with receipt/evaluation corroborated by signed provider events and state. This does not test arbitrary compromised code/hosts, key theft, transport confidentiality, all malformed inputs, crash/reboot, concurrency, offline delivery, global chronology, association-chain integrity, quorum or all architectural variations. The recorder is evidentiary and does not authorize execution. Laboratory keys are intentionally supplied for reproduction; post-publication historical authenticity against a holder of those keys is not established.
