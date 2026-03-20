# Provider

This is the authoritative verification and execution component in the NUVL architecture.

It is the only system that:

- validates requests  
- verifies tokens  
- enforces replay protection  
- initiates execution  

NUVL does not authorize anything. All decisions happen here.

---

## Role

The provider receives artifacts forwarded by NUVL and determines whether a request is valid.

If and only if validation succeeds, the provider initiates execution.

Successful validation results in:

`INITIATED`

---

## Accessibility

The provider is not publicly exposed.

- It does not accept external traffic  
- It is only reachable internally  
- Direct access is rejected  

All interaction must pass through NUVL.

---

## Request Format

The provider expects a JSON payload:

{ "request_repr": "", "verification_context": "", "provider_token": "" }

---

## Token Structure

The `provider_token` is a base64-encoded JSON object:

{ "r": "", "c": "", "n": "", "e": "", "s": "" }

All fields must be present and valid.

---

## Validation Process

The provider enforces:

1. JSON integrity  
2. Required fields present  
3. Token decoding  
4. Type validation  
5. Request hash match (`r == request_repr`)  
6. Context match (`c == verification_context`)  
7. Expiry check  
8. Signature verification (HMAC-SHA256)  
9. Replay protection (nonce tracking)  

Any failure results in rejection.

---

## Replay Protection

- Nonces are tracked in memory  
- Expired nonces are cleaned automatically  
- Reuse of a nonce results in rejection  

---

## Execution

If all validation checks pass:

- the request is considered valid  
- the provider initiates execution  
- `INITIATED` is printed  

This is the only success condition in the system.

---

## Stats

The provider continuously tracks runtime metrics:

- total attempts  
- initiated operations  
- denied requests  
- denial reasons  
- average response time  
- requests per second  
- uptime  
- peak CPU usage  
- peak memory usage  

Stats are written to `stats.json` and updated continuously while running.

Live stats are available at:
http://134.209.221.94:8000/stats

---

## Security Model

- Provider is not externally reachable  
- All requests must pass through NUVL  
- Signing secret never leaves the provider  
- Verification occurs entirely within this boundary  

There is no external authority.

---

## Notes

- This is an enforcement boundary, not a simulation  
- No identity system is used  
- Authority is execution-scoped and provider-controlled
