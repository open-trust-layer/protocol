# Milestone 23 — Transport Encoding Core

Milestone 23 makes the deterministic, non-network transport-encoding subset of Specification 0012 executable without making HTTP, JSON, or any server architecture part of OLP evidence identity.

## Executable capability

`olp.transport-encoding.v1` is exposed through the separate `transport-encoding-v1` conformance profile.

The executable operations are:

```text
encode_identity_text
decode_identity_text
encode_ojve
decode_ojve
encode_transport_envelope
decode_transport_envelope
transport_record_equivalence
transport_proof_equivalence
```

The capability contains no sockets, DNS, HTTP client/server behavior, authentication, authorization, redirects, caching, request signatures, content digests, or ambient network I/O.

## Textual identity forms

The core implements the Specification 0012 textual presentations:

```text
Record Identity  -> r1_<base64url-no-padding>
Proof Identity   -> p1_<base64url-no-padding>
Bundle ID        -> b1_<base64url-no-padding>
```

A textual identity body represents exactly 32 octets and therefore contains exactly 43 base64url characters.

Decoders reject:

- padding;
- standard Base64 `+` or `/`;
- whitespace or other forbidden characters;
- wrong decoded length;
- non-canonical pad bits; and
- typed-prefix mismatch when a caller requires a specific identity context.

`b1_` is a typed transport presentation of the manifest Record Identity, not a new identity function.

## OJVE-1

The implementation provides the reversible OLP JSON Value Encoding v1 (`OJVE-1`) for:

```text
null
boolean
integer
byte string
text string
array
map
```

Integers in JavaScript's safe integer range may use JSON integer numbers. Larger OLP v1 integers use the exact canonical decimal wrapper:

```json
{"$olp":"int","v":"18446744073709551615"}
```

Byte strings use canonical unpadded base64url:

```json
{"$olp":"bytes","v":"SGVsbG8"}
```

Every abstract OLP map uses the explicit pair form:

```json
{"$olp":"map","v":[[<key>,<value>], ...]}
```

This preserves distinctions such as:

```text
integer key 1
text key "1"
byte-string key h'31'
boolean key true
```

The implementation uses a pair-preserving internal representation at the generic transport layer so host-language dictionary equality or hash coercion cannot collapse distinct abstract keys. Conversion to a concrete protocol object happens only after transport decoding and applies that object's own map-key restrictions.

## Canonical and malformed handling

The core rejects:

- unsafe bare JSON integers that should use the OJVE integer wrapper;
- non-canonical decimal integer spellings;
- duplicate abstract OJVE map keys;
- malformed wrapper shapes;
- unsupported `$olp` tags as unsupported rather than malformed;
- floating-point transport values; and
- excessive depth, collection size, text size, or byte-string size according to explicit implementation limits.

The conformance JSON boundary independently rejects duplicate JSON object names before OJVE interpretation.

## Single-object transport envelope

Milestone 23 implements the Specification 0012 single-object envelope:

```text
OLPTransportEnvelopeV1 = [
    "OLP-TRANSPORT",
    1,
    messageType,
    payload
]
```

For JSON, the corresponding wire object is:

```json
{
  "olp": 1,
  "type": "record",
  "payload": <OJVE-1 value>
}
```

Core message types are accepted directly. Third-party message types must be absolute URI identifiers. Unsupported envelope versions remain distinct from malformed message types.

CBOR output uses the existing deterministic CBOR implementation for reproducible test output, but transport determinism does not create or alter OLP object identity.

## Identity-preserving object round trips

The M23 acceptance corpus includes record and proof equivalence operations.

For records, the implementation:

1. materializes the supplied abstract record under the RecordV1 schema;
2. computes Record Identity;
3. transports the same abstract object through the JSON envelope/OJVE path;
4. decodes and reconstructs RecordV1; and
5. recomputes Record Identity.

The before/after digests must match exactly.

For proofs, the same process reconstructs the actual proof data model and recomputes Proof Identity. `proofValue` bytes must also remain exact.

These tests make the core invariant executable:

```text
transport representation != evidence identity
```

## Deliberate M23 boundary

Milestone 23 does **not** make the HTTP/API sections of Specification 0012 executable.

Deferred to a separately reviewed network/API milestone are:

- streaming frames and sequence truncation;
- HTTP endpoint routing and status mapping;
- immutable HTTP retrieval checks;
- content negotiation;
- `Content-Digest` handling;
- HTTP Message Signatures;
- authentication and authorization;
- redirects and downgrade policy;
- caching and conditional requests;
- rate limits; and
- live network privacy behavior.

Separating encoding from network semantics keeps parser/canonicalization risk independently reviewable before adding request-routing and network trust boundaries.

## Conformance

Milestone 23 uses a separate 22-case `transport-encoding-v1` corpus covering:

- Record, Proof, and Bundle textual identity presentations;
- canonical textual identity decoding;
- byte-string preservation;
- positive and negative large-integer preservation;
- heterogeneous map-key preservation;
- nested OJVE decoding;
- single-envelope JSON/CBOR projection;
- absolute-URI extension message types;
- Record Identity preservation across transport;
- Proof Identity and proof-value preservation across transport;
- forbidden identity padding;
- non-canonical base64url pad bits;
- typed identity-context mismatch;
- unsafe bare JSON integers;
- non-canonical integer wrapper values;
- duplicate abstract map keys;
- malformed message types;
- unsupported OJVE tags; and
- unsupported envelope versions.

The profile is additive. Frozen `core-v1` and all previously accepted higher-layer profiles remain separate and unchanged.

Acceptance requires Python 3.11–3.14 and the independent dependency-free Rust 1.85 implementation to pass the same 22 cases, plus explicit Python↔Rust interoperability tests and source-contract guards preserving implementation independence and identity recomputation.
