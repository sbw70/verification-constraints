# Provider isolation and provider-controlled key placement — preparation only

No commands in this procedure have been run on a lab host. Actual MH001 provider
keys and initialized provider state are deliberately absent from this local tree.
Source copies contain only `provider_a.py`/`provider_b.py` and the original mint
tool. No historical key, ledger, snapshot, execution log, or evidence was copied.

## Historical placement disclosure

Historical MP005 trees on the OmniBook contain provider issuance private keys
beside the mint tools, and the MP005 `prepare_authority` helper launches those
mint tools from its requester/controller tree. The historical published test
reference also contains deliberately published test private keys. Thus historical
MP issuance was not exclusively provider-host-resident. MH001 must not inherit
that placement or trust, even though its provider source is byte-identical.
Leave the historical trees and their trust/state/evidence unchanged.

## Later provider-host setup, only after separate explicit authorization

1. Complete the read-only host inventory in `OPERATOR_GATES.md`. Confirm the
   operator-selected provider role/machine, existing Python/cryptography/OpenSSL
   availability, persistent filesystem, and exclusive MH001 paths and ports.
   No dependency installation or service changes are implicit in this procedure.
2. On each respective provider host, create a new exclusive
   `/home/<operator>/MULTI_HUB_001/<run>/provider_a/` or `provider_b/` directory.
   Create separate `state/` and `evidence/` siblings. Refuse an existing run root.
   Install only that provider's verified source and mint tool, byte-for-byte.
   Verify against both hashes/commit in `validation/final/provider_source_identity.json`.
3. Generate fresh issuance and boundary-signing pairs **on that provider host**,
   or an explicitly approved provider-controlled environment. Never run this
   on the OmniBook; never transfer either private key to requester, observer, or
   hubs. The provider source imports keys from fixed filenames beside its source.
   The mint tool checks that issuance private/public keys match.

The following is a provider-host-only shell template. It is not a local-build
command. Set `role` to exactly the role of that host and first change into the
new, verified provider-source directory. If OpenSSL is unavailable, STOP rather
than installing it or generating keys elsewhere without new authorization.

```sh
role=provider_a  # provider_b on Provider B only
umask 077
python3 -B -c 'import sys; assert sys.platform == "linux"'
for suffix in issuance_private issuance_public private public; do
  test ! -e "${role}_${suffix}.pem" || exit 1
done
openssl genpkey -algorithm ED25519 -out "${role}_issuance_private.pem" || exit 1
openssl pkey -in "${role}_issuance_private.pem" -pubout -out "${role}_issuance_public.pem" || exit 1
openssl genpkey -algorithm ED25519 -out "${role}_private.pem" || exit 1
openssl pkey -in "${role}_private.pem" -pubout -out "${role}_public.pem" || exit 1
```

If a generation step fails, preserve its partial outputs and STOP; do not rerun
over existing files. These names exactly match unchanged provider/mint imports.
Record public key fingerprints and the approved provider-owned run identity.

4. With the new key domain approved and confirmed, initialize a **new** durable
   consume ledger and spent snapshot using the unchanged MP005
   `harness/ledger_evidence.py::bootstrap`, on Linux, pointed exclusively at this
   sanctioned MH001 state directory. That helper has been copied byte-for-byte
   to `provider_support/ledger_evidence.py`; it does not generate keys. It is not
   called during local validation. Review its explicit bootstrap action before use.
   Expected initial ledger is empty and snapshot is version 1, empty spent set,
   sequence 0, null head. Never initialize over existing files, reuse historical
   issuance trust, or erase/repair prior consumption history. The hub never calls
   this helper. No state reset is part of T01–T04.
5. Prepare a reviewed provider-host launcher with only these configuration
   overrides after importing the byte-identical provider from its isolated tree:
   `HOST`, `PORT`, `ASSOCIATION_URL`, `CONSUME_LEDGER_PATH`, `SPENT_STATE_PATH`,
   `EXECUTION_LOG_PATH`. Import must resolve only that directory's new key files.
   Do not replace verification, signing, ledger, reconciliation, or execution
   functions. A launcher/configuration is a remaining live-phase review artifact;
   the historical MP005 launcher enforces MP005 manifests and cannot simply be
   pointed at an unreviewed MH001 run. Do not start either provider in this phase.
6. The observer receives only new boundary **public** keys and a new provider
   registry/session configuration. Provider-signed START/COMPLETE/DENY are sent
   directly to that observer URL, independent of both hubs. Retain the established
   Ed25519 verification and ledger-head/authorization correlation. Provider
   identity/key verification and independently captured provider ingress are both
   mandatory; hub transport acknowledgments cannot replace them.
7. The requester writes operation bytes and a provider-approved context. Transfer
   those operation bytes/context to the corresponding issuer under provider
   control. Run unchanged `mint_authorization_a.py` or `_b.py` there, using its
   `--request-file`, `--context`, and `--output` arguments. Return only the issued
   package, original operation bytes/context, and public provenance/identity.
   No issuance private key or minting capability goes to the requester.
8. On the requester, `requester.py prepare --operation <operation> --issued
   <package> --context <context> --destination PROVIDER_A|PROVIDER_B --output
   <new-artifact-directory>` constructs the complete provider-bound request.
   Preserve its exact `request.http` for T03. Fresh T04 authority is separately
   issued under the same approved provider-controlled mechanism.

The read-only source gate confirms both providers ignore X-MH-Destination and
Host. Reconfirm actual installed hashes and binding behavior before deployment.
Never alter provider verification to accommodate a Host mismatch.

Hub installations receive only `hub.py`, `wire.py`, `routes.py`, both reviewed
route files for offline pair checking, and fresh observation-log paths. They
receive no provider source dependencies, provider keys, or provider state.
