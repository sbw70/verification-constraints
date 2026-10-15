# MP002 Provenance

This document records the implementation lineage, test configuration, deployment identity, evidence handling, and publication staging for MP002.

MP002 extends the MP001 multi-provider baseline with one narrow experimental change: Provider B gained a deterministic provider-local policy gate used to test whether independently controlled providers can reach different execution decisions for the same distributed operation without another component overriding either provider.

## Test identity

Test:

`MP002`

Scored session:

`MP002_SCORED_20261013`

Primary claim under test:

**Independent providers can receive the same operation with valid provider-specific authorization and retain independent provider-local execution judgment.**

The scored campaign contained:

- `B01_CONTROL`
- `D01_POLICY_DIVERGENCE`

## Relationship to MP001

MP002 was built from the MP001 physically distributed multi-provider implementation.

The architecture remained:

Requester  
→ NUVL relay  
→ Provider A and Provider B  
→ association recorder

Provider A and Provider B remained separate authority domains.

The relay remained shared transport.

The association remained an evidence-verification and recording component rather than an execution authority.

MP002 did not redesign the authorization format, request binding, boundary-event format, association record format, or provider-local spent-state mechanism.

## Experimental delta

The substantive MP002 change was made in the Provider B runtime.

Provider B gained:

`POLICY_DENY_CONTEXT = "CTX_MP002_DIVERGE"`

and a provider-local branch that emits:

`DENY policy_denied`

when the verified request carries that context.

The policy check occurs before `consume_authorization`.

Accordingly, when D01 reached Provider B:

- the Provider B authorization was validated;
- Provider B applied its own local policy;
- Provider B denied;
- the authorization was not consumed;
- no Provider B `START` was emitted;
- no Provider B execution occurred;
- no Provider B `COMPLETE` was emitted.

The MP001-to-MP002 Provider B source difference is preserved in:

`provider_b/MP001_TO_MP002_PROVIDER_B.diff`

The diff was generated against the Provider B runtime actually used in the MP001 scored deployment.

The MP001 Provider B baseline runtime SHA-256 was:

`7759ae86...`

The complete baseline hash is preserved in the MP001 evidence and deployment-hash record.

The MP002 Provider B runtime SHA-256 is:

`5e0ab4b79df4c97bc7bc324d63da85711728d625b82306cdce6c92592e2ee13e`

The diff also contains a startup-banner change from the MP001 name to the MP002 name and a trailing newline difference.

No claim is made that those cosmetic changes affect the tested property.

## Reused components

Several MP001 components were intentionally reused unchanged.

### Provider A runtime

SHA-256:

`c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606`

### Provider A mint utility

SHA-256:

`1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec`

### Provider B mint utility

SHA-256:

`1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb`

The Provider B mint utility hash matches the MP001 version.

### NUVL relay

SHA-256:

`09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4`

### Association recorder

SHA-256:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

### Provider registry

SHA-256:

`59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d`

The publication-staging audit confirmed that the staged source files match the hashes recorded in:

`evidence/scored/deployed_implementation_hashes.txt`

## Reused startup banners

Because some implementations were reused byte-for-byte from MP001, their startup banners retain MP001 naming.

In particular:

- the relay still identifies itself with the MP001 relay banner;
- Provider A may still identify itself with the MP001 Provider A banner;
- the association recorder still identifies itself as `MP001_ASSOCIATION_RECORDER`.

These banners are implementation labels, not scored-session identifiers.

The MP002 campaign is identified independently by:

- the MP002 contract;
- the MP002 run manifest;
- the scored session identifier;
- deployed implementation hashes;
- request and authorization artifacts;
- provider-local final state;
- association evidence.

No source file was modified merely to change those reused banners before the scored run.

## Locked contract

The scored MP002 contract is:

`configs/MP002_CONTRACT.md`

SHA-256:

`e795f55172ea27d8ee434679ab9ea4a1b07e1154a708dfd5ad846fdd0f4ab18d`

The contract was fixed before the scored campaign.

It defines the authorization and boundary-event representations, provider validation sequence, Provider B policy behavior, durable authorization consumption, signed boundary evidence, and stated claim boundaries.

A copy is also preserved inside:

`evidence/scored/MP002_CONTRACT.md`

The publication-staging audit confirmed that the configuration copy and scored-evidence copy are byte-identical.

## Locked run manifest

The scored run manifest is:

`configs/MP002_RUN_MANIFEST.json`

SHA-256:

`3f4b317e3c3fc8f34e579941ec79f0f0191fcef122be320973a88b84e5750845`

The manifest defines the scored B01 and D01 cases and records the fixed implementation identities and excluded claims.

A copy is also preserved inside:

`evidence/scored/MP002_RUN_MANIFEST.json`

The publication-staging audit confirmed that the configuration copy and scored-evidence copy are byte-identical.

## Provider keys

Each provider used separate laboratory signing material for:

- authorization issuance;
- boundary-event signing.

The provider source directories publish the corresponding laboratory private and public PEM files intentionally for reproducibility.

These are test keys, not production credentials.

The architecture tested during MP002 remains provider-scoped even though the laboratory keys are subsequently published with the test package.

Publication of those keys does not retroactively change which components held or exercised them during the scored run.

## Deployment

The scored MP002 roles were physically distributed across separate hosts.

### Provider A

Host:

`Xer0trust-3`

Address:

`192.168.1.118`

Remote working directory:

`/home/seth/MULTI_PROVIDER_002/provider_a`

### Provider B

Host:

`Xer0trust2`

Address:

`192.168.1.106`

Remote working directory:

`/home/seth/MULTI_PROVIDER_002/provider_b`

### NUVL relay

Host:

`nuvl-relay`

Address:

`192.168.1.100`

Remote working directory:

`/home/seth/MULTI_PROVIDER_002/intermediary`

### Association

The association recorder ran on the requester/coordinator system.

The scored association session identifier was:

`MP002_SCORED_20261013`

MP002 does not make a globally synchronized cross-host timing claim from this deployment.

## Pre-scored smoke run

A smoke session was performed before scoring:

`MP002_SMOKE_001`

The smoke run exercised both intended paths:

### Smoke B01

Both providers permitted and executed.

### Smoke D01

Provider A executed.

Provider B returned:

`DENY policy_denied`

Provider B did not consume the D01 authorization.

The smoke artifacts are retained under:

`evidence/smoke/`

They are preserved for deployment provenance and troubleshooting.

They are not substituted for the scored evidence.

## State reset before scoring

After the smoke run, the scored provider state was reset to clean valid state.

Provider spent-state files were restored from known-good local JSON rather than reconstructed through an inline remote shell command.

The fresh scored state was verified as valid JSON.

Before the scored run:

- Provider A spent count was `0`;
- Provider B spent count was `0`;
- Provider A scored execution log was absent;
- Provider B scored execution log was absent.

Fresh provider-specific authorizations were then minted for the scored campaign.

Smoke authorizations were not reused.

## Scored B01 control

Request representation:

`7bf65d11928d3e32ae1245ce5a6a2f8aeb12ba53644b868630b9e814adc7e35f`

Verification context:

`CTX_ALPHA`

Provider A authorization ID:

`6a7394b62385b6ea2ff9f72a0271c27e75b1c4081d1aa4ff3eb509468587354a`

Provider B authorization ID:

`84064da5fac9cb562ac1f85c96db3fe334725f595e7ed6967babd9ec6df195ea`

Observed association events:

- Provider A `START`
- Provider B `START`
- Provider A `COMPLETE`
- Provider B `COMPLETE`

All four submissions were recorded with:

`sig_valid=True`

and:

`verification_code=ok`

The relay returned HTTP:

`204`

Final provider state confirmed one B01 execution and one consumed B01 authorization at each provider.

Result:

**PASS**

## Scored D01 policy divergence

Request representation:

`7c954784d82d0d80509f70e8eca810f2dbbf1c6ae74b6fe72672903d73c30505`

Verification context:

`CTX_MP002_DIVERGE`

Provider A authorization ID:

`07f8f83fc040d9f88d2b1f98dabb5ed73ad1788dd96de58ed1da41fb32a30e98`

Provider B authorization ID:

`017ea9125ded9e79bf52b10be8471744848417f37c5e8d121828aa470757bfab`

Observed association events:

- Provider B `DENY policy_denied`
- Provider A `START`
- Provider A `COMPLETE`

All three submissions were recorded with valid signatures.

Final provider state confirmed:

- Provider A consumed the D01 authorization;
- Provider A executed D01;
- Provider B did not consume the D01 authorization;
- Provider B did not execute D01.

Result:

**PASS**

## Association provenance

The association recorder was unchanged from MP001.

It verifies individual provider boundary submissions and appends them to a hash-chained record.

It does not calculate:

- provider quorum;
- `1/2` or `2/2` completion;
- distributed commit;
- overall operation authorization;
- cross-provider success or failure.

Accordingly, MP002 publication material does not attribute such a decision to the scored recorder.

The recorded D01 facts are:

- Provider B produced a valid signed denial;
- Provider A produced valid signed start and completion events.

Any higher-level summary of those facts is documentation or post-run interpretation, not an execution decision made by the association.

## Association log integrity

Final association record hash:

`7002cd90fcf586dd145c6156ca3ed5da18f267138796099f536c4df53798013a`

SHA-256 of the preserved scored `association.jsonl`:

`d3025b6b55331dfe4505f0a1ddc82fdb1776f5dcc30449b77f683b7ed258d9e8`

The association hash chain was independently checked during publication staging and terminated at the same final record hash recorded in the scorecard.

## Final scored provider state

Provider A:

- executions: `2`
- spent authorizations: `2`

Provider B:

- executions: `1`
- spent authorizations: `1`

D01 Provider A authorization consumed:

`True`

D01 Provider B authorization consumed:

`False`

These counts reconcile with the scored cases:

- Provider A executed B01 and D01.
- Provider B executed B01 only.

The final provider state was copied into:

`evidence/scored/final_provider_a/`

and:

`evidence/scored/final_provider_b/`

before the provider processes were shut down.

## Shutdown verification

After evidence capture:

- Provider A was stopped.
- Provider B was stopped.
- the relay was stopped.
- the association recorder was stopped.

Subsequent process checks returned:

`PROVIDER_A_DOWN`

`PROVIDER_B_DOWN`

`RELAY_DOWN`

No listener remained on the association port.

## Scored evidence integrity

The scored evidence tree contains:

- locked contract;
- locked run manifest;
- scorecard;
- association log;
- deployed implementation hashes;
- B01 request and authorization artifacts;
- D01 request and authorization artifacts;
- final Provider A state;
- final Provider B state;
- `SHA256SUMS.txt`.

During publication staging:

- all 19 entries in the scored `SHA256SUMS.txt` verified;
- the staged scored copy matched the source scored folder byte-for-byte;
- the scored folder contained no additional unlisted files;
- the source implementations matched the recorded deployed hashes.

## Publication staging

The publication tree was built as a copy.

Nothing in the working MP002 tree was moved, renamed, or rewritten in order to construct the GitHub package.

Staging location:

`MULTI_PROVIDER_002/github/modules/multi-provider/MP002/`

The staged tree contained 56 files before the publication documentation files were added.

Original filenames were preserved.

This includes the provider key filenames used by the actual implementation.

No key files were renamed merely to make the tree stylistically uniform.

## Files excluded from publication staging

The staging process excluded:

- `__pycache__/`
- compiled Python cache files;
- provider working runtime-state duplicates where authoritative scored copies already exist under `evidence/scored/`.

No scored evidence was discarded as part of those exclusions.

The preserved final provider execution and spent-state files remain in the scored evidence tree.

## Cross-provider atomicity

MP002 intentionally does not provide cross-provider atomicity.

In D01:

- Provider A executed.
- Provider B denied.

Provider A does not wait for Provider B.

Provider B does not wait for Provider A.

The test therefore demonstrates independent provider-local judgment, not an all-or-nothing distributed transaction.

A system that requires every necessary provider to approve before any provider produces an external consequence would require a separate composition, quorum, or pre-execution gating mechanism.

That mechanism was not part of MP002.

## Unconsumed Provider B authorization

Provider B's D01 authorization remained valid and unspent after the policy denial because the policy branch occurs before authorization consumption.

This was an observed consequence of the locked implementation ordering.

MP002 did not subsequently change Provider B's policy and replay that authorization.

The test therefore does not establish what would occur under later:

- policy change;
- expiration;
- revocation;
- restart;
- reuse.

No such claim is made.

## Claim boundaries

MP002 supports a narrow result:

**Two independently controlled providers received the same distributed operation with valid provider-specific authorization and retained independent execution judgment. Provider A executed while Provider B denied under its own local policy, and no relay, provider, or association component overrode Provider B's decision.**

MP002 does not establish:

- cross-provider atomicity;
- quorum-gated execution;
- all-provider approval before consequence;
- globally synchronized chronology;
- implementation diversity;
- compromised-provider containment;
- independent association re-verification as part of the scored run;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- physical actuation;
- independent hardware-witness evidence.

Those properties require separate tests.

## Publication principle

MP002 is published so the implementation, experimental delta, locked conditions, provider evidence, association record, and stated limitations can be inspected independently.

The intended evidentiary chain is:

locked test definition  
→ identifiable deployed implementation  
→ preserved request and authorization artifacts  
→ provider-local durable state  
→ signed association evidence  
→ integrity manifests  
→ scoped interpretation

The documentation does not replace that evidence.

It describes what the preserved evidence supports and where the test stops.
