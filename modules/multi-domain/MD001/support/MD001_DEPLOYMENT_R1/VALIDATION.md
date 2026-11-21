# Adapter validation and STOP report

LOCAL_ADAPTERS_VALIDATED_AWAITING_DEPLOYMENT_APPROVAL

Final adapter integration run: validation/20261118T035328Z_c2e46f14/RESULTS.json:
12 PASS, 0 FAIL. Actual subprocesses use loopback substitutions of the physical
configuration, not the physical addresses. Checks cover producer operation/sign/send,
matching B01 ingress bytes and frozen relay diagnostic hashes, downstream N01 mutation
with original signature and invalid_signature rejection, restarted verifier acceptance
of original artifact without producer/key, repeated acceptance, unused A route local
denial, invalid path rejection, Pi-peer filtering, original project preservation,
and copied runtime integrity. Python3.14.3 / cryptography49.0.0 on Windows was used.
These are supporting adapter checks, not additional scored cases.

Offline extraction checks: validation/20261118T035639Z_b8352e18/RESULTS.json:
6 PASS, 0 FAIL. Synthetic single-direction HTTP export extracts exactly; truncated,
extra-request, wrong-path, wrong-destination and chunked streams reject. No physical
pcap/reassembly workflow has been validated by these unit checks.

Total final checks: 18 PASS, 0 FAIL, with B01/N01/B02 adapter behavior demonstrated
locally. Previous attempts remain preserved: two initial failures at loopback sending
(the second records Windows sandbox WinError10013); one subsequent 9-pass/1-fail run
exposed HTTP rejection closing before request-body drain. The adapter was corrected
to read bounded framed input before sending a denied-peer response; final test passed.
No failed local attempts or old project evidence were overwritten.

runtime/artifact.py, hub.py, wire.py and routes.py are byte-for-byte copies from
the existing project. ORIGINAL_PROJECT_LOCK.json records all208 original project
files; final integration checked the entire mapping unchanged. Preparation files live
only in this sibling directory. The original offline harness was not rerun or edited.

Remaining prerequisites before scored physical work:

- Explicit deployment approval at the existing STOP gate; then physical application
  preflight; then separate scored-test approval.
- Approved Linux account/install paths and HP transfer/management channel (only
  controller SSH to Dell/Pi has been reported successful).
- Compatible Python/cryptography installation on all hosts, especially Pi OS/architecture;
  reviewed wheelhouse where package-network access is absent. No silent dependency change.
- HP return route to30.30.30.30 via40.40.40.1; actual port18081/18443 reachability,
  binds and host firewall rules. Current port allows are operator-reported, untested here.
- Direct A-to-B explicit logged-deny evidence and effective applicable rule export;
  no-explicit-allow and a timeout alone are insufficient.
- Independent Pi capture, complete TCP reconstruction/export and actual four-point
  body-byte equality. No fabricated ingress/egress capture hashes are supplied.
- Out-of-band public trust provisioning, preserved B01 custody, A power-off observation
  and failed known endpoint connection, fresh verifier identity for physical B02.

X01.md documents unchanged artifact fields and new adapter-visible metadata. Complete
its physical observation portion using actual wire evidence. Source checks show no
verification-driven execution capability; no ESP physical isolation is claimed here.
No deployment, network change, physical scoring, key issuance for ESP or actuation
was performed. STOP before deployment; user review is the next step.
