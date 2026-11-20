# MD-001 v1 contract

The envelope has exactly `event` (object) and `signature` (string). The event has
exactly six fields. Unknown fields and duplicate keys are rejected. Signed bytes are
the ASCII prefix `NUVL-MD001-ARTIFACT-v1|` followed immediately by canonical UTF-8 JSON
of the event. There is no trailing newline or BOM. SHA-256 artifact observations cover
the entire transmitted envelope, including the signature.

| Signed field | Type | Constraint |
|---|---|---|
| version | JSON integer | exactly 1; boolean rejected |
| producer_id | string | DOMAIN_A is the provisioned producer |
| key_id | string | `sha256:` plus lowercase SHA-256 of raw 32-byte Ed25519 public key |
| artifact_id | string | canonical lowercase hyphenated UUID; UUID4 produced |
| event_id | string | local criteria require LOCAL_SORT_V1 |
| outcome | string | local criteria require SUCCESS |

Strings must match `[A-Za-z0-9_:.\-]{1,128}`. JSON canonicalization sorts object keys,
uses separators `,` and `:`, `ensure_ascii=False`, `allow_nan=False`, and UTF-8.
The constrained schema avoids float and Unicode-normalization ambiguity. The complete
envelope must itself equal its canonical encoding. Signature is Ed25519, encoded as
canonical unpadded URL-safe Base64 (86 characters, exactly 64 decoded bytes).
Algorithm is fixed by version and therefore needs no unsigned algorithm selector.

Each verification parses and validates structure, selects a public key only from the
local producer/key mapping, checks the key fingerprint, performs Ed25519 verification,
and applies the event/outcome criteria. Unknown producers/keys, bad bindings, malformed
input, invalid signatures, and failed criteria reject. Maximum input is 65,536 bytes.
Results distinguish malformed, untrusted binding, invalid signature, and local criteria
rejection. Invalid local configuration fails closed. No timestamp, counter, previous ID,
cached decision, producer database, live producer call, or prior session participates.

Trust mapping: `{ "DOMAIN_A": { "sha256:<fingerprint>": "<raw-public-key-hex>" } }`.
The run records its hash and provisioning method separately. A matching key ID supplied
by the artifact alone establishes no trust. Shared algorithm code provides no shared
operational state. Evidence output is downstream of the pure verification function and
is never read for an acceptance decision.
