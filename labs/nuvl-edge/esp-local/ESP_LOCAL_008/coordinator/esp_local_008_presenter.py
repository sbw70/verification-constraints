#!/usr/bin/env python3
"""
ESP-LOCAL-008 directionality presenter.

Presents ONE frozen provider-signed authority to ONE endpoint, captures the
verdict, and (optionally) brackets the presentation in an independent witness
run so physical evidence lines up with the TCP-level evidence.

ESP-LOCAL-008 tests explicit directionality enforcement: a valid
provider-signed authority scoped to one endpoint is rejected by another
endpoint at a dedicated target-identity gate BEFORE persistent authority
state is consulted or modified.

The scored matrix (run in this order):

  S1        --authority X --target servo2 --expect target_id_mismatch --live
            AUTH-X (esp32-xiao-servo-01) presented to Servo #2.
            Must be denied at the target gate: reason "target_id_mismatch",
            NOT "authority_state_mismatch", NOT "semantic_denied". Servo #2
            does not move, and its AUTH-Y stays UNSPENT (verify by state
            readback afterward) -- the gate refused before touching state.

  C2        --authority Y --target servo2 --expect accepted --live
            AUTH-Y (esp32-xiao-servo-02) presented to Servo #2.
            Positive control: accepted, Servo #2 moves, AUTH-Y spent.
            Proves Servo #2 was live and capable when it refused AUTH-X.

  POST-S1   --authority X --target servo1 --expect accepted --live
            AUTH-X presented to Servo #1 (its correct target).
            Accepted, Servo #1 moves, AUTH-X spent. Proves AUTH-X was valid
            all along -- wrong target for Servo #2 was the only reason it
            was refused there.

Run S1 before C2 so Servo #2 still holds an UNSPENT AUTH-Y at the moment it
refuses AUTH-X (closes the "endpoint was just out of gas" objection).

Safety:
  - Default is a REHEARSAL: sends a deliberately malformed line. The endpoint
    rejects it before the target gate or any state access, so a rehearsal
    can never spend an authority and never triggers a servo. Use it to prove
    connectivity, response capture, and witness bracketing for free.
  - --live sends the REAL authority bytes and requires you to type back the
    authority_id this script computes from the request file itself. There is
    no auto-fire of the whole matrix: one authority, one target, per run.
  - "accepted" over TCP is NOT a scored PASS on its own. A scored acceptance
    also needs the endpoint's own serial log (008_ACCEPT_EXECUTED + one
    PWM_COMMAND_BEGIN/END), one witness servo-like burst, and a post-run
    nuvl_state readback showing SPENT. A scored denial needs the endpoint
    log to show the denial at the target gate and the witness to show ZERO
    bursts. Capture those before rebooting or running anything else.

Usage:
  # harmless pipeline/witness check, spends nothing, no servo motion:
  python esp_local_008_presenter.py --run-id RH001 --authority X --target servo2

  # scored S1 (non-spending denial at the gate):
  python esp_local_008_presenter.py --run-id S1 --authority X --target servo2 \
      --expect target_id_mismatch --live
"""

import argparse
import base64
import hashlib
import json
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ----------------------------------------------------------------------
# Endpoint identities (network identity only; COM ports are not test
# identity and are deliberately absent). Fill SERVO2_HOST once Servo #2 is
# flashed and reports its 008_WIFI_GOT_IP, or pass --host/--port to override.
# ----------------------------------------------------------------------

TARGETS = {
    "servo1": {
        "host": "192.168.0.81",      # COM14 (MAC 11:e8), confirmed live from 008_WIFI_GOT_IP
        "port": 19081,
        "identity": "esp32-xiao-servo-01",
    },
    "servo2": {
        "host": "192.168.0.186",     # COM15 (MAC 10:a4), confirmed live from 008_WIFI_GOT_IP
        "port": 19081,
        "identity": "esp32-xiao-servo-02",
    },
}

# Frozen authority ground truth (SHA-256 of canonical bytes). The script also
# recomputes the id from the request file; these are only for a sanity print.
FROZEN = {
    "X": {
        "scope": "esp32-xiao-servo-01",
        "authority_id": "a1eb22c7b5530b644302f03c3d3a75ef5ebc115ecdca7028809f4cb1c5da104c",
    },
    "Y": {
        "scope": "esp32-xiao-servo-02",
        "authority_id": "5d2b8162de0923fcc08d39d7cf8715a37e25bf548c0344e802f3cfbc91b16fa9",
    },
    "X2": {
        "scope": "esp32-xiao-servo-01",
        "authority_id": "0acbe0f43890299440c0f85b0b8a2c27e5cc38268a746f9bf296b765949f2710",
    },
    "Y2": {
        "scope": "esp32-xiao-servo-02",
        "authority_id": "3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519",
    },
    "X3": {
        "scope": "esp32-xiao-servo-01",
        "authority_id": "5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef",
    },
    "Y3": {
        "scope": "esp32-xiao-servo-02",
        "authority_id": "2c7ded33c6d5cc142c6f4ba91c04add1803fc361d00f34b9d288b3bb67f711fa",
    },
}

WITNESS_HOST_DEFAULT = "192.168.0.216"
WITNESS_CONTROL_PORT = 19072
WITNESS_MAGIC = "W007"   # 008 witness is an unmodified 007 RMT witness copy

REHEARSAL_LINE = b'{"authority_b64":"UkVIRUFSU0FM","signature_b64":"UkVIRUFSU0FM"}\n'


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


# ----------------------------------------------------------------------
# Request bytes
# ----------------------------------------------------------------------

def request_file_for(authority: str) -> Path:
    base = Path(__file__).resolve().parent.parent / "provider" / "authorities"
    return base / f"ESP_LOCAL_008_AUTH_{authority}_REQUEST.json"


def load_request_line(path: Path) -> bytes:
    if not path.exists():
        raise SystemExit(f"REFUSING TO PROCEED: request file not found: {path}")
    raw = path.read_bytes().strip()
    # Must be the exact wire shape the endpoint's literal parser accepts.
    # Do not re-serialize -- key order/whitespace would break the match and
    # the signature.
    if not (raw.startswith(b'{"authority_b64":"') and raw.endswith(b'}')):
        raise SystemExit(
            f"REFUSING TO PROCEED: {path} is not a frozen ESP_LOCAL_008 "
            f"request line. Not touching the network."
        )
    return raw + b"\n"


def compute_authority_id(request_line: bytes):
    """Hash the authority the same way the endpoint does -- sha256 of the
    exact canonical bytes decoded from the request itself. Ground truth
    computed here, not transcribed from anywhere."""
    obj = json.loads(request_line.decode("utf-8"))
    canonical = base64.b64decode(obj["authority_b64"])
    authority_id = hashlib.sha256(canonical).hexdigest()
    decoded = json.loads(canonical.decode("utf-8"))
    return authority_id, decoded


# ----------------------------------------------------------------------
# Witness UDP control (independent RMT capture witness; authority role NONE)
# ----------------------------------------------------------------------

class Witness:
    def __init__(self, host, port, timeout=3.0):
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

    def _send_recv(self, command, retries=3):
        payload = f"{WITNESS_MAGIC} {command}".encode()
        last_err = None
        for _ in range(retries):
            try:
                self.sock.sendto(payload, self.addr)
                data, _ = self.sock.recvfrom(2048)
                return json.loads(data.decode())
            except socket.timeout as exc:
                last_err = exc
                continue
        return {"type": "no_reply", "error": str(last_err), "command": command}

    def status(self):
        return self._send_recv("STATUS")

    def start(self, run_id, utc_anchor):
        return self._send_recv(f"START {run_id} {utc_anchor}")

    def mark(self, text):
        return self._send_recv(f"MARK {text}")

    def stop(self, utc_anchor):
        return self._send_recv(f"STOP {utc_anchor}")


# ----------------------------------------------------------------------
# Single presentation
# ----------------------------------------------------------------------

def recv_line(sock, timeout):
    sock.settimeout(timeout)
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    line, _, _ = buf.partition(b"\n")
    return line


def present(host, port, request_line, connect_timeout, response_timeout):
    result = {
        "host": host, "port": port,
        "t_connect_start": None, "t_connect_done": None,
        "t_send": None, "t_response": None,
        "response_line": None, "parsed_response": None,
        "error": None,
    }
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(connect_timeout)
        result["t_connect_start"] = time.time()
        sock.connect((host, port))
        result["t_connect_done"] = time.time()

        sock.settimeout(response_timeout)
        result["t_send"] = time.time()
        sock.sendall(request_line)

        resp = recv_line(sock, response_timeout)
        result["t_response"] = time.time()
        result["response_line"] = resp.decode(errors="replace")
        try:
            result["parsed_response"] = json.loads(result["response_line"])
        except Exception:
            result["parsed_response"] = None
        sock.close()
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--run-id", required=True, help="Evidence/witness run id (<=20 chars)")
    ap.add_argument("--authority", required=True, choices=["X", "Y", "X2", "Y2", "X3", "Y3"],
                    help="Which frozen authority to present")
    ap.add_argument("--target", required=True, choices=["servo1", "servo2"],
                    help="Which endpoint to present to")
    ap.add_argument("--host", default=None, help="Override target host (else from TARGETS)")
    ap.add_argument("--port", type=int, default=None, help="Override target port (else from TARGETS)")
    ap.add_argument("--expect", default=None,
                    help='Expected verdict: "accepted" or a denial reason '
                         '(e.g. target_id_mismatch). Scored against actual.')
    ap.add_argument("--live", action="store_true",
                    help="Send the REAL authority bytes. Default is a harmless rehearsal.")
    ap.add_argument("--connect-timeout", type=float, default=5.0)
    ap.add_argument("--response-timeout", type=float, default=20.0)  # > endpoint 15s SO_RCVTIMEO
    ap.add_argument("--evidence-dir", type=Path, default=Path.cwd())
    ap.add_argument("--skip-witness", action="store_true",
                    help="Do not talk to the witness (endpoint-only)")
    ap.add_argument("--witness-host", default=WITNESS_HOST_DEFAULT)
    args = ap.parse_args()

    tgt = dict(TARGETS[args.target])
    host = args.host or tgt["host"]
    port = args.port or tgt["port"]
    if host.endswith("_TBD"):
        raise SystemExit(
            f"Target {args.target} host is not set yet. Flash Servo #2, note its "
            f"008_WIFI_GOT_IP, then set TARGETS['{args.target}']['host'] or pass --host."
        )

    evidence_path = args.evidence_dir / f"ESP_LOCAL_008_PRESENTER_{args.run_id}_{int(time.time())}.json"
    if evidence_path.exists():
        raise SystemExit(f"Evidence file exists, refusing to overwrite: {evidence_path}")

    req_path = request_file_for(args.authority)

    if args.live:
        request_line = load_request_line(req_path)
        authority_id, decoded = compute_authority_id(request_line)
        frozen = FROZEN[args.authority]
        print("=" * 72)
        print("LIVE MODE -- presenting a real authority.")
        print(f"authority        : AUTH-{args.authority}  (scope {frozen['scope']})")
        print(f"request file     : {req_path}")
        print(f"decoded authority: {json.dumps(decoded)}")
        print(f"authority_id     : {authority_id}")
        print(f"frozen id (check): {frozen['authority_id']}  "
              f"[{'MATCH' if authority_id == frozen['authority_id'] else 'MISMATCH'}]")
        print(f"target           : {args.target}  ({tgt['identity']})  {host}:{port}")
        print(f"expected verdict : {args.expect}")
        print("=" * 72)
        if authority_id != frozen["authority_id"]:
            raise SystemExit("Computed authority_id does not match the frozen id. Aborting.")
        typed = input("Type the authority_id above, exactly, to proceed: ").strip()
        if typed != authority_id:
            raise SystemExit("Authority id did not match. Aborting. Nothing was sent.")
    else:
        request_line = REHEARSAL_LINE
        authority_id, decoded = None, None
        print("Rehearsal mode: sending a deliberately malformed line. The endpoint "
              "denies it before the target gate or any state access -- no spend, no "
              "servo motion. Pass --live for the real presentation.")

    # --- optional witness bracket ---
    witness = None
    w_before = w_start = w_stop = w_after = None
    if not args.skip_witness:
        witness = Witness(args.witness_host, WITNESS_CONTROL_PORT)
        w_before = witness.status()
        print(f"witness status (pre) : {w_before}")
        w_start = witness.start(args.run_id, utc_now_iso())
        print(f"witness start        : {w_start}")

    # --- present ---
    result = present(host, port, request_line, args.connect_timeout, args.response_timeout)

    if witness is not None:
        witness.mark("presentation_complete")
        time.sleep(0.25)
        w_stop = witness.stop(utc_now_iso())
        print(f"witness stop         : {w_stop}")
        w_after = witness.status()
        print(f"witness status (post): {w_after}")

    # --- verdict + scoring ---
    parsed = result["parsed_response"]
    status = parsed.get("status") if parsed else None
    reason = parsed.get("reason") if parsed else None

    print("-" * 72)
    if result["error"]:
        print(f"ERROR: {result['error']}")
    else:
        print(f"response: status={status} reason={reason}")

    score = None
    if args.expect is not None and parsed is not None:
        if args.expect == "accepted":
            score = (status == "accepted")
        else:
            score = (status == "denied" and reason == args.expect)
        print(f"expected: {args.expect}   ->  {'MATCH' if score else 'MISMATCH'}")
    print("-" * 72)

    if args.live and status == "accepted":
        print("REMINDER: TCP 'accepted' is not the scored PASS. Confirm in the endpoint "
              "serial log: 008_TARGET_ID_MATCH, 008_AUTHORITY_UNSPENT_PASS, one "
              "008_PWM_COMMAND_BEGIN/END, 008_ACCEPT_EXECUTED; one witness servo-like "
              "burst; then reread nuvl_state -> SPENT. Do it before rebooting.")
    if args.live and status == "denied":
        print("REMINDER: confirm in the endpoint serial log that the denial is at the "
              f"target gate (008_DENY_{ (reason or '').upper() }) with NO state access "
              "after it, the witness shows ZERO servo-like bursts, and (for S1) the "
              "target's own authority is still UNSPENT on readback.")

    evidence = {
        "test_id": "ESP_LOCAL_008",
        "run_id": args.run_id,
        "live": args.live,
        "authority_label": f"AUTH-{args.authority}",
        "authority_id": authority_id,
        "target": {"label": args.target, "identity": tgt["identity"], "host": host, "port": port},
        "expected_verdict": args.expect,
        "response": {"status": status, "reason": reason, "line": result["response_line"]},
        "scored_match": score,
        "error": result["error"],
        "timing": {
            "connect_start": result["t_connect_start"],
            "connect_done": result["t_connect_done"],
            "send": result["t_send"],
            "response": result["t_response"],
        },
        "witness": None if witness is None else {
            "host": args.witness_host, "port": WITNESS_CONTROL_PORT,
            "status_before": w_before, "start": w_start,
            "stop": w_stop, "status_after": w_after,
        },
        "recorded_at_utc": utc_now_iso(),
    }

    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, indent=2))
    print(f"evidence written: {evidence_path}")


if __name__ == "__main__":
    main()
