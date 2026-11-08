"""Run sequential offline validation and write a reviewable result/inventory."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import unittest

import routes
import test_offline
import verify_provider_sources

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-root", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="New directory; never overwritten")
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=False)
    provenance = verify_provider_sources.verify(args.historical_root)
    routes.validate_pair(ROOT / "configs/hub_a.json", ROOT / "configs/hub_b.json")
    log = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_offline)
    started = datetime.now(timezone.utc).isoformat()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    (output / "offline_tests.txt").write_text(log.getvalue(), encoding="utf-8", newline="\n")
    (output / "provider_source_identity.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    report = {"status": "LOCAL_BUILD_VALIDATED_NOT_DEPLOYED" if result.wasSuccessful() else "LOCAL_BUILD_VALIDATION_FAILED",
        "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "submissions": "SEQUENTIAL_LOOPBACK_MOCKS_ONLY",
        "hub_a_timeout_seconds": 15, "hub_b_timeout_seconds": 10,
        "actual_provider_keys_generated": False, "mock_signing_keys_generated": False,
        "lab_hosts_contacted": False, "scored_transactions_executed": False,
        "deployed": False, "published": False,
        "configuration_sha256": {p.name: sha(p) for p in sorted((ROOT / "configs").glob("*.json"))},
        "source_sha256": {p.name: sha(p) for p in sorted(ROOT.glob("*.py"))},
        "provider_source_identity": provenance,
        "pending": ["STOP 1 approval", "Authorized host/Python/process/listener/autostart inventory",
                    "Provider-host key generation and sanctioned new state", "Live endpoint configuration and new hashes",
                    "Observer trust, independent ingress capture and signed-denial freshness gates",
                    "Authorized rehearsal latency measurement; STOP at approach to 8 seconds",
                    "STOP 2 immediately before scored Hub A termination"],
        "initial_validation_attempt": "Windows sandbox denied OS temp-file writes; rerun with explicit execution approval passed before final recorded run"}
    (output / "LOCAL_VALIDATION.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    # Inventory covers the new package, including validation evidence; no historical writes.
    manifest = ROOT / "SHA256SUMS.txt"
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and p != manifest
                   and "__pycache__" not in p.parts)
    manifest.write_text("".join(f"{sha(p)}  {p.relative_to(ROOT).as_posix()}\n" for p in files), encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "tests": result.testsRun,
                      "failures": len(result.failures), "errors": len(result.errors),
                      "inventory_files": len(files), "inventory_sha256": sha(manifest)}))
    if not result.wasSuccessful():
        print(log.getvalue())
        raise SystemExit(1)


if __name__ == "__main__":
    main()
