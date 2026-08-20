# Milestone 23 Transport Encoding Vector Index

Profile: `transport-encoding-v1`

Capability: `olp.transport-encoding.v1`

Total cases: **22**

| Case | Category | Operation |
|---|---|---|
| `m23.identity.record.001` | positive | `encode_identity_text` |
| `m23.identity.proof.001` | positive | `encode_identity_text` |
| `m23.identity.bundle-alias.001` | positive | `encode_identity_text` |
| `m23.identity.decode.001` | positive | `decode_identity_text` |
| `m23.ojve.bytes.001` | positive | `encode_ojve` |
| `m23.ojve.large-positive.001` | positive | `encode_ojve` |
| `m23.ojve.large-negative.001` | positive | `encode_ojve` |
| `m23.ojve.map-keys.001` | positive | `encode_ojve` |
| `m23.ojve.nested.001` | positive | `decode_ojve` |
| `m23.envelope.json.001` | positive | `encode_transport_envelope` |
| `m23.envelope.extension.001` | positive | `decode_transport_envelope` |
| `m23.record.equivalence.001` | positive | `transport_record_equivalence` |
| `m23.proof.equivalence.001` | positive | `transport_proof_equivalence` |
| `m23.identity.padding.001` | malformed | `decode_identity_text` |
| `m23.identity.padbits.001` | malformed | `decode_identity_text` |
| `m23.identity.kind-mismatch.001` | malformed | `decode_identity_text` |
| `m23.ojve.unsafe-number.001` | malformed | `decode_ojve` |
| `m23.ojve.noncanonical-int.001` | malformed | `decode_ojve` |
| `m23.ojve.duplicate-key.001` | malformed | `decode_ojve` |
| `m23.envelope.message-type.001` | malformed | `encode_transport_envelope` |
| `m23.ojve.unknown-tag.001` | unsupported | `decode_ojve` |
| `m23.envelope.version.001` | unsupported | `decode_transport_envelope` |

The profile is additive and does not modify frozen `core-v1`, `bundle-v1`, `resolution-v1`, `identity-authority-lifecycle-v1`, or `privacy-disclosure-v1` case sets.

The corpus intentionally covers only the deterministic non-network subset of Specification 0012. Streaming, HTTP endpoint/status semantics, content negotiation, `Content-Digest`, HTTP Message Signatures, authentication/authorization, redirects, caching, rate limiting, and live network privacy are outside M23 and require separate review.
