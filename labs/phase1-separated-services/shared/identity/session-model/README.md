# Session Model

This directory defines the shared session behavior used across both benchmark paths.

The session model exists to ensure both architectures operate against equivalent session lifecycle behavior during benchmark execution.

Session definitions may include:
- active sessions
- expired sessions
- revoked sessions
- replayed sessions
- invalid session states
- concurrent session behavior

Responsibilities may include:
- session tracking
- expiration handling
- session validation
- replay detection
- lifecycle state transitions

The session model is shared so differences in benchmark behavior are caused by request ordering rather than inconsistent session handling.
