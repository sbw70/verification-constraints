# Client

This is a reference implementation of a valid request path through NUVL.

It demonstrates how a request is structured and sent, without exposing how tokens are generated or validated.

---

## Role

The client sends requests to NUVL using the expected headers and payload format.

It represents the normal, non-malicious path through the system.

This file does not:

- generate tokens  
- validate tokens  
- contain any signing logic  

It only demonstrates request structure.

---

## Target

Requests are sent to:

`NUVL`

All requests must pass through this boundary.

The client does not and cannot communicate directly with the provider.

---

## Request Structure

Each request includes:

### Body

{"op":"initiate","target":"gate","mode":"standard"}

### Headers

Content-Type: application/octet-stream X-Verification-Context:  X-Provider-Token: 

---

## Token Handling

The client does not create tokens.

A valid token must be supplied externally:

PROVIDER_TOKEN = "PASTE_PROVIDER_TOKEN_HERE"

Without a valid token, requests will be rejected by the provider.

---

## Behavior

- Sends one request every 60 seconds  
- Prints response status codes  
- Continues running until stopped  

This creates a low, steady stream of legitimate traffic.

---

## Purpose

This client exists to:

- show the expected request format  
- demonstrate the correct request path  
- provide baseline traffic during testing  

It does not assist in bypassing validation.

---

## Notes

- This is not an exploit tool  
- No secrets are included  
- All validation occurs inside the provider  
- Requests that succeed will cause the provider to print:

`INITIATED`
