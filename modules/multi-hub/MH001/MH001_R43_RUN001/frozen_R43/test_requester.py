"""Requester allowlist checks. Remote addresses use mocks only, never real sockets."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import requester
import wire

ROOT = Path(__file__).resolve().parent
REMOTE = {"host": "192.0.2.10", "port": 18080}  # Documentation-only, not a lab host.
PACKET = (b"POST /ingest?opaque=%2f HTTP/1.1\r\nHost: unchanged.invalid\r\n"
          b"X-MH-Destination: PROVIDER_A\r\nAuthorization:\t opaque.signature  \r\n"
          b"X-Custom: one\r\nX-Custom: two\r\nContent-Length: 4\r\n\r\n\x00A\xff!")
RESPONSE = b"HTTP/1.0 204 No Content\r\nX-Mock: untouched\r\n\r\n"


class RequesterAllowlist(unittest.TestCase):
    def setUp(self):
        temporary = ROOT / "validation/temporary"
        temporary.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temporary)
        self.root = Path(self.temp.name)
        self.root.resolve().relative_to(temporary.resolve())
        self.addCleanup(self.temp.cleanup)
        self.socket = MagicMock()
        self.socket.__enter__.return_value = self.socket
        self.socket.makefile.side_effect = lambda _: io.BytesIO(RESPONSE)
        self.patcher = patch.object(wire, "connect", return_value=self.socket)
        self.connect = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def config(self, entries):
        path = self.root / "approved.json"
        path.write_text(json.dumps({"approved_hubs": entries}))
        return path

    def approved(self):
        return requester.load_approved_hubs(self.config([REMOTE]))

    def test_loopback_continues_without_configuration(self):
        for index, host in enumerate(("127.0.0.1", "::1")):
            endpoint = {"host": host, "port": 18080}
            requester.submit(PACKET, endpoint, self.root / (str(index)+".jsonl"))
            self.connect.assert_called_with(endpoint, 20)
        self.assertEqual(self.connect.call_count, 2)
        self.assertEqual(self.socket.sendall.call_count, 2)

    def test_remote_denied_by_default_before_io(self):
        receipt = self.root / "never.jsonl"
        with self.assertRaisesRegex(ValueError, "remote_destination_not_approved"):
            requester.submit(PACKET, REMOTE, receipt)
        self.assertFalse(receipt.exists())
        self.connect.assert_not_called()

    def test_shipped_configuration_is_empty(self):
        approved = requester.load_approved_hubs(ROOT / "configs/approved_hubs.json")
        self.assertEqual(approved, frozenset())
        with self.assertRaises(ValueError):
            requester.validate_destination(REMOTE, approved)
        self.connect.assert_not_called()

    def test_exact_approved_ip_port_passes_validation(self):
        self.assertEqual(requester.validate_destination(REMOTE, self.approved()), REMOTE)
        self.connect.assert_not_called()

    def test_unapproved_ip_and_changed_port_rejected(self):
        approved = self.approved()
        for endpoint in ({"host": "192.0.2.11", "port": 18080},
                         {"host": "192.0.2.10", "port": 18081}):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                requester.submit(PACKET, endpoint, self.root / "never.jsonl", approved)
        self.connect.assert_not_called()

    def test_literal_addresses_and_valid_ports_only(self):
        for host in ("pi.local", "localhost", "192.0.2.010", "fe80::1%1", "0.0.0.0", "224.0.0.1"):
            with self.subTest(host=host), self.assertRaises((ValueError, TypeError)):
                requester.load_approved_hubs(self.config([{"host": host, "port": 18080}]))
        for port in (0, 65536, -1, True, "18080"):
            with self.subTest(port=port), self.assertRaises(ValueError):
                requester.load_approved_hubs(self.config([{"host": "192.0.2.10", "port": port}]))
        self.connect.assert_not_called()

    def test_invalid_configuration_fails_closed(self):
        path = self.root / "invalid.json"
        invalid = ('{}', '{"approved_hubs":{}}', '{"approved_hubs":[],"routes":{}}',
                   '{"approved_hubs":[],"approved_hubs":[]}',
                   '{"approved_hubs":[{"host":"192.0.2.10","port":1,"port":2}]}',
                   json.dumps({"approved_hubs": [REMOTE, REMOTE]}),
                   json.dumps({"approved_hubs": [dict(REMOTE, extra=True)]}),
                   '{"approved_hubs":[null]}')
        for raw in invalid:
            path.write_text(raw)
            with self.subTest(raw=raw), self.assertRaises((ValueError, TypeError)):
                requester.load_approved_hubs(path)
        self.connect.assert_not_called()

    def test_approved_mock_transmits_exact_request_once(self):
        reply = requester.submit(PACKET, REMOTE, self.root / "receipt.jsonl", self.approved())
        self.connect.assert_called_once_with(REMOTE, 20)
        self.socket.sendall.assert_called_once_with(PACKET)
        self.assertEqual(reply, RESPONSE.replace(b"HTTP/1.0", b"HTTP/1.1", 1))
        record = json.loads((self.root / "receipt.jsonl").read_text().splitlines()[-1])
        self.assertEqual(record["packet_sha256"], requester.digest(PACKET))
        self.assertEqual(record["body_sha256"], requester.digest(PACKET.split(b"\r\n\r\n")[1]))
        self.assertEqual(record["provider_execution"], "NOT_INFERRED")

    def test_connect_send_and_response_failures_never_retry(self):
        approved = self.approved()
        for stage in ("connect", "send", "response"):
            self.connect.reset_mock()
            self.socket.sendall.reset_mock()
            self.connect.side_effect = TimeoutError if stage == "connect" else None
            self.socket.sendall.side_effect = OSError if stage == "send" else None
            self.socket.makefile.side_effect = ((lambda _: io.BytesIO(b"bad\r\n"))
                                               if stage == "response" else lambda _: io.BytesIO(RESPONSE))
            with self.subTest(stage=stage), self.assertRaises((OSError, wire.WireError)):
                requester.submit(PACKET, REMOTE, self.root / (stage+".jsonl"), approved)
            self.connect.assert_called_once_with(REMOTE, 20)
            self.assertEqual(self.socket.sendall.call_count, 0 if stage == "connect" else 1)

    def test_cli_optional_approved_config_and_unchanged_bytes(self):
        packet = self.root / "request.http"
        packet.write_bytes(PACKET)
        args = ["requester.py", "send", "--request", str(packet), "--host", REMOTE["host"],
                "--port", str(REMOTE["port"]), "--receipt", str(self.root / "cli.jsonl"),
                "--approved-hubs", str(self.config([REMOTE]))]
        with patch("sys.argv", args), contextlib.redirect_stdout(io.StringIO()):
            requester.main()
        self.connect.assert_called_once_with(REMOTE, 20)
        self.socket.sendall.assert_called_once_with(PACKET)
        self.assertEqual(packet.read_bytes(), PACKET)

    def test_cli_denies_remote_without_config_or_with_empty_config(self):
        for config_args in ([], ["--approved-hubs", str(ROOT / "configs/approved_hubs.json")]):
            args = ["requester.py", "send", "--request", str(self.root / "absent.http"),
                    "--host", REMOTE["host"], "--port", str(REMOTE["port"]),
                    "--receipt", str(self.root / "never.jsonl")] + config_args
            with patch("sys.argv", args), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                requester.main()
            self.assertEqual(error.exception.code, 2)
        self.connect.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
