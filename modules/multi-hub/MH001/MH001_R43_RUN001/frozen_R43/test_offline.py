"""Sequential loopback-only byte-capturing mocks. Never import/launch MP providers."""
import ast
import base64
import copy
import hashlib
import io
import ipaddress
import json
from pathlib import Path
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import hub
import requester
import routes
import wire

ROOT = Path(__file__).resolve().parent
REAL_CONNECT = wire.connect


def loopback_connect(address, timeout):
    if not ipaddress.ip_address(address["host"]).is_loopback:
        raise AssertionError("TEST_ATTEMPTED_NON_LOOPBACK_CONNECTION")
    return REAL_CONNECT(address, timeout)


class Capture(socketserver.StreamRequestHandler):
    def handle(self):
        first = self.rfile.readline()
        fields, raw_head = [], first
        while True:
            row = self.rfile.readline()
            raw_head += row
            if row == b"\r\n":
                break
            if not row:
                return
            fields.append(row[:-2])
        length = next(int(row.partition(b":")[2]) for row in fields
                      if row.partition(b":")[0].lower() == b"content-length")
        body = self.rfile.read(length)
        self.server.deliveries.append({"first": first, "headers": fields, "body": body,
                                       "body_sha256": hub.digest(body), "raw": raw_head + body})
        self.wfile.write(self.server.reply)


class Mock(socketserver.TCPServer):
    allow_reuse_address = False

    def __init__(self):
        self.deliveries = []
        self.reply = b"HTTP/1.0 207 Mock Multi Status\r\nContent-Length: 5\r\nX-Mock: opaque\r\n\r\n\x00ok\xff!"
        super().__init__(("127.0.0.1", 0), Capture)


def address(server):
    return {"host": "127.0.0.1", "port": server.server_address[1]}


class Offline(unittest.TestCase):
    def setUp(self):
        temporary_root = ROOT / "validation/temporary"
        temporary_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temporary_root)
        self.root = Path(self.temp.name)
        # Verify the recursive-cleanup target is strictly inside this workspace.
        self.root.resolve().relative_to(temporary_root.resolve())
        self.patch = patch.object(wire, "connect", side_effect=loopback_connect)
        self.connector = self.patch.start()
        self.addCleanup(self.patch.stop)
        self.addCleanup(self.temp.cleanup)
        self.servers, self.threads, self.logs = [], [], []
        self.addCleanup(self.cleanup_servers)
        self.pa, self.pb = Mock(), Mock()
        self.start(self.pa)
        self.start(self.pb)
        # Bind hub listeners first, then validate generated configuration pair.
        a, b = copy.deepcopy(routes.validate_pair(ROOT / "configs/hub_a.json", ROOT / "configs/hub_b.json"))
        for config in (a, b):
            config["listen"]["port"] = 0
        for config in (a, b):
            config["routes"]["PROVIDER_A"]["endpoint"] = address(self.pa)
        b["routes"]["PROVIDER_B"]["endpoint"] = address(self.pb)
        self.blog = io.StringIO()
        self.b = hub.Hub(b, self.blog)
        b["listen"] = address(self.b)
        a["routes"]["PROVIDER_B"]["endpoint"] = address(self.b)
        self.alog = io.StringIO()
        self.a = hub.Hub(a, self.alog)
        a["listen"] = address(self.a)
        self.write_pair(a, b)
        routes.validate_pair(self.root / "a.json", self.root / "b.json")
        self.start(self.b)
        self.start(self.a)

    def start(self, server):
        self.servers.append(server)
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        self.threads.append(thread)
        thread.start()

    def cleanup_servers(self):
        for server in reversed(self.servers):
            server.shutdown()
            server.server_close()
        for thread in self.threads:
            thread.join(2)

    def write_pair(self, a, b):
        (self.root / "a.json").write_text(json.dumps(a))
        (self.root / "b.json").write_text(json.dumps(b))

    def packet(self, destination=b"PROVIDER_A", body=b"\x00opaque authority\xff\r\n", extra=b"", method=b"PATCH", target=b"/raw//%2f;thing?q=%ff&x=1&x=2", version=b"1.1"):
        return (method + b" " + target + b" HTTP/" + version + b"\r\nHost: original.invalid\r\n"
                + b"X-MH-Destination: " + destination + b"\r\nContent-Length: "
                + str(len(body)).encode() + b"\r\n" + extra + b"\r\n" + body)

    def send(self, packet, server=None):
        with loopback_connect(address(server or self.a), 25) as sock:
            sock.sendall(packet)
            sock.shutdown(socket.SHUT_WR)
            parts = []
            while True:
                part = sock.recv(65536)
                if not part:
                    break
                parts.append(part)
        return b"".join(parts)

    def error(self, packet, code=400, identifier=None, server=None):
        before = (len(self.pa.deliveries), len(self.pb.deliveries))
        response = self.send(packet, server)
        self.assertTrue(response.startswith(f"HTTP/1.1 {code} ".encode()), response)
        self.assertIn(b"MH_HUB_ERROR HUB_", response)
        self.assertNotIn(b'"stage":"DENY"', response)
        if identifier:
            self.assertIn(identifier.encode(), response)
        self.assertEqual(before, (len(self.pa.deliveries), len(self.pb.deliveries)))

    def test_direct_and_chained_opaque_bytes_and_headers(self):
        opaque = b"X-Provider-Authorization:\t not-json!\xff  \r\nX-Custom: one\r\nX-Custom: two\r\n"
        exclusions = b"".join(name + b": opaque\r\n" for name in
                               (b"Keep-Alive", b"Proxy-Connection", b"TE", b"Trailer", b"Upgrade",
                                b"Proxy-Authenticate", b"Proxy-Authorization"))
        for destination, provider in ((b"PROVIDER_A", self.pa), (b"PROVIDER_B", self.pb)):
            with self.subTest(destination=destination):
                packet = self.packet(destination, extra=opaque + exclusions + b"Connection: close, TE, Upgrade\r\n")
                response = self.send(packet)
                captured = provider.deliveries[-1]
                self.assertEqual(captured["first"], packet.split(b"\r\n")[0] + b"\r\n")
                self.assertEqual(captured["body"], packet.split(b"\r\n\r\n", 1)[1])
                original = packet.split(b"\r\n\r\n", 1)[0].split(b"\r\n")[1:]
                expected = [line for line in original if line.partition(b":")[0].lower() not in wire.EXCLUDED]
                actual = [line for line in captured["headers"] if not line.lower().startswith(b"host:")]
                self.assertEqual(actual, expected)
                self.assertIn(b"Host: " + wire.authority(address(provider)), captured["headers"])
                self.assertEqual(response, provider.reply.replace(b"HTTP/1.0", b"HTTP/1.1", 1))
        self.assertEqual((len(self.pa.deliveries), len(self.pb.deliveries)), (1, 1))
        self.assertEqual(len([r for r in self.rows(self.blog) if r["observation"] == "result"]), 1)

    @staticmethod
    def rows(log):
        return [json.loads(row) for row in log.getvalue().splitlines()]

    def test_identical_body_sequences_and_hashes_no_secrets(self):
        packet = self.packet(b"PROVIDER_B", extra=b"Authorization: SECRET_CANARY\r\n")
        self.send(packet)
        self.send(packet, self.b)  # Same bytes, fresh sequence at B; no authority interpretation.
        rows = [r for r in self.rows(self.blog) if r["observation"] == "result"]
        self.assertEqual([r["sequence"] for r in rows], [1, 2])
        digest = self.pb.deliveries[0]["body_sha256"]
        for log in (self.alog, self.blog):
            self.assertNotIn("SECRET_CANARY", log.getvalue())
            self.assertNotIn("opaque authority", log.getvalue())
            for row in self.rows(log):
                self.assertEqual(row["ingress_body_sha256"], digest)
                if row["observation"] == "result":
                    self.assertEqual(row["egress_body_sha256"], digest)
                    self.assertEqual(row["transport_result"], "response_forwarded")
                self.assertTrue(row["timestamp"])
                auth = next(v for v in row["preserved_headers"] if v["name"] == "Authorization")
                self.assertEqual(auth["value_sha256"], hub.digest(b"SECRET_CANARY"))

    def test_destination_header_name_case_insensitive(self):
        self.send(self.packet().replace(b"X-MH-Destination", b"x-mH-deSTination"))
        self.assertEqual(len(self.pa.deliveries), 1)

    def test_destination_rejections(self):
        self.error(self.packet().replace(b"X-MH-Destination: PROVIDER_A\r\n", b""))
        for value in (b"", b"provider_a", b"PROVIDER_C", b"PROVIDER_A, PROVIDER_B", b"\"PROVIDER_A\"", b"PROVIDER_\x00A"):
            with self.subTest(value=value):
                self.error(self.packet(value))
        self.error(self.packet(extra=b"x-mh-destination: PROVIDER_A\r\n"))
        self.error(self.packet(extra=b"X-MH-Destination: PROVIDER_B\r\n"))
        self.error(self.packet().replace(b"X-MH-Destination:", b"X-MH-Destination :"))

    def test_request_framing_rejections(self):
        packet = self.packet(body=b"x")
        self.error(packet.replace(b"Content-Length: 1\r\n", b""), 411)
        for value in (b"-1", b"+1", b"1, 1", b"x", b"65537"):
            self.error(packet.replace(b"Content-Length: 1", b"Content-Length: " + value))
        for extra in (b"Content-Length: 1\r\n", b"Content-Length: 2\r\n",
                      b"Transfer-Encoding: chunked\r\n", b"Transfer-Encoding: identity\r\n",
                      b"Connection: Authorization\r\n", b"Connection: Content-Length\r\n",
                      b"Connection: \r\n", b"Bad Header: x\r\n", b" Folded: x\r\n"):
            self.error(self.packet(extra=extra))
        self.error(packet[:-1], identifier="truncated_body")
        self.error(packet.replace(b"\r\n", b"\n", 1))

    def test_body_limit_zero_and_full_64k(self):
        for body in (b"", bytes(range(256)) * 256):
            self.send(self.packet(body=body))
            self.assertEqual(self.pa.deliveries[-1]["body"], body)

    def test_methods_queries_versions_and_head(self):
        for method in (b"POST", b"PUT", b"DELETE", b"OPTIONS", b"custom-METHOD"):
            self.send(self.packet(method=method, version=b"1.0"))
            self.assertTrue(self.pa.deliveries[-1]["first"].startswith(method + b" /raw//%2f;thing?"))
            self.assertTrue(self.pa.deliveries[-1]["first"].endswith(b" HTTP/1.1\r\n"))
        self.pa.reply = b"HTTP/1.0 200 Representation\r\nContent-Length: 27\r\n\r\n"
        self.assertEqual(self.send(self.packet(method=b"HEAD")), self.pa.reply.replace(b"HTTP/1.0", b"HTTP/1.1"))

    def test_response_status_reason_headers_and_body(self):
        self.pa.reply = (b"HTTP/1.0 403 Provider opaque reason!\r\nContent-Length: 4\r\n"
                         b"X-Signed: \xffopaque \t\r\nX-Mock: 1\r\nX-Mock: 2\r\n"
                         b"Host: downstream.invalid\r\nConnection: close\r\nKeep-Alive: 1\r\n"
                         b"Proxy-Connection: close\r\nTE: trailers\r\nTrailer: X-No\r\nUpgrade: xyz\r\n"
                         b"Proxy-Authenticate: x\r\nProxy-Authorization: y\r\n\r\n\xff\x00ok")
        result = self.send(self.packet())
        head, body = result.split(b"\r\n\r\n", 1)
        self.assertEqual(body, b"\xff\x00ok")
        self.assertEqual(head.split(b"\r\n")[0], b"HTTP/1.1 403 Provider opaque reason!")
        expected = [row for row in self.pa.reply.split(b"\r\n\r\n")[0].split(b"\r\n")[1:]
                    if row.partition(b":")[0].lower() not in wire.EXCLUDED]
        self.assertEqual(head.split(b"\r\n")[1:], expected)

    def test_provider_204_without_length(self):
        self.pa.reply = b"HTTP/1.0 204 No Content\r\nServer: BaseHTTP/mock\r\n\r\n"
        self.assertEqual(self.send(self.packet()), self.pa.reply.replace(b"HTTP/1.0", b"HTTP/1.1"))

    def test_unsupported_response_framing_and_no_retry(self):
        replies = [b"HTTP/1.1 200 OK\r\n\r\nunknown",
                   b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\n",
                   b"HTTP/1.1 200 OK\r\nContent-Length: 1\r\nContent-Length: 1\r\n\r\nx",
                   b"HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\nx",
                   b"HTTP/1.1 200 OK\r\nContent-Length: -1\r\n\r\n",
                   b"HTTP/1.1 204 OK\r\nContent-Length: 1\r\n\r\nx",
                   b"HTTP/1.1 100 Continue\r\n\r\n",
                   b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\nConnection: X-Signed\r\n\r\n"]
        for reply in replies:
            self.pa.reply = reply
            before, connects = len(self.pa.deliveries), self.connector.call_count
            response = self.send(self.packet())
            self.assertIn(b"502 Bad Gateway", response)
            self.assertIn(b"MH_HUB_ERROR HUB_A unsupported_downstream_response", response)
            self.assertEqual(len(self.pa.deliveries), before + 1)
            self.assertEqual(self.connector.call_count, connects + 1)

    def test_unreachable_no_retry(self):
        # Refuse a single numeric endpoint; no DNS or retry/failover path.
        with patch.object(wire, "connect", side_effect=ConnectionRefusedError) as connector:
            self.error(self.packet(), 502, "downstream_unreachable_or_io")
            self.assertEqual(connector.call_count, 1)
            self.assertEqual(connector.call_args.args[1], 15)

    def test_timeout_classification_fixed_values(self):
        for server, timeout in ((self.a, 15), (self.b, 10)):
            with patch.object(wire, "connect", side_effect=TimeoutError) as connector:
                self.error(self.packet(), 504, "downstream_timeout", server)
                self.assertEqual(connector.call_count, 1)
                self.assertEqual(connector.call_args.args[1], timeout)

    def test_hub_b_transport_error_preserved_through_hub_a(self):
        def fail_provider(endpoint, timeout):
            if endpoint == address(self.pb):
                raise TimeoutError
            return loopback_connect(endpoint, timeout)
        with patch.object(wire, "connect", side_effect=fail_provider) as connector:
            response = self.send(self.packet(b"PROVIDER_B"))
            self.assertIn(b"HTTP/1.1 504 Gateway Timeout", response)
            self.assertIn(b"MH_HUB_ERROR HUB_B downstream_timeout", response)
            self.assertNotIn(b"MH_HUB_ERROR HUB_A", response)
            self.assertEqual(connector.call_count, 2)

    def test_real_downstream_read_timeout_no_retry(self):
        # Exercise the real 10-second socket read timeout, without changing config.
        class Stall(Capture):
            def handle(inner):
                inner.server.received.set()
                inner.server.release.wait(12)
        stalled = socketserver.TCPServer(("127.0.0.1", 0), Stall)
        stalled.received, stalled.release = threading.Event(), threading.Event()
        self.addCleanup(stalled.release.set)
        self.start(stalled)
        original = self.b.config["routes"]["PROVIDER_A"]["endpoint"]
        self.b.config["routes"]["PROVIDER_A"]["endpoint"] = address(stalled)
        start = time.monotonic()
        try:
            reply = self.send(self.packet(), self.b)
        finally:
            stalled.release.set()
            self.b.config["routes"]["PROVIDER_A"]["endpoint"] = original
        self.assertTrue(stalled.received.is_set())
        self.assertIn(b"504 Gateway Timeout", reply)
        self.assertIn(b"MH_HUB_ERROR HUB_B downstream_timeout", reply)
        self.assertGreaterEqual(time.monotonic() - start, 9)

    def test_static_config_duplicate_keys_reverse_routes_and_loops(self):
        a, b = routes.validate_pair(self.root / "a.json", self.root / "b.json")
        for raw in ('{"hub_id":"HUB_A","hub_id":"HUB_A"}',
                    (self.root / "a.json").read_text().replace('"port":', '"port":1,"port":', 1)):
            (self.root / "bad.json").write_text(raw)
            with self.assertRaises(ValueError):
                routes.load(self.root / "bad.json")
        for modifier in ("reverse", "self", "alias", "bad_timeout", "default", "wrong_endpoint"):
            aa, bb = copy.deepcopy(a), copy.deepcopy(b)
            if modifier == "reverse":
                bb["routes"]["PROVIDER_B"]["next_hop"] = "HUB_A"
            elif modifier == "self":
                aa["routes"]["PROVIDER_B"]["endpoint"] = aa["listen"]
            elif modifier == "alias":
                bb["routes"]["PROVIDER_B"]["endpoint"] = bb["listen"]
            elif modifier == "bad_timeout":
                bb["timeout_seconds"] = 8
            elif modifier == "default":
                aa["routes"]["*"] = copy.deepcopy(aa["routes"]["PROVIDER_A"])
            else:
                aa["routes"]["PROVIDER_B"]["endpoint"] = address(self.pa)
            self.write_pair(aa, bb)
            with self.assertRaises(ValueError):
                routes.validate_pair(self.root / "a.json", self.root / "b.json")

    def test_requester_constructs_only_outer_binding_from_issued_bytes(self):
        issued = b' {"MOCK_ALREADY_ISSUED":"not a key or valid signature"}\n'
        packet = requester.prepare(b"original operation", issued, "CTX_MH001_MOCK", "PROVIDER_B", self.root / "artifact")
        reply = requester.submit(packet, address(self.a), self.root / "receipt.jsonl")
        artifact = json.loads(self.pb.deliveries[0]["body"])
        self.assertEqual(base64.urlsafe_b64decode(artifact["provider_authorization_b64"] + "=="), issued)
        expected_repr = hub.digest(b"original operation")
        self.assertEqual(artifact["request_repr"], expected_repr)
        self.assertEqual(artifact["binding"], hub.digest(("NUVL_BIND_V1|" + expected_repr + "|CTX_MH001_MOCK").encode()))
        self.assertIn(b"207 Mock Multi Status", reply)
        self.assertEqual(self.pb.deliveries[0]["body"], (self.root / "artifact/body.bin").read_bytes())
        with self.assertRaises(FileExistsError):
            requester.submit(packet, address(self.a), self.root / "receipt.jsonl")
        self.assertEqual(len(self.pb.deliveries), 1)

    def test_hub_has_no_authority_or_execution_processing(self):
        for name in ("hub.py", "wire.py", "routes.py"):
            tree = ast.parse((ROOT / name).read_text())
            imported = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
            imported += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
            self.assertFalse(any(x.startswith(("cryptography", "provider", "requester", "subprocess")) for x in imported))
        # Nonsense authority is transported, with no parse/repair/deny from the hub.
        self.send(self.packet(body=b"not even JSON", extra=b"Authorization: garbage.invalid.signature\r\n"))
        self.assertEqual(self.pa.deliveries[0]["body"], b"not even JSON")

    def test_two_separate_hub_processes(self):
        configs = [copy.deepcopy(self.a.config), copy.deepcopy(self.b.config)]
        # Reserve fresh loopback endpoints; no configured lab addresses are used.
        with socket.socket() as sa, socket.socket() as sb:
            sa.bind(("127.0.0.1", 0))
            sb.bind(("127.0.0.1", 0))
            configs[0]["listen"]["port"] = sa.getsockname()[1]
            configs[1]["listen"]["port"] = sb.getsockname()[1]
        configs[0]["routes"]["PROVIDER_B"]["endpoint"] = configs[1]["listen"]
        self.write_pair(*configs)
        processes = []
        try:
            for config in reversed(configs):
                identity = config["hub_id"]
                command = [sys.executable, "-B", str(ROOT / "hub.py"),
                           "--hub-a", str(self.root / "a.json"), "--hub-b", str(self.root / "b.json"),
                           "--identity", identity, "--log", str(self.root / (identity + ".jsonl"))]
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                processes.append(process)
                ready = process.stdout.readline()
                self.assertTrue(ready, "Mock hub process did not start")
                self.assertEqual(json.loads(ready)["status"], "LISTENING")
            self.assertNotEqual(processes[0].pid, processes[1].pid)
            for destination in (b"PROVIDER_A", b"PROVIDER_B"):
                packet = self.packet(destination)
                with loopback_connect(configs[0]["listen"], 20) as sock:
                    sock.sendall(packet)
                    while sock.recv(65536):
                        pass
            self.assertEqual((len(self.pa.deliveries), len(self.pb.deliveries)), (1, 1))
            for identity, expected in (("HUB_A", 2), ("HUB_B", 1)):
                rows = [json.loads(row) for row in (self.root / (identity + ".jsonl")).read_text().splitlines()]
                self.assertEqual(len([r for r in rows if r["observation"] == "result"]), expected)
                self.assertTrue(all(r["ingress_body_sha256"] == r["egress_body_sha256"]
                                    for r in rows if r["observation"] == "result"))
        finally:
            for process in reversed(processes):
                # Teardown only these locally spawned mock-test hubs, never scored Hub A.
                process.terminate()
                process.communicate(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
