# Request Generation

This directory contains request construction and request emission logic used throughout the benchmark environment.

Request generation exists to ensure both benchmark paths receive structurally equivalent requests during testing.

Responsibilities may include:
- request creation
- token assignment
- trace identifier generation
- payload generation
- request serialization
- header generation
- request scheduling
- randomized request variation

Generated requests may include:
- valid requests
- invalid requests
- expired token requests
- replay requests
- administrative actions
- stateful operations
- mixed workload traffic

The purpose of request generation is to normalize request behavior across both architectures so operational differences remain attributable to request ordering rather than inconsistent request construction.
