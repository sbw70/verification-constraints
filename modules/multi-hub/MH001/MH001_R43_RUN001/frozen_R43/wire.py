"""Bounded HTTP/1 framing; opaque field lines are preserved byte-for-byte."""
import ipaddress
import re
import socket

MAX_BODY = 65536
MAX_HEAD = 65536
TOKEN = rb"[!#$%&'*+.^_`|~0-9A-Za-z-]+"
EXCLUDED = frozenset((b"host", b"connection", b"keep-alive", b"proxy-connection",
                     b"te", b"trailer", b"transfer-encoding", b"upgrade",
                     b"proxy-authenticate", b"proxy-authorization"))


class WireError(Exception):
    def __init__(self, identifier, status=400):
        self.identifier, self.status = identifier, status
        super().__init__(identifier)


def line(stream):
    value = stream.readline(MAX_HEAD + 1)
    if len(value) > MAX_HEAD or not value.endswith(b"\r\n"):
        raise WireError("malformed_http_line")
    return value[:-2]


def headers(stream):
    result, size = [], 0
    while True:
        raw = line(stream)
        size += len(raw) + 2
        if size > MAX_HEAD or len(result) > 100:
            raise WireError("headers_too_large")
        if not raw:
            return result
        name, colon, value = raw.partition(b":")
        if not colon or not re.fullmatch(TOKEN, name):
            raise WireError("malformed_header")
        if any(c < 32 and c != 9 or c == 127 for c in value):
            raise WireError("malformed_header_value")
        result.append((name.lower(), value.strip(b" \t"), raw))


def values(fields, name):
    return [value for key, value, _ in fields if key == name]


def connection_check(fields):
    for value in values(fields, b"connection"):
        for token in value.lower().split(b","):
            token = token.strip(b" \t")
            if token not in EXCLUDED | {b"close", b"keep-alive"}:
                raise WireError("unsupported_connection_token")


def length(fields, required=True):
    if values(fields, b"transfer-encoding"):
        raise WireError("unsupported_transfer_encoding")
    lengths = values(fields, b"content-length")
    if not lengths:
        if required:
            raise WireError("content_length_required", 411)
        return None
    if len(lengths) != 1 or not re.fullmatch(rb"[0-9]{1,20}", lengths[0]):
        raise WireError("invalid_content_length")
    return int(lengths[0])


def read_exact(stream, count):
    body = stream.read(count)
    if len(body) != count:
        raise WireError("truncated_body")
    return body


def request_head(stream):
    first = line(stream)
    match = re.fullmatch(b"(" + TOKEN + rb") ([\x21-\x7e]+) HTTP/(1\.[01])", first)
    if not match or not match[2].startswith(b"/") or b"#" in match[2]:
        raise WireError("unsupported_request_line")
    method, target, version = match.groups()
    if method == b"CONNECT":
        raise WireError("unsupported_tunnel")
    fields = headers(stream)
    hosts = values(fields, b"host")
    if len(hosts) > 1 or (version == b"1.1" and (len(hosts) != 1 or not hosts[0])):
        raise WireError("invalid_host")
    connection_check(fields)
    count = length(fields)
    if count > MAX_BODY:
        raise WireError("request_body_too_large")
    # No interim 100 response or tunnel/upgrade protocol is implemented.
    if values(fields, b"expect"):
        raise WireError("unsupported_expect")
    return method, target, fields, count


def kept(fields):
    return [(key, value, raw) for key, value, raw in fields if key not in EXCLUDED]


def authority(address):
    host, port = address["host"], address["port"]
    return (f"[{host}]:{port}" if ":" in host else f"{host}:{port}").encode("ascii")


def connect(address, timeout):
    # One numeric endpoint, one connect call: no DNS, failover, redirect, or retry.
    family = socket.AF_INET6 if ipaddress.ip_address(address["host"]).version == 6 else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_STREAM)
    try:
        sock.settimeout(timeout)
        sock.connect((address["host"], address["port"]))
        return sock
    except BaseException:
        sock.close()
        raise


def request_bytes(method, target, fields, body, address):
    return (method + b" " + target + b" HTTP/1.1\r\nHost: " + authority(address) + b"\r\n"
            + b"".join(raw + b"\r\n" for _, _, raw in kept(fields)) + b"\r\n" + body)


def response(stream, method):
    first = line(stream)
    match = re.fullmatch(rb"HTTP/1\.[01] ([0-9]{3}) ([\x09\x20-\x7e\x80-\xff]*)", first)
    if not match or not 200 <= int(match[1]) <= 599:
        raise WireError("unsupported_response_status")
    code, reason = match.groups()
    fields = headers(stream)
    connection_check(fields)
    no_body = method == b"HEAD" or code in (b"204", b"304")
    count = length(fields, required=not no_body)
    if code == b"204" and count not in (None, 0):
        raise WireError("invalid_204_length")
    # Buffer the complete framed response before forwarding; no partial provider reply
    # can be followed by a fabricated hub error. Response bodies have no 64-KiB cap.
    body = b"" if no_body else read_exact(stream, count)
    return (b"HTTP/1.1 " + code + b" " + reason + b"\r\n"
            + b"".join(raw + b"\r\n" for _, _, raw in kept(fields)) + b"\r\n" + body)
