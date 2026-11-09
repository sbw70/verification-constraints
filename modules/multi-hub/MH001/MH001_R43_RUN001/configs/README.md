# MH001 — Experiment Configuration Records

## Purpose

This directory preserves the reviewed configuration files and preparation templates for the MH001 R4.3 scored experiment.

The configurations identify the provider endpoints, independent observer, approved requester destinations, and requirements for establishing provider trust and operator startup approval.

**Session:** `MH001_R43_RUN001`

**Experiment:** Multi-Hub Authority Persistence and Replay Denial

These are historical configuration artifacts. They are not a current network inventory or authorization to restart the experiment.

## 1. Directory Contents

```text
configs/
├── approved_hubs.json
├── observer.json
├── provider_a.json
├── provider_b.json
├── provider_keys.template.json
├── provider_registry.template.json
└── STOP1_APPROVAL.template.json
```

| File | Responsibility |
|---|---|
| `approved_hubs.json` | Restricts requester connections to approved hub IP/port pairs |
| `observer.json` | Identifies the independent observer session and listener |
| `provider_a.json` | Provider A runtime identity and endpoint |
| `provider_b.json` | Provider B runtime identity and endpoint |
| `provider_keys.template.json` | Unapproved template for provider signing-key identities |
| `provider_registry.template.json` | Template for observer public-key registration |
| `STOP1_APPROVAL.template.json` | Unapproved operator startup authorization template |

The three templates are preserved preparation artifacts, not substitutes for the finalized trust and approval records.

## 2. Original Network Configuration

The published configuration establishes these endpoints:

| Component | IP address | Port |
|---|---|---|
| Hub A | `192.168.1.100` | `18080` |
| Hub B | `192.168.1.106` | `18081` |
| Provider A | `192.168.1.118` | `18090` |
| Provider B | `192.168.1.107` | `18091` |
| Independent observer | `192.168.1.102` | `9191` |

The observer receives provider-signed boundary events at:

`http://192.168.1.102:9191/boundary`

The hub listener addresses and routes are preserved separately under:

`frozen_R43/live_review_R43/`

All paths are relative to the scored-run root.

These IP addresses describe the original test environment. They must not be assumed to remain assigned or reachable.

## 3. Approved Requester Hubs

File:

`approved_hubs.json`

The original allowlist contains exactly two endpoints:

```json
{
  "approved_hubs": [
    {
      "host": "192.168.1.100",
      "port": 18080
    },
    {
      "host": "192.168.1.106",
      "port": 18081
    }
  ]
}
```

The frozen requester accepts loopback endpoints by default.

For non-loopback destinations, it requires an exact host-and-port match in the supplied approved-hubs file.

The requester uses this list only when explicitly invoked with:

`--approved-hubs`

The requester does not load the hubs' internal route files.

The approved-hubs list permits connection to specified forwarding endpoints. It does not grant provider execution authority.

Original SHA-256:

`4588635b63ebc1dee6ca15b3de930726edb503cd3032a93d66bf79ba8b2c54b8`

## 4. Provider Configurations

### Provider A

File:

`provider_a.json`

Identity:

`PROVIDER_A`

Role:

`provider_a`

Listener:

`192.168.1.118:18090`

Original provider run root:

`/home/seth/MULTI_HUB_001/MH001_R43_RUN001`

Observer destination:

`http://192.168.1.102:9191/boundary`

SHA-256:

`4f89bc9f0f29e39393ecab26c6001b7d6d6f6b1aaaca614da71e82c6d0ddb58b`

### Provider B

File:

`provider_b.json`

Identity:

`PROVIDER_B`

Role:

`provider_b`

Listener:

`192.168.1.107:18091`

Original provider run root:

`/home/seth/MULTI_HUB_001/MH001_R43_RUN001`

Observer destination:

`http://192.168.1.102:9191/boundary`

SHA-256:

`661754ab55105b4fa154b77b8cc16a5da52809269140d185115fab00888ebfcf`

The providers have separate execution state and signing identities.

They share an observer destination but not authorization authority.

## 5. Independent Observer Configuration

File:

`observer.json`

Session:

`MH001_R43_RUN001`

Listener:

`192.168.1.102:9191`

Original Windows run root:

`C:/Users/holiw/esp32-main/MULTI_HUB_001/MH001_R43_RUN001`

SHA-256:

`4960e35cfde9a1bd43cddb615030e0ef83b478c717c59049f59616e3d367735a`

The observer's configured run root contains the public-key registry and the output evidence log.

The independent observer records provider-signed events rather than relying on HTTP responses returned through the hubs.

The historical output is:

`evidence/observer.jsonl`

## 6. Frozen Hub Routing

Although hub route files are not stored directly in `configs/`, they establish the forwarding behavior expected by these configurations.

Their historical copies are:

- `frozen_R43/live_review_R43/hub_a.json`
- `frozen_R43/live_review_R43/hub_b.json`

### Hub A

| Destination | Next hop |
|---|---|
| PROVIDER_A | Provider A — `192.168.1.118:18090` |
| PROVIDER_B | Hub B — `192.168.1.106:18081` |

Timeout: 15 seconds.

### Hub B

| Destination | Next hop |
|---|---|
| PROVIDER_A | Provider A — `192.168.1.118:18090` |
| PROVIDER_B | Provider B — `192.168.1.107:18091` |

Timeout: 10 seconds.

This creates the original T01 paths:

```text
Requester → Hub A → Provider A

Requester → Hub A → Hub B → Provider B
```

After Hub A termination, T03 and T04 use:

```text
Requester → Hub B → Provider A

Requester → Hub B → Provider B
```

The route topology is changed by selecting a different approved first hop, not by granting new authority to a hub.

## 7. Provider Trust Template

File:

`provider_keys.template.json`

The template identifies two providers and two signing-key roles per provider.

Its original status is:

`AWAITING_PROVIDER_HOST_KEYS`

Its key identifiers are initially `null`.

The completed, approved record is preserved at:

`trust/provider_keys.json`

The approved record must contain four distinct, reviewed key identifiers.

The template itself is not approved trust and cannot authorize live startup.

## 8. Observer Registry Template

File:

`provider_registry.template.json`

This template maps Provider A and Provider B to the expected public-key filenames.

The `key_id` fields initially contain `null`.

The completed registry is preserved at:

`association/provider_registry.json`

Its two public keys are located under:

`association/trust/`

The completed registry identifies the boundary-event signing keys, not the issuance keys used to mint provider authorization packages.

The observer validates the completed registry against the approved provider trust record.

## 9. STOP 1 Approval Template

File:

`STOP1_APPROVAL.template.json`

The original template contains:

```json
{
  "authorized": false,
  "phase": "LIVE_STARTUP",
  "session": "MH001_R43_RUN001",
  "config_sha256": null,
  "trust_sha256": null,
  "source_sha256": {}
}
```

This is an unapproved starting point.

The completed original startup approval records are preserved under:

`authorizations/`

They bind approval to:

- The specific session.
- The reviewed component configuration.
- The approved provider trust file.
- The required source-code identities.

The deployment checks reject missing approval, a false authorization value, or mismatched hashes.

The template must not be treated as approval to start a service.

A new experiment requires its own reviewed configuration and explicit operator authorization.

## 10. Verify Original Configuration Integrity

All seven files are included in the final 132-file manifest:

`evidence/MH001_FINAL_SHA256SUMS.txt`

From the scored-run root on Linux:

```bash
grep '  configs/' evidence/MH001_FINAL_SHA256SUMS.txt | sha256sum -c -
```

Expected result:

**7/7 configuration files pass.**

On Windows PowerShell, from the `configs/` directory:

```powershell
Get-ChildItem -File | Where-Object Name -ne 'README.md' | Get-FileHash -Algorithm SHA256
```

Compare the results to the seven `configs/` entries in the published manifest.

Adding this README does not change the historical configuration hashes.

## 11. Reproduction Procedure

For an independent reproduction:

1. Create a new isolated run directory.
2. Inventory actual host interfaces, IP addresses, ports, and existing listeners.
3. Select nonconflicting provider, hub, and observer endpoints.
4. Prepare new configuration files in the reproduction workspace.
5. Review both hub route files together.
6. Confirm Provider A and Provider B are mapped to their intended destinations.
7. Approve only the exact requester hub endpoints needed.
8. Establish provider-controlled signing identities and persistent state.
9. Construct the corresponding observer registry.
10. Verify all source, trust, and configuration hashes.
11. Obtain the required operator startup approvals.
12. Complete the reviewed preflight before any live execution.

Do not modify the historical configuration files to accommodate a new lab.

For the complete reviewed deployment constraints, consult:

`frozen_R43/OPERATOR_GATES.md`

Changing an endpoint, timeout, trust identity, or reviewed source file requires reassessing the applicable approvals and configuration hashes.

## 12. Preservation Boundary

All seven original configuration files belong to the 132-file scored evidence inventory.

This README is supplemental documentation.

Do not:

- Overwrite the original provider or observer configurations.
- Replace the historical approved-hubs list.
- Convert a pending template into a historical approval.
- Modify the frozen hub route files.
- Recalculate original hashes to conceal configuration changes.
- Treat historical IP addresses as current deployment authorization.

A new experiment must preserve its own configuration identities and evidence independently.

## Conclusion

The original MH001 configuration established two independent providers, two forwarding hubs, and a separate observer.

The requester could select approved forwarding paths, but neither routing configuration nor hub membership conferred authority to execute provider operations.
