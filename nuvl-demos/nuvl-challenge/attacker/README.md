# Attacker

This is a multi-strategy attack harness targeting the NUVL → provider request path.

It simulates real-world attempts to bypass provider-side verification.

---

## Role

The attacker generates and sends high volumes of malformed and adversarial requests through NUVL.

It attempts to:

- forge valid tokens  
- bypass validation  
- exploit parsing weaknesses  
- replay previously seen tokens  
- overwhelm the system  

All requests still pass through NUVL.

The attacker has no direct access to the provider.

---

## Target

Requests are sent to:

`NUVL`

All traffic is routed through the verification boundary.

---

## Attack Strategies

This harness includes multiple concurrent attack threads:

- **valid shape attacks**  
  Structurally correct requests with invalid signatures  

- **expired tokens**  
  Tokens with timestamps already expired  

- **missing fields**  
  Tokens missing required components  

- **wrong types**  
  Tokens with invalid data types  

- **context swapping**  
  Reusing tokens with mismatched contexts  

- **replay attacks**  
  Reusing previously sent tokens  

- **body mutation**  
  Corrupting or altering request bodies  

- **malformed base64**  
  Invalid or non-decodable token payloads  

- **oversized payloads**  
  Large request bodies to stress handling  

- **burst traffic**  
  High-concurrency request spikes  

- **signature guessing**  
  Attempts using common and brute-force signing patterns  

---

## Token Generation

The attacker generates tokens using:

- random values  
- guessed structures  
- common signing patterns  
- incorrect or partial data  

No valid signing key is available.

---

## Behavior

- Runs multiple attack threads in parallel  
- Continuously sends requests  
- Tracks basic stats:
  - requests sent  
  - errors  
  - token pool size  
- Prints status updates every 5 seconds  

---

## Purpose

This tool exists to:

- demonstrate attack surface coverage  
- show what has already been attempted  
- validate that provider-side enforcement holds under pressure  

---

## Notes

- This is not a proof-of-concept exploit  
- It does not contain the provider signing key  
- All requests still pass through NUVL  
- Successful bypass requires causing the provider to print:

`INITIATED`
