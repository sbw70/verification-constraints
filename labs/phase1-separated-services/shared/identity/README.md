# Identity Service

This directory contains the shared identity and session infrastructure used by both benchmark paths.

The identity layer exists to ensure both environments operate against the same authentication source, token structure, session behavior, and user model.

This component is shared so identity itself does not become the benchmark variable.

Responsibilities may include:
- token issuance
- session handling
- OAuth/OIDC simulation
- user role definitions
- credential validation
- identity metadata
- token expiration behavior

The purpose of the shared identity layer is to keep request-ordering as the primary comparison focus rather than differences in authentication implementation.
