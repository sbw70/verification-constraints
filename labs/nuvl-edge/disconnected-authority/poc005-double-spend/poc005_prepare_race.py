#!/usr/bin/env python3
import json
import secrets
import urllib.request
from pathlib import Path

PI_BASE = "http://192.168.8.234:8089"
OUTPUT_PATH = Path(__file__).resolve().parent / "poc005_race_artifact.json"

issue_request = {
    "device_id": "esp32-s3-poc005",
    "context": "field_led_demo",
    "requested_action": "accept",
    "nonce": secrets.token_hex(16),
}

body = json.dumps(
    issue_request,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")

request = urllib.request.Request(
    PI_BASE + "/issue",
    data=body,
    method="POST",
    headers={"Content-Type": "application/json"},
)

print("POC005_PREPARE_START")

with urllib.request.urlopen(request, timeout=10) as response:
    result = json.loads(response.read().decode("utf-8"))

passed = (
    result.get("decision") == "issued"
    and result.get("reason") == "provider_signed_bounded_artifact"
    and result.get("provider_verified") is True
    and isinstance(result.get("package"), dict)
)

artifact = (result.get("package") or {}).get("artifact") or {}
artifact_id = artifact.get("artifact_id")

record = {
    "issue_request": issue_request,
    "package": result.get("package"),
}

if passed:
    OUTPUT_PATH.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )

print(
    "ISSUE expected=issued/provider_signed_bounded_artifact/True "
    "actual={}/{}/{} result={}".format(
        result.get("decision"),
        result.get("reason"),
        result.get("provider_verified"),
        "PASS" if passed else "FAIL",
    )
)
print("artifact_id=", artifact_id)
print("artifact_expiry=", artifact.get("expiry"))
print("artifact_file=", OUTPUT_PATH.name)
print("artifact_file_bytes=", OUTPUT_PATH.stat().st_size if passed else 0)
print("STOP_PROVIDER_BEFORE_RACE=True")
print("POC005_PREPARE_END")

if not passed:
    raise SystemExit(1)
