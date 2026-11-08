# Local validation record

The requester allowlist revision is recorded separately in
`requester_allowlist/LOCAL_VALIDATION.json` and `requester_allowlist/offline_tests.txt`.
It reruns the original 18 tests plus the requester-only mock suite. All earlier
records remain byte-identical. `requester_allowlist/PREVIOUS_SHA256SUMS.txt`
preserves the package inventory before this change. Approved remote endpoints
exist only as mocked documentation-address fixtures; the shipped list is empty.

`final/LOCAL_VALIDATION.json` and `final/offline_tests.txt` record the passing
expanded suite: 18 tests, zero failures/errors, sequential loopback mocks only.
The final run used explicitly approved execution outside the Windows sandbox,
because the sandbox denied loopback socket connections with WinError 10013.

`sandbox_socket_denied/` preserves the preceding sandbox-blocked 18-test attempt.
Its errors and dependent delivery-count failure are environment failures; that
attempt is explicitly labeled LOCAL_BUILD_VALIDATION_FAILED. It is not evidence
of successful transport or a scored provider failure.

An earlier development attempt was blocked by Windows sandbox OS-temp-file
permissions. Its approved rerun passed the then-current 16 tests. Tests now place
temporary artifacts under this package's validation/temporary directory, verify
the cleanup target stays there, and remove only those temporary artifacts.

No live provider, real/mocked signing key, lab endpoint, or scored transaction was
used. Authority-shaped mock bytes are deliberately invalid. Independent-hub
subprocesses are created and terminated only for local mock integration tests.

Package hashes are in ../SHA256SUMS.txt. Configuration review hashes and local-only
endpoint scope are recorded in ../CONFIGURATION_FREEZE.json. This local freeze
does not authorize live deployment or approve future live endpoint configurations.
