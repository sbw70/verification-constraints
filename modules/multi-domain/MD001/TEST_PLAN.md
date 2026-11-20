# Physical test and observation plan — pending approval

B01: Dell executes LOCAL_SORT_V1, checks [1,2,4,9], signs assertion, and transmits its
own exact artifact via HTTP POST /verify to Pi. Pi's unchanged mechanical forwarder
opens a separate connection to HP ingress. Pass ingress writes received bytes and
forwards them unchanged to loopback verifier. B validates schema, provisioned producer
key binding, Ed25519 signature and local criteria. Preserve operation record, signature
bytes, four independent byte observations, decision, process and config identities.
Require accepted=true, signature_checks=1, and byte equality producer/Pi-ingress/
Pi-egress/verifier-ingress. Also require physical preflight exports and denial evidence.

N01: valid original has first been accepted in B01. Same original travels through Pi
into HP ingress explicitly started with ingress_N01.json. It changes only signed
outcome, retains signature, saves original, mutation and new bytes, and delivers to
unchanged verifier. Require HTTP422 and invalid_signature, actual signature check,
different original/modified hashes, same original signature, and frozen relay source
integrity. Pi egress must equal original; HP verifier ingress must equal modified.
Never compare all N01 observation hashes as if they should remain equal.

B02: preserve B01 artifact outside Dell before shutdown. Record observed physical
power-off and failed known endpoint connection. Stop/restart verifier only after
recording old PID/start/instance. Keep public trust, create a new evidence directory,
and ensure pass ingress. On Pi, resubmit original stored B01 bytes through the relay;
no producer/key required. Require new PID/instance/start identity, accepted=true,
signature_checks=1 and unchanged original hash. B must make no producer connection
and consult no prior verification record. Verifier uses the unchanged pure artifact
module with no network, file or artifact-history decision dependencies. Preserve
actual new process records and network observations. Fresh launch alone is not a PASS.

## Independent Pi observations

Frozen relay log ingress and egress hashes are diagnostics. Egress diagnostic is a
send-attempt observation and cannot stand alone as received-wire proof. External
capture is required for physical B01. Identify actual Pi interface via operator's
known configuration; do not assume eth0. Run approved tcpdump with a unique output:

```sh
sudo tcpdump -i ACTUAL_PI_INTERFACE -s 0 -U -w UNIQUE_CASE.pcap 'tcp port 18081 or tcp port 18443'
```

Retain complete pcap plus capture tool/version, interface, loss summary, flow tuples,
case windows and timestamps. Distinguish A10.10.10.10->Pi30.30.30.30:18081 from
Pi30.30.30.30->HP40.40.40.40:18443. B02 ingress source changes to Pi itself; capture
that local connection using the actual Linux capture interface (possibly lo/any),
while egress is still Pi->HP. Record topology and avoid duplicate captures as evidence.

On the analysis machine, use a reviewed TCP reassembly tool (e.g. Wireshark Follow
TCP Stream) and export ONLY the client-to-server direction as raw reassembled bytes.
Record tool/version, TCP stream number and exact tuple alongside each export.
Inspect for missing segments, conflicting overlap/retransmits and complete boundaries;
if reassembly is ambiguous, case evidence is incomplete. observe.py parses an already
reassembled direction; it does not reconstruct packets or certify capture completeness.
For each one-request stream, preserve the raw export and extract its HTTP body:

```sh
python -B observe.py extract --stream PI_INGRESS_DIRECTION.bin --out PI_INGRESS_ARTIFACT.bin
python -B observe.py extract --stream PI_EGRESS_DIRECTION.bin --out PI_EGRESS_ARTIFACT.bin
python -B observe.py compare --producer B01_ORIGINAL.json --relay-ingress PI_INGRESS_ARTIFACT.bin --relay-egress PI_EGRESS_ARTIFACT.bin --verifier HP_VERIFIER_INGRESS.bin --out B01_BYTE_COMPARISON.json
```

Observe.py rejects truncated Content-Length bodies, extra requests/data, unsupported
framing and wrong path/destination. Its equality decision compares actual bytes,
not merely caller-supplied hashes. All output files must be new. It cannot turn relay
log hashes into independent packet observations. TLS is not in this lab transport;
if encryption/offload/capture gaps prevent reliable reconstruction, record limitation
and do not award physical B01 PASS. Tool installation/reassembly workflow remains a
physical preflight prerequisite and is not claimed validated on Pi or Linux here.

## Evidence and limitations

Gather source/runtime locks, config, provisioning, operation and artifacts, raw bytes,
process metadata/stdout/stderr, responses, pcap/exports/extraction records, applicable
firewall exports/logs, and case-specific operator observations in new run directories.
Create a new SHA-256 manifest after each completed physical evidence collection;
never edit desktop or previous run manifests. Score cases only after all required
evidence agrees. No producer private key, shared history, clock-based acceptance,
execution authority or ESP actuation enters these verification cases. The public
trust config persists; evidence files never determine acceptance. Shared source
does not mean shared operational state. No signature proves underlying event truth.
