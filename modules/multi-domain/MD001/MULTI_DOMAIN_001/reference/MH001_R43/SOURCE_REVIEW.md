# MH001 R4.3 architectural source review

## Authority boundary and source identity

`hub.py` uses `socketserver.TCPServer`, without threading/forking mixins, worker
pools, background forwarding, redirects, connection pooling, or application
retries. A hub chooses exactly one route from the single unsigned
`X-MH-Destination` field, before reading body bytes. Header names are compared
case-insensitively; field values are compared exactly after removing HTTP field
delimiter optional whitespace. Quotes, comma lists, unknown/lowercase values,
duplicates (even identical values), invalid names, folding, and control bytes
are rejected. No signature parsing, authority reconstruction, provider policy,
spent state, execution state, or signing material exists in the hub call path.

`wire.connect` makes one numeric-address socket and one connect call. It does not
perform DNS resolution, multiple-address fallback, proxy lookup, or redirection.
`sendall` may issue multiple operating-system writes to transmit a single request;
it never resubmits a request after an error. A transport failure after any bytes
are sent leaves provider execution unknown. Never resend automatically.

Provider A SHA-256:
`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

Provider B SHA-256:
`618ec76ef5dd3bfa3ba7b1ad3941ed0516a7511b72957d7efb82ec565905b605`

Both prepared provider files match the frozen historical local files under
`C:\Users\holiw\esp32-main\MULTI_PROVIDER_005` and the published MP005 paths at
commit `73713f6e9ed9c95251cc69ec88ef816cab771ac0` in
`sbw70/verification-constraints`. The read-only GitHub connector retrieved the
commit-addressed source. Its UTF-8 text payload and URLs are preserved in
`provenance/github_source_text.json`, with exact decoded source in
`provenance/published/`. No provider-source discrepancy was found. The historical
manifest's older `fa541618...` commit is MP003 baseline provenance, not the
published hardened MP005 source identity. A separate reference-checkout Git read
was permission-denied; it was not needed for the successful historical-file and
published-commit comparison. Historical material was never repaired or rewritten.

## Binding compatibility gate — inspected, not live-tested

Both frozen providers compute:

```text
request_repr = SHA256(original operation bytes)  [constructed by requester]
binding = SHA256(UTF8("NUVL_BIND_V1|" + request_repr + "|" + verification_context))
operation_id = SHA256(UTF8("NUVL-MP-OP-v1|" + binding))
```

The issued authorization signs provider identity, request digest, context, nonce,
and authorization identity. `process_artifact` verifies provider identity, the
authorization ID, Ed25519 signature, request/context agreement, and consumption.
Provider B also checks its existing `CTX_MP002_DIVERGE` policy-denial context;
MH001 authority must use an appropriate provider-approved context, not that value.

The inspected provider HTTP handlers read only `Content-Length` from request
headers. They ignore `Host` and `X-MH-Destination`. HTTP method/path/query are not
part of the signed binding, but handlers dispatch only the existing endpoint
methods/paths. All are preserved through hubs regardless. Actual deployed source
hashes must be reconfirmed before deployment. If actual binding includes Host,
STOP; do not patch provider verification. Application-layer source has no peer-IP
allowlist or hub-identity authorization grant; OS/network constraints remain pending.

## Requester adapter — necessary and disclosed

The historical MP005 requester sent operation bytes plus provider authorization
headers to the fan-out relay. That relay created the artifact consumed by
`/ingest`. Reusing it would violate MH001. `requester.py` now constructs the
complete outer artifact before the first hub: request digest, context, mechanical
binding, and base64 of the **exact already-issued package bytes**. The requester
does not change, decode/re-encode, sign, enlarge, restore, or issue that package.
Its supplied context/operation must match issuance; the provider independently
enforces that agreement. The adapter reports that it has not verified a signature.

Preparation saves the complete HTTP request, body bytes, and requester hashes in
a new exclusive artifact directory. Replays use the same `request.http`, not a
new call to `prepare`. Send receipts contain hashes and transport results only;
an existing receipt path prevents another send. There is one transmission attempt.
The CLI and `submit()` default to loopback-only. The optional requester-specific
`--approved-hubs` JSON configuration permits only exact canonical literal IP/port
pairs. Its shipped list is empty. Duplicate keys/entries, unknown fields, invalid
ports, DNS names and scoped addresses are rejected. Approval is checked before
opening a receipt or socket, and never changes request bytes. The configuration
is not a hub routing file. Verified entries and their new hash require STOP 1
approval before live use; no further requester code change is needed.

## HTTP wire contract and supported framing

Request method, origin-form path/query octets, body, and all nonexcluded raw
header lines (including duplicates and field casing/spacing) are copied. Only
Host is rewritten to the numeric next-hop authority. The exact frozen exclusions
in both directions are Host, Connection, Keep-Alive, Proxy-Connection, TE, Trailer,
Transfer-Encoding, Upgrade, Proxy-Authenticate, Proxy-Authorization. Nothing else
is silently dropped. Connection tokens naming another field are rejected; close,
keep-alive, and names in the frozen exclusion set are accepted.

One nonnegative decimal Content-Length is mandatory on requests; zero is allowed,
64 KiB is allowed, larger bodies are rejected with 400. Any Transfer-Encoding,
duplicate Content-Length (identical or conflicting), folded/malformed header,
truncated body, or unsupported framing is rejected. Missing length produces 411.
Headers are limited to 64 KiB/100 fields and request lines to 64 KiB. Origin-form
HTTP/1.0 and HTTP/1.1 are supported; CONNECT/tunneling, fragments, absolute-form,
and Expect/interim handshakes are outside the controlled protocol and rejected.
These limits do not exclude any header on an accepted request.

Downstream responses support one final HTTP/1.0 or HTTP/1.1 status in 200–599.
Responses carrying a body require exactly one valid Content-Length; the complete
body is read before anything is sent upstream. Response bodies do not inherit
the request's 64-KiB cap. HEAD/304 use HTTP no-body semantics and may retain a
representation length; 204 allows no Content-Length or zero. The frozen providers'
HTTP/1.0 204 without Content-Length is supported exactly as a zero-body response.
Chunked, EOF-delimited body responses, interim/101, malformed/duplicate lengths,
truncated bodies, and unsupported Connection tokens yield an identified 502 hub
transport error. No partial downstream response is emitted before validation.
Timeout yields 504; neither establishes whether a provider executed. A client
write failure after response forwarding starts closes the connection and never
appends a fabricated hub error to a partial provider reply.

Each hop uses separate plain TCP connections. Outgoing request and response
versions are HTTP/1.1, even when the incoming version was HTTP/1.0. Each connection
closes after one exchange; no keepalive or pipelined second request is served.
Status code/reason octets and permitted response header lines/body are preserved;
no Server/Date/Connection headers are automatically inserted. Host in a response
is excluded and is not invented. If later controlled provider responses require
other framing, STOP and review instead of improvising a conversion.

## Mechanical evidence

Each accepted request produces ingress and result JSONL observations with the
same per-process monotonically increasing sequence. Ingress is flushed before
connecting downstream. Result contains ingress/egress body SHA-256, header names
and opaque value hashes, next-hop identity, timestamp, and transport result.
`value_sha256` hashes the field value after delimiter optional whitespace;
`wire_value_sha256` additionally covers the exact bytes after the colon. Since
preserved lines are copied verbatim, these hashes describe both ingress and
egress preserved fields. Host is excluded. No authorization fields are sought.

Rejected/incomplete requests use null body hashes when a complete body was not
read; failed connections use null egress hashes when no send was attempted.
Egress hashes identify bytes supplied to the single send attempt, not delivery or
execution proof. Interrupted/partial sends and missing result observations are
incomplete evidence. Result logs never claim provider acceptance, denial, or
execution. Fresh log files are exclusive; sequences restart only in a new process
and must be scoped to that run's PID/source/configuration identity externally.

Requester and provider-boundary ingress observations remain separate. For the
chained route, compare requester → Hub A ingress/egress → Hub B ingress/egress →
provider ingress, plus preserved-header hashes. Hub logs cannot replace provider
ingress evidence or independently verified signed decisions.

## Validation boundary

Mocks capture exact bytes; submissions are sequential. Tests use threads only to
host separate single-threaded mock/hub servers, plus an integration case launches
two independent hub subprocesses. No actual provider is imported, no provider
authority is consumed, and no signing key (real or mock) is generated. Both timeout
configuration values are checked, failure classification is injected, and the
real Hub B downstream socket read timeout is exercised at 10 seconds. This proves
local transport behavior, not Dell latency, live ingress capture, real signatures,
provider execution, or machine/service isolation. Hub source is approximately
100 lines plus explicit shared framing/configuration modules; correctness checks
were kept readable rather than compressed to an unsafe total line target.
