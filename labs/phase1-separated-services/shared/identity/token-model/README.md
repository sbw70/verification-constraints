# Token Model

This directory defines the token model used by both benchmark paths.

The token model is shared so conventional and provider-first paths evaluate the same identity material under different request ordering.

Token definitions may include:
- valid user tokens
- valid admin tokens
- invalid tokens
- expired tokens
- replay tokens
- wrong-scope tokens
- wrong-account tokens

The token model exists to ensure both paths receive equivalent identity inputs while preserving request ordering as the primary benchmark variable.
