# MD001 — Physical Application Configurations

This directory contains four JSON configuration files used by the MD001 R1 deployment adapter, [`../md001.py`](../md001.py).

The configurations define listener addresses, permitted source peers, downstream destinations, and whether the HP ingress forwards an artifact unchanged or deliberately modifies it for the N01 negative test.

They do not define signing authority, provider trust anchors, or authorization policy.

## Configuration inventory

| File | Role | Listener | Downstream | Mode |
|---|---|---|---|---|
| `relay.json` | Pi application relay | `30.30.30.30:18081` | `40.40.40.40:18443` | `pass` |
| `ingress.json` | HP ingress | `40.40.40.40:18443` | `127.0.0.1:18444` | `pass` |
| `ingress_N01.json` | HP negative-test ingress | `40.40.40.40:18443` | `127.0.0.1:18444` | `tamper` |
| `verifier.json` | HP verifier | `127.0.0.1:18444` | None | `pass` |

These are the published laboratory addresses, not automatically discovered network settings.

## Relay configuration

[`relay.json`](relay.json) defines the Raspberry Pi application relay.

The relay receives requests at `30.30.30.30:18081` and forwards the selected provider-bound request to `40.40.40.40:18443`.

Its `allowed_peer` value is `null`, so this configuration does not impose an application-level source-IP restriction. Network segmentation and firewall enforcement are separate controls.

The deployment adapter uses the frozen forwarding implementation in [`../runtime/`](../runtime/). The relay does not evaluate the artifact signature or determine verification acceptance.

## Pass-through ingress

[`ingress.json`](ingress.json) defines the normal HP ingress.

It accepts requests from the configured relay address, `30.30.30.30`, and forwards the received artifact body to the local verifier at `127.0.0.1:18444`.

Its mode is `pass`.

This configuration is used for unchanged artifact delivery in the B01 and B02 procedures.

## Negative-test ingress

[`ingress_N01.json`](ingress_N01.json) defines the downstream mutation adapter used for N01.

It uses the same listener, permitted peer, and verifier destination as the normal ingress, but sets:

```json
"mode": "tamper"
```

The implementation changes the signed `event.outcome` field from `SUCCESS` to `FAILURE`, without replacing the original signature.

This tests whether the unchanged verifier rejects a modified signed assertion.

The two ingress configurations use the same listening address and port. They are alternatives, not simultaneous listeners.

## Verifier configuration

[`verifier.json`](verifier.json) binds the verifier to `127.0.0.1:18444`.

It permits only the loopback peer, has no downstream target, and uses `pass` mode.

The verifier independently evaluates the received artifact using a separately provisioned public trust configuration.

The public trust file is supplied through the deployment adapter's `--trust` argument; it is not one of the four configuration files in this directory.

## Configuration validation

The `config()` function in [`../md001.py`](../md001.py) validates the configuration structure before starting a service.

Its checks include:

- Exact required top-level fields.
- Recognized service roles.
- Numeric IPv4 listener and destination addresses.
- Valid TCP port ranges.
- Supported ingress modes.
- A required relay destination.
- Loopback-only verifier binding and peer restriction.
- Rejection of tamper mode outside the ingress role.

The published files can be inspected without starting any network service:

```sh
python3 -m json.tool configs/relay.json
python3 -m json.tool configs/ingress.json
python3 -m json.tool configs/ingress_N01.json
python3 -m json.tool configs/verifier.json
```

Run these commands from the MD001 experiment root.

JSON parsing confirms syntax only. It does not establish successful deployment, connectivity, firewall enforcement, or experimental outcomes.

## Execution and evidence

The deployment adapter accepts a configuration using the `serve` command:

```sh
python3 -B md001.py serve --config configs/relay.json --out NEW_EVIDENCE_DIRECTORY
```

This example starts the relay service and is not a passive configuration check. It requires the configured network environment and an unused output directory.

Other service roles use their corresponding configuration files. The verifier additionally requires a public trust file.

The adapter records process identity, startup time, configuration content and configuration digest in its evidence output.

See [`../COMMANDS.md`](../COMMANDS.md) for operating procedures and [`../TEST_PLAN.md`](../TEST_PLAN.md) for case-specific requirements.

## Integrity and scope

These configuration files are part of the published implementation baseline. Their original bytes should be preserved when inspecting or reproducing the recorded experiment.

A configuration change creates a different experimental condition and must not be represented as the original scored setup.

The files specify application behavior only. They do not independently prove that network isolation was enforced or that a request traversed the intended physical path.

Verification of a signed assertion does not authorize execution of the underlying operation.
