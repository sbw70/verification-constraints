MD001 B01 — Valid Cross-Domain Verification

Overview

B01 is the positive-control scored run for MD001, the Multi-Domain Stateless Verification experiment.

The run examines whether a signed operation-completion assertion originating in Domain A can be transported through an intermediary and independently verified in Domain B without modification of the signed artifact.

Scored evidence directory: "B01_SCORED_20261119_223940"
Recorded execution: November 20, 2026 UTC
Recorded outcome: PASS — artifact bytes preserved; signature accepted

B01 establishes the valid-artifact baseline used to interpret the subsequent negative and producer-unavailable cases.

1. Test Objective

The experiment evaluates three observable properties:

1. Domain A produces an assertion describing a completed local operation.
2. The assertion remains byte-identical across the recorded transport and verification boundaries.
3. Domain B independently evaluates the assertion against provisioned trust material and records its verification decision.

The relay is a transport component. It does not originate the signed assertion or determine its cryptographic validity.

2. Recorded Architecture

Domain A — Producer
10.10.10.10
       |
       | Signed assertion
       v
Mechanical Relay
30.30.30.30:18081
       |
       | PROVIDER_B route
       v
Domain B — Ingress
40.40.40.40:18443
       |
       | Forwarded assertion
       v
Domain B — Verifier
       |
       v
Signature verification and response

The recorded relay configuration identifies "HUB_B" and a static route to "PROVIDER_B".

The ingress transport record identifies an HTTP "POST" to "/verify", with a 332-byte request body and the destination header "X-MH-Destination: PROVIDER_B".

3. Operation and Signed Artifact

The producer's recorded operation is "LOCAL_SORT_V1".

The operation record contains:

Field| Recorded value
Event| "LOCAL_SORT_V1"
Boundary| "sort_completed"
Input| "[9,1,4,2]"
Observed output| "[1,2,4,9]"

The producer's "artifact.json" contains the signed assertion submitted for independent verification.

The associated "signed-bytes.bin" preserves the bytes used for the signature operation.

This run records a software operation-completion assertion. It does not establish physical actuation or independent verification of the underlying sorting operation.

4. Evidence Directory

The B01 evidence is organized by observation point.

Producer — "B01_sender_20261120T033737Z_18481/"

File| Purpose
"operation.json"| Recorded local operation
"artifact.json"| Signed assertion
"signed-bytes.bin"| Original signed bytes
"submission.json"| Submission endpoint and artifact identity
"response.bin"| Returned response bytes
"result.json"| Parsed response and recorded outcome

Relay — "B01_relay_20261120T033236Z_5344/"

File| Purpose
"effective-hub-config.json"| Effective relay routing configuration
"process.json"| Relay process identity
"relay.jsonl"| Relay event log

Domain B Ingress — "B01_ingress_20261120T033452Z_99409/"

The ingress directory contains "process.json" and five request-specific records identified by the prefix:

"2895dd5533c84359a9e5ad04dc34e31a"

These preserve ingress bytes, egress bytes, downstream response bytes, transport metadata, and the recorded response.

Domain B Verifier — "B01_verifier_20261120T033407Z_99396/"

The verifier directory contains "process.json", "trust-provisioned.json", and three request-specific records identified by the prefix:

"066c3bc0df2b4aec91e7960fd38ff442"

These preserve the received artifact bytes, transport metadata, and verification decision.

The trust-provisioning record identifies the configured Domain A verification material used by the verifier.

Independent Transport Evidence

File| Purpose
"MD001_B01_20261120T033349Z.pcap"| Packet capture
"PI_INGRESS_ARTIFACT.bin"| Artifact observed at relay ingress
"PI_EGRESS_ARTIFACT.bin"| Artifact observed at relay egress
"B01_BYTE_COMPARISON.json"| Recorded cross-boundary byte and SHA-256 comparison
"TCP_CONVERSATIONS.txt"| Extracted TCP conversation information
"TCP_PACKET_ANALYSIS.txt"| Packet-analysis record
"TSHARK_VERSION.txt"| Packet-analysis tool version
"stream_0.bin", "stream_1.bin"| Extracted binary TCP streams
"stream_0.txt", "stream_1.txt"| Text representations of extracted streams

5. Recorded Results

Artifact Integrity

"B01_BYTE_COMPARISON.json" records identical artifact content at four observation points:

Observation point| Bytes| SHA-256 agreement
Producer| 332| Match
Relay ingress| 332| Match
Relay egress| 332| Match
Verifier ingress| 332| Match

All four records identify the same SHA-256 digest:

61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a

The comparison record reports "equal: true".

Verification Decision

The verifier's preserved response records:

{
  "accepted": true,
  "reason": "accepted",
  "signature_checks": 1
}

The response identifies the same artifact SHA-256 digest recorded at the transport observation points.

The producer's recorded result contains HTTP status "200" and the accepted verification response.

B01 result: PASS for the recorded valid-artifact transport and independent verification case.

6. Independent Evidence Review

A reviewer can inspect the historical result without starting the laboratory services.

1. Inspect the producer's "operation.json", "artifact.json", and "signed-bytes.bin" to establish the operation record and signed assertion.
2. Compare the artifact SHA-256 values in "B01_BYTE_COMPARISON.json" with the corresponding preserved binary artifacts.
3. Inspect the relay configuration and "relay.jsonl" to establish the recorded forwarding path.
4. Inspect the ingress transport record and preserved ingress/egress bytes.
5. Inspect "trust-provisioned.json" and the verifier's decision record to establish the recorded trust configuration and verification outcome.
6. Use the packet capture and extracted TCP streams to cross-check the transport observations.

The historical evidence review is distinct from a new live execution. A fresh reproduction additionally requires the published implementation, compatible runtime, trust configuration, and laboratory network setup documented at the MD001 level.

7. Scope and Limitations

B01 demonstrates a successful recorded path for a valid signed assertion and byte preservation across the identified observation points.

It does not, by itself, establish:

- Prevention of replay or duplicate execution.
- Durable single-use authority consumption.
- Provider enforcement of an execution boundary.
- Physical execution or independent measurement of the local sorting operation.
- Security against compromise of the producer or its signing key.
- Correct behavior under arbitrary network failures or malicious intermediary modifications.

The negative mutation case is evaluated separately in N01. Verification with the original producer unavailable is evaluated separately in B02.

B01 should therefore be interpreted as the positive-control evidence for cross-domain signed-artifact transport and independent cryptographic verification, not as a general authorization or execution-enforcement result.
