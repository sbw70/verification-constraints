# MD-001 physical adapter preparation R1

Status: LOCAL_ADAPTERS_VALIDATED_AWAITING_DEPLOYMENT_APPROVAL.
This sibling directory adds application deployment preparation without modifying any
existing MULTI_DOMAIN_001 file, original harness, evidence, manifest or prior handoff ZIP.
Use COMMANDS.md for operator review. No command there has been run on physical hosts.

Operator-supplied network status: Dell 10.10.10.10/gateway 10.10.10.1;
Pi 30.30.30.30/gateway 30.30.30.1; HP 40.40.40.40/gateway 40.40.40.1;
OmniBook controller 192.168.1.102. Firewall is Vault/OPNsense, switch GS308Ev4.
Allowed paths supplied: Dell->Pi TCP18081, Pi->HP TCP18443. Direct Dell->HP
and unsolicited HP->Dell have no explicit allow. Controller SSH to Dell/Pi succeeded;
Pi's gateway is saved in NetworkManager; Vault ICMP to HP succeeded; the Vault VLAN30
addressing error was corrected. These are operator-reported facts, not new desktop
network observations. No subnet masks, interface names, SSH usernames or HP management
access were inferred. Earlier proposed 10.77.* deployment addresses are superseded
for this preparation only; historical project documents remain unchanged.

Application flow:

    Dell produce-send -> Pi frozen HUB_B :18081
                       -> HP ingress :18443 -> HP verifier 127.0.0.1:18444

The relay opens its own downstream TCP connection. It does no signature or outcome
interpretation. HP ingress records actual received bytes and normally forwards them
unchanged. Only explicit N01 ingress configuration changes signed outcome SUCCESS to
FAILURE with original signature retained. Verifier remains stateless and unchanged.
The ingress allows only source 30.30.30.30. Verifier accepts loopback peers only.
The relay's external peer filtering relies on reviewed host/firewall policy, not
`allowed_peer` in its config (which must remain null). Its otherwise unused PROVIDER_A
route terminates in a dedicated ephemeral local denial responder returning HTTP403;
it can never send to Dell. This avoids port1 guesses or a reverse-domain route.

Files: md001.py (producer/sender/resubmitter/service launch adapters), configs/*.json
(supplied addresses), runtime/{artifact,hub,wire,routes}.py (byte-identical existing
code), RUNTIME_LOCK.json (checked before every adapter command), observe.py (offline
HTTP body extraction and exact byte comparison), test_local.py (new local adapter
tests), ORIGINAL_PROJECT_LOCK.json (all existing file hashes), COMMANDS.md,
TEST_PLAN.md, X01.md and VALIDATION.md. No historic runtime is edited or monkeypatched.

Persistent services required after approval: one frozen relay launcher on Pi;
one verifier and one ingress on HP. Dell producer/sender is a one-shot command.
No controller verification service, recorder authority, shared history database,
producer online API, ESP service, or auto-start service is required. Operator-controlled
foreground processes are proposed first, making case transitions and restarts explicit.
Every service launch requires a new output directory and records PID, random instance,
UTC start time, config hash, adapter hash and runtime lock hash. Request evidence uses
exclusive UUID filenames and never participates in acceptance. There are no retries.
Send failure leaves delivery uncertain; preserve it and do not auto-repeat a scored run.

Deployment archive contains code/config/docs only, excluding validation keys/evidence.
Package SHA256SUMS.txt covers preparation and all retained local validation attempts.
The original manifest is preserved and is not regenerated to include sibling additions.
Disposable test key is created on Dell later; transfer only public trust to HP out of
band and compare fingerprint. No pre-generated local validation key is to be deployed.

STOP remains in force before deployment. A later successful physical preflight does
not authorize scored tests; require separate scored-run approval. ESP execution is
outside this adapter package and still needs separate approval and witness preparation.
