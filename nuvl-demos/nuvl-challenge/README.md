# NUVL Challenge

This is a live demonstration of a provider-isolated verification boundary. $100 bounty.

## What you're looking at

- `nuvl_core.py`  
  Stateless verification boundary. Does not authorize. Does not hold keys.

- `provider.py`  
  The only authority in the system. Validates requests and decides outcomes.

- `client.py`  
  Reference implementation of a valid request path.

- `attacker.py`  
  Attack harness. Includes multiple strategies already attempted at scale.

---

## Architecture

`client / attacker → NUVL → provider`

- NUVL forwards requests but does not decide outcomes
- Provider performs all verification
- Provider is not publicly exposed

---

## Objective

Make the provider print:

`INITIATED`

That is the only success condition to win **$100**.

If you achieve this, the provider has:

- validated your request
- validated the token
- initiated execution

---

## Constraints

- You do not have the provider signing key
- There is no identity system to exploit
- NUVL does not authorize anything
- All authority exists behind the provider boundary
- Replay attempts are detected and rejected

---

## Observability

The provider tracks:

- total attempts
- initiated operations
- denied requests
- denial reasons
- performance metrics
- system load

Stats update continuously.

Your traffic will show up in real time.

---

## What has already been tried

The included attacker covers:

- malformed tokens
- signature guessing
- replay attacks
- context swapping
- body mutation
- invalid encodings
- burst and load attacks

---

## Notes

- This is not a simulation
- The boundary is real
- The provider enforces all decisions

If you can cause the provider to print:

`INITIATED`

the **$100** is yours.

Good luck.

---

## Live endpoint

Endpoint: `https://challenge.xer0trust.com

Explore the rest of the repository for the full architecture and additional demos.
