# MP002 Results

## Result

MP002 passed both scored cases.

The test demonstrates that independently controlled providers can receive the same distributed operation with valid provider-specific authorization and still reach different execution decisions under their own local authority.

The scored campaign contained:

- **B01_CONTROL** — both providers permit and execute.
- **D01_POLICY_DIVERGENCE** — Provider A permits and executes while Provider B denies under Provider B's own local policy.

The observed result was:

**provider-local judgment remained independent.**

Provider A's approval did not cause Provider B to execute.

Provider B's denial did not prevent Provider A from exercising Provider A's own authority.

The relay did not override either provider.

The association did not override either provider.

## Claim under test

MP002 asks:

**If multiple independent providers participate in the same distributed operation and each receives valid provider-specific authorization, can each provider retain its own execution decision without another provider or shared infrastructure becoming authoritative over it?**

The scored result supports that claim within the tested implementation.

## Architecture under test

The tested path was:

Requester  
→ NUVL relay  
→ Provider A and Provider B  
→ association recorder

The authority model was:

- Provider A controls Provider A authorization and execution.
- Provider B controls Provider B authorization and execution.
- the relay transports provider-specific authorization but does not originate or enlarge it.
- the association verifies and records signed provider evidence but does not authorize execution.

MP002 extends the MP001 multi-provider baseline with a deterministic local policy gate at Provider B.

## Scored campaign

Scored session:

`MP002_SCORED_20261013`

The contract and manifest were fixed before execution.

Contract SHA-256:

`e795f55172ea27d8ee434679ab9ea4a1b07e1154a708dfd5ad846fdd0f4ab18d`

Manifest SHA-256:

`3f4b317e3c3fc8f34e579941ec79f0f0191fcef122be320973a88b84e5750845`

## B01_CONTROL

### Purpose

B01 established the control path with both providers independently permitting the same operation.

Verification context:

`CTX_ALPHA`

Request representation:

`7bf65d11928d3e32ae1245ce5a6a2f8aeb12ba53644b868630b9e814adc7e35f`

Provider A authorization ID:

`6a7394b62385b6ea2ff9f72a0271c27e75b1c4081d1aa4ff3eb509468587354a`

Provider B authorization ID:

`84064da5fac9cb562ac1f85c96db3fe334725f595e7ed6967babd9ec6df195ea`

### Observed behavior

Provider A:

- authorization accepted;
- authorization consumed;
- `START` emitted;
- local execution recorded;
- `COMPLETE` emitted.

Provider B:

- authorization accepted;
- authorization consumed;
- `START` emitted;
- local execution recorded;
- `COMPLETE` emitted.

The relay returned HTTP:

`204`

The association recorded four valid signed boundary submissions:

- Provider A `START`
- Provider B `START`
- Provider A `COMPLETE`
- Provider B `COMPLETE`

Each recorded submission showed:

`sig_valid=True`

and:

`verification_code=ok`

### Result

**PASS**

Both independent providers completed the control operation under their own provider-specific authority.

## D01_POLICY_DIVERGENCE

### Purpose

D01 tested whether the providers could receive the same distributed operation with valid provider-specific authorization and still reach different execution decisions.

Verification context:

`CTX_MP002_DIVERGE`

Request representation:

`7c954784d82d0d80509f70e8eca810f2dbbf1c6ae74b6fe72672903d73c30505`

Provider A authorization ID:

`07f8f83fc040d9f88d2b1f98dabb5ed73ad1788dd96de58ed1da41fb32a30e98`

Provider B authorization ID:

`017ea9125ded9e79bf52b10be8471744848417f37c5e8d121828aa470757bfab`

### Provider A behavior

Provider A:

- validated its provider-specific authorization;
- permitted the request;
- durably consumed the authorization;
- emitted signed `START`;
- recorded local execution;
- emitted signed `COMPLETE`.

### Provider B behavior

Provider B:

- validated its provider-specific authorization;
- applied its own local policy;
- returned signed `DENY`;
- reported reason `policy_denied`;
- did not consume the D01 authorization;
- did not emit `START`;
- did not execute;
- did not emit `COMPLETE`.

### Association evidence

For D01, the association recorded:

- Provider B `DENY policy_denied`
- Provider A `START`
- Provider A `COMPLETE`

All three submissions passed signature verification.

The association recorder preserves receipt order, but MP002 does not treat that ordering as a globally synchronized chronology across independent hosts.

The recorder does not calculate an authoritative cross-provider result such as `1/2`, `2/2`, quorum, commit, or distributed success.

It records and verifies the provider-produced evidence.

### Result

**PASS**

Provider A executed under Provider A's authority.

Provider B denied under Provider B's authority.

No shared component converted Provider B's denial into Provider B execution.

## Final provider state

After both scored cases, Provider A contained:

- `2` execution records;
- `2` spent authorizations.

Provider B contained:

- `1` execution record;
- `1` spent authorization.

For D01:

`D01_PROVIDER_A_AUTHORIZATION_CONSUMED=True`

`D01_PROVIDER_B_AUTHORIZATION_CONSUMED=False`

The counts reconcile with the scored cases:

- Provider A executed B01 and D01.
- Provider B executed B01 only.

## Provider B policy behavior

The MP002 Provider B policy was deliberately simple and deterministic.

Provider B denies when the verified context is:

`CTX_MP002_DIVERGE`

The claim is not that this is a sophisticated policy engine.

The tested property is that a provider-local decision remains effective at that provider boundary.

In D01:

- Provider A could not override B.
- the relay could not override B.
- the association could not override B.

Provider B retained control over Provider B execution.

## Authorization consumption behavior

Provider B's policy check occurs before durable authorization consumption.

Because D01 was denied at that stage, Provider B's valid D01 authorization remained unspent.

This means MP002 demonstrates:

**authority can remain intact while execution is withheld by provider-local judgment.**

MP002 did not subsequently change Provider B's policy and present the same unconsumed authorization again.

The test therefore does not establish what would occur under later:

- policy change;
- expiration;
- revocation;
- restart;
- reuse.

## Cross-provider atomicity

MP002 does not provide cross-provider atomic execution.

In D01:

- Provider A executed.
- Provider B denied.

Provider A did not wait for Provider B.

Provider B did not wait for Provider A.

That behavior is consistent with the architecture under test and is part of the result.

MP002 therefore demonstrates independent provider judgment, not an all-or-nothing distributed transaction.

A design requiring all required providers to approve before any external consequence occurs would require a separate composition, quorum, or pre-execution gating mechanism.

That behavior was not tested in MP002.

## Experimental delta from MP001

MP002 reused the MP001 distributed baseline and changed Provider B narrowly.

The Provider B runtime added:

`POLICY_DENY_CONTEXT = "CTX_MP002_DIVERGE"`

and a local policy branch that returns:

`DENY policy_denied`

before authorization consumption.

The source difference is published as:

`provider_b/MP001_TO_MP002_PROVIDER_B.diff`

The following scored components were reused unchanged from MP001:

- Provider A runtime;
- Provider A mint utility;
- Provider B mint utility;
- NUVL relay;
- association recorder;
- provider registry.

This narrow delta allows the D01 result to be interpreted as a provider-local policy-divergence test rather than a new architecture.

## Implementation hashes

Provider A runtime:

`c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606`

Provider A mint utility:

`1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec`

Provider B runtime:

`5e0ab4b79df4c97bc7bc324d63da85711728d625b82306cdce6c92592e2ee13e`

Provider B mint utility:

`1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb`

NUVL relay:

`09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4`

Association recorder:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

Provider registry:

`59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d`

## Association integrity

Final association record hash:

`7002cd90fcf586dd145c6156ca3ed5da18f267138796099f536c4df53798013a`

SHA-256 of the scored `association.jsonl`:

`d3025b6b55331dfe4505f0a1ddc82fdb1776f5dcc30449b77f683b7ed258d9e8`

The hash chain was checked during publication staging and terminated at the same final record hash recorded in the scorecard.

## Evidence integrity

The scored evidence set contains:

- locked contract;
- locked run manifest;
- exact B01 request and authorization artifacts;
- exact D01 request and authorization artifacts;
- association log;
- final Provider A durable state;
- final Provider B durable state;
- deployed implementation hashes;
- scorecard;
- `SHA256SUMS.txt`.

During publication staging:

- all 19 entries in `SHA256SUMS.txt` verified;
- the staged scored evidence matched the source scored evidence byte-for-byte;
- the scored directory contained no additional unlisted files;
- staged source files matched their recorded deployment hashes.

The smoke evidence is retained separately and is not substituted for the scored campaign.

## What MP002 establishes

Within the tested implementation, MP002 demonstrates:

1. Multiple providers can receive the same distributed operation without sharing provider authority.
2. Each provider can validate its own provider-specific authorization.
3. Providers can independently reach different execution decisions.
4. Provider A's approval does not cause Provider B to execute.
5. Provider B's denial does not prevent Provider A from exercising Provider A's own authority.
6. The relay does not become provider execution authority.
7. The association can preserve signed evidence of divergent provider outcomes without becoming execution authority.
8. Provider-local denial can occur before authorization consumption, leaving the valid authorization unspent.

## What MP002 does not establish

MP002 does not establish:

- cross-provider atomicity;
- quorum-gated execution;
- all-provider approval before consequence;
- globally synchronized cross-host chronology;
- implementation diversity between providers;
- behavior of the unconsumed D01 authorization after a later policy change;
- compromised-provider containment;
- independent association re-verification as part of the scored run;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- physical actuation;
- independent hardware-witness evidence.

Those properties require separate tests.

## Conclusion

MP001 established that the multi-provider architecture could operate across physically separate hosts while preserving provider-specific authorization boundaries.

MP002 extends that result from **separate control** to **separate judgment**.

Both providers received the same distributed operation with valid provider-specific authorization.

One executed.

One denied.

Neither provider's decision became authority over the other, and neither the relay nor the association replaced those provider-local decisions.

That is the result MP002 was designed to test.
