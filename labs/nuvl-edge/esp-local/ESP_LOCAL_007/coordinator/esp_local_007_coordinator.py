#!/usr/bin/env python3
"""
ESP-LOCAL-007 coordinated multi-requester contention coordinator.

Talks to two independent parties over the network:

  - the endpoint under test (ESP_LOCAL_007_CONCURRENT.c on
    esp32-xiao-servo-02): TCP, one task per accepted connection.
    Each task sends READY, then blocks on one request line, then
    replies {"status":"accepted"|"denied", ...}. No lock guards
    process_request()/durable_consume() -- that's the thing being
    raced.

  - the independent witness (ESP_LOCAL_007_WITNESS_V3B.py on
    esp32-witness-007): UDP control channel, "W007 <CMD> ...".
    Authority role: NONE. It only watches GPIO5 electrically and
    timestamps what it sees; it never touches nuvl_state.

This script:
  1. connects N requester sockets to the endpoint
  2. waits for READY on every one of them
  3. releases identical request bytes to all N as close to
     simultaneously as a Python thread barrier allows
  4. captures every response independently, with timestamps
  5. wraps the release in a witness START/STOP run so the burst
     evidence lines up with the TCP-level evidence
  6. writes one machine-readable JSON evidence file

Safety:
  - Default mode is a REHEARSAL: it sends a deliberately malformed
    line instead of your real request. The endpoint rejects malformed
    envelopes before it ever reaches durable_consume(), so a rehearsal
    cannot spend a real authority no matter how many times you run it.
    This exercises 100% of the coordination path (connect, READY,
    barrier release, response capture, witness START/STOP) for free.
  - Sending the real request bytes requires --live AND typing back
    the authority_id this script computes from the request file
    itself (not from anything pasted anywhere). There is no retry
    of a live send within a single run: if the requester barrier
    doesn't complete because a socket didn't arm in time, the whole
    release aborts for everyone and nothing is sent.

Usage:
  # safe, does not touch AUTH1, exercises the full pipeline:
  python esp_local_007_coordinator.py --run-id RH001

  # the real, scored, one-shot race:
  python esp_local_007_coordinator.py --run-id R001 --live
"""

import argparse
import base64
import hashlib
import json
import socket
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


# ----------------------------------------------------------------------
# Fixed network identity (from ESP_LOCAL_007_CONCURRENT.c /
# ESP_LOCAL_007_WITNESS_V3B.py). COM ports are not test identity and are
# deliberately absent from this script.
# ----------------------------------------------------------------------

ENDPOINT_HOST = "192.168.0.186"
ENDPOINT_PORT = 19061

WITNESS_HOST = "192.168.0.216"
WITNESS_CONTROL_PORT = 19072
WITNESS_MAGIC = "W007"

DEFAULT_REQUEST_FILE = Path(__file__).resolve().parent.parent / "provider" / "ESP_LOCAL_007_AUTH2_REQUEST.json"

REHEARSAL_LINE = b'{"authority_b64":"UkVIRUFSU0FM","signature_b64":"UkVIRUFSU0FM"}\n'

# Exact bytes the 007 concurrent runtime sends unsolicited right after
# accept(), per client_request_task()/send_client_ready() in
# ESP_LOCAL_007_CONCURRENT.c. Anything else -- a denial line arriving late
# from a serialized listener, a timeout, a closed connection -- is not
# READY and must not be treated as an armed requester.
EXPECTED_READY_LINE = b'{"ready":true,"test":"ESP_LOCAL_007"}'
# Deliberately malformed base64 (not a multiple-of-4-safe real signature) --
# the endpoint's parse_relay_envelope()/strict_base64_decode() reject this
# before authority hashing or state lookup ever run. See
# ESP_LOCAL_007_CONCURRENT.c: process_request() -> "authority_base64_invalid"
# or similar, always before durable_consume().


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


# ----------------------------------------------------------------------
# Request bytes
# ----------------------------------------------------------------------

def load_request_line(path: Path) -> bytes:
    raw = path.read_bytes().strip()
    # Sanity: must be exactly the wire shape the endpoint's strict parser
    # accepts. We don't re-serialize it -- re-encoding JSON could reorder
    # keys or change whitespace and the endpoint's parser is a literal
    # prefix/middle/suffix match, not a general JSON parser.
    if not (raw.startswith(b'{"authority_b64":"') and raw.endswith(b'}')):
        raise SystemExit(
            f"REFUSING TO PROCEED: {path} does not look like a frozen "
            f"ESP_LOCAL_007 request line. Not touching the network."
        )
    return raw + b"\n"


def compute_authority_id(request_line: bytes) -> tuple[str, dict]:
    """Decode authority_b64 out of the frozen request and hash it the same
    way the endpoint does (sha256 of the exact canonical bytes), so the
    operator confirms against ground truth computed here -- not against
    any value transcribed in a handoff doc."""
    obj = json.loads(request_line.decode("utf-8"))
    canonical = base64.b64decode(obj["authority_b64"])
    authority_id = hashlib.sha256(canonical).hexdigest()
    decoded = json.loads(canonical.decode("utf-8"))
    return authority_id, decoded


# ----------------------------------------------------------------------
# Witness UDP control
# ----------------------------------------------------------------------

class Witness:
    def __init__(self, host, port, timeout=3.0):
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

    def _send_recv(self, command, retries=3):
        payload = f"{WITNESS_MAGIC} {command}".encode()
        last_err = None
        for attempt in range(retries):
            try:
                self.sock.sendto(payload, self.addr)
                data, _ = self.sock.recvfrom(2048)
                return json.loads(data.decode())
            except socket.timeout as exc:
                last_err = exc
                continue
        return {"type": "no_reply", "error": str(last_err), "command": command}

    def discover(self):
        return self._send_recv("DISCOVER")

    def status(self):
        return self._send_recv("STATUS")

    def start(self, run_id, utc_anchor):
        reply = self._send_recv(f"START {run_id} {utc_anchor}")
        # UDP ack can be lost even though START landed -- treat
        # run_already_active as success too (idempotent from our side).
        if reply.get("ok") is True:
            return reply
        if reply.get("detail") == "run_already_active":
            return reply
        return reply

    def mark(self, text):
        return self._send_recv(f"MARK {text}")

    def stop(self, utc_anchor):
        return self._send_recv(f"STOP {utc_anchor}")


# ----------------------------------------------------------------------
# Requester
# ----------------------------------------------------------------------

class RequesterResult:
    def __init__(self, index):
        self.index = index
        self.error = None
        self.t_connect_start = None
        self.t_connect_done = None
        self.t_ready_recv = None
        self.ready_line = None
        self.t_release_pre_send = None
        self.t_release_post_send = None
        self.t_response_recv = None
        self.response_line = None
        self.parsed_response = None

    def as_dict(self):
        d = self.__dict__.copy()
        return d


def requester_thread(
    index,
    request_line,
    barrier,
    result: RequesterResult,
    connect_timeout,
    response_timeout,
):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(connect_timeout)

        result.t_connect_start = time.time()
        sock.connect((ENDPOINT_HOST, ENDPOINT_PORT))
        result.t_connect_done = time.time()

        sock.settimeout(response_timeout)

        # READY comes unsolicited right after accept().
        ready = _recv_line(sock, response_timeout)
        result.t_ready_recv = time.time()
        result.ready_line = ready.decode(errors="replace")

        # Hard gate: this must be the exact concurrent-runtime READY
        # object, not a denial line, not a timeout artifact, not anything
        # else. A serialized (pre-007) listener sends no unsolicited READY
        # at all -- if a line shows up here that isn't READY, the endpoint
        # is not running the runtime this test requires, and no requester
        # may proceed to the release phase. Break the barrier for
        # everyone rather than let this requester wait on it.
        if ready != EXPECTED_READY_LINE:
            result.error = f"not_ready_aborting: got {result.ready_line!r}"
            try:
                barrier.abort()
            except Exception:
                pass
            sock.close()
            return

        # Hold here until every requester has READY in hand.
        try:
            barrier.wait(timeout=connect_timeout + response_timeout)
        except threading.BrokenBarrierError:
            if result.error is None:
                result.error = "barrier_broken_no_send"
            sock.close()
            return

        result.t_release_pre_send = time.perf_counter_ns()
        sock.sendall(request_line)
        result.t_release_post_send = time.perf_counter_ns()

        resp = _recv_line(sock, response_timeout)
        result.t_response_recv = time.time()
        result.response_line = resp.decode(errors="replace")
        try:
            result.parsed_response = json.loads(result.response_line)
        except Exception:
            result.parsed_response = None

        sock.close()

    except Exception as exc:
        result.error = f"{type(exc).__name__}: {exc}"
        try:
            barrier.abort()
        except Exception:
            pass


def _recv_line(sock, timeout):
    sock.settimeout(timeout)
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    line, _, _ = buf.partition(b"\n")
    return line


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True, help="Witness run id (letters/digits/-/_ only, <=20 chars)")
    ap.add_argument("--requesters", type=int, default=2, help="Number of concurrent requesters (default 2)")
    ap.add_argument("--request-file", type=Path, default=DEFAULT_REQUEST_FILE, help="Frozen provider request JSON")
    ap.add_argument("--live", action="store_true", help="Send the REAL request bytes. Default is a harmless rehearsal.")
    ap.add_argument("--connect-timeout", type=float, default=5.0)
    ap.add_argument("--response-timeout", type=float, default=20.0)  # > endpoint's own 15s SO_RCVTIMEO
    ap.add_argument("--evidence-dir", type=Path, default=Path.cwd())
    ap.add_argument("--skip-witness", action="store_true", help="Do not talk to the witness (endpoint-only rehearsal)")
    args = ap.parse_args()

    evidence_path = args.evidence_dir / f"ESP_LOCAL_007_COORDINATOR_{args.run_id}_{int(time.time())}.json"
    if evidence_path.exists():
        raise SystemExit(f"Evidence file already exists, refusing to overwrite: {evidence_path}")

    if args.live:
        request_line = load_request_line(args.request_file)
        authority_id, decoded = compute_authority_id(request_line)
        print("=" * 70)
        print("LIVE MODE -- this will present a real authority to the endpoint.")
        print(f"request file     : {args.request_file}")
        print(f"decoded authority: {json.dumps(decoded, indent=2)}")
        print(f"authority_id     : {authority_id}")
        print(f"requesters       : {args.requesters}")
        print(f"run id           : {args.run_id}")
        print("=" * 70)
        typed = input("Type the authority_id above, exactly, to proceed: ").strip()
        if typed != authority_id:
            raise SystemExit("Authority id did not match what was typed. Aborting. Nothing was sent.")
    else:
        request_line = REHEARSAL_LINE
        authority_id = None
        print("Rehearsal mode: sending a deliberately malformed line. "
              "The endpoint will deny it before touching persistent state. "
              "Pass --live to run the real, one-shot race.")

    witness = None
    witness_start_reply = None
    witness_stop_reply = None
    witness_status_before = None
    witness_status_after = None

    if not args.skip_witness:
        witness = Witness(WITNESS_HOST, WITNESS_CONTROL_PORT)
        witness_status_before = witness.status()
        print(f"witness status (pre)  : {witness_status_before}")

        start_anchor = utc_now_iso()
        witness_start_reply = witness.start(args.run_id, start_anchor)
        print(f"witness start reply   : {witness_start_reply}")
        if witness_start_reply.get("ok") is not True and witness_start_reply.get("detail") != "run_already_active":
            raise SystemExit(
                f"Witness refused to start run '{args.run_id}': {witness_start_reply}. "
                f"Aborting before touching the endpoint."
            )

    # --- arm all requesters, then release together ---
    n = args.requesters
    barrier = threading.Barrier(n)
    results = [RequesterResult(i) for i in range(n)]
    threads = [
        threading.Thread(
            target=requester_thread,
            args=(i, request_line, barrier, results[i], args.connect_timeout, args.response_timeout),
            daemon=True,
        )
        for i in range(n)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=args.connect_timeout + args.response_timeout + 5)

    if witness is not None:
        witness.mark("requesters_complete")
        stop_anchor = utc_now_iso()
        witness_stop_reply = witness.stop(stop_anchor)
        print(f"witness stop reply    : {witness_stop_reply}")
        witness_status_after = witness.status()
        print(f"witness status (post) : {witness_status_after}")

    # --- summarize ---
    accepted = [r for r in results if r.parsed_response and r.parsed_response.get("status") == "accepted"]
    denied = [r for r in results if r.parsed_response and r.parsed_response.get("status") == "denied"]
    broken = [r for r in results if r.error]

    send_timestamps = [r.t_release_pre_send for r in results if r.t_release_pre_send is not None]
    skew_ns = (max(send_timestamps) - min(send_timestamps)) if len(send_timestamps) >= 2 else None

    print("-" * 70)
    print(f"accepted: {len(accepted)}   denied: {len(denied)}   errored: {len(broken)}")
    for r in denied:
        print(f"  requester {r.index} denied: {r.parsed_response.get('reason')}")
    for r in broken:
        print(f"  requester {r.index} error: {r.error}")

    not_ready = [r for r in results if r.error and r.error.startswith("not_ready_aborting")]
    if not_ready:
        print("-" * 70)
        print(
            "ABORTED BEFORE RELEASE: at least one requester did not receive the "
            "concurrent-runtime READY object. The endpoint likely is not running "
            "ESP_LOCAL_007_CONCURRENT.c yet -- a serialized (006-style) listener "
            "sends no unsolicited READY, so any line arriving here is something "
            "else (often a delayed denial). Nothing was released. Build/flash the "
            "007 concurrent runtime before trying again."
        )

    if skew_ns is not None:
        print(f"release send-start skew across requesters: {skew_ns} ns")
    print("-" * 70)

    if args.live:
        print(
            "REMINDER: this script's 'accepted' count is TCP-level evidence only. "
            "Scored PASS/FAIL also requires: exactly one PWM_COMMAND_BEGIN/END/"
            "ACCEPT_EXECUTED in the endpoint's own serial log, exactly one witness "
            "servo-like burst, witness queue_drops == 0, and a final nuvl_state "
            "readback confirming SPENT. Capture the endpoint serial log and reread "
            "nuvl_state now, before rebooting or running anything else."
        )

    evidence = {
        "test_id": "ESP_LOCAL_007",
        "run_id": args.run_id,
        "live": args.live,
        "authority_id": authority_id,
        "endpoint": {"host": ENDPOINT_HOST, "port": ENDPOINT_PORT},
        "witness": {"host": WITNESS_HOST, "port": WITNESS_CONTROL_PORT} if witness else None,
        "witness_status_before": witness_status_before,
        "witness_start_reply": witness_start_reply,
        "witness_stop_reply": witness_stop_reply,
        "witness_status_after": witness_status_after,
        "requesters": [r.as_dict() for r in results],
        "summary": {
            "accepted_count": len(accepted),
            "denied_count": len(denied),
            "error_count": len(broken),
            "denied_reasons": [r.parsed_response.get("reason") for r in denied],
            "release_send_skew_ns": skew_ns,
        },
        "recorded_at_utc": utc_now_iso(),
    }

    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, indent=2))
    print(f"evidence written: {evidence_path}")


if __name__ == "__main__":
    main()
