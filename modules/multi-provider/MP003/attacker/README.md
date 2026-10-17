# Attacker Material

This directory contains the attacker-side material that models compromise of Provider A's authorization-issuance key in MP003.

It is the only new material in MP003. All provider, relay, and association code is reused unchanged from MP002.

## Contents

| File | Role | SHA-256 |
|---|---|---|
| `compromised_provider_a_issuance_private.pem` | attacker's copy of Provider A's issuance private key | `37f808b6901f5020fb7b68924217d76f7923d898e44913a6338008d85ac15fd8` |
| `provider_a_issuance_public.pem` | Provider A's issuance public key, used for the mint's keypair check | `a52276369981962b878311ec4e33186af25ac10cd359fafbc760e118e607ad71` |
| `mint_compromised_a.py` | mints authorizations claiming `PROVIDER_A` with the compromised key | `41306a6fe2f4751443b531e0938128ec08c771aea62d68e8fc4b952dc2284f10` |
| `mint_forged_b_with_a_key.py` | mints authorizations claiming `PROVIDER_B` with the compromised key | `7963cf83496aca069e51cd2cc7fcedb4f9720b8b0f2684303bea15d863b3ef1b` |

All four hashes match the locked MP003 run manifest.

## The compromised key is real

`compromised_provider_a_issuance_private.pem` is byte-identical to `../provider_a/provider_a_issuance_private.pem`. `provider_a_issuance_public.pem` is byte-identical to `../provider_a/provider_a_issuance_public.pem`.

This is not a simulated or look-alike key. In MP003 the attacker holds exactly the key Provider A's legitimate mint uses. C01 confirms this: Provider A accepted and executed an authorization minted with it.

## How the attacker mints differ from the legitimate mint

`mint_compromised_a.py` is `../provider_a/mint_authorization_a.py` with one line changed: the private key file name.

```diff
-    BASE_DIR / "provider_a_issuance_private.pem"
+    BASE_DIR / "compromised_provider_a_issuance_private.pem"
```

`mint_forged_b_with_a_key.py` is `mint_compromised_a.py` with one line changed: the claimed provider.

```diff
-PROVIDER_ID = "PROVIDER_A"
+PROVIDER_ID = "PROVIDER_B"
```

Everything else is identical: canonical JSON, authorization-ID derivation, signing domain, package format, fresh random nonce, and the check that the private key matches the supplied public key before signing.

Because the authorization ID is derived from the forged object itself, `mint_forged_b_with_a_key.py` produces a package that passes Provider B's identity and authorization-ID checks and fails only at signature verification. That is what C03 requires.

## Usage

Both utilities take the same arguments:

```
python mint_compromised_a.py --request-file <request.json> --context <CTX> --output <package.json>
```

Each writes the package JSON and a sibling `<package.json>.b64` containing the base64url header value. Each refuses to overwrite an existing output. Each prints the provider ID, request representation, authorization ID, nonce, and package SHA-256.

## Where each utility was used

| Utility | Scored case | Authorization ID | Outcome |
|---|---|---|---|
| `mint_compromised_a.py` | C01 | `6e3ce147…` | executed by Provider A |
| `mint_compromised_a.py` | C02 | `0e2ed472…` | executed by Provider A; refused by Provider B (`auth_provider_mismatch`) |
| `mint_forged_b_with_a_key.py` | C03 | `11e016ab…` | refused by Provider B (`auth_bad_sig`) |

Preflight dry-run mints from both utilities are in `../evidence/preflight/`. They were never sent.

## Scope of the modeled compromise

The attacker has Provider A's issuance private key and nothing else.

Not compromised in MP003:

- Provider A's boundary-signing key;
- any Provider B key;
- association trust material;
- the relay implementation;
- any host.

Within this scope, the attacker can originate Provider A authority but does not hold the keys needed to forge Provider A boundary events or to sign Provider B authority. Whether Provider A authority can nonetheless be made to act as Provider B authority is exactly what C02 and C03 test.

## Related material

`../provider_a/` — the legitimate Provider A mint and keys

`../provider_b/`

`../configs/MP003_CONTRACT.md` — §20

`../evidence/scored/C01_COMPROMISED_A_TO_A/`

`../evidence/scored/C02_PROVIDER_A_AUTH_TO_B/`

`../evidence/scored/C03_CLAIM_B_SIGNED_BY_A/`
