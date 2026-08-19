# FLEET-007 — One Noisy Endpoint

## Classification

**Category 1 — NUVL core / no architecture change**

This test exercises the existing five-endpoint NUVL authority path under asymmetric participant load.

No new authority mechanism, trust relationship, execution path, or architectural component was introduced.

## Module / Use Case

Five-endpoint autonomous heterogeneous fleet.

Participant load isolation under disproportionate request generation by one fleet endpoint.

## Objective

Determine whether substantially increased request traffic from one endpoint can degrade, starve, contaminate, or alter expected authorization behavior for the other four fleet participants.

The test specifically evaluates whether:

- the noisy endpoint continues receiving correctly bound authorization results;
- the remaining four endpoints continue autonomous operation;
- authorization outcomes remain correctly associated with endpoint identity;
- physical-effector endpoints continue operating through the normal authority path; and
- asymmetric traffic produces errors, timeouts, unavailable results, duplicate run identifiers, or incorrect authorization outcomes.

## Test Fleet

The five-endpoint fleet consisted of:

- `esp32-field-01`
- `esp32-s3-02`
- `esp32-s3-03`
- `esp32-xiao-servo-01`
- `esp32-xiao-servo-02`

Shared infrastructure:

- Raspberry Pi 5 boundary/coordinator
- Archer network
- provider-controlled decision path
- autonomous endpoint-local request schedules

Authority path remained:

```text
endpoint
  ->
network
  ->
NUVL boundary
  ->
provider-controlled decision
  ->
endpoint action
