# Open Layer Protocol — 0003 — Record Representation and Identity

**Status:** Draft  
**Version:** v0.1  
**Stability:** Experimental  
**Milestone:** 3 — Record Representation  
**Filename:** `specification/0003-record-representation.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) record representation layer.

It makes the conceptual Record envelope from Specification 0002 deterministic and content-addressable by defining:

- the abstract OLP record value model;
- the OLP Canonical Identity Encoding v1 (`OLP-CIE-1`);
- the OLP Content Identity construction v1 (`OLP-CI-1`);
- the stable 32-octet Record Identity digest;
- semantic identifiers and extension naming;
- reference and resource identity rules;
- core record-envelope validation;
- semantic binding/profile representation;
- temporal and lifecycle representation boundaries;
- native interchange requirements; and
- conformance vectors and security requirements.

The record layer establishes immutable identity-bearing evidence.

It does **not** define cryptographic signatures, trust scores, universal identity, reputation, or transport APIs.

Proofs are defined by Specification 0004 and are detached from records.

---

## 2. Scope

This specification answers:

> Given an abstract OLP record, how do independent implementations decide whether it is well-formed and derive exactly the same Record Identity bytes?

It defines the identity representation, not one mandatory storage or transport representation.

An implementation MAY store or transport a record using JSON, CBOR, a database object, an in-memory structure, or another format, provided conversion to the abstract OLP value is unambiguous and produces the same `OLP-CIE-1` identity bytes.

---

## 3. Requirements language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are interpreted as described by RFC 2119 and RFC 8174 when written in all capitals.

---

## 4. Core invariants

### 4.1 Identity is derived from semantic content

A Record Identity MUST be derived from the exact identity-bearing abstract record value defined by this specification.

### 4.2 Transport is not identity

Whitespace, JSON member order, database column order, HTTP framing, filenames, and other transport/storage details MUST NOT change Record Identity when they decode to the same abstract record.

### 4.3 Identity-bearing mutation creates a new record

After a Record Identity is established, changing any identity-bearing field creates a different Record Identity.

### 4.4 Proofs are detached

Proofs, resolver results, local verification results, and application trust decisions MUST NOT be inserted into the Record Identity preimage merely because they are stored next to a record.

### 4.5 Local metadata is excluded

Local ingestion time, cache state, database identifiers, UI labels, and processing status are not identity-bearing unless intentionally represented inside the record itself.

### 4.6 Canonicalization is deterministic

Two conforming implementations given the same abstract record MUST produce byte-for-byte identical `OLP-CIE-1` identity bytes and the same SHA-256 Record Identity digest.

### 4.7 No Unicode guessing

Text strings are authenticated as exact Unicode scalar sequences encoded as UTF-8.

Implementations MUST NOT silently apply Unicode normalization, case folding, trimming, URI normalization, or locale-dependent transformation during identity construction unless a specific semantic profile defines such transformation before the abstract record is formed.

### 4.8 No floating-point ambiguity

Floating-point values are not permitted in the `OLP-CIE-1` identity value model.

Applications requiring decimal or scientific quantities SHOULD use an explicit semantic representation such as scaled integers, decimal strings with profile-defined grammar, or a future standardized numeric profile.

---

## 5. Abstract identity value model

An identity-bearing OLP value is one of:

```text
null
boolean
integer
byte string
text string
array
map
```

### 5.1 Null

Exactly one null value exists.

### 5.2 Boolean

Exactly `false` or `true`.

### 5.3 Integer

Integers MUST be mathematical integers representable by deterministic CBOR major types 0 or 1 without bignum tags.

Draft v0.1 therefore permits values in the range supported by unsigned 64-bit CBOR argument encoding and its corresponding negative range:

```text
-18446744073709551616 .. 18446744073709551615
```

Profiles SHOULD use narrower ranges when interoperability with common programming languages requires it.

### 5.4 Byte string

An ordered sequence of zero or more octets.

### 5.5 Text string

A sequence of Unicode scalar values encoded as well-formed UTF-8.

Ill-formed UTF-8 is forbidden.

### 5.6 Array

An ordered finite sequence of identity values.

Array order is semantically significant unless the specification defining the field explicitly declares set semantics and specifies deterministic pre-sorting.

### 5.7 Map

A finite mapping whose keys MUST be text strings and MUST be unique.

Duplicate map keys are malformed.

The value for each key is any permitted identity value.

### 5.8 Forbidden CBOR/host-language values

The identity model does not include:

- floating-point numbers;
- NaN or infinity;
- CBOR `undefined`;
- arbitrary CBOR tags;
- indefinite-length values;
- duplicate map keys; or
- host-language objects without an explicit OLP mapping.

---

## 6. OLP Canonical Identity Encoding v1 (`OLP-CIE-1`)

### 6.1 Basis

`OLP-CIE-1` encodes the abstract identity value using deterministic CBOR compatible with RFC 8949.

It is an internal canonical identity encoding.

It is not a requirement that OLP records be transported as CBOR.

### 6.2 Preferred integer and length encoding

Integers and lengths MUST use the shortest CBOR representation that preserves the value.

Non-preferred integer or length encodings are non-canonical for identity construction.

### 6.3 Definite lengths

Arrays, maps, byte strings, and text strings MUST use definite lengths.

Indefinite-length encoding is forbidden.

### 6.4 Map ordering

Before encoding a map, implementations MUST deterministically encode every text-string key using `OLP-CIE-1` and sort entries in ascending bytewise lexicographic order of the complete deterministic CBOR encoding of each key.

This ordering is part of `OLP-CIE-1`, matches the deterministic-CBOR rule used by Specification 0004, and MUST NOT depend on source-language map iteration order.

### 6.5 Simple values

`false`, `true`, and `null` use their preferred single-octet CBOR encodings.

No other simple values are defined by `OLP-CIE-1` v1.

### 6.6 Tags

CBOR tags MUST NOT appear in `OLP-CIE-1` v1.

Semantic meaning is carried by OLP structures and semantic identifiers rather than CBOR tags.

### 6.7 Exact round trip

A conforming decoder used for identity validation MUST reject encodings that cannot be mapped unambiguously to the abstract OLP value model.

A transport decoder MAY accept non-canonical transport CBOR where the transport specification permits it, but Record Identity MUST always be computed by re-encoding the abstract record through `OLP-CIE-1`.

---

## 7. Semantic identifiers

### 7.1 Purpose

A `SemanticIdentifier` names a record type, profile, binding role, extension, relation, action, or other protocol semantic value where a specification requires an identifier.

### 7.2 Core identifiers

Core OLP specifications MAY define compact lowercase ASCII identifiers.

A compact core identifier MUST match:

```text
[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*
```

Core compact identifiers are reserved to OLP specifications.

### 7.3 Extension identifiers

Third-party semantic identifiers MUST be globally unambiguous absolute URIs unless a later registry/profile explicitly defines another collision-resistant namespace.

### 7.4 Exact comparison

Semantic identifiers are compared as exact strings unless the defining specification explicitly states otherwise.

A processor MUST NOT silently URI-normalize, case-fold, percent-decode/re-encode, or otherwise rewrite an authenticated identifier.

---

## 8. Record envelope v1

The abstract Record envelope is:

```text
RecordV1 = {
    "envelope_version": 1,
    "type": SemanticIdentifier,
    "content": OLPValue,
    "semantic_bindings"?: Map,
    "profiles"?: Array,
    "relationships"?: Array,
    "extensions"?: Map
}
```

### 8.1 Required fields

The following fields are REQUIRED:

```text
envelope_version
type
content
```

### 8.2 `envelope_version`

MUST equal integer `1` for Draft v0.1.

### 8.3 `type`

MUST be a valid `SemanticIdentifier`.

### 8.4 `content`

MUST be a valid OLP identity value.

The semantic profile identified by `type` determines additional content constraints.

### 8.5 `semantic_bindings`

If present, MUST be a map from semantic identifiers to identity values defined by the applicable binding specification.

The map MUST NOT contain duplicate keys.

### 8.6 `profiles`

If present, MUST be an array of unique semantic identifiers.

`profiles` has set semantics.

Before identity construction, profile identifiers MUST be sorted in ascending bytewise lexicographic order of their UTF-8 encodings.

An empty `profiles` array MUST be treated as absent when constructing `OLP-CI-1`.

### 8.7 `relationships`

If present, MUST be an array whose semantics are defined by the record type/profile.

General evidence-graph relationships SHOULD use Specification 0005 relationship records.

An empty `relationships` array MUST be treated as absent when constructing `OLP-CI-1`.

### 8.8 `extensions`

If present, MUST be a map keyed by globally unambiguous extension identifiers.

Core field names MUST NOT be redefined inside `extensions`.

An empty extension map MUST be treated as absent when constructing `OLP-CI-1`.

### 8.9 Duplicate source properties

A serialized representation containing duplicate record-envelope property names MUST be rejected before identity construction.

Implementations MUST NOT use parser-specific “first wins” or “last wins” behavior.

---

## 9. OLP Content Identity v1 (`OLP-CI-1`)

### 9.1 Identity preimage

Record Identity is computed over the following exact eight-element abstract array:

```text
OLPCI1RecordPreimage = [
    "OLP-RECORD",
    1,
    type,
    content,
    semanticBindings,
    profiles,
    relationships,
    extensions
]
```

The array MUST contain exactly eight elements.

### 9.2 Optional-field canonical values

For identity construction:

- absent `semantic_bindings` is encoded as an empty map `{}`;
- absent `profiles` is encoded as an empty array `[]`;
- absent `relationships` is encoded as an empty array `[]`; and
- absent `extensions` is encoded as an empty map `{}`.

This removes absent-versus-empty identity ambiguity.

### 9.3 Domain separation

The fixed text string `OLP-RECORD` is the v1 record-identity domain separator.

It MUST appear exactly at index `0`.

### 9.4 Version

Integer `1` at index `1` identifies the `OLP-CI-1` preimage structure.

It is deliberately separate from future transport versions.

### 9.5 Canonical bytes

The complete preimage is encoded using `OLP-CIE-1`.

The resulting byte string is called the **Record Identity Bytes**.

### 9.6 Digest

The **Record Identity Digest** is:

```text
SHA-256(Record Identity Bytes)
```

and is exactly 32 octets.

SHA-256 is fixed for `OLP-CI-1`.

Changing the hash algorithm would define a different Record Identity version rather than silently changing v1 identity.

### 9.7 Equality

Two records have the same OLP v1 Record Identity if and only if their 32-octet Record Identity Digests are byte-for-byte equal.

Applications comparing records SHOULD also retain or obtain the underlying record when collision consequences matter; as with any hash identity, security relies on the collision resistance of the selected algorithm.

---

## 10. Textual Record Identity

Binary identity digests are authoritative.

For logs, APIs, filenames, and presentation, Specification 0012 defines the canonical v1 textual form:

```text
r1_<base64url-no-padding>
```

The prefix is a type marker for presentation and is not included in the SHA-256 preimage.

Earlier or application-specific textual encodings MUST NOT change binary Record Identity equality.

---

## 11. Definition Identity

Some ecosystems need stable identity for reusable semantic definitions such as schemas or profiles without confusing those definitions with ordinary evidence records.

`DefinitionIdentityV1` is derived from:

```text
DefinitionIdentityPreimageV1 = [
    "OLP-DEFINITION",
    1,
    semanticIdentifier,
    definitionValue
]
```

The preimage is encoded with `OLP-CIE-1` and hashed with SHA-256.

The resulting digest is exactly 32 octets.

Definition Identity establishes content identity for a definition; it does not make the definition trusted or universally authoritative.

A profile MAY instead identify definitions using an established external content-identity system. OLP SHOULD interoperate rather than duplicate existing schemes where practical.

---

## 12. Blob Identity

External binary resources MAY need content identity without being converted into Records.

`BlobIdentityV1` is:

```text
SHA-256(
    OLP-CIE-1([
        "OLP-BLOB",
        1,
        mediaTypeOrNull,
        rawBlobBytes
    ])
)
```

The digest is exactly 32 octets.

`mediaTypeOrNull` is either a lower-level profile-defined media-type string or `null`.

Including media type prevents applications from silently treating the same octets as semantically interchangeable when the profile considers representation type security-relevant.

A later resource profile MAY define additional content-addressing mechanisms.

---

## 13. References

### 13.1 Record references

A Record reference used for cryptographic processing SHOULD carry the exact 32-octet Record Identity Digest rather than depending only on a mutable database identifier or URL.

Specification 0005 defines the canonical typed `EvidenceRefV1` form for record/proof evidence graphs.

### 13.2 External references

An external reference MAY use an absolute URI or another identifier defined by the applicable profile.

Resolution of an external reference is separate from Record Identity verification.

### 13.3 Reference substitution

A processor MUST NOT substitute the object returned by a locator for a content-addressed target without checking the expected content identity when one is provided.

---

## 14. Semantic bindings and profiles

Semantic bindings and profile identifiers are identity-bearing when present.

A participant cannot change the declared semantic interpretation of an already identified record while retaining the same Record Identity.

A profile declaration is not proof that the record actually conforms to the profile.

Conformance remains a validation result.

---

## 15. Core record content profiles

This specification does not attempt to define every domain schema.

It recognizes the conceptual categories from Specification 0002 and provides minimum expectations.

### 15.1 Claim

A Claim content value MUST identify the proposition being asserted and SHOULD identify its subject where the subject is not implicit in the proposition.

### 15.2 Attestation

An Attestation content value MUST identify the asserted proposition or evidence being attested.

Producer attribution SHOULD be established by an OLP proof rather than an unsigned mutable `signer` field.

### 15.3 Observation

An Observation content value SHOULD distinguish:

- the observed subject;
- the observed value/event/state;
- observation time if asserted; and
- relevant measurement or method context.

### 15.4 Event

An Event content value SHOULD distinguish the event semantics from participant assertions about the event.

### 15.5 StatusChange

A StatusChange content value MUST identify its target and operation under the applicable profile.

Later Specification 0007 defines generic lifecycle statements and should be used for interoperable lifecycle evidence.

---

## 16. Time representation

When a record profile uses a date-time string, it SHOULD use RFC 3339 with an explicit UTC offset unless that profile requires another representation.

The exact authenticated text is identity-bearing unless the profile explicitly defines canonical conversion before record construction.

A producer-declared timestamp is an assertion by the record/proof producer.

It is not independent evidence that the object existed at that time.

---

## 17. Status, correction, dispute, and supersession

Record identity is immutable.

A later lifecycle or relationship statement MUST NOT alter the Record Identity of the historical target.

The following are represented additively:

- correction;
- dispute;
- support;
- contradiction;
- supersession;
- suspension;
- resumption;
- revocation;
- retirement;
- compromise; and
- deprecation.

Specifications 0005 and 0007 define reusable relationship and lifecycle semantics.

---

## 18. Native interchange

An OLP implementation MUST maintain a clear boundary between:

```text
transport representation
        -> abstract OLP value
        -> validation
        -> OLP-CI-1 preimage
        -> OLP-CIE-1 bytes
        -> Record Identity digest
```

A transport adapter MUST NOT calculate Record Identity directly over arbitrary received JSON text, non-canonical CBOR bytes, database serialization, or application object memory.

Specification 0012 defines interoperable JSON and CBOR transport mappings.

---

## 19. Unknown fields and extensions

Unknown top-level record-envelope fields are not permitted in RecordV1.

Third-party identity-bearing data belongs inside `extensions` or a defined semantic `content` profile.

This prevents one parser from including an unknown top-level field in identity while another silently discards it.

Unknown semantic content MAY be preserved when the envelope is structurally valid, but a processor MUST NOT claim to understand or validate unknown semantics.

---

## 20. Resource limits

Implementations MUST impose finite limits suitable for their environment on:

- nesting depth;
- map size;
- array size;
- text-string size;
- byte-string size;
- total record size; and
- canonicalization work.

A record may be structurally valid in the abstract protocol while exceeding a particular implementation's advertised resource profile.

Resource-limit rejection is distinct from cryptographic Record Identity mismatch.

---

## 21. Security considerations

### 21.1 Parser differentials

Duplicate properties, duplicate map keys, non-shortest integer encodings, invalid UTF-8, and ambiguous host-language values can cause different implementations to hash different meanings.

Conforming implementations MUST eliminate these ambiguities before identity construction.

### 21.2 Unicode confusion

Visual similarity and Unicode normalization are application concerns.

Record identity deliberately authenticates exact text.

Applications SHOULD display security-sensitive identifiers in ways that reduce spoofing risk without changing the authenticated value.

### 21.3 Numeric ambiguity

Floating point is forbidden from the identity model because language- and serialization-specific rounding can break deterministic identity.

### 21.4 Hash collision resistance

Record Identity security depends on SHA-256 collision resistance.

A future incompatible identity version MAY adopt another construction if required; it MUST NOT silently reinterpret existing `OLP-CI-1` identities.

### 21.5 Maliciously large records

Canonicalization is attacker-controlled work when records are untrusted.

Implementations MUST enforce resource limits before allocating unbounded memory or recursively processing arbitrary depth.

### 21.6 Semantic confusion

A stable hash proves object identity, not that an application understands the record's semantics.

Unknown or unsupported semantic profiles MUST remain visible.

### 21.7 Local metadata injection

Systems MUST NOT allow database, resolver, cache, or transport metadata to alter the identity-bearing record without intentionally constructing a new record.

---

## 22. Privacy considerations

Content addressing can improve integrity while increasing linkability.

The same record disclosed in multiple contexts has the same Record Identity.

Applications SHOULD therefore:

- avoid unnecessarily monolithic records;
- avoid embedding sensitive data that is not required for the statement;
- use separate records when claims have genuinely separable disclosure needs;
- avoid treating stable Record Identity as an innocuous correlation-free identifier; and
- apply Specification 0010 before exposing evidence broadly.

Deleting a field from an identified record creates a different record; it is not redaction of the same Record Identity.

---

## 23. Conformance requirements

A conforming Record Identity implementation MUST:

1. validate the RecordV1 envelope;
2. reject duplicate source properties;
3. map the record into the exact abstract identity value model;
4. normalize optional absent/empty envelope fields as specified by Section 9.2;
5. sort set-semantic fields before identity construction;
6. construct the exact eight-element `OLPCI1RecordPreimage`;
7. encode it using `OLP-CIE-1`;
8. hash those bytes using SHA-256; and
9. expose the exact 32-octet Record Identity Digest.

It MUST NOT:

- hash arbitrary JSON text;
- hash non-canonical transport CBOR directly;
- include detached proofs;
- include local storage metadata; or
- apply undocumented semantic normalization.

---

## 24. OLP-TV-1 interoperability vector

This vector fixes the basic `OLP-CI-1` pipeline independently of JSON transport.

### 24.1 Abstract record

```text
RecordV1 = {
    "envelope_version": 1,
    "type": "claim",
    "content": {
        "subject": "urn:example:subject:1",
        "statement": "example"
    }
}
```

For identity construction, absent optional fields become:

```text
semanticBindings = {}
profiles         = []
relationships    = []
extensions       = {}
```

The preimage is therefore:

```text
[
    "OLP-RECORD",
    1,
    "claim",
    {
        "subject": "urn:example:subject:1",
        "statement": "example"
    },
    {},
    [],
    [],
    {}
]
```

### 24.2 Expected `OLP-CIE-1` bytes

The exact canonical identity bytes are 72 octets:

```text
886a4f4c502d5245434f52440165636c61696da2677375626a6563747575726e3a6578616d706c653a7375626a6563743a316973746174656d656e74676578616d706c65a08080a0
```

### 24.3 Expected Record Identity digest

```text
c69ed0f4c22fc0242da939d45448ec1fab7464fa054af334927dc0f91741cbb4
```

The digest is exactly 32 octets.

### 24.4 Expected textual presentation

Using the textual form later standardized by Specification 0012:

```text
r1_xp7Q9MIvwCQtqTnUVEjsH6t0ZPoFSvM0kn3A-RdBy7Q
```

A conforming implementation MUST reproduce the exact 72 identity octets and exact SHA-256 digest above from the abstract record in Section 24.1.

---

## 25. Relationship to later specifications

Specification 0004 consumes the exact `OLP-CIE-1` bytes of the `OLP-CI-1` record preimage when computing proof `recordCommitment` values.

It MUST NOT introduce another record canonicalization algorithm.

Specification 0005 uses the exact 32-octet Record Identity Digest inside typed `EvidenceRefV1` record references.

Specification 0008 uses the Record Identity of a bundle manifest record as the bundle's stable identity.

Specification 0012 defines textual presentation and transport mappings without changing binary Record Identity.

---

## 26. References

### Normative

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels.
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
- RFC 3339 — Date and Time on the Internet: Timestamps.
- RFC 3629 — UTF-8, a transformation format of ISO 10646.
- RFC 3986 — Uniform Resource Identifier (URI): Generic Syntax.
- RFC 4648 — Base-N Encodings.
- RFC 8949 — Concise Binary Object Representation (CBOR).
- FIPS PUB 180-4 — Secure Hash Standard (SHA-256).
- OLP Specification 0001 — Terminology.
- OLP Specification 0002 — Protocol Objects.

### Informative

- RFC 8785 — JSON Canonicalization Scheme (JCS), for comparison with serialization-specific canonicalization approaches.

---

## 27. Deferred work

The following are intentionally defined by later specifications:

- detached proof structures and cryptosuites;
- proof identity;
- evidence graph references;
- identity/authority profiles;
- generic lifecycle evaluation;
- bundle manifests;
- resolver/discovery profiles;
- privacy/selective-disclosure profiles;
- executable conformance corpus; and
- JSON/CBOR/HTTP transport profiles.

---

## 28. Design summary

```text
abstract RecordV1
       |
       v
validate exact OLP value model
       |
       v
construct OLP-CI-1 identity preimage
       |
       v
OLP-CIE-1 deterministic CBOR
       |
       v
Record Identity Bytes
       |
       v
SHA-256
       |
       v
32-octet Record Identity Digest
```

Record identity is stable.

Transport is replaceable.

Proofs are detached.

History changes by adding evidence, not rewriting old records.

---

**End of OLP Specification 0003 — Draft v0.1**
