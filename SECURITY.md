# Security

This repository contains reference code and architectural constraint documentation for provider-controlled verification systems.

The reference implementation is intentionally minimal. It is not a complete security product, identity provider, policy engine, service mesh, API gateway, or authorization service.

## Reporting Issues

Report security issues or boundary inconsistencies to:

contact@xer0trust.com

Please include:

- affected file or module
- expected behavior
- observed behavior
- reproduction steps, if available
- whether the issue could allow invalid traffic to be accepted, misclassified, replayed, or forwarded incorrectly

## Boundary Rule

Components outside the provider-controlled execution boundary should not acquire authorization authority.

NUVL specifically should not:

- mint provider tokens
- hold provider signing material
- evaluate provider authorization policy
- retain cross-request authorization state
- decide execution
- relay provider decisions as its own authority

Provider systems remain responsible for signing material, token issuance, policy, authorization, execution, logging, and downstream controls.
