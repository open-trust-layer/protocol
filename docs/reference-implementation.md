# OLP Reference Implementation — Milestone 13

**Status:** experimental / pre-0.1  
**Specification target:** Draft v0.1, Specifications 0003 and 0004

This directory documents the first executable reference slice of Open Layer Protocol.
It is intentionally small: the implementation proves the deterministic record and proof
core before higher-layer graphs, authority, lifecycle, bundles, resolution profiles, or
network transports are implemented.

## Implemented

- `RecordV1` abstract record envelope validation;
- OLP-CIE-1 deterministic CBOR encoding for the required abstract value subset;
- OLP-CI-1 canonical Record Identity bytes and SHA-256 digest;
- canonical `r1_<base64url-no-padding>` Record Identity presentation;
- Definition Identity v1 and Blob Identity v1;
- algorithm-agile `RecordCommitment` with mandatory COSE hash algorithm `-16` (SHA-256);
- exact nine-element `ProofInputV1` construction;
- authenticated standard proof metadata, extensions, and sorted critical-extension declarations;
- mandatory `eddsa-ed25519-v1` proof creation and verification;
- explicit `ResolvedVerificationMethod` input with no hidden network resolution;
- structured verification results and Specification 0004 reason codes;
- temporal/context checks that remain separate from mathematical signature validity;
- verification-method status reporting that does not retroactively rewrite signature validity;
- implementation resource limits for canonical encoding; and
- executable vectors and negative/mutation tests.

## Deliberately not implemented in Milestone 13

- network/DID/HTTPS resolution;
- proof identifiers and evidence graphs;
- authority evaluation;
- lifecycle/status discovery;
- bundle exchange;
- JSON/CBOR transport decoders from Specification 0012;
- HTTP APIs;
- additional signature suites; or
- a production trust-policy engine.

These belong to later milestones. Their absence is intentional rather than accidental.

## Install for development

```bash
python -m venv .venv
```

Activate the environment, then install the project with test dependencies:

```bash
python -m pip install -e ".[test]"
```

## Run tests

```bash
pytest
```

The Milestone 13 acceptance suite must reproduce the exact bytes and signatures published
in Specifications 0003 and 0004.

## Minimal usage

```python
from olp import RecordV1, ResolvedVerificationMethod, create_proof, verify_proof
from olp.crypto.ed25519 import public_key_bytes

seed = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)

record = RecordV1(
    envelope_version=1,
    type="claim",
    content={
        "subject": "urn:example:subject:1",
        "statement": "example",
    },
)

proof = create_proof(
    record,
    proof_purpose="assertion",
    verification_method="urn:example:olp:test-key-1",
    private_key=seed,
)

method = ResolvedVerificationMethod(
    identifier="urn:example:olp:test-key-1",
    key_type="Ed25519",
    public_key=public_key_bytes(seed),
)

result = verify_proof(record, proof, resolved_method=method)
assert result.cryptographically_valid
```

The private seed above is a public test-vector seed and MUST NOT be used for production keys.

## Implementation philosophy

The reference implementation follows three rules:

1. **Specification first.** Normative behavior comes from the specification, not convenience APIs.
2. **Exact bytes matter.** Canonicalization is tested byte-for-byte, not merely semantically.
3. **No hidden policy.** Cryptographic validity, resolution, context matching, lifecycle state, and trust remain separate results.

If code exposes an ambiguity in the specification, the correct response is to record and fix the
specification rather than silently establishing implementation-specific behavior.
