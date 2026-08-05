#!/usr/bin/env python3

from pathlib import Path
import hashlib
import json
import urllib.request


PI_BASE = "http://192.168.0.94:8092"

ARTIFACT_PATH = (
    Path(__file__).resolve().parent
    / "wp2_t1_temp_fsync_artifact.json"
)


print("WP2_T1_REPLAY_CHECK_START")


with urllib.request.urlopen(
    PI_BASE + "/provider-status",
    timeout=5,
) as response:
    provider_status = json.loads(
        response.read().decode("utf-8")
    )


provider_offline = (
    provider_status.get("provider_available") is False
)

print(
    "PROVIDER_STATUS available={} result={}".format(
        provider_status.get("provider_available"),
        "PASS" if provider_offline else "FAIL",
    )
)

if not provider_offline:
    raise RuntimeError(
        "Provider must remain offline"
    )


record = json.loads(
    ARTIFACT_PATH.read_text(encoding="utf-8")
)

issue_request = record["issue_request"]
package = record["package"]

artifact = package.get("artifact") or {}
artifact_id = artifact.get("artifact_id")


spend_request = {
    "device_id": issue_request["device_id"],
    "context": issue_request["context"],
    "requested_action": issue_request["requested_action"],
    "nonce": issue_request["nonce"],
}


payload = json.dumps(
    {
        "package": package,
        "spend_request": spend_request,
    },
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")


request = urllib.request.Request(
    PI_BASE + "/spend",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)


with urllib.request.urlopen(
    request,
    timeout=10,
) as response:
    result = json.loads(
        response.read().decode("utf-8")
    )


artifact_preserved = ARTIFACT_PATH.exists()

artifact_hash = hashlib.sha256(
    ARTIFACT_PATH.read_bytes()
).hexdigest()


passed = (
    provider_offline
    and result.get("decision") == "denied"
    and result.get("reason") == "replay_detected"
    and result.get("provider_verified") is True
    and result.get("provider_contacted_for_spend") is False
    and result.get("artifact_id") == artifact_id
    and artifact_preserved
)


print("artifact_id={}".format(artifact_id))
print("decision={}".format(result.get("decision")))
print("reason={}".format(result.get("reason")))
print(
    "provider_verified={}".format(
        result.get("provider_verified")
    )
)
print(
    "provider_contacted_for_spend={}".format(
        result.get("provider_contacted_for_spend")
    )
)
print(
    "artifact_file_preserved={}".format(
        artifact_preserved
    )
)
print("artifact_sha256={}".format(artifact_hash))
print("result={}".format("PASS" if passed else "FAIL"))
print("WP2_T1_REPLAY_CHECK_END")


if not passed:
    raise SystemExit(1)
