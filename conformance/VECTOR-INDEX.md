# Conformance Vector Index

Harness version: `0.1.0`

Total cases: **41**

| Case | Category | Capability | Operation |
|---|---|---|---|
| `record.identity.spec-vector.001` | positive | `olp.record-identity.v1` | `derive_record_identity` |
| `record.identity.map-order.001` | positive | `olp.record-identity.v1` | `derive_record_identity` |
| `record.identity.profile-set-order.001` | positive | `olp.record-identity.v1` | `derive_record_identity` |
| `record.identity.unicode-no-normalization.001` | positive | `olp.record-identity.v1` | `derive_record_identity` |
| `record.identity.malformed.version.001` | malformed | `olp.record-identity.v1` | `derive_record_identity` |
| `record.identity.malformed.missing-content.001` | malformed | `olp.record-identity.v1` | `derive_record_identity` |
| `record.identity.malformed.duplicate-profile.001` | malformed | `olp.record-identity.v1` | `derive_record_identity` |
| `record.identity.malformed.extension-name.001` | malformed | `olp.record-identity.v1` | `derive_record_identity` |
| `record.commitment.sha256.001` | positive | `olp.record-commitment.sha256.v1` | `derive_record_commitment` |
| `record.commitment.unsupported.algorithm.001` | unsupported | `olp.record-commitment.sha256.v1` | `derive_record_commitment` |
| `proof.input.spec-vector.001` | positive | `olp.proof-input.v1` | `encode_proof_input` |
| `proof.input.metadata-extensions.001` | positive | `olp.proof-input.v1` | `encode_proof_input` |
| `proof.input.critical-order.001` | positive | `olp.proof-input.v1` | `encode_proof_input` |
| `proof.create.end-to-end.001` | positive | `olp.proof.eddsa-ed25519.v1` | `create_proof` |
| `proof.create.metadata.001` | positive | `olp.proof.eddsa-ed25519.v1` | `create_proof` |
| `proof.create.unsupported.cryptosuite.001` | unsupported | `olp.proof.eddsa-ed25519.v1` | `create_proof` |
| `proof.create.unsupported.commitment.001` | unsupported | `olp.proof.eddsa-ed25519.v1` | `create_proof` |
| `proof.create.malformed.verification-method.001` | malformed | `olp.proof.eddsa-ed25519.v1` | `create_proof` |
| `proof.create.malformed.created.001` | malformed | `olp.proof.eddsa-ed25519.v1` | `create_proof` |
| `proof.create.malformed.critical-missing.001` | malformed | `olp.proof.eddsa-ed25519.v1` | `create_proof` |
| `proof.create.malformed.private-key.001` | malformed | `olp.proof.eddsa-ed25519.v1` | `create_proof` |
| `proof.verify.valid.001` | positive | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.context.001` | positive | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.negative.signature.001` | negative | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.negative.record.001` | negative | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.negative.purpose-context.001` | negative | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.negative.method.001` | negative | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.negative.domain.001` | negative | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.negative.challenge.001` | negative | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.negative.expired.001` | negative | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.negative.revoked-status.001` | negative | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.negative.method-unavailable.001` | negative | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.unsupported.cryptosuite.001` | unsupported | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.unsupported.critical-extension.001` | unsupported | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.unsupported.commitment.001` | unsupported | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.unsupported.version.001` | unsupported | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.malformed.proof-value-length.001` | malformed | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.malformed.relative-method.001` | malformed | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.malformed.critical-duplicate.001` | malformed | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.malformed.critical-absent.001` | malformed | `olp.proof-verification.v1` | `verify_proof` |
| `proof.verify.malformed.public-key-length.001` | malformed | `olp.proof-verification.v1` | `verify_proof` |

## Category totals

- positive: 12
- negative: 9
- malformed: 13
- unsupported: 7
