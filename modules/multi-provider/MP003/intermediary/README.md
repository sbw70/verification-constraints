# Intermediary (NUVL Relay)

This directory contains the relay used in MP003.

| File | SHA-256 |
|---|---|
| `nuvl_multi_relay.py` | `09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4` |

The file is byte-identical to the relay used in MP001 and MP002. Its startup banner therefore still reads `MP001_NUVL_MULTI_PROVIDER_RELAY`.

## Deployment in MP003

- Host: Raspberry Pi 3B+ (`nuvl-relay`, 192.168.1.100)
- Listens on `0.0.0.0:8080`, endpoint `POST /nuvl`
- Provider A destination: `http://192.168.1.118:9090/ingest`
- Provider B destination: `http://192.168.1.106:9090/ingest`

## What the relay does

For each request, the relay:

1. reads the request body (maximum 64 KiB);
2. reads `X-Verification-Context`;
3. computes `request_repr = SHA256(request body)`;
4. computes the mechanical binding `SHA256("NUVL_BIND_V1|" + request_repr + "|" + context)`;
5. builds one artifact per provider containing `request_repr`, `verification_context`, `binding`, and that provider's authorization header value;
6. sends `X-Provider-A-Authorization` to Provider A and `X-Provider-B-Authorization` to Provider B, each in a separate background thread;
7. returns HTTP `204` to the requester.

If an authorization header is absent, the relay forwards an empty string for that provider. Provider code treats an empty value as `auth_missing`. That is how the manifest's "absent" header positions produced `auth_missing` in C01, C03, and B02.

## What the relay does not do

The relay:

- does not decode, parse, or verify authorization packages;
- holds no provider issuance or boundary keys;
- cannot mint, enlarge, or substitute provider authority;
- does not decide which provider should execute.

Its startup banner states this directly:

`Provider authorization verification: False`

`Provider secrets present: False`

In MP003 the relay forwarded attacker-supplied authorization unchanged. In C02 it sent the same Provider A authorization to both providers, and in C03 it sent the forged `PROVIDER_B` claim to Provider B. Both providers made their own decisions; the relay converted nothing.

## Behavior to be aware of

- **`204` means received, not delivered.** The relay returns `204` before provider delivery completes, and it discards provider responses and delivery errors (2-second timeout). A `204` does not show that either provider received, accepted, or executed anything. Provider outcomes are established by the signed association record and provider state, not by the relay response.
- **Oversized requests are dropped silently.** Bodies over 64 KiB receive `204` and are not forwarded. No MP003 request approached this limit; each was 43 bytes.
- **No per-request logging.** The relay logs nothing about individual requests. Its console transcript for the scored session (`../evidence/scored/operator_transcripts/relay_console.txt`) contains only the startup banner and the Ctrl+C shutdown.

## What this does not establish

MP003 does not test a compromised or malicious relay host, relay availability, or relay behavior under load. The contract notes that a hostile relay could recompute the non-secret binding. It still could not produce valid provider authorization without the corresponding issuance key, which the relay does not have.

## Related material

Contract, §§2–4 and §§9–10:

`../configs/MP003_CONTRACT.md`

Scored evidence:

`../evidence/scored/`
