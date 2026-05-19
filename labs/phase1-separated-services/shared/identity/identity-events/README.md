# Identity Events

This directory defines the identity-related event vocabulary used throughout the benchmark environment.

Identity events exist to normalize authentication and session-related telemetry across both request paths.

Standard identity events may include:
- token_received
- token_validated
- token_rejected
- token_expired
- session_created
- session_validated
- session_rejected
- replay_detected
- scope_validation_failed
- identity_context_loaded

The purpose of the identity event layer is to ensure authentication and session behavior remain observable and comparable across both architectures.

Both paths should emit identity events using the same event vocabulary and telemetry structure whenever possible.
