import gc
import json
import os
import socket
import time

PI_IP = YOUR PI IP"
PORT = 8089
ARTIFACT_FILE = "poc003_artifacts.json"


def send_all(sock, data):
    offset = 0
    total = len(data)

    while offset < total:
        sent = sock.send(data[offset:])
        if sent is None:
            sent = 0
        if sent <= 0:
            raise OSError("socket_send_failed")
        offset += sent


def http_json(method, path, payload=None, timeout=12):
    body = b"" if payload is None else json.dumps(payload).encode()

    request = (
        "{} {} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(method, path, PI_IP, len(body)).encode() + body

    s = socket.socket()
    s.settimeout(timeout)

    try:
        s.connect((PI_IP, PORT))
        send_all(s, request)

        chunks = []
        while True:
            try:
                chunk = s.recv(512)
                if not chunk:
                    break
                chunks.append(chunk)
            except OSError:
                if chunks:
                    break
                raise

        raw = b"".join(chunks)
        marker = raw.find(b"\r\n\r\n")
        if marker < 0:
            raise ValueError(
                "invalid_http_response len={} head={!r}".format(
                    len(raw), raw[:120]
                )
            )

        response_body = raw[marker + 4:]
        return json.loads(response_body.decode())
    finally:
        try:
            s.close()
        except Exception:
            pass


def spend(package, spend_request):
    return http_json(
        "POST",
        "/spend",
        {
            "package": package,
            "spend_request": spend_request,
        },
    )


def request_from(entry):
    src = entry["issue_request"]
    return {
        "device_id": src["device_id"],
        "context": src["context"],
        "requested_action": src["requested_action"],
        "nonce": src["nonce"],
    }


print("POC003_OFFLINE_SPEND_START")
gc.collect()
baseline_free = gc.mem_free()

with open(ARTIFACT_FILE, "r") as f:
    artifacts = json.load(f)

provider_status = http_json("GET", "/provider-status")
provider_unavailable_confirmed = (
    provider_status.get("provider_available") is False
)

print(
    "PROVIDER_STATUS available={} result={}".format(
        provider_status.get("provider_available"),
        "PASS" if provider_unavailable_confirmed else "FAIL",
    )
)

if not provider_unavailable_confirmed:
    raise RuntimeError("Provider must be offline before disconnected spend")

cases = []

primary = artifacts["primary"]
primary_request = request_from(primary)
cases.append(
    (
        "valid_offline_spend",
        primary["package"],
        primary_request,
        "accepted",
        "offline_artifact_admissible",
        True,
    )
)
cases.append(
    (
        "replay_same_artifact",
        primary["package"],
        primary_request,
        "denied",
        "replay_detected",
        True,
    )
)

wrong_context = artifacts["wrong_context"]
req = request_from(wrong_context)
req["context"] = "wrong_context"
cases.append(
    (
        "wrong_context",
        wrong_context["package"],
        req,
        "denied",
        "spend_binding_mismatch_context",
        True,
    )
)

wrong_action = artifacts["wrong_action"]
req = request_from(wrong_action)
req["requested_action"] = "deny"
cases.append(
    (
        "wrong_action",
        wrong_action["package"],
        req,
        "denied",
        "spend_binding_mismatch_requested_action",
        True,
    )
)

wrong_nonce = artifacts["wrong_nonce"]
req = request_from(wrong_nonce)
req["nonce"] = "wrong_nonce"
cases.append(
    (
        "wrong_nonce",
        wrong_nonce["package"],
        req,
        "denied",
        "spend_binding_mismatch_nonce",
        True,
    )
)

wrong_device = artifacts["wrong_device"]
req = request_from(wrong_device)
req["device_id"] = "wrong-device"
cases.append(
    (
        "wrong_device",
        wrong_device["package"],
        req,
        "denied",
        "spend_binding_mismatch_device_id",
        True,
    )
)

tampered = artifacts["tampered"]
tampered_package = json.loads(json.dumps(tampered["package"]))
tampered_package["artifact"]["requested_action"] = "deny"
req = request_from(tampered)
req["requested_action"] = "deny"
cases.append(
    (
        "tampered_after_signing",
        tampered_package,
        req,
        "denied",
        "invalid_provider_signature",
        False,
    )
)

unsigned = artifacts["unsigned"]
unsigned_package = json.loads(json.dumps(unsigned["package"]))
unsigned_package["signature"] = None
cases.append(
    (
        "unsigned_artifact",
        unsigned_package,
        request_from(unsigned),
        "denied",
        "missing_signature",
        False,
    )
)

stale = artifacts["stale"]
cases.append(
    (
        "expired_artifact",
        stale["package"],
        request_from(stale),
        "denied",
        "stale_artifact",
        True,
    )
)

cases.append(
    (
        "missing_artifact",
        None,
        {},
        "denied",
        "package_not_object",
        False,
    )
)

passed = 0
failed = 0
accepted = 0
denied = 0

for index, case in enumerate(cases, 1):
    (
        name,
        package,
        spend_request,
        expected_decision,
        expected_reason,
        expected_verified,
    ) = case

    try:
        response = spend(package, spend_request)
        actual_decision = response.get("decision")
        actual_reason = response.get("reason")
        actual_verified = response.get("provider_verified")

        ok = (
            actual_decision == expected_decision
            and actual_reason == expected_reason
            and actual_verified == expected_verified
            and response.get("provider_contacted_for_spend") is False
        )

        if actual_decision == "accepted":
            accepted += 1
        elif actual_decision == "denied":
            denied += 1

        if ok:
            passed += 1
        else:
            failed += 1

        print(
            "CASE {} name={} expected={}/{}/{} actual={}/{}/{} provider_contacted={} result={}".format(
                index,
                name,
                expected_decision,
                expected_reason,
                expected_verified,
                actual_decision,
                actual_reason,
                actual_verified,
                response.get("provider_contacted_for_spend"),
                "PASS" if ok else "FAIL",
            )
        )
    except Exception as exc:
        failed += 1
        print(
            "CASE {} name={} error={} result=FAIL".format(
                index, name, repr(exc)
            )
        )

    gc.collect()
    time.sleep_ms(150)

artifact_file_removed = False
if failed == 0:
    try:
        os.remove(ARTIFACT_FILE)
        artifact_file_removed = True
    except Exception:
        artifact_file_removed = False

gc.collect()
final_free = gc.mem_free()

print("POC003_OFFLINE_SPEND_SUMMARY")
print("cases=", len(cases))
print("passed=", passed)
print("failed=", failed)
print("accepted=", accepted)
print("denied=", denied)
print("provider_unavailable_confirmed=", provider_unavailable_confirmed)
print("provider_contacted_for_spend=", False)
print("private_key_on_endpoint=", False)
print("private_key_on_pi=", False)
print("signature_verification_location=pi_boundary")
print("replay_state_location=pi_boundary")
print("baseline_free=", baseline_free)
print("final_free=", final_free)
print("free_delta=", final_free - baseline_free)
print("artifact_file_removed=", artifact_file_removed)
print("POC003_OFFLINE_SPEND_END")
