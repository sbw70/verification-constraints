"""Actual loopback tests; no physical network, firewall, or ESP evidence."""
import ast
import copy
from datetime import datetime, timezone
import http.client
import json
import os
from pathlib import Path
import platform
import queue
import socket
import subprocess
import sys
import threading
import uuid
from unittest.mock import patch
import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from artifact import canonical_bytes, digest, key_id, loads, produce, signed_bytes, verify


def save(path, obj):
    with path.open("xb") as f:
        f.write(canonical_bytes(obj))


def main():
    run = ROOT / "evidence/offline" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ_") + uuid.uuid4().hex[:8])
    run.mkdir(parents=True, exist_ok=False)
    checks, processes, handles = [], [], []

    def check(name, condition, observed=None):
        checks.append(dict(name=name, status="PASS" if condition else "FAIL", observed=observed))

    def launch(role, name, **options):
        directory = run / name
        cmd = [sys.executable, "-B", str(ROOT / "src/service.py"), role, "--directory", str(directory)]
        for k, v in options.items():
            cmd.extend(["--" + k, str(v)])
        err = (run / (name + "-stderr.txt")).open("xb")
        handles.append(err)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err, cwd=ROOT,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        processes.append(proc)
        q = queue.Queue()
        threading.Thread(target=lambda: q.put(proc.stdout.readline()), daemon=True).start()
        line = q.get(timeout=20)
        (run / (name + "-stdout.txt")).write_bytes(line)
        if not line:
            raise RuntimeError("service startup failed: " + name)
        identity = json.loads(line)
        save(run / (name + "-process.json"), dict(identity=identity, command=cmd))
        return proc, identity

    def stop(proc):
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=10)

    def send(port, raw):
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        c.request("POST", "/verify", raw, {"Content-Type": "application/json", "X-MH-Destination": "PROVIDER_B"})
        r = c.getresponse()
        status, body = r.status, r.read()
        c.close()
        return status, json.loads(body)

    error = None
    try:
        snapshot = run / "build_snapshot"
        snapshot.mkdir()
        source_hashes = {}
        for source in [ROOT / "src/artifact.py", ROOT / "src/service.py", Path(__file__).resolve(), ROOT / "requirements.txt"]:
            relative = source.relative_to(ROOT)
            target = snapshot / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            source_hashes[relative.as_posix()] = digest(source.read_bytes())
        save(run / "build_identity.json", dict(revision="MD001_R1_LOCAL_CONTENT_IDENTIFIED",
             source_sha256=source_hashes, inventory_sha256=digest((ROOT / "reference/SOURCE_INVENTORY.json").read_bytes())))
        inventory = json.loads((ROOT / "reference/SOURCE_INVENTORY.json").read_bytes())
        identities_before = {row["source_path"]: digest(Path(row["source_path"]).read_bytes()) for row in inventory["files"]}
        check("reference_bytes_match_inventory", all(digest((ROOT / r["copy_path"]).read_bytes()) == r["sha256"]
                                                     == identities_before[r["source_path"]] for r in inventory["files"]))
        keys = run / "test_keys"
        keys.mkdir()
        key = Ed25519PrivateKey.generate()
        private_path = keys / "domain_a_TEST_ONLY_private.pem"
        private_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                                  serialization.NoEncryption()))
        public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        trust = {"DOMAIN_A": {key_id(key.public_key()): public.hex()}}
        trust_path = run / "trust.json"
        save(trust_path, trust)
        save(run / "trust_provisioning.json", dict(method="out-of-band local harness configuration",
             producer_id="DOMAIN_A", key_id=key_id(key.public_key()), raw_public_key_hex=public.hex(),
             trust_config_sha256=digest(trust_path.read_bytes()), disposable_test_key=True))
        producer, a = launch("producer", "producer", key=private_path)
        original = (run / "producer/artifact.json").read_bytes()
        original_hash = digest(original)
        (run / "signed_bytes.bin").write_bytes(signed_bytes(loads(original)["event"]))
        verifier, b = launch("verifier", "verifier_before", trust=trust_path)
        tap, t = launch("tap", "relay_egress_tap", target=b["port"])
        relay, r = launch("relay", "relay", target=t["port"])
        ingress, i = launch("tap", "relay_ingress_tap", target=r["port"])
        status, decision = send(i["port"], original)
        save(run / "B01-response.json", dict(http_status=status, decision=decision))
        observations = {"producer": original_hash,
            "relay_ingress_external_tap": digest((run / "relay_ingress_tap/001-egress.bin").read_bytes()),
            "relay_egress_external_tap": digest((run / "relay_egress_tap/001-ingress.bin").read_bytes()),
            "verifier_ingress": digest((run / "verifier_before/001-ingress.bin").read_bytes())}
        save(run / "B01-observed_hashes.json", dict(mode="LOOPBACK_APPLICATION_TAPS_NOT_PACKET_CAPTURE", hashes=observations))
        check("B01_cross_domain_simulation", status == 200 and decision["accepted"] and decision["signature_checks"] == 1
              and len(set(observations.values())) == 1, observations)
        # Every send begins before the frozen relay. Mutation is downstream only.
        tamper, n = launch("tamper", "tampering_adapter", target=b["port"])
        relay_n, rn = launch("relay", "relay_N01", target=n["port"])
        status_n, rejection = send(rn["port"], original)
        save(run / "N01-response.json", dict(http_status=status_n, decision=rejection))
        mutated = (run / "tampering_adapter/001-egress.bin").read_bytes()
        check("N01_tampered_rejected_after_unchanged_relay", status_n == 422 and rejection["reason"] == "invalid_signature"
              and rejection["signature_checks"] == 1 and digest(mutated) != original_hash
              and (run / "tampering_adapter/001-ingress.bin").read_bytes() == original,
              dict(original_sha256=original_hash, modified_sha256=digest(mutated), rejection=rejection))
        check("tampering_adapter_preserves_original_signature", loads(original)["signature"] == loads(mutated)["signature"])
        # Stop producer and first verifier; a refused loopback endpoint is simulation evidence only.
        stop(producer)
        try:
            with socket.create_connection(("127.0.0.1", a["port"]), timeout=1):
                unavailable = False
        except OSError as ex:
            unavailable = True
            save(run / "B02-producer-unavailable.json", dict(simulated=True, endpoint=a, error=str(ex),
                 terminated_process_returncode=producer.returncode, physical_power_off_observed=False))
        stop(verifier)
        verifier2, b2 = launch("verifier", "verifier_after_restart", trust=trust_path)
        # Re-convey original bytes through another frozen relay instance to the new B.
        relay2, r2 = launch("relay", "relay_B02", target=b2["port"])
        status2, decision2 = send(r2["port"], original)
        save(run / "B02-response.json", dict(http_status=status2, decision=decision2, old_process=b, new_process=b2))
        check("B02_producer_offline_fresh_verifier_simulation", checks[1]["status"] == "PASS" and unavailable
              and b["pid"] != b2["pid"] and b["process_instance"] != b2["process_instance"]
              and decision2["accepted"] and decision2["signature_checks"] == 1
              and (run / "verifier_after_restart/001-ingress.bin").read_bytes() == original,
              dict(old_pid=b["pid"], new_pid=b2["pid"], fresh_signature_checks=decision2["signature_checks"]))
        status3, repeated = send(r2["port"], original)
        check("same_artifact_repeated_fresh_signature_check", status3 == 200 and repeated["signature_checks"] == 1)
        check("valid_ed25519", verify(original, trust)["accepted"])
        check("modified_signed_field", verify(mutated, trust)["reason"] == "invalid_signature")
        unknown = copy.deepcopy(loads(original)); unknown["event"]["key_id"] = "sha256:" + "0" * 64
        check("unknown_key_rejected", verify(canonical_bytes(unknown), trust)["reason"] == "untrusted_producer_key_binding")
        mismatch = copy.deepcopy(loads(original)); mismatch["event"]["producer_id"] = "DOMAIN_B"
        check("producer_key_mismatch_rejected", verify(canonical_bytes(mismatch), trust)["reason"] == "untrusted_producer_key_binding")
        malformed = [b"{", b"[]", b"null", b'{"event":{},"event":{}}', b"\xff", b"{}", b"x" * 65537]
        for name, value in [("version", True), ("outcome", 1), ("artifact_id", "invalid"), ("extra", "field")]:
            obj = copy.deepcopy(loads(original)); obj["event"][name] = value
            malformed.append(canonical_bytes(obj))
        malformed.extend([original + b"\n", original.replace(b'"version":1', b'"version":NaN')])
        check("malformed_artifacts_rejected", all(not verify(raw, trust)["accepted"] for raw in malformed), len(malformed))
        e = loads(original)["event"]
        check("deterministic_canonical_encoding", canonical_bytes(e) == canonical_bytes(dict(reversed(list(e.items()))))
              and produce(key, e["artifact_id"]) == original)
        check("unique_artifact_ids_supported", len({loads(produce(key))["event"]["artifact_id"] for _ in range(100)}) == 100)
        other = Ed25519PrivateKey.generate()
        import base64
        wrong_key = copy.deepcopy(loads(original))
        wrong_key["signature"] = base64.urlsafe_b64encode(other.sign(signed_bytes(wrong_key["event"]))).rstrip(b"=").decode()
        check("wrong_private_key_signature_rejected", verify(canonical_bytes(wrong_key), trust)["reason"] == "invalid_signature")
        bad = copy.deepcopy(loads(original)); bad["signature"] = "A" * 86
        check("invalid_signature_bytes_rejected", verify(canonical_bytes(bad), trust)["reason"] == "invalid_signature")
        criteria = copy.deepcopy(loads(original))["event"]; criteria["outcome"] = "FAILURE"
        criteria_raw = canonical_bytes(dict(event=criteria, signature=base64.urlsafe_b64encode(key.sign(signed_bytes(criteria))).rstrip(b"=").decode()))
        check("valid_signature_local_criteria_rejected", verify(criteria_raw, trust)["reason"] == "local_criteria_rejected")
        before_trust = canonical_bytes(trust)
        with patch("socket.socket", side_effect=AssertionError("network forbidden")), patch("builtins.open", side_effect=AssertionError("file access forbidden")):
            decisions = [verify(original, trust) for _ in range(3)]
        check("no_history_no_producer_network_no_evidence_read", all(d["accepted"] and d["signature_checks"] == 1 for d in decisions)
              and before_trust == canonical_bytes(trust))
        tree = ast.parse((ROOT / "src/artifact.py").read_text())
        imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)] + [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        check("verification_has_no_execution_import_or_command_client", not any("esp" in name.lower() or name in {"socket", "subprocess", "pathlib"} for name in imports), imports)
        check("original_sources_and_reference_unchanged", all(digest(Path(r["source_path"]).read_bytes()) == r["sha256"]
              == digest((ROOT / r["copy_path"]).read_bytes()) for r in inventory["files"]))
        relay_records = [json.loads(line) for line in (run / "relay/relay.jsonl").read_text().splitlines()]
        check("relay_transport_observations_match_external_bytes", any(x["transport_result"] == "response_forwarded"
              and x["ingress_body_sha256"] == original_hash and x["egress_body_sha256"] == original_hash for x in relay_records))
        check("saved_evidence_matches_responses", json.loads((run / "verifier_before/001-decision.json").read_bytes()) == decision
              and json.loads((run / "verifier_before/002-decision.json").read_bytes()) == rejection
              and json.loads((run / "verifier_after_restart/001-decision.json").read_bytes()) == decision2)
    except Exception as ex:
        import traceback
        error = traceback.format_exc()
        (run / "HARNESS_ERROR.txt").write_text(error, encoding="utf-8")
        check("harness_completed", False, str(ex))
    finally:
        for proc in reversed(processes):
            stop(proc)
        for handle in handles:
            handle.close()
    passed = sum(c["status"] == "PASS" for c in checks)
    result = dict(mode="OFFLINE_LOOPBACK_SIMULATION_ONLY", utc=datetime.now(timezone.utc).isoformat(),
                  python=sys.version, platform=platform.platform(), cryptography=cryptography.__version__,
                  passed=passed, failed=len(checks)-passed, checks=checks,
                  status="MD001_LOCAL_BUILD_VALIDATED_NOT_DEPLOYED" if passed == len(checks) and not error else "LOCAL_VALIDATION_FAILED",
                  physical_network_scored=False, physical_esp_completed=False)
    save(run / "RESULTS.json", result)
    files = sorted(p for p in run.rglob("*") if p.is_file())
    (run / "SHA256SUMS.txt").write_text("".join(f"{digest(p.read_bytes())}  {p.relative_to(run).as_posix()}\n" for p in files), encoding="utf-8")
    print(json.dumps(dict(run=str(run), passed=passed, failed=len(checks)-passed, status=result["status"]), indent=2))
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
