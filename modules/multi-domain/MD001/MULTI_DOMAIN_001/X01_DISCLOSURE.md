# X01 disclosure inventory (unscored)

Inventory is grounded in the saved canonical `producer/artifact.json` and external
application tap observations in the validated run, with matching hashes in
`B01-observed_hashes.json`. No physical Pi packet capture exists yet.

| Field | Type | Origin / purpose | External | Verification | Internal logic / operational state |
|---|---|---|---|---|---|
| event.version | integer | protocol / select v1 | yes | required | no |
| event.producer_id | string | producer config / identity assertion | yes | required | identity disclosure |
| event.key_id | string | public-key fingerprint / trust selector | yes | required | key identity and linkability, no private key |
| event.artifact_id | string | producer UUID4 / identify assertion | yes | identification, no single-use role | issuance identity, no history |
| event.event_id | string | provider boundary / LOCAL_SORT_V1 | yes | local criteria | deliberately reveals event category |
| event.outcome | string | operation completion / SUCCESS | yes | local criteria | deliberately reveals asserted outcome |
| signature | string | Ed25519 over tagged canonical event / authenticity | yes | required | no internal logic; linked to public key |

Envelope field names and nesting disclose the format. No other artifact fields exist.
No operation inputs, sorted output, operation record, database contents, execution
algorithm, authorization token, target command, timestamp, or private key is sent in
the artifact. Event identity and success are deliberate assertions and constitute a
limited operational disclosure. They do not independently prove the underlying event.

Outside Domain A, plaintext HTTP transport exposes addresses/ports, request timing,
sizes, direction, method POST, target /verify, Host, Content-Length, Content-Type,
X-MH-Destination PROVIDER_B, connection behavior, and protocol headers such as
Accept-Encoding. The Python test verifier response also reveals acceptance/rejection,
reason, artifact hash, signature-check count, verifier PID/process-instance and UTC
evidence time; HTTP server headers can reveal Python/server version and time. These
are diagnostic test metadata and are outside the signed artifact. A physical adapter
must inventory its actual wire headers and response too. Relay operational logs expose
route destination, header hashes, timing, transport results and body hashes.

The producer operation record and test private key are retained in operator evidence,
not sent through the relay. Publishing that evidence deliberately expands disclosure
to the included sort inputs/output and disposable test key. Keep publication claims
separate from this artifact-transport boundary. The local harness can inspect every
process and therefore provides no confidentiality isolation from its operator.

This inventory describes observed assertions and transport metadata. It makes no
absolute confidentiality claim and does not rule out timing channels, other software,
host compromise, unobserved traffic, or every possible information leak.
