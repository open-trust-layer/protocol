# OLP Reference Vectors

This directory contains machine-readable vectors used by the reference implementation and specification review.

- `0003-record-identity-v1.json` reproduces the Specification 0003 Record Identity vector.
- `0004-proof-input-v1.json` reproduces the Specification 0004 ProofInputV1 and Ed25519 vector.
- `0005-proof-identity-v1.json` freezes the Specification 0005 Proof Identity v1 construction for the published mandatory-suite proof.
- `0005-evidence-ref-v1.json` freezes `EvidenceRefV1` encodings for both a RecordRef and a ProofRef.
- `milestone13-end-to-end-v1.json` exercises the reference create/verify pipeline.

Draft v0.2 does not alter the existing 0003/0004 bytes. The 0005 vectors were promoted in Milestone 18 only after independent Python/Rust reproduction.

Normative vectors are append-only within a version except for explicitly recorded errata.

Test-vector private keys MUST NOT be reused in production.
