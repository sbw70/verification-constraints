"""MD-001 assertions only. No network, history, execution, or evidence dependencies."""
import base64
import hashlib
import json
import re
import uuid
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

TAG = b"NUVL-MD001-ARTIFACT-v1|"
FIELDS = {"version", "producer_id", "key_id", "artifact_id", "event_id", "outcome"}


def canonical_bytes(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def key_id(key):
    return "sha256:" + digest(key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))


def unique(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("duplicate_json_key")
        result[k] = v
    return result


def loads(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))


def signed_bytes(event):
    return TAG + canonical_bytes(event)


def produce(key, artifact_id=None):
    event = dict(version=1, producer_id="DOMAIN_A", key_id=key_id(key.public_key()),
                 artifact_id=artifact_id or str(uuid.uuid4()), event_id="LOCAL_SORT_V1", outcome="SUCCESS")
    signature = base64.urlsafe_b64encode(key.sign(signed_bytes(event))).rstrip(b"=").decode("ascii")
    return canonical_bytes({"event": event, "signature": signature})


def verify(raw, trust):
    result = {"accepted": False, "reason": "malformed", "signature_checks": 0,
              "artifact_sha256": digest(raw)}
    try:
        if len(raw) > 65536:
            raise ValueError("oversize")
        package = loads(raw)
        if type(package) is not dict or set(package) != {"event", "signature"}:
            raise ValueError("envelope_fields")
        e, sig = package["event"], package["signature"]
        if type(e) is not dict or set(e) != FIELDS or type(e["version"]) is not int or e["version"] != 1:
            raise ValueError("event_fields")
        for name in FIELDS - {"version"}:
            if type(e[name]) is not str or not re.fullmatch(r"[A-Za-z0-9_:.\-]{1,128}", e[name]):
                raise ValueError("field_type_or_encoding")
        if str(uuid.UUID(e["artifact_id"])) != e["artifact_id"]:
            raise ValueError("artifact_id")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", e["key_id"]):
            raise ValueError("key_id")
        if type(sig) is not str or not re.fullmatch(r"[A-Za-z0-9_-]{86}", sig):
            raise ValueError("signature_encoding")
        decoded = base64.urlsafe_b64decode(sig + "==")
        if base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii") != sig:
            raise ValueError("signature_encoding")
        if raw != canonical_bytes(package):
            raise ValueError("noncanonical_envelope")
        public_hex = trust.get(e["producer_id"], {}).get(e["key_id"])
        if public_hex is None:
            result["reason"] = "untrusted_producer_key_binding"
            return result
        key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_hex))
        if key_id(key) != e["key_id"]:
            raise ValueError("invalid_local_trust_configuration")
        result["signature_checks"] = 1
        key.verify(decoded, signed_bytes(e))
        if e["event_id"] != "LOCAL_SORT_V1" or e["outcome"] != "SUCCESS":
            result["reason"] = "local_criteria_rejected"
        else:
            result.update(accepted=True, reason="accepted")
    except InvalidSignature:
        result["reason"] = "invalid_signature"
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        result["detail"] = str(error)
    return result
