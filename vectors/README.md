# OLP Reference Vectors

This directory contains machine-readable vectors used by the reference implementation.

- `0003-record-identity-v1.json` reproduces OLP Specification 0003, Section 24 (`OLP-TV-1`).
- `0004-proof-input-v1.json` reproduces OLP Specification 0004, Section 26, including the deterministic ProofInputV1 bytes and Ed25519 proof value.
- `milestone13-end-to-end-v1.json` combines the Specification 0003 record with the Specification 0004 test seed to exercise the full Milestone 13 create/verify pipeline.

The first two vectors are normative-specification reproductions. The end-to-end vector is reference-derived and is intended to become input to the executable conformance corpus in Milestone 14.

Test-vector private keys MUST NOT be reused in production.
