# NUVL Intermediary

This directory contains the MP001 NUVL multi-provider relay.

The relay accepts an opaque request, derives non-secret correlation material, selects the provider-specific authorization header for each configured provider, forwards separate artifacts asynchronously, and returns HTTP 204 to the requester.

It does not validate provider authorization.

It does not possess provider issuance keys.

It does not decide whether either provider executes.

It cannot originate or enlarge Provider A or Provider B authority.

## File

### `nuvl_multi_relay.py`

The MP001 intermediary implementation.

The relay listens on:

`0.0.0.0:8080`

and accepts requests at:

`POST /nuvl`

The maximum accepted request body size is:

`64 KiB`

Requests outside that limit receive HTTP 204 without provider forwarding.

## Inputs

The relay uses three requester-supplied inputs:

- raw request-body bytes
- `X-Verification-Context`
- provider-specific authorization headers

The provider authorization headers are:

- `X-Provider-A-Authorization`
- `X-Provider-B-Authorization`

The relay does not decode or verify either authorization package.

It mechanically selects the Provider A header for Provider A and the Provider B header for Provider B.

## Request representation

For each accepted request, the relay computes:

`request_repr = SHA-256(raw request body)`

The raw request bytes remain opaque to the relay.

The relay does not interpret the request body to determine whether execution should occur.

## Mechanical binding

The relay computes the MP001 mechanical binding from:

- request representation
- verification context

using the domain-separated form defined by the MP001 contract:

`NUVL_BIND_V1|request_repr|verification_context`

The resulting SHA-256 value is non-secret correlation and integrity material.

It is not provider authority.

A relay capable of recomputing this binding still cannot mint a valid replacement Provider A or Provider B authorization.

## Provider artifacts

For each configured provider, the relay constructs an artifact containing:

- `request_repr`
- `verification_context`
- `binding`
- that provider's authorization transport value

Provider A receives the value supplied in:

`X-Provider-A-Authorization`

Provider B receives the value supplied in:

`X-Provider-B-Authorization`

The relay does not combine the two authorizations into a shared authorization object.

## Provider destinations

The MP001 deployment used:

Provider A:

`http://192.168.1.118:9090/ingest`

Provider B:

`http://192.168.1.106:9090/ingest`

Each provider receives its artifact independently.

These addresses are part of the tested MP001 laboratory topology, not a general deployment requirement.

## Asynchronous forwarding

Provider forwarding is asynchronous.

The relay starts a separate daemon thread for each provider destination.

It does not wait for either provider to:

- validate authorization
- consume authorization
- execute
- emit a boundary statement
- return an application-level outcome

before responding to the requester.

The requester receives:

`HTTP 204`

after the forwarding work has been initiated.

The 204 response therefore establishes receipt and relay handling at the intermediary. It does not establish provider execution.

## Failure behavior

Provider forwarding errors are not returned to the requester.

If a provider destination is unavailable, times out, or otherwise fails during forwarding, the forwarding thread exits without changing the requester's 204 response.

This behavior prevents the relay from becoming the component that decides whether the overall operation is authorized.

Provider availability and provider authorization remain separate concerns.

## What the relay does not do

The relay does not:

- possess provider issuance private keys
- possess provider boundary-signing private keys
- validate provider authorization signatures
- determine whether an authorization is spent
- maintain provider spent state
- maintain provider execution state
- inspect provider-local policy
- create provider authorization IDs
- sign provider boundary statements
- authorize Provider A
- authorize Provider B
- wait for agreement between providers
- require one provider to succeed before forwarding to the other
- make association decisions

The relay's role is transport and mechanical representation handling.

## Hostile-relay significance

MP001 includes a scored hostile-relay mutation case.

In N02, request material was altered and the non-secret binding was recomputed while the original provider authorizations were retained.

Both providers independently rejected the resulting artifacts with:

`auth_request_mismatch`

That result demonstrates the distinction between recomputable relay-side material and provider-issued authority.

A relay that can alter request representation and recompute the public binding still does not acquire the provider issuance keys needed to authorize the changed request.

The corresponding retained artifacts are under:

`../evidence/MP001_SCORED_20261009/`

## Scored implementation hash

The deployed relay used for the scored MP001 campaign had SHA-256:

`09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4`

The value is retained in:

`../evidence/MP001_SCORED_20261009/deployed_implementation_hashes.txt`

## Contract

The normative request representation, mechanical binding, authorization transport, and provider-artifact rules are defined in:

`../configs/MP001_CONTRACT.md`

The contract, rather than this README, is authoritative for the MP001 wire format.

## Scope

This directory contains the intermediary implementation used by MP001.

It does not by itself establish:

- provider authorization validity
- provider execution
- authorization consumption
- association verification
- physical actuation
- campaign PASS or FAIL status

Those properties are documented by the provider implementations and retained MP001 evidence.
