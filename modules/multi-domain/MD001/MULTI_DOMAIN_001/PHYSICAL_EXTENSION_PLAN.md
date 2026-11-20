# ESP-LOCAL-008 extension — design only

No ESP command client was loaded in Domain B in this desktop build, no ESP endpoint
was contacted, and no physical zero-actuation or positive-control result is claimed.
The baseline verifier imports no execution client and issues no execution command.
This source separation is a software property, not independent PWM witness evidence.

Inspect the retained copies and the original ESP_LOCAL_008 provider/presenter,
endpoint-runtime C source and witness README before any bench setup. The source
explicitly configures endpoint PWM GPIO5 for both endpoint instances. The witness
README records final wiring: Servo1 signal -> witness GPIO5; Servo2 signal -> witness
GPIO4. Endpoint GPIO numbers and witness input numbers are distinct. One provider
comment associates Servo2 with GPIO4, but actual runtime source and final witness
documentation distinguish endpoint GPIO5 from witness GPIO4. Do not infer new wiring
from the provider comment. Inspect actual common reference/ground, endpoint identity,
witness pin/build, signal connection and bench wiring before approval.

Frozen endpoint has TCP listener port 19081. Historical addresses and device IDs
in the presenter are evidence-era settings, not verified current assignments.
The witness uses W007 UDP port 19072 and independent RMT RX capture. Published
witness C source selects GPIO5; historical Servo2 capture used a GPIO4 build.
Retrieve and verify the appropriate existing frozen build rather than silently
rewriting source. Retain source/build hashes and partition evidence identities.

Architecture for later review:

1. B artifact handler calls only the assertion verifier and writes a decision.
2. Separate B execution-command handler loads and configures the existing 008 presenter
   capability with a real approved endpoint route, witness control and independent
   provider-issued authority input. It must be present, functioning and available
   during verification windows; disabling/disconnecting it is insufficient.
3. Provider-controlled issuance remains the original 008 provider path, using the
   established ESP_LOCAL_004 test key and unchanged 008 target-bound authority format.
   No MD001 artifact, verdict or signing key is an issuance input. A B acceptance must
   not mint, enlarge, substitute or transmit execution authority.

The original provider requires
`labs/nuvl-edge/esp-local/ESP_LOCAL_004/provider/keys/esp_local_004_private.pem`,
which is absent in this checkout. It pins its private-key SHA-256 and raw public key.
Do not generate a replacement. Restore the established bench test key through the
operator's existing preservation procedure. Confirm its hash and public anchor.
Existing historical authority files may already be spent and must not be treated
as fresh positive-control authority. Resolve available endpoint state, issuance and
the original presenter's frozen-label/typed-authority-ID confirmation workflow before
approving a fresh positive control. No authority was minted here.

Before the extension: inspect handler call graphs and dependency boundaries; prepare
the functioning command client and endpoint connection; verify approved routes without
spending authority; retain configuration and command-handler readiness evidence. Plan
independent witness brackets around B01, B02 and N01, expected zero execution-triggered
servo-like PWM bursts in each. During B02 restart, command capability must be loaded
again and available before the repeated artifact verification.

After separate actuation approval, bracket one independently authorized 008 command
as positive control. Expect one endpoint PWM_COMMAND_BEGIN/END pair, one witness
servo-like burst and established durable authority-consumption evidence. Capture
pre/post witness health and ensure overflow/truncation/error counters do not increase.
Use STATUS/START/MARK/STOP and unique <=20-character run IDs under the original
witness procedure; retain returned hashes, raw witness records/partition images,
serial endpoint logs, state evidence and presenter records. A failed START or pin
mismatch invalidates a zero-signal conclusion. The witness measures electrical
control signals, not mechanical displacement. Restore no state or firmware silently.

Unresolved prerequisites: original key availability; bench identities and wiring;
matching existing firmware/witness binaries and hashes; endpoint authority state;
loaded and functional separate B command path; witnessed brackets and capture health;
separate scored-run and physical-actuation approvals. None blocks desktop validation.
