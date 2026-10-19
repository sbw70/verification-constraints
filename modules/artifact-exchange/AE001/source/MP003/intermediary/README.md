# AE001 Intermediary Source

This directory contains the copied MP003 relay implementation used as the AE001 intermediary.

## Contents

```text
intermediary/
└── nuvl_multi_relay.py
```

## Role

The relay accepts the requester submission, derives the request representation and binding required by the existing MP003 protocol, and forwards provider-specific authorization material to the configured providers.

Its role is transport and request construction.

It does not become the provider's authorization authority.

The relay does not:

- issue provider authorization;
- verify provider authorization signatures for admission;
- decide whether a provider should execute;
- mark provider authorization as spent;
- generate provider `START`, `COMPLETE`, or `DENY` packages; or
- receive provider authority merely because authorization material passes through it.

## Request Binding

AE001 reused the existing MP003 request-binding scheme.

The relay derives:

```text
request_repr = SHA256(exact request bytes)
```

and:

```text
binding = SHA256(
    UTF8("NUVL_BIND_V1|" + request_repr + "|" + context)
)
```

The provider-side operation identity is then derived by the unchanged MP003 implementation from that binding.

AE001 did not introduce a new binding scheme.

## Authorization Material

Provider authorization travels through provider-specific HTTP headers.

For the scored AE001 cases, Provider B was the target provider.

The relay mechanically forwarded the supplied Provider B authorization header value without deciding whether that authorization was valid.

In N02, a valid Provider A authorization was deliberately placed in the Provider B header.

The relay transported it.

Provider B rejected it with authenticated:

```text
DENY auth_provider_mismatch
```

That result is part of the tested property: transport by the intermediary did not make Provider A authority valid for Provider B.

## Altered Artifact Case

In N01, a Provider B authorization with an altered signature was transported through the relay.

The relay did not reject the artifact on Provider B's behalf.

Provider B evaluated the artifact and returned authenticated:

```text
DENY auth_bad_sig
```

No Provider B execution or state consumption occurred.

## Relay Response

The requester received HTTP `204` from the relay for transport handling.

That response is not an authorization decision and is not evidence that provider execution occurred.

AE001 establishes provider execution using provider-generated signed boundary packages together with provider execution and state records.

## Observational Audit Hook

AE001's launcher adds an observational outbound `urllib` audit hook around the relay deployment.

The hook records outbound request-construction attempts for evidence collection.

It does not replace relay logic, evaluate authorization semantics, or determine provider execution.

Relay audit entries are therefore corroborating transport evidence.

They are not provider admission evidence by themselves.

## Relationship to the Association Recorder

The relay and association recorder ran as separate processes on the same Raspberry Pi host.

Provider boundary signals were sent directly to the association recorder rather than being returned through the relay as authorization decisions.

The relay therefore did not gain provider authority through the evidence path.

No stronger claim of host isolation between relay and recorder is made.

## Source Identity

`nuvl_multi_relay.py` is a copied MP003 source file used by AE001.

Its exact identity is recorded in:

`../../../configs/AE001_SOURCE_MANIFEST.json`

and the scored run manifest:

`../../../configs/AE001_RUN_MANIFEST.json`

Campaign provenance is documented in:

`../../../PROVENANCE.md`

## Scope

AE001 demonstrates the relay's role within the tested four-case software configuration.

It does not establish:

- resistance to arbitrary relay-host compromise;
- transport confidentiality;
- denial-of-service resistance;
- statelessness as a scored property;
- offline or delayed-delivery behavior;
- global event chronology; or
- universal behavior for every possible intermediary implementation.

The bounded result is that, in the tested configuration, conveying the provider-issued artifact did not transfer provider authorization authority to the intermediary.
