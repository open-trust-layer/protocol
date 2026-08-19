# Open Layer Protocol
## 0003 — Record Representation and Identity
### Draft v0.1

**Status:** Draft  
**Specification:** `0003-record-representation.md`  
**Protocol:** Open Layer Protocol (OLP)

---

## 1. Abstract

This specification defines the representation, canonical encoding, identity construction, semantic-definition binding, reusable representation structures, core Record schemas, interchange format, resource-processing model, and normative conformance vectors for Open Layer Protocol version 1.

Its central requirement is:

> Two independent conforming implementations that possess the same logical OLP Record MUST be able to determine that they possess the same Record without relying on a central registry, mutable network service, transport serialization, application-specific Trust Model, or semantic interpretation of the Record type.

OLP therefore separates:

- logical protocol data from transport representation;
- canonical identity encoding from arbitrary interchange formats;
- immutable Record identity from truth, Trust, authority, provenance, and status;
- semantic identifiers from mutable discovery;
- declared attribution from verified attribution;
- represented occurrence from proof that the occurrence happened;
- status-change evidence from mutable global state.

OLP v1 defines:

```text
Logical OLP value
        ↓
OLP-CIE-1
        ↓
canonical deterministic bytes
```

and:

```text
Logical identity-bearing object
        ↓
OLP-CI-1 domain-separated preimage
        ↓
OLP-CIE-1
        ↓
SHA-256
        ↓
ContentIdentity
```

The design intentionally permits unknown future semantic types to remain preservable, canonicalizable, and identity-verifiable without requiring the implementation to understand their semantics.

---

## 2. Conformance Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as normative requirement terms in the sense of RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

A structure described as **closed** permits exactly the fields defined by its applicable schema and no additional fields.

The notation used in examples is descriptive unless explicitly identified as normative byte representation.

For example:

```text
Example {
    required_field: Value,
    optional_field?: Value
}
```

means that `required_field` is mandatory and `optional_field` is optional.

Human-readable examples in this specification are not an alternative OLP serialization.

---

## 3. Scope

This specification defines:

1. the OLP logical primitive data model;
2. canonical map-key syntax;
3. exact integer and Decimal representation;
4. `OLP-CIE-1`, the canonical identity encoding;
5. SemanticIdentifier syntax and namespace rules;
6. Semantic Definition Manifest v1;
7. `OLP-CI-1`, ContentIdentity, RecordIdentity, DefinitionIdentity, and BlobIdentity;
8. canonical human-readable ContentIdentity text;
9. Record envelope v1;
10. reusable structures used by core Records;
11. Claim v1;
12. Attestation v1;
13. Observation v1;
14. Event v1;
15. Interaction v1;
16. StatusChange v1;
17. temporal representation;
18. schema evolution and unknown-semantics behavior;
19. validation-layer separation;
20. resource and defensive-processing rules;
21. native binary interchange and Record Sequence v1;
22. the baseline implementation capability `OLP-BP-1`;
23. the normative conformance vector suite `OLP-TV-1`;
24. security and privacy considerations relevant to representation and identity.

This specification does not define a universal:

- Trust Model;
- Trust score;
- reputation model;
- identity registry;
- proof or signature suite;
- Holder protocol;
- selective-disclosure mechanism;
- encryption format;
- namespace-authority proof mechanism;
- discovery service;
- synchronization protocol;
- global mutable status registry;
- JSON interchange format.

Such mechanisms MAY be defined independently without altering the immutable representation rules defined here.

---

## 4. Representation Invariants

The following invariants govern OLP v1 representation.

### 4.1 Record identity is not transport identity

A Record is identified from its logical OLP value.

Different lossless transport representations MAY represent the same logical Record.

Transport syntax therefore does not define Record equality.

### 4.2 Identity does not imply truth

A valid RecordIdentity proves only identity of the represented immutable Record under the applicable identity suite.

It does not prove:

- truth;
- authorship;
- attribution;
- authority;
- provenance authenticity;
- current status;
- Trust;
- application acceptance.

### 4.3 Canonicalization is context-free

Canonical identity calculation MUST NOT depend on:

- network access;
- current DNS state;
- Identifier resolution;
- mutable registries;
- current time;
- application Trust Models;
- semantic-definition retrieval;
- current status;
- external aliases.

### 4.4 Unknown semantics do not prevent identity calculation

An implementation MUST be able to canonicalize an otherwise valid OLP logical value without understanding the semantic meaning of its Record type, Predicate, Profile, Extension, Relationship, Identifier scheme, or other semantic identifier.

Semantic understanding and identity calculation are separate processing layers.

### 4.5 Canonicalization does not normalize semantics

`OLP-CIE-1` MUST NOT:

- insert schema defaults;
- remove fields;
- reorder semantically ordered arrays;
- deduplicate values;
- normalize Unicode;
- normalize Identifiers;
- normalize URIs;
- normalize locators;
- convert units;
- convert time systems;
- canonicalize semantic aliases;
- resolve external references.

Schema-level canonical authoring constraints are validated separately from generic canonical encoding.

---

# Part I — Logical Data Model

## 5. OLP Logical Primitive Types

OLP v1 defines exactly the following primitive logical types:

```text
null
boolean
integer
byte string
text string
array
map
```

The recursive logical value model is:

```text
OLPValue =
      null
    | boolean
    | int64
    | byte_string
    | text_string
    | array<OLPValue>
    | map<ProtocolKey, OLPValue>
```

The primitive type universe of `OLP-CIE-1` is permanently frozen.

Future OLP specifications MAY define new semantic structures using these primitives, but MUST NOT silently add new primitive logical types to `OLP-CIE-1`.

A future protocol generation requiring a genuinely new primitive MUST introduce explicitly versioned representation machinery.

---

## 6. Integer

The OLP primitive integer type is an exact signed 64-bit integer:

```text
-9223372036854775808
    <= integer <=
9223372036854775807
```

equivalently:

```text
-2^63 <= integer <= 2^63 - 1
```

An implementation MUST NOT:

- wrap;
- truncate;
- round;
- silently convert through floating point;
- interpret an out-of-range value as an OLP integer.

Values outside this range are not valid OLP v1 primitive integers.

---

## 7. Floating Point

Floating-point values are not an OLP v1 primitive type.

CBOR floating-point representations MUST therefore be rejected when interpreted as OLP v1 logical values.

OLP does not define primitive representations for:

- binary floating point;
- NaN;
- positive infinity;
- negative infinity;
- negative zero.

Exact finite decimal quantities use the reusable `Decimal` semantic structure.

---

## 8. Decimal

OLP v1 defines:

```text
Decimal {
    coefficient: text_string,
    exponent: int64
}
```

The map is closed.

The represented mathematical value is:

```text
coefficient × 10^exponent
```

where `coefficient` is interpreted as an arbitrary-precision signed base-10 integer.

### 8.1 Coefficient lexical grammar

The coefficient MUST be exactly either:

```text
"0"
```

or:

```text
"-"? [1-9][0-9]*
```

subject to the additional rule that a non-zero coefficient MUST NOT end in ASCII digit `0`.

Invalid examples include:

```text
"+1"
"01"
"-01"
"-0"
"1.0"
"1e3"
" 1"
"1 "
"1_000"
"120"
```

A value such as:

```text
120 × 10^-2
```

MUST instead be expressed canonically as:

```text
12 × 10^-1
```

### 8.2 Zero

Zero MUST be represented exactly as:

```text
Decimal {
    coefficient: "0",
    exponent: 0
}
```

No other Decimal representation of zero is valid.

### 8.3 Decimal semantics

Decimal is:

- finite;
- exact;
- non-rounded.

The coefficient is not bounded mathematically by OLP semantics.

Implementation resource guarantees are defined separately in `OLP-BP-1`.

The exponent is an OLP int64.

A semantic schema MAY impose narrower Decimal ranges or precision constraints.

The OLP-CIE-1 encoder MUST NOT rewrite a schema-invalid Decimal into another representation.

---

## 9. Text Strings

An OLP text string is valid Unicode represented as UTF-8 by `OLP-CIE-1`.

OLP core performs no implicit:

- NFC normalization;
- NFD normalization;
- case folding;
- whitespace normalization;
- confusable mapping;
- locale-sensitive transformation.

Therefore the following logically distinct Unicode strings remain distinct:

```text
U+00E9
```

and:

```text
U+0065 U+0301
```

even if they render similarly.

Exact text equality is exact logical Unicode-string equality.

---

## 10. Byte Strings

Byte strings and text strings are distinct OLP primitive types.

A byte string containing UTF-8 bytes is not automatically equivalent to the corresponding text string.

For example:

```text
text "123"
```

is not equal to:

```text
bytes 31 32 33
```

No implicit encoding or decoding occurs.

---

## 11. ProtocolKey

Every map key in the OLP v1 logical model MUST be a text string conforming to:

```text
[a-z][a-z0-9_]{0,63}
```

Therefore:

```text
1 <= ProtocolKey length <= 64 ASCII octets
```

Valid examples:

```text
type
content
semantic_id
shipment_delivered
x509_certificate
```

Invalid examples:

```text
Type
_shipment
123abc
shipment-delivered
shipment delivered
café
```

The restriction applies to:

- core maps;
- type-specific content maps;
- Profile maps;
- Extension maps;
- unknown future OLP-v1 maps;
- Semantic Definition maps;
- Predicate argument maps.

ProtocolKey comparison is exact ASCII comparison.

ProtocolKey is never localized.

---

## 12. Map Semantics

Map ordering has no logical semantic significance.

Duplicate map keys are prohibited.

An implementation MUST detect duplicate map keys before accepting an untrusted input as an OLP logical map.

A parser that silently applies "first wins" or "last wins" semantics to duplicate keys does not conform.

All map keys MUST satisfy ProtocolKey syntax.

---

## 13. Array Semantics

Array order is semantically significant by default.

The generic OLP-CIE-1 encoder MUST preserve array order exactly.

A semantic schema MAY define a particular array as set-like.

If an array is set-like, its schema MUST define one canonical ordering and duplicate policy.

Set-like canonical ordering is validated at the semantic-schema layer, not performed automatically by the OLP-CIE-1 encoder.

Unless a more specific ordering is defined, a set-like collection of structured OLP values SHOULD use lexicographic comparison of each element's standalone `OLP-CIE-1` bytes.

---

## 14. Missing, Null, and Empty Values

OLP distinguishes all of:

```text
absent
null
false
0
""
empty byte string
[]
{}
```

### 14.1 Absence

A field is absent only when the map key is not present.

There is no OLP `undefined` logical value.

### 14.2 Null

`null` means an explicitly present null value.

Schemas SHOULD permit `null` only where null has defined semantics.

An optional field with no value SHOULD normally be omitted rather than set to null.

### 14.3 Empty values

Empty text, empty bytes, empty arrays, and empty maps are real values unless the applicable schema prohibits them.

### 14.4 Defaults

`OLP-CIE-1` MUST NOT:

- insert defaults;
- remove explicit default values;
- translate absence into null;
- translate null into absence;
- normalize empty values.

Schemas SHOULD avoid creating multiple structurally different representations for one semantic state.

---

# Part II — Canonical Identity Encoding

## 15. OLP Canonical Identity Encoding v1

The normative canonical identity encoding for OLP v1 is:

```text
OLP Canonical Identity Encoding v1
OLP-CIE-1
```

`OLP-CIE-1` is a frozen strict deterministic profile of CBOR as defined by RFC 8949.

It maps any valid OLP logical value to exactly one deterministic byte sequence.

---

## 16. OLP-CIE-1 CBOR Profile

`OLP-CIE-1` SHALL use the following restrictions.

### 16.1 Definite lengths only

Indefinite-length:

- byte strings;
- text strings;
- arrays;
- maps;

are prohibited.

### 16.2 Preferred/shortest integer encodings

Integers and lengths MUST use their shortest permitted CBOR representation.

Non-minimal encodings MUST be rejected as native `OLP-CIE-1`.

### 16.3 Map ordering

Map entries MUST be ordered according to the RFC 8949 core deterministic encoding rule:

> bytewise lexicographic comparison of each map key's deterministic CBOR encoding.

Since OLP v1 map keys are text ProtocolKeys, their deterministic CBOR text encoding is used for the comparison.

The encoder MUST NOT rely on source-language insertion order.

### 16.4 Map keys

All map keys MUST be text strings satisfying ProtocolKey syntax.

### 16.5 Duplicate keys

Duplicate map keys are invalid.

### 16.6 Floating point

CBOR floating-point values are prohibited.

### 16.7 Tags

CBOR semantic tags are prohibited.

This includes generic date/time tags and the self-described-CBOR tag.

### 16.8 Simple values

The only permitted CBOR simple values are:

```text
false
true
null
```

Other CBOR simple values, including `undefined`, are prohibited.

### 16.9 Text

Text strings MUST contain valid UTF-8.

No Unicode normalization is performed.

### 16.10 Arrays

Array ordering is preserved exactly.

`OLP-CIE-1` never sorts arrays.

---

## 17. Strict Canonical Acceptance

A byte sequence claiming to be native `OLP-CIE-1` MUST itself satisfy the canonical encoding rules.

An implementation MUST NOT silently:

```text
accept noncanonical CBOR
        ↓
decode it
        ↓
re-encode canonically
        ↓
claim the original input was canonical OLP
```

For accepted native bytes `B` representing logical value `V`:

```text
OLP-CIE-1(V) == B
```

MUST hold byte-for-byte.

---

## 18. Schema Canonicalization Versus Encoding Canonicalization

`OLP-CIE-1` canonicalizes representation, not domain semantics.

For example:

```text
{
    coefficient: "01",
    exponent: 0
}
```

can be validly encoded as an OLP logical map, while simultaneously failing the Decimal schema.

Similarly, a set-like array can be valid `OLP-CIE-1` while failing its schema-defined element ordering.

Therefore:

```text
CIE validity
    ≠
semantic-schema validity
```

An encoder MUST NOT "repair" schema-invalid values.

---

# Part III — Semantic Identifiers

## 19. SemanticIdentifier

A `SemanticIdentifier` is an ASCII-only canonical name for versioned semantics.

It is a name, not a locator.

SemanticIdentifier equality is exact byte-for-byte ASCII string equality.

A SemanticIdentifier is not a URI.

OLP performs no:

- URI normalization;
- percent decoding;
- path normalization;
- case folding;
- Unicode normalization;
- trailing-slash normalization;
- network resolution.

---

## 20. SemanticIdentifier Grammar

OLP defines two forms.

### 20.1 Core form

```text
olp/core/<kind>/<name>/<version>
```

### 20.2 Authority-based form

```text
olp/<method>/<authority>/<kind>/<name>/<version>
```

The first component is always the literal lowercase string:

```text
olp
```

---

## 21. SemanticIdentifier Components

### 21.1 `method`

`method` MUST conform to ProtocolKey syntax.

### 21.2 `kind`

`kind` MUST conform to ProtocolKey syntax.

### 21.3 `name`

`name` MUST conform to ProtocolKey syntax.

### 21.4 `version`

Version syntax is:

```text
v[1-9][0-9]*
```

with numeric value:

```text
1 <= version <= 9223372036854775807
```

Invalid examples include:

```text
v0
v01
V1
v1.0
v1.2.3
v+1
```

Version is not SemVer.

A higher version number does not automatically imply:

- compatibility;
- incompatibility;
- currentness;
- preference;
- supersession;
- superiority.

A version identifies one immutable normative semantic definition.

Normative semantic changes require a new versioned SemanticIdentifier unless variation was explicitly part of the existing frozen definition.

Editorial changes outside identity-bound normative semantics do not require a new SemanticIdentifier.

---

## 22. SemanticIdentifier Length

A complete SemanticIdentifier MUST contain no more than:

```text
512 ASCII octets
```

Since SemanticIdentifiers are ASCII-only, each character occupies one octet.

Component-specific limits continue to apply independently.

---

## 23. Core Namespace

The core form is:

```text
olp/core/<kind>/<name>/<version>
```

The `core` namespace is reserved for semantics defined by the OLP specification process.

Third parties MUST NOT assign new semantics within `olp/core/...`.

A syntactically valid future core SemanticIdentifier unknown to an older implementation SHOULD be classified as unsupported rather than malformed.

---

## 24. Semantic Kinds

OLP v1 recognizes or reserves the following `kind` tokens:

```text
type
profile
extension
relationship
role
proof
identity
predicate
identifier
time_system
event
status_operation
definition_format
```

`proof` is reserved for later proof semantics.

The lexical grammar intentionally allows unknown ProtocolKey-compatible kind tokens.

A lexically valid unknown kind is unsupported, not malformed.

---

## 25. Namespace Methods

OLP v1 normatively supports:

```text
dns
```

as its decentralized namespace method.

Future specifications MAY define additional methods such as self-certifying namespace methods.

An unknown method satisfying the generic lexical envelope is unsupported rather than automatically malformed.

---

## 26. Generic Authority Envelope

For an authority-based SemanticIdentifier:

```text
olp/<method>/<authority>/<kind>/<name>/<version>
```

the authority occupies exactly one path component.

The generic authority component MUST:

- contain 1–253 ASCII characters;
- begin with a lowercase ASCII letter or digit;
- end with a lowercase ASCII letter or digit;
- contain internally only:

```text
a-z
0-9
-
.
_
~
```

A specific namespace method MAY narrow these rules.

It MUST NOT broaden them without explicitly versioned future SID grammar.

---

## 27. DNS Namespace Authority

For:

```text
method = "dns"
```

the authority MUST use canonical lowercase hostname-style ASCII syntax.

Define:

```text
lower = "a"..."z"
digit = "0"..."9"
alnum = lower | digit
```

A DNS label is either:

```text
alnum
```

or:

```text
alnum *(alnum | "-") alnum
```

subject to:

```text
1 <= label length <= 63 ASCII octets
```

Labels are separated by exactly one ASCII period.

The complete authority MUST contain at most:

```text
253 ASCII octets
```

### 27.1 Allowed

Examples:

```text
example.com
3.example.com
123.example
xn--bcher-kva.example
```

### 27.2 Prohibited

Examples:

```text
-example.com
example-.com
foo..example.com
foo_bar.example.com
.example.com
example.com.
Example.COM
bücher.example
```

Uppercase is invalid in canonical OLP DNS authorities.

A terminal DNS root dot is prohibited.

DNS escapes and quoted labels are prohibited.

The DNS root alone is not a valid OLP DNS authority.

---

## 28. Internationalized Domain Names

Unicode U-labels MUST NOT appear directly inside OLP SemanticIdentifiers.

Where an internationalized domain is used, authoring software MAY convert it into an appropriate lowercase ASCII IDNA A-label before the SemanticIdentifier is finalized.

OLP core itself MUST NOT perform:

- U-label to A-label conversion;
- A-label to U-label conversion;
- Unicode domain normalization;

during:

- parsing;
- canonicalization;
- equality comparison;
- RecordIdentity calculation.

A label beginning with `xn--` is not automatically assumed to be a valid IDNA A-label for display purposes.

User interfaces MUST NOT blindly render an unvalidated `xn--` label as Unicode.

Canonical OLP SID comparison remains ASCII byte comparison.

---

## 29. DNS Resolution and Authority

Lexical validity does not require:

- current DNS registration;
- DNS resolution;
- network availability;
- current ownership;
- current certificate validity.

The exact canonical DNS authority identifies the namespace.

The following remain distinct namespaces:

```text
olp/dns/example.com/...
olp/dns/schema.example.com/...
olp/dns/alias.example/...
```

OLP does not follow:

- CNAME;
- DNAME;
- HTTP redirects;
- A/AAAA records;
- TLS certificates;

to determine SemanticIdentifier equality.

Domain transfer or expiration MUST NOT retroactively redefine historical SemanticIdentifiers.

Namespace-assignment authority is a separate verification concern.

---

## 30. Lexically Invalid Versus Unsupported

These states are distinct.

### 30.1 Invalid

For example:

```text
OLP/core/type/claim/v1
olp/core/type/Claim/v1
olp/core/type/claim/v01
olp/core/type/claim/v0
olp/dns/Example.com/type/foo/v1
```

### 30.2 Well-formed but unsupported

For example, in an OLP v1 implementation:

```text
olp/dns/example.com/future_kind/foo/v1
```

or a future namespace method satisfying the generic grammar.

Such identifiers remain preservable as strings.

---

# Part IV — Semantic Definition Binding

## 31. Semantic Definition Concepts

OLP separates:

```text
SemanticIdentifier
SemanticDefinition
DefinitionIdentity
SemanticBinding
DiscoveryLocator
```

A SemanticIdentifier names semantics.

A Semantic Definition defines immutable normative semantics.

A DefinitionIdentity cryptographically identifies an exact immutable Semantic Definition Manifest.

A SemanticBinding binds a SemanticIdentifier to a DefinitionIdentity.

A DiscoveryLocator is only a retrieval hint.

Retrieval location MUST NOT define historical semantics.

---

## 32. SemanticDefinitionManifest v1

A Semantic Definition Manifest is not an OLP Record.

It is an independently canonical OLP logical structure used to calculate `DefinitionIdentity`.

Its schema is:

```text
SemanticDefinitionManifest {
    manifest_version: 1,
    definitions: [SemanticDefinitionEntry, ...],
    dependencies?: [SemanticBinding, ...]
}
```

The map is closed.

`manifest_version` and `definitions` are mandatory.

`dependencies` is optional.

---

## 33. Manifest Version

For this specification:

```text
manifest_version = 1
```

Manifest format version and SemanticIdentifier definition version are independent version axes.

For example:

```text
manifest_version: 1
```

may contain:

```text
semantic_id: ".../v7"
```

---

## 34. SemanticDefinitionEntry

Each entry is:

```text
SemanticDefinitionEntry {
    semantic_id: SemanticIdentifier,
    format: SemanticIdentifier,
    definition: map<ProtocolKey, OLPValue>
}
```

The map is closed.

All fields are mandatory.

`format` MUST be a SemanticIdentifier of kind:

```text
definition_format
```

The Definition Format determines the schema and normative interpretation of `definition`.

---

## 35. Definition Format Bootstrap

OLP v1 defines:

```text
olp/core/definition_format/normative_text/v1
```

Its `definition` schema is:

```text
{
    text: text_string
}
```

The map is closed.

`text` MUST be non-empty.

The exact Unicode text is the immutable normative definition.

No normalization or markup interpretation is implied by OLP core.

`normative_text/v1` is a bootstrap format, not a universal machine-readable schema language.

An implementation can:

```text
verify manifest integrity     yes
preserve normative text       yes
understand arbitrary semantics maybe not
```

---

## 36. Machine-Readable Definition Formats

Additional Definition Formats MAY be standardized by OLP or defined permissionlessly.

Such formats can define:

- declarative schemas;
- constraints;
- ontology structures;
- formal rules;
- other semantic representations.

Retrieving or verifying a Semantic Definition MUST NOT automatically authorize execution of code contained or referenced by it.

Executable semantics require a separately defined security model.

---

## 37. Definition Sets

`definitions` MUST:

- contain at least one entry;
- contain each `semantic_id` at most once;
- be sorted by ascending ASCII `semantic_id`.

Array ordering is a schema-level canonical requirement.

The generic OLP-CIE-1 encoder does not sort the array.

---

## 38. Multiple Definitions in One Manifest

A manifest MAY export more than one SemanticIdentifier.

All exported definitions form one atomic immutable semantic package and share one DefinitionIdentity.

For example:

```text
A → DefinitionIdentity D
B → DefinitionIdentity D
```

does not imply:

```text
A == B
```

It means only that A and B are defined by the same immutable manifest.

Authors SHOULD normally use one definition per manifest.

Multiple definitions SHOULD be grouped only when atomic packaging is intentional, especially for mutually recursive semantics.

---

## 39. Internal Semantic Recursion

Definitions exported by the same manifest MAY refer semantically to one another without creating external DefinitionIdentity dependencies.

Self-recursive semantics are also permitted within one manifest.

This permits:

```text
A refers to B
B refers to A
```

when A and B are defined atomically within one manifest.

---

## 40. External Dependencies

`dependencies`, when present, contains SemanticBinding structures.

It MUST:

- contain at least one entry;
- contain each dependency SemanticIdentifier at most once;
- be sorted by ascending ASCII `semantic_id`;
- exclude core OLP SemanticIdentifiers;
- exclude SemanticIdentifiers exported by the same manifest.

Dependencies bind external non-core semantics required for normative interpretation.

A non-core Definition Format used by an entry MUST itself be bound as a dependency unless it is exported by the same manifest.

---

## 41. Dependency Discovery

The applicable Definition Format determines which positions inside its definition body constitute semantic references requiring bindings.

For machine-readable formats, dependency completeness MAY be mechanically validated where the format permits it.

For:

```text
olp/core/definition_format/normative_text/v1
```

the definition author MUST declare every external non-core SemanticIdentifier on whose semantics the normative text depends.

However, generic automated software MUST NOT claim to have mechanically established complete natural-language dependency coverage merely by scanning the text.

For normative text, dependency completeness MAY require human semantic review.

---

## 42. Dependency Verification

A dependency binding:

```text
X → DX
```

is satisfied only when a candidate manifest:

1. computes to DefinitionIdentity `DX`; and
2. exports SemanticIdentifier `X`.

The correct retrieval procedure is:

```text
retrieve candidate
        ↓
calculate DefinitionIdentity
        ↓
require identity == DX
        ↓
require manifest exports X
        ↓
dependency satisfied
```

A manifest with the correct identity but not exporting X does not satisfy the binding.

---

## 43. Definition Dependency Cycles

Exact external DefinitionIdentity dependency cycles are prohibited.

For example:

```text
D1 depends on D2
D2 depends on D1
```

MUST NOT be required.

Likewise a manifest MUST NOT externally depend on its own DefinitionIdentity.

Such dependencies cannot be constructed without cryptographic fixed-point assumptions.

Intentional semantic recursion SHOULD instead be represented inside one atomic manifest.

---

## 44. DefinitionIdentity Immutability

DefinitionIdentity is calculated over the complete manifest.

Changing any identity-relevant manifest value creates a different DefinitionIdentity.

This includes changes to:

- normative text;
- definition body;
- exported SemanticIdentifier set;
- Definition Format;
- external dependency set.

Therefore identity-bound normative material is immutable.

Non-normative material SHOULD remain outside the manifest, including:

- tutorials;
- examples;
- translations;
- websites;
- repository metadata;
- discovery information;
- implementation guidance.

---

## 45. Semantic Binding Conflict

If the same SemanticIdentifier is associated with two different DefinitionIdentities:

```text
X → D1
X → D2
```

where:

```text
D1 != D2
```

the result is a competing semantic binding.

OLP MUST NOT resolve the conflict through:

- "latest wins";
- current DNS contents;
- download time;
- lexical DefinitionIdentity order;
- website contents;
- implementation preference.

Namespace-assignment authority and applicable policy must be evaluated separately.

---

## 46. Namespace Authority Is Separate

A manifest that contains:

```text
semantic_id:
    "olp/dns/example.com/predicate/foo/v1"
```

does not prove that the manifest was authorized by `example.com`.

Likewise, SemanticBinding integrity does not prove namespace assignment authority.

OLP separates:

```text
which exact semantics?
        ↓
DefinitionIdentity
```

from:

```text
who had authority to assign them to this SID?
        ↓
separate Evidence / policy
```

---

## 47. Discovery Is Not Identity

SemanticDefinitionManifest v1 contains no generic:

```text
url
homepage
repository
mirror
download_url
```

fields.

Discovery hints are mutable operational information and normally remain outside DefinitionIdentity.

A retrieved manifest is trusted for semantic integrity only after its DefinitionIdentity is verified.

---

# Part V — Content Identity

## 48. ContentIdentity

OLP defines a reusable native identity structure:

```text
ContentIdentity {
    domain: IdentityDomain,
    suite: SemanticIdentifier,
    digest: byte_string
}
```

The map is closed.

All three fields are mandatory.

Native equality is exact equality of:

```text
domain
suite
digest
```

---

## 49. OLP Content Identity Suite v1

The OLP v1 canonical content identity suite is:

```text
OLP-CI-1
```

with SemanticIdentifier:

```text
olp/core/identity/content/v1
```

The frozen human alias is:

```text
ci1
```

`OLP-CI-1` uses:

```text
canonical encoding:
    OLP-CIE-1

hash:
    SHA-256

digest length:
    256 bits / 32 bytes

salt:
    none

key:
    none

truncation:
    none
```

Per-object choice of arbitrary hash algorithms is not permitted in OLP v1.

Hash agility occurs through explicit future suite versions.

---

## 50. Identity Domains

OLP-CI-1 defines exactly three identity-domain tokens:

```text
record
semantic_definition
blob
```

These are core closed tokens, not SemanticIdentifiers and not user-extensible values within CI-1.

---

## 51. IdentityPreimage

The exact CI-1 logical preimage is:

```text
IdentityPreimage {
    domain: IdentityDomain,
    suite: SemanticIdentifier,
    value: OLPValue
}
```

The map is closed.

All fields are mandatory.

For CI-1:

```text
suite =
    "olp/core/identity/content/v1"
```

always.

The digest is:

```text
SHA-256(
    OLP-CIE-1(
        IdentityPreimage
    )
)
```

---

## 52. RecordIdentity

For logical Record `R`:

```text
IdentityPreimage {
    domain: "record",
    suite: "olp/core/identity/content/v1",
    value: R
}
```

The complete 32-byte digest becomes:

```text
RecordIdentity
```

as a ContentIdentity whose domain is `record`.

RecordIdentity is a mandatory property of a finalized OLP Record but MAY be derived rather than serialized.

The Record MUST NOT contain its own RecordIdentity inside the identity-bearing Record envelope.

---

## 53. DefinitionIdentity

For SemanticDefinitionManifest `M`:

```text
IdentityPreimage {
    domain: "semantic_definition",
    suite: "olp/core/identity/content/v1",
    value: M
}
```

The digest becomes DefinitionIdentity.

The manifest MUST NOT contain its own DefinitionIdentity.

---

## 54. BlobIdentity

For exact byte string `B`:

```text
IdentityPreimage {
    domain: "blob",
    suite: "olp/core/identity/content/v1",
    value: B
}
```

The digest becomes BlobIdentity.

BlobIdentity identifies exact bytes only.

It does not imply:

- media-type equivalence;
- semantic equivalence;
- authorship;
- confidentiality;
- Trust.

---

## 55. CI-1 Cryptographic Input Bound

SHA-256 under CI-1 is defined only for complete canonical identity preimages containing fewer than:

```text
2^64 bits
```

Since the OLP-CIE-1 representation is byte-oriented, the maximum complete identity-preimage byte length is:

```text
2^61 - 1 bytes
```

This bound applies to the complete encoded IdentityPreimage, including:

- domain;
- suite;
- value;
- CBOR structural overhead.

This is a cryptographic-suite bound, not an arbitrary application resource limit.

A future identity suite MAY define different limits.

---

## 56. Suite Use in OLP v1

Although the ContentIdentity structure is suite-aware, OLP v1 native semantic structures requiring RecordIdentity, DefinitionIdentity, or BlobIdentity MUST use:

```text
olp/core/identity/content/v1
```

Specifically:

```text
RecordReference.identity
ContentReference.identity
LocatorReference.target_identity
SemanticBinding.definition
```

MUST use OLP-CI-1 in OLP v1.

Future suite migration MUST use explicitly versioned protocol semantics.

A Record MUST NOT freely choose a different identity suite per instance while claiming OLP v1 canonical representation.

---

## 57. Identity Domain Separation

The following are intentionally distinct:

```text
RecordIdentity(R)
BlobIdentity(OLP-CIE-1(R))
```

even though both ultimately use SHA-256.

Likewise DefinitionIdentity is distinct from both.

The domain token is part of the hashed preimage and native ContentIdentity.

This prevents cross-domain substitution.

---

## 58. ContentIdentity Text Representation

OLP v1 defines exactly one canonical text representation for each CI-1 domain.

SHA-256's 32-byte digest is encoded using:

```text
RFC 4648 Base32
uppercase
no "=" padding
```

The Base32 portion therefore contains exactly:

```text
52 characters
```

### 58.1 RecordIdentity text

```text
olp-record-ci1-<BASE32>
```

### 58.2 DefinitionIdentity text

```text
olp-definition-ci1-<BASE32>
```

### 58.3 BlobIdentity text

```text
olp-blob-ci1-<BASE32>
```

The text representation is not a URI.

---

## 59. Strict ContentIdentity Text Parsing

Canonical parsing MUST reject:

- lowercase Base32;
- `=` padding;
- whitespace;
- newlines;
- invalid Base32 characters;
- incorrect length;
- incorrect domain token;
- incorrect suite alias;
- non-zero unused Base32 pad bits.

For strict canonical parsing:

```text
canonical_encode(parse(input)) == input
```

MUST hold exactly.

This re-encoding requirement prevents multiple Base32 text forms from decoding to one digest.

A user interface MAY accept lowercase convenience input, but it MUST decode it into the native ContentIdentity and re-emit the canonical uppercase form.

Convenience acceptance is not canonical text parsing.

---

## 60. Abbreviated Identities

Abbreviated ContentIdentity displays MAY be used as:

- UI hints;
- log shorthand;
- local search prefixes.

They MUST NOT be treated as canonical ContentIdentity values.

Identity-sensitive protocol operations MUST use complete native or canonical textual ContentIdentity values.

---

## 61. ContentIdentity Is Not Authorship or Truth

ContentIdentity establishes neither:

- who created an object;
- who signed it;
- whether a Claim is true;
- whether an Event happened;
- whether an Issuer was authorized;
- whether a Record is trustworthy.

Those are separate Evidence and evaluation questions.

---

## 62. Collision Handling

A ContentIdentity digest MUST NOT be treated as mathematical proof that two arbitrary preimages are identical.

If an implementation possesses two complete canonical identity preimages that:

```text
produce equal ContentIdentity
```

but:

```text
have different canonical preimage bytes
```

the implementation MUST treat the condition as:

```text
identity ambiguity / cryptographic collision
```

and fail closed for identity equivalence.

It MUST NOT:

- silently overwrite one object;
- merge their Histories;
- union semantic data;
- treat them as one immutable object.

Object stores keyed by ContentIdentity SHOULD retain collision-safe insertion checks whenever the complete candidate object is available.

---

# Part VI — Reusable Structures

## 63. SemanticBinding

```text
SemanticBinding {
    semantic_id: SemanticIdentifier,
    definition: DefinitionIdentity
}
```

The map is closed.

Both fields are mandatory.

A SemanticBinding means:

> the enclosing object associates this SemanticIdentifier with this exact immutable Semantic Definition Manifest.

It does not prove namespace assignment authority.

---

## 64. ProfileEntry

```text
ProfileEntry {
    id: SemanticIdentifier,
    critical: boolean
}
```

The map is closed.

`id` MUST be a SemanticIdentifier of kind:

```text
profile
```

Both fields are mandatory.

---

## 65. RelationshipEntry

```text
RelationshipEntry {
    relationship: SemanticIdentifier,
    target: Reference,
    critical: boolean
}
```

The map is closed.

`relationship` MUST be a SemanticIdentifier of kind:

```text
relationship
```

All fields are mandatory.

A Relationship states how the enclosing Record is represented as related to the target.

Reference identity alone does not imply endorsement or Trust.

---

## 66. ExtensionEntry

```text
ExtensionEntry {
    id: SemanticIdentifier,
    critical: boolean,
    content: map<ProtocolKey, OLPValue>
}
```

The map is closed.

`id` MUST be a SemanticIdentifier of kind:

```text
extension
```

All fields are mandatory.

`content` MAY be `{}` only if the applicable Extension definition permits presence-only semantics.

Only one occurrence of a particular Extension SID is permitted in one Record.

Multiplicity needed by an Extension belongs inside its own `content`.

---

## 67. Criticality

`critical: true` means:

> understanding and correctly applying this component is required before claiming full relevant semantics of the Record are understood.

`critical: false` means:

> processing MAY continue for independent understood semantics without understanding the component, if the applicable definition permits non-critical use.

Criticality does not mean:

- severity;
- importance;
- Trust;
- authority;
- priority;
- precedence;
- cryptographic strength.

Unknown critical semantics result in semantic support being unavailable for the relevant complete Record semantics.

Unknown non-critical semantics MAY be skipped for scoped interpretation, but MUST still be preserved if the same Record is relayed or stored.

---

## 68. Criticality Requirements

Every Profile, Relationship, and Extension SemanticDefinition MUST state whether:

```text
critical: false
```

is permitted.

If a component:

- changes;
- qualifies;
- conditions;
- overrides;
- narrows;
- broadens;

otherwise understood Record semantics, its definition MUST require:

```text
critical: true
```

The definition's requirement is a minimum.

An author MAY set `critical: true` even where false is permitted.

Criticality is identity-relevant.

---

## 69. Profile Composition

Multiple Profiles jointly apply unless an explicit composition rule says otherwise.

The default is effectively:

```text
Profile A
AND
Profile B
AND
Profile C
```

Known incompatible Profile requirements result in semantic-conformance failure.

Profiles MAY constrain or refine a core type.

They MUST NOT incompatibly redefine an intrinsic core field's meaning.

A genuinely incompatible reinterpretation requires a new semantic type version.

---

## 70. Reference

OLP v1 defines a closed discriminated `Reference` union with three forms.

### 70.1 RecordReference

```text
{
    kind: "record",
    identity: RecordIdentity
}
```

This references one exact immutable OLP Record.

### 70.2 ContentReference

```text
{
    kind: "content",
    identity: BlobIdentity
}
```

This references one exact byte string.

### 70.3 LocatorReference

Unbound:

```text
{
    kind: "locator",
    locator: text_string
}
```

or content-bound:

```text
{
    kind: "locator",
    locator: text_string,
    target_identity: BlobIdentity
}
```

A bound locator provides a retrieval hint plus an expected exact-byte identity.

`target_identity` is restricted to BlobIdentity.

OLP Records themselves are referenced through RecordReference.

Semantic Definitions are bound through SemanticBinding rather than LocatorReference.

---

## 71. Reference Semantics

The exact `kind` tokens are:

```text
record
content
locator
```

They are core discriminator tokens, not SemanticIdentifiers.

Reference maps are closed.

A Reference identifies or locates a target.

It does not imply:

- endorsement;
- ownership;
- authority;
- Trust;
- relationship meaning.

That meaning belongs to the semantic structure containing the Reference.

---

## 72. Locator Semantics

Locator text is preserved exactly.

OLP core performs no:

- URI normalization;
- percent decoding;
- case folding;
- redirect rewriting;
- Unicode normalization;
- whitespace trimming.

A Profile or application MAY constrain acceptable locator schemes.

A bare LocatorReference does not provide immutable target identity.

For a bound locator, retrieved bytes MUST match the expected BlobIdentity before the target is considered identity-verified.

Retrieval failure does not make the enclosing Record structurally invalid.

Where the target is required for evaluation, retrieval failure can make that evaluation indeterminate.

---

## 73. Reference Availability

A Reference does not guarantee target availability.

Basic Reference structural validation and RecordIdentity calculation MUST NOT require retrieving the referenced target.

References are therefore compatible with:

- offline verification;
- unavailable archives;
- selective disclosure;
- partial History.

---

## 74. Exact Reference Dependency Graphs

A finalized RecordReference requires the referenced RecordIdentity to already be known.

OLP MUST NOT require self-referential or mutually cyclic exact content-identity dependencies such as:

```text
R1 references RecordIdentity(R2)
R2 references RecordIdentity(R1)
```

where neither identity can be constructed first.

Similarly:

```text
R references itself by its own RecordIdentity
```

MUST NOT be required.

The intrinsic exact RecordReference dependency graph therefore behaves as a constructible content-addressed dependency DAG.

The broader semantic Evidence graph can still express arbitrarily rich apparent cycles through later Records referring to earlier Records.

---

## 75. Identifier

```text
Identifier {
    scheme: SemanticIdentifier,
    value: text_string | byte_string
}
```

The map is closed.

Both fields are mandatory.

`scheme` MUST be a SemanticIdentifier of kind:

```text
identifier
```

The applicable Identifier scheme defines:

- accepted primitive type;
- lexical syntax;
- constraints;
- canonical authoring requirements.

---

## 76. Identifier Semantics

OLP core treats Identifier values as opaque.

It MUST NOT implicitly perform:

- case folding;
- Unicode normalization;
- whitespace trimming;
- URI normalization;
- DNS lookup;
- punctuation removal;
- scheme-specific parsing.

Generic Identifier equality requires:

```text
same scheme
AND
same primitive value type
AND
same exact value
```

An Identifier identifies a value within an identification system.

It does not prove:

- entity existence;
- identifier authenticity;
- control;
- authority;
- ownership;
- Trust.

---

## 77. EntityReference

```text
EntityReference {
    identifiers?: [Identifier, ...],
    record?: RecordReference
}
```

The map is closed.

At least one of:

```text
identifiers
record
```

MUST be present.

If `identifiers` is present, it MUST contain at least one Identifier.

`record` contains at most one RecordReference.

---

## 78. EntityReference Identifier Set

`identifiers` is set-like.

Exact duplicate Identifier values are prohibited.

Canonical ordering is lexicographic order of each Identifier's standalone `OLP-CIE-1` encoding.

OLP-CIE-1 itself does not sort the array.

---

## 79. Entity Co-reference

Multiple Identifiers inside one EntityReference assert:

> those Identifiers are being used here as identifiers of the same entity.

If both `identifiers` and `record` are present, their co-occurrence asserts that the Identifiers and referenced Record are being used as references to the same entity in that occurrence.

This is protocol information, not proof.

It does not create universal, permanent Identifier equivalence.

Another Record may dispute the association.

---

## 80. EntityReference Is Not a Global Identity Object

EntityReference does not define intrinsic fields for:

```text
name
display_name
entity_type
public_key
verification_method
issuer
holder
subject
trust
```

Names, classifications, key control, authority, and other properties are separate semantic assertions.

EntityReference is an embedded structure and does not receive RecordIdentity merely by existing.

OLP core does not resolve EntityReferences into one globally canonical real-world entity during identity calculation.

---

## 81. ClaimExpression

```text
ClaimExpression {
    predicate: SemanticIdentifier,
    arguments: map<ProtocolKey, OLPValue>
}
```

The map is closed.

Both fields are mandatory.

`predicate` MUST be a SemanticIdentifier of kind:

```text
predicate
```

`arguments` is always present.

`{}` is permitted only where the Predicate permits a zero-argument proposition.

The Predicate SemanticDefinition defines the closed argument schema and canonical authoring rules.

---

## 82. ClaimExpression Semantics

A ClaimExpression represents exactly one proposition.

No universal fields are defined for:

```text
subject
issuer
truth_value
confidence
negated
timestamp
evidence
status
trust
```

Subjects or equivalent argument roles are defined by the Predicate where relevant.

Negation is not a universal OLP Claim operator.

A distinct proposition requiring negation semantics uses an appropriate Predicate.

---

## 83. ClaimExpression Equality

Exact ClaimExpression equality requires:

```text
same predicate SID
AND
same complete arguments logical map
```

OLP core does not establish equivalence through:

- natural-language similarity;
- Identifier resolution;
- ontology reasoning;
- unit conversion;
- external state;
- semantic aliases.

---

## 84. Embedded Versus Materialized Claims

A ClaimExpression embedded in another Record is not an implicit nested Claim Record.

It has no independent RecordIdentity.

If independently materialized, it can become the `content` of a Claim Record.

Where the independent Claim Record's:

- Profiles;
- Relationships;
- Extensions;
- lifecycle;
- provenance;

matter, the Claim Record itself should be referenced explicitly.

---

# Part VII — Temporal Model

## 85. TimePoint

```text
TimePoint {
    system: SemanticIdentifier,
    value: map<ProtocolKey, OLPValue>
}
```

The map is closed.

Both fields are mandatory.

`system` MUST be a SemanticIdentifier of kind:

```text
time_system
```

The Time System SemanticDefinition defines interpretation of `value`.

Non-core Time Systems require SemanticBinding in the enclosing Record.

---

## 86. Core UTC Time System

OLP v1 defines:

```text
olp/core/time_system/utc/v1
```

with value schema:

```text
{
    timestamp: CanonicalUtcTimestamp
}
```

---

## 87. CanonicalUtcTimestamp

The UTC timestamp MUST be a strict UTC-only RFC 3339-style timestamp:

```text
YYYY-MM-DDTHH:MM:SSZ
```

or:

```text
YYYY-MM-DDTHH:MM:SS.<fraction>Z
```

Rules:

1. full date is mandatory;
2. full time is mandatory;
3. seconds are mandatory;
4. uppercase `T` is mandatory;
5. uppercase `Z` is mandatory;
6. numeric UTC offsets are prohibited;
7. named time zones are prohibited;
8. whitespace is prohibited;
9. fractional seconds are optional;
10. if a fractional part is present, it contains decimal digits only;
11. the final fractional digit MUST NOT be `0`.

Therefore:

```text
2026-08-19T17:11:42Z
2026-08-19T17:11:42.5Z
2026-08-19T17:11:42.000001Z
```

are canonical.

These are not canonical:

```text
2026-08-19T17:11:42.0Z
2026-08-19T17:11:42.500Z
2026-08-19t17:11:42z
2026-08-19T19:11:42+02:00
```

Lexical formatting does not encode clock accuracy.

Leap-second notation permitted by the applicable UTC/RFC 3339 temporal semantics MAY be represented.

Whether a particular asserted leap-second label corresponds to an actual applicable leap second is semantic temporal validation, not OLP-CIE-1 canonicalization.

---

## 88. Local Civil Time

An unqualified local wall-clock value that does not uniquely identify a temporal position MUST NOT be silently converted into a core UTC TimePoint.

If historical Evidence says only:

```text
02:30 local time
```

that fact should be represented through appropriate explicit semantics rather than inventing a UTC instant.

---

## 89. Time-Zone Names

Time-zone names are not part of the core UTC TimePoint.

If a named time zone is semantically relevant, it MUST be represented separately.

Time-zone database changes MUST NOT silently change an immutable UTC TimePoint.

---

## 90. TemporalValue

OLP defines a closed discriminated union:

```text
instant
interval
window
```

### 90.1 Instant

```text
{
    kind: "instant",
    at: TimePoint
}
```

This represents one asserted temporal point.

### 90.2 Interval

```text
{
    kind: "interval",
    start: TimePoint,
    end: TimePoint
}
```

This represents a phenomenon asserted to extend over:

```text
[start, end)
```

### 90.3 Window

```text
{
    kind: "window",
    start: TimePoint,
    end: TimePoint
}
```

This means that the applicable temporal point is asserted to lie somewhere in:

```text
[start, end)
```

It does not mean the phenomenon persisted throughout the range.

---

## 91. Temporal Range Rules

For both interval and window:

```text
start < end
```

MUST hold according to the applicable Time System semantics.

Both endpoints MUST use the same Time System SemanticIdentifier.

Zero-length intervals and windows are prohibited.

An exact point uses `instant`.

---

## 92. Temporal Epistemics

A TimePoint or TemporalValue represents temporal protocol information.

It does not prove:

- a trusted clock observed the time;
- the time is historically authentic;
- the Record existed at that time;
- the Event occurred at that time;
- an Issuer acted at that time.

Independent Evidence is required for stronger temporal verification.

---

## 93. No Implicit Now

Missing temporal information MUST NOT be interpreted automatically as:

```text
current time
parse time
receipt time
signing time
storage time
```

There is no protocol-global default time.

---

## 94. Precision and Uncertainty

OLP MUST NOT infer:

- measurement resolution;
- clock accuracy;
- statistical uncertainty;
- temporal uncertainty;

from fractional-second digit count.

Where an uncertain occurrence time is adequately represented as a range, a `window` SHOULD be used.

Other accuracy and uncertainty concepts belong to explicit semantic definitions.

---

# Part VIII — Party and Core Record Envelope

## 95. Party

```text
Party {
    role: SemanticIdentifier,
    entity: EntityReference
}
```

The map is closed.

Both fields are mandatory.

`role` MUST be a SemanticIdentifier of kind:

```text
role
```

Party is embedded and has no independent RecordIdentity.

---

## 96. Core Participant Role

OLP v1 defines:

```text
olp/core/role/participant/v1
```

with minimal meaning:

> the EntityReference is represented as participating in the applicable Event or Interaction without a more specific role assertion.

It does not imply:

- consent;
- authority;
- ownership;
- responsibility;
- endorsement;
- legal status;
- Trust.

---

## 97. Canonical Record Envelope

Every OLP v1 Record uses the following top-level structure:

```text
Record {
    envelope_version: 1,
    type: SemanticIdentifier,
    content: map<ProtocolKey, OLPValue>,
    semantic_bindings?: [SemanticBinding, ...],
    profiles?: [ProfileEntry, ...],
    relationships?: [RelationshipEntry, ...],
    extensions?: [ExtensionEntry, ...]
}
```

The top-level map is closed.

The only permitted top-level keys are:

```text
envelope_version
type
content
semantic_bindings
profiles
relationships
extensions
```

---

## 98. Mandatory Envelope Fields

The following are mandatory:

```text
envelope_version
type
content
```

### 98.1 envelope_version

For this specification:

```text
envelope_version = 1
```

### 98.2 type

`type` contains one versioned SemanticIdentifier of kind:

```text
type
```

No separate `type_version` field exists.

### 98.3 content

`content` is always:

```text
map<ProtocolKey, OLPValue>
```

Type-specific schemas define its permitted keys and values.

---

## 99. Optional Envelope Components

The following are optional:

```text
semantic_bindings
profiles
relationships
extensions
```

If an optional array would contain zero entries, the field MUST be omitted.

The empty-array forms:

```text
semantic_bindings: []
profiles: []
relationships: []
extensions: []
```

do not conform to the v1 envelope schema.

---

## 100. Fields Not Present in the Universal Envelope

The v1 envelope does not universally contain:

```text
id
created_at
issuer
subject
proof
signature
status
trust
reputation
metadata
```

RecordIdentity is derived.

Type-specific semantics belong in `content`.

Local operational metadata belongs outside the Record identity boundary unless deliberately protocolized through explicit semantics.

---

## 101. Semantic Bindings in Records

`semantic_bindings` contains SemanticBinding values for directly used non-core SemanticIdentifiers requiring immutable definitions.

Core OLP SemanticIdentifiers MUST NOT be redundantly bound.

Each non-core directly used SID is bound at most once.

The array is sorted by ascending ASCII `semantic_id`.

A fully semantically understood Record MUST NOT contain unused bindings.

For embedded structures, required bindings are supplied by the enclosing Record rather than duplicated inside each embedded value.

Definition manifests bind their own external semantic dependencies.

---

## 102. Profiles

`profiles`:

- is set-like;
- uses one entry per Profile SID;
- is sorted by ascending ASCII `id`;
- contains no duplicates.

Each Profile is identity-relevant.

Profiles may refine or constrain semantics but cannot incompatibly redefine core intrinsic fields.

---

## 103. Relationships

`relationships` is set-like.

Canonical ordering is lexicographic comparison of each complete RelationshipEntry's standalone `OLP-CIE-1` encoding.

The pair:

```text
(relationship, target)
```

MUST occur at most once, irrespective of `critical`.

Different Relationship kinds MAY refer to the same target.

Generic Relationships contain no arbitrary per-edge payload.

A domain needing edge-specific data SHOULD define explicit semantic structures rather than extending generic RelationshipEntry ad hoc.

---

## 104. Extensions

`extensions`:

- is set-like;
- is sorted by ascending ASCII `id`;
- permits one occurrence per Extension SID.

An Extension's own content schema defines its allowed fields.

No `x_` or `vendor_` ad-hoc field-prefix extension mechanism exists.

---

## 105. Record Immutability

A finalized Record is semantically immutable.

Any identity-relevant change creates a distinct RecordIdentity.

Corrections, revocations, supersession, qualification, and later Evidence MUST NOT silently rewrite historical Record content.

Local metadata outside the identity boundary MAY change without changing RecordIdentity.

---

## 106. Unknown Envelope Versions

If an implementation can parse the generic OLP logical representation and encounters a detectable envelope version it does not support, the correct semantic classification is:

```text
unsupported
```

rather than automatically:

```text
invalid
```

The implementation MUST NOT apply the v1 envelope schema to a future envelope version unless an explicit compatibility rule permits it.

Identity calculation at the logical representation level can remain possible independently of semantic support.

---

# Part IX — Core Record Types

## 107. Claim v1

The Claim Record type is:

```text
olp/core/type/claim/v1
```

Its `content` is exactly one ClaimExpression:

```text
{
    predicate: SemanticIdentifier,
    arguments: map<ProtocolKey, OLPValue>
}
```

The content map is closed.

A Claim Record represents one independently materialized proposition.

---

## 108. Claim Semantics

A Claim Record does not inherently mean that anyone asserts the proposition is true.

Its:

- existence;
- storage;
- serialization;
- transport;
- possession;

does not constitute attributable assertion.

Attribution belongs to Attestation.

Trust belongs to evaluation.

---

## 109. Attestation v1

The Attestation Record type is:

```text
olp/core/type/attestation/v1
```

Its content is:

```text
AttestationContent {
    issuer: EntityReference,
    claims: [ClaimExpression, ...]
}
```

The map is closed.

Both fields are mandatory.

---

## 110. Attestation Issuer

`issuer` contains exactly one EntityReference.

It means:

> the propositions in this Attestation are represented as attributable to this entity.

This is **declared attribution**.

It is not automatically verified attribution.

Issuer does not imply:

- creator;
- serializer;
- transport sender;
- Holder;
- signer;
- key controller;
- authorized representative;
- trustworthy entity.

---

## 111. Issuer Versus Signer

Attestation v1 contains no intrinsic `signer` field.

A cryptographic proof may establish that key K signed some data.

Separate Evidence may establish a relationship between K and the declared Issuer.

Only the complete applicable verification process may establish verified attribution.

Therefore:

```text
signature valid under K
    ≠
declared Issuer made the assertion
```

without the necessary identity and authority Evidence.

---

## 112. One Issuer

Attestation v1 contains exactly one Issuer.

Where Alice and Bob independently assert the same Claim:

```text
Attestation A
    issuer = Alice

Attestation B
    issuer = Bob
```

SHOULD normally be used.

A collective organization MAY itself be represented by one EntityReference and act as the single Issuer.

---

## 113. Attestation Claims

`claims` contains one or more embedded ClaimExpressions.

Attestation v1 does not permit Claim RecordReference as an alternative representation of the asserted proposition.

The core assertion mechanism has one representation:

```text
embedded ClaimExpression
```

If a proposition concerns a particular Claim Record artifact, the applicable Predicate can contain a RecordReference as an argument.

---

## 114. Attestation Claim Collection

`claims` is set-like.

Rules:

1. at least one ClaimExpression is required;
2. exact duplicate ClaimExpressions are prohibited;
3. canonical ordering is lexicographic comparison of standalone ClaimExpression `OLP-CIE-1` bytes.

Array order carries no:

- priority;
- chronology;
- importance;
- override;
- presentation order.

Each ClaimExpression is individually asserted by the declared Issuer.

Common membership establishes common attribution and Record packaging, not hidden logical relations between Claims.

---

## 115. Attestation Excluded Fields

Attestation v1 contains no universal intrinsic:

```text
subject
signer
holder
proof
signature
verification_method
issued_at
created_at
confidence
truth_value
purpose
audience
context
status
revocation
trust
reputation
```

Subject roles arise from Predicate arguments.

Proof semantics are separate.

Status changes use StatusChange Records.

Temporal issuance semantics can be represented through explicit future or extension semantics without modifying Attestation v1.

---

## 116. Attestation Verification Layers

A Record may simultaneously have:

```text
Attestation schema                 valid
RecordIdentity                     verified
Issuer declaration                 present
cryptographic attribution          not established
Claim truth                        not established
Trust                              context-dependent
```

No single `valid = true` result may erase these distinctions.

---

## 117. Observation v1

The Observation Record type is:

```text
olp/core/type/observation/v1
```

Its content is:

```text
ObservationContent {
    results: [ClaimExpression, ...],
    observer?: EntityReference,
    procedure?: Reference
}
```

The map is closed.

`results` is mandatory.

`observer` and `procedure` are optional.

---

## 118. Observation Semantics

An Observation represents that one or more result propositions were purportedly produced through an act or process such as:

- observation;
- sensing;
- measurement;
- examination;
- detection.

The word **purportedly** is normative to the conceptual model.

Being represented as an Observation does not establish:

- accuracy;
- objectivity;
- scientific validity;
- provenance authenticity;
- truth;
- Trust.

An Observation is Evidence, not a truth oracle.

---

## 119. Observation Results

`results` contains one or more ClaimExpressions.

Each result is represented as having been produced through the represented observational process.

`results` is set-like.

Exact duplicates are prohibited.

Canonical ordering uses standalone ClaimExpression OLP-CIE-1 bytes.

Result order carries no chronology or priority.

If sequence is intrinsic to a result, the sequence belongs inside the appropriate ClaimExpression argument.

---

## 120. Shared Observation Provenance

All results within one Observation share the Observation-level:

```text
observer
procedure
```

where present.

If different results were produced by different observers or procedures, separate Observations SHOULD normally be used.

---

## 121. Observer

`observer`, when present, contains exactly one EntityReference.

It means:

> this entity is represented as having performed or directly produced the observational process/result.

OLP core does not require the observer to be:

- a person;
- physical sensor;
- software;
- laboratory;
- AI system;
- device.

Observer identity does not prove provenance authenticity.

Therefore:

```text
declared observer
    ≠
verified observational provenance
```

---

## 122. Observer Is Not Issuer

Observation v1 has no Issuer.

Observer is not:

- Issuer;
- Holder;
- signer;
- transport sender;
- storage provider.

An Attestation may separately make attributable Claims about an Observation Record.

---

## 123. Procedure

`procedure`, when present, contains one Reference.

It identifies the target represented as describing or constituting the procedure used for the Observation.

The Reference may be a:

- RecordReference;
- ContentReference;
- LocatorReference;

subject to applicable Profile constraints.

Procedure presence does not prove:

- the procedure was followed;
- it was implemented correctly;
- it was scientifically appropriate;
- it was trustworthy.

---

## 124. Observation Fields Not Universalized

Observation v1 does not independently define universal fields for:

```text
observed_property
feature_of_interest
subject
result_value
unit
phenomenon_time
confidence
accuracy
uncertainty
raw_data
time
observed_at
issuer
proof
signature
```

Result Predicate semantics define the proposition.

Observation-process temporal semantics can be represented through explicit future/Profile/Extension semantics.

The absence of a generic time field intentionally avoids conflating phenomenon time, process time, result time, receipt time, and proof time.

---

## 125. Event v1

The Event Record type is:

```text
olp/core/type/event/v1
```

Its content is:

```text
EventContent {
    event_type: SemanticIdentifier,
    arguments: map<ProtocolKey, OLPValue>,
    time?: TemporalValue,
    parties?: [Party, ...]
}
```

The map is closed.

`event_type` and `arguments` are mandatory.

`time` and `parties` are optional.

---

## 126. Event Type

`event_type` MUST be a SemanticIdentifier of kind:

```text
event
```

The Event SemanticDefinition defines:

- occurrence semantics;
- argument schema;
- applicable Party roles;
- cardinality constraints;
- temporal constraints;
- whether the Event type is permitted as an Interaction.

A non-core Event type requires SemanticBinding.

---

## 127. Event Arguments

`arguments` is always present.

The Event SemanticDefinition defines its closed schema.

`{}` is permitted only if the Event definition permits a zero-argument occurrence.

---

## 128. Event Semantics

An Event is an immutable representation of a purported occurrence.

It does not itself prove that the occurrence happened.

An Event is distinct from a Claim:

```text
Claim
    → proposition

Event
    → first-class represented occurrence
```

An Event can itself be referenced, attested, observed, related, superseded, or revoked.

---

## 129. Event Time

`time`, when present, is the represented occurrence time or temporal extent of the Event itself.

It does not mean:

- Record creation time;
- Observation time;
- receipt time;
- proof time;
- storage time.

Temporal authenticity remains separate.

---

## 130. Event Parties

`parties`, when present, MUST be non-empty.

The array is set-like.

Canonical ordering is lexicographic standalone Party OLP-CIE-1 bytes.

The pair:

```text
(role, entity)
```

MUST occur at most once.

One EntityReference MAY occupy multiple roles.

Multiple EntityReferences MAY occupy one role where permitted by the Event definition.

Party presence constitutes represented participation, not verified participation.

---

## 131. One Semantic Fact, One Canonical Channel

A SemanticDefinition MUST NOT define two interchangeable structural representations for the same identity-relevant semantic fact.

For Event in particular:

1. an Event definition MUST NOT define an argument semantically equivalent to the generic `time` field;
2. an Event definition MUST NOT duplicate a Party participation role through an equivalent ordinary argument.

An EntityReference MAY still appear in `arguments` when it serves a non-Party semantic role.

For example:

```text
parties:
    inspector = Alice

arguments:
    inspected_asset = Machine42
```

is valid because `Machine42` is represented as the object of inspection, not necessarily a participating Party.

---

## 132. Event Excluded Fields

Event v1 contains no universal intrinsic:

```text
issuer
observer
proof
signature
verification_method
outcomes
trust
status
```

Attribution belongs to Attestation.

Observation belongs to Observation.

Proof remains separate.

Status belongs to StatusChange.

---

## 133. Outcome Representation

OLP does not define a universal mutable `outcomes` field.

An Outcome is an asserted consequence, result, or state associated with an Event or Interaction.

It can be represented through:

- a Claim referring to the Event;
- an Event-specific intrinsic argument where the result is genuinely part of that Event's definition;
- explicit Relationships;
- domain-specific semantics.

Supplied outcomes may conflict and need not be known when the original Event is created.

---

## 134. Interaction v1

The Interaction Record type is:

```text
olp/core/type/interaction/v1
```

Interaction is a core specialization of Event.

Its content uses the Event structure:

```text
InteractionContent {
    event_type: SemanticIdentifier,
    arguments: map<ProtocolKey, OLPValue>,
    time?: TemporalValue,
    parties: [Party, ...]
}
```

For Interaction, `parties` is mandatory.

---

## 135. Interaction Entity Requirement

An Interaction MUST contain:

- at least two Party entries; and
- at least two logically distinct EntityReference values.

For example:

```text
buyer  Alice
seller Bob
```

can satisfy the requirement.

But:

```text
buyer  Alice
seller Alice
```

does not contain two logically distinct represented entities.

Logical distinctness is exact EntityReference logical inequality.

It is not proof that the real-world entities are actually distinct.

---

## 136. Interaction Event Types

The applicable Event SemanticDefinition MUST explicitly permit use as an Interaction.

Merely adding two Parties to an Event type that does not describe an interaction does not make it a valid Interaction.

---

## 137. Interaction Semantics

Interaction represents a purported:

- shared activity;
- exchange;
- process;
- relationship;

involving multiple represented entities.

Interaction does not automatically imply:

- consent;
- agreement;
- authorization;
- legitimacy;
- voluntariness;
- legal validity;
- acknowledgement;
- successful completion;
- Trust.

An attack, collision, unauthorized access attempt, or dispute may all be represented as Interactions where defined by the Event semantics.

Entities represented as Parties need not themselves use OLP or have participated in creating the Record.

---

## 138. StatusChange v1

The StatusChange Record type is:

```text
olp/core/type/status_change/v1
```

Its content is:

```text
StatusChangeContent {
    actor: EntityReference,
    target: RecordReference,
    operation: SemanticIdentifier,
    parameters: map<ProtocolKey, OLPValue>,
    effective: TemporalValue
}
```

The map is closed.

All five fields are mandatory.

---

## 139. Status Actor

`actor` contains exactly one EntityReference.

It means:

> this entity is represented as exercising or issuing the status-changing action.

This is declared status attribution, not verified status authority.

Actor does not automatically mean:

- Issuer;
- creator;
- signer;
- owner;
- controller;
- authorized administrator.

---

## 140. Status Authority

OLP core defines no universal status authority applicable to all Record types.

Whether an actor has authority for a status operation depends on:

- applicable semantic definitions;
- Evidence;
- delegation;
- Profiles;
- policy;
- jurisdiction;
- Trust Model;
- application Context.

The declared Issuer of an Attestation does not automatically receive universal protocol-level revocation authority merely by being the Issuer.

A structurally valid StatusChange may therefore be recognized as unauthorized and have no derived status effect under a particular policy.

---

## 141. Status Target

`target` contains exactly one RecordReference.

StatusChange v1 applies to one exact immutable OLP Record.

Core StatusChange does not target:

- a query;
- all Records from an entity;
- a LocatorReference;
- an arbitrary Blob.

Batch semantics require separate explicit definitions.

---

## 142. Status Operation

`operation` MUST be a SemanticIdentifier of kind:

```text
status_operation
```

`parameters` is always present and is governed by the applicable Status Operation SemanticDefinition.

Unknown operations are preservable but semantically unsupported.

---

## 143. Effective Time

`effective` MUST contain either:

```text
instant
```

or:

```text
window
```

TemporalValue `interval` is not permitted for core StatusChange effective semantics.

### 143.1 Instant

An instant represents one asserted transition point.

### 143.2 Window

A window represents uncertainty about the exact transition point.

Before the window begins, the transition is not effective on the basis of that StatusChange alone.

At or after the end of the window, the transition is represented as having occurred somewhere in the window, if the StatusChange is otherwise applicable.

Within the window, effective status MAY be temporally indeterminate.

Effective time is still asserted information, not trusted timestamp proof.

---

## 144. Revocation v1

OLP defines:

```text
olp/core/status_operation/revocation/v1
```

with parameters exactly:

```text
{}
```

Revocation means:

> the actor represents that reliance on the target Record should be withdrawn from the applicable effective transition onward within contexts that recognize the actor's authority.

Revocation does not:

- erase the Record;
- change RecordIdentity;
- prove the Record never existed;
- automatically establish historical invalidity;
- automatically establish that associated Claims are false.

Historical existence, historical validity, and current reliance status are separate properties.

---

## 145. Revocation Reason and Scope

Core Revocation v1 defines no universal:

```text
reason
reason_code
comment
condition
```

field.

Scoped or conditional status semantics MUST use:

- an explicit specialized Status Operation;
- a critical Profile;
- a critical Extension;
- another explicitly defined semantic mechanism.

Unknown critical qualifications MUST NOT be silently ignored.

---

## 146. Supersession v1

OLP defines:

```text
olp/core/status_operation/supersession/v1
```

Its `parameters` map contains exactly:

```text
{
    replacements: [RecordReference, ...]
}
```

The map is closed.

`replacements` MUST contain at least one RecordReference.

---

## 147. Supersession Replacement Set

`replacements` is set-like.

Rules:

- exact duplicates are prohibited;
- canonical ordering uses standalone RecordReference OLP-CIE-1 bytes;
- the StatusChange target MUST NOT appear as its own replacement.

If multiple replacement Records are present, they collectively form the replacement set.

They are not unspecified alternatives.

---

## 148. Supersession Semantics

Supersession means:

> the actor represents that the target should, from the effective transition onward, be treated as superseded by the designated replacement Record or Record set for applicable interpretation.

Supersession does not erase the historical target.

Supersession and Revocation are distinct status dimensions.

A Record MAY be both:

```text
revoked
```

and:

```text
superseded
```

under an applicable evaluation.

---

## 149. Derived Status

Current status is not an intrinsic mutable field of the target Record.

Status is derived from immutable Evidence such as StatusChange Records together with:

- available History;
- semantic support;
- effective times;
- authority evaluation;
- status of relevant Evidence;
- evaluation Context.

Therefore:

```text
no observed StatusChange
```

does not prove:

```text
active
valid
unrevoked
current
acceptable
```

Absence of a Record from available History is not proof that it never existed.

---

## 150. No Last-Write-Wins Status

OLP defines no generic:

- latest StatusChange wins;
- highest timestamp wins;
- newest arrival wins;
- lexicographically smallest identity wins;
- largest version wins.

Chronology does not create authority.

Conflicting applicable StatusChanges MAY coexist.

Where no explicit resolution rule exists, evaluation may result in:

- conflict;
- ambiguity;
- indeterminate status.

---

## 151. StatusChange of StatusChange

A StatusChange is an ordinary Record and MAY itself become a target of later StatusChange Records.

Historical StatusChange Records MUST NOT be silently mutated or deleted.

Revoking a Revocation does not automatically reinstate the original target.

Reinstatement or temporary suspension SHOULD use explicit status-operation semantics rather than inferred double negatives.

---

## 152. No Status Cascade

Changing status of Record R does not automatically change status of Records:

- referenced by R;
- related to R;
- embedded conceptually within R;
- derived from R.

Status effects apply to the exact target unless explicit semantics define otherwise.

---

# Part X — Evolution and Unknown Semantics

## 153. Closed Schemas by Default

Every versioned OLP map schema is closed by default unless it explicitly defines a controlled extension point.

Unknown intrinsic fields in a known supported type/version are a schema-conformance failure.

Unknown intrinsic fields are not implicit Extensions.

---

## 154. Schema Evolution

A published semantic version MUST NOT silently gain new intrinsic fields.

Even adding an apparently optional field changes the accepted schema and therefore requires:

- an Extension;
- a Profile;
- or a new semantic version.

Existing semantic versions are never silently redefined.

---

## 155. Unknown Types and Versions

If an envelope is supported but its semantic Record type/version is unknown:

```text
Record envelope parsing      supported
Record preservation          supported
RecordIdentity               computable
type semantics               unsupported
```

The implementation MUST NOT apply the schema of a known older version to the unknown version unless explicit compatibility semantics authorize that behavior.

---

## 156. Unknown Information Preservation

An implementation claiming to preserve or relay the same Record MUST preserve all identity-relevant logical information.

It may change transport representation if the recovered logical Record remains exactly equal.

It MUST NOT drop unknown:

- content fields of an unknown type;
- Extensions;
- Profiles;
- Relationships;
- bindings;

while claiming the result is the same Record.

A lossy transformation creates a different object or fails preservation.

---

## 157. Unsupported Critical Semantics

Unknown critical Profile, Relationship, or Extension semantics prevent claiming full relevant semantic understanding.

The Record may still remain:

- parseable;
- preservable;
- identity-verifiable.

This is `unsupported`, not automatically `invalid`.

---

## 158. Unsupported Non-Critical Semantics

Unknown non-critical semantics MAY permit processing of independent understood portions of the Record.

The unknown component MUST still be preserved when the same Record is preserved.

The implementation MUST NOT claim to have validated the unknown component's semantics.

---

# Part XI — Validation and Processing Layers

## 159. Independent Validation Layers

OLP processing MUST distinguish at least the following conceptual layers:

1. transport framing;
2. OLP-CIE-1 canonical representation;
3. OLP logical primitive validity;
4. Record envelope conformance;
5. type-specific schema conformance;
6. ContentIdentity calculation;
7. expected identity match;
8. semantic-definition support;
9. SemanticBinding integrity;
10. reference completeness;
11. proof verification;
12. attribution verification;
13. status interpretation;
14. Claim/Evidence evaluation;
15. Trust evaluation;
16. application decision.

A positive result at one layer MUST NOT be treated as an automatic positive result at another.

---

## 160. Processing Outcomes

Depending on the processing layer, meaningful results include:

```text
satisfied / valid
failed / invalid
unsupported
indeterminate
not_applicable
```

These are not interchangeable.

### 160.1 Unsupported

The implementation lacks required semantic or protocol support.

### 160.2 Indeterminate

The applicable semantics are understood but available information is insufficient to establish the requested conclusion.

### 160.3 Invalid

A required representation, schema, integrity, or other checked condition actually failed.

### 160.4 Not applicable

The evaluated property does not apply to the object or operation.

---

## 161. Resource Processing Outcome

OLP additionally defines the operational outcome:

```text
resource_limit_exceeded
```

This means:

> processing was intentionally terminated because an implementation resource bound was reached before the requested result could be established.

It is not equivalent to:

```text
invalid
unsupported
indeterminate
```

The affected evaluation is conceptually:

```text
not evaluated
reason = resource_limit_exceeded
```

An implementation MUST NOT report a validation conclusion it did not actually establish before terminating processing.

---

# Part XII — Resource and Defensive Processing

## 162. Validity Versus Capacity

Protocol validity, semantic support, and implementation capacity are distinct.

A logically valid Record does not become invalid because one implementation lacks:

- RAM;
- CPU;
- storage;
- recursion depth;
- network capacity;
- time budget.

Except for explicit grammar and cryptographic-suite limits, OLP core defines no arbitrary global maximum object size solely for implementation-resource reasons.

---

## 163. Semantic Resource Bounds

A particular SemanticDefinition or Profile MAY define genuine semantic bounds.

For example:

```text
Profile X:
    maximum claims = 8
```

is a semantic conformance rule.

This differs from an implementation saying:

```text
I only have enough memory for 8 Claims.
```

which is a local resource policy.

---

## 164. OLP Baseline Processing Profile v1

OLP defines the implementation capability:

```text
OLP-BP-1
```

This is not a Record Profile and is not identity-relevant protocol data.

An implementation claiming `OLP-BP-1` MUST be capable of generic processing for an OLP v1 Record or SemanticDefinitionManifest satisfying all of these limits simultaneously:

| Resource | Minimum guaranteed capacity |
|---|---:|
| Standalone canonical OLP-CIE-1 size | 1 MiB |
| Container nesting depth | 32 |
| Entries in one map | 1,024 |
| Elements in one array | 4,096 |
| UTF-8 bytes in one text string | 256 KiB |
| Bytes in one embedded byte string | 256 KiB |
| Decimal coefficient digits | 1,024 |

These are minimum guaranteed capacities, not maximum valid OLP values.

Implementations MAY support larger values.

---

## 165. Constrained Implementations

A constrained implementation MAY implement a smaller subset appropriate to its environment.

It MUST NOT claim `OLP-BP-1` if it does not satisfy the baseline capacity.

A constrained sensor and an archival server may therefore both implement OLP without redefining Record semantics.

---

## 166. Container Depth

Container depth counts nested maps and arrays.

The root map or array has depth:

```text
1
```

Each contained map or array increases depth by one.

Primitive values do not increase container depth.

Example:

```text
{
    a: [
        {
            b: "hello"
        }
    ]
}
```

has maximum container depth:

```text
3
```

The small OLP-CI-1 IdentityPreimage wrapper does not reduce the baseline depth capacity available to the identity-bearing object.

An OLP-BP-1 identity implementation must handle that wrapper overhead in addition to the baseline object.

---

## 167. Canonical Size Measurement

The `1 MiB` baseline refers to:

> the byte length of the standalone logical object's OLP-CIE-1 encoding.

It does not refer to:

- JSON size;
- compressed transport size;
- HTTP message size;
- database storage;
- debug display.

---

## 168. Defensive Allocation

Implementations processing untrusted data SHOULD inspect declared definite lengths before potentially dangerous allocation.

The sequence SHOULD be:

```text
read declared length
        ↓
validate against budget
        ↓
perform allocation / processing
```

rather than allocating first and checking later.

---

## 169. Checked Arithmetic

Length, count, offset, cumulative-size, and allocation arithmetic derived from untrusted input MUST use checked arithmetic.

Integer overflow or wraparound MUST cause safe processing termination.

Examples include:

```text
offset + string_length
map_entries * 2
current_size + next_item_size
```

---

## 170. Duplicate-Key Validation Under Resource Pressure

Resource pressure does not permit skipping duplicate map-key validation.

An implementation MUST either:

- establish map-key uniqueness; or
- stop processing safely.

It MUST NOT silently accept ambiguous maps.

---

## 171. Streaming Canonical Processing

Native OLP-CIE-1 can often be validated and hashed incrementally.

An implementation MAY avoid constructing a complete application object tree if it can still correctly:

- validate canonical representation;
- validate required OLP primitive restrictions;
- preserve all data;
- calculate the required identity.

Streaming and object-tree implementations MUST produce identical identity results.

---

## 172. Preservation by Canonical Bytes

A generic relay or archive MAY preserve already validated native OLP-CIE-1 bytes directly instead of instantiating all unknown semantic structures.

This is a valid lossless strategy if:

1. the complete canonical object was validated;
2. the exact bytes are retained unchanged.

---

## 173. Graph Traversal Is Separately Budgeted

RecordIdentity calculation does not require recursive Reference retrieval.

Higher-level evaluation MAY traverse:

- References;
- SemanticDefinition dependencies;
- StatusChanges;
- Evidence relationships.

Implementations evaluating untrusted graphs MUST bound applicable resources such as:

- graph depth;
- objects visited;
- total bytes fetched;
- number of fetches;
- redirects;
- processing duration.

Exhausting such a budget results in:

```text
resource_limit_exceeded
```

and MUST NOT be interpreted as evidence that unexplored objects do not exist.

---

## 174. Dependency Traversal

SemanticDefinition dependency processors SHOULD maintain a visited set.

If a prohibited exact DefinitionIdentity dependency cycle is actually established, semantic-definition conformance fails.

If processing stops before establishing that conclusion because a resource budget is reached, the result is resource-limit termination rather than invalidity.

---

## 175. Blob Processing

Blob size is not constrained by the `OLP-BP-1` Record/Manifest object-size guarantee.

BlobIdentity SHOULD support incremental hashing.

However, OLP-CIE-1 uses definite-length byte strings.

Therefore an implementation hashing a BlobIdentity CI-1 preimage must know the exact Blob length before encoding the Blob byte-string header.

If the length is not known beforehand, the implementation MAY:

- determine it first;
- spool the content;
- perform multiple passes.

It MUST NOT:

- use indefinite-length CBOR;
- hash the raw Blob bytes directly as a replacement for the CI-1 preimage.

Local Blob retrieval/hashing limits produce resource outcomes, not Blob semantic invalidity.

---

## 176. Reference Validation Does Not Fetch Content

Validating:

```text
ContentReference
```

or:

```text
BlobIdentity
```

does not require obtaining the Blob.

Likewise RecordReference structural validation does not require obtaining the Record.

Retrieval is a separate operation.

---

# Part XIII — Native Interchange

## 177. Native Record Bytes

For logical Record `R`:

```text
NativeRecordBytes(R)
    = OLP-CIE-1(R)
```

These exact bytes are the normative standalone OLP v1 binary interchange representation of the Record.

There is no second binary Record format.

---

## 178. Native Semantic Definition Bytes

For SemanticDefinitionManifest `M`:

```text
NativeDefinitionBytes(M)
    = OLP-CIE-1(M)
```

The expected top-level artifact class is supplied by processing context.

An identity verifier MUST NOT heuristically guess the identity domain from content shape.

---

## 179. Standalone Native Object

A standalone native OLP object contains exactly:

```text
one complete OLP-CIE-1 item
```

and no other bytes.

There is no OLP-internal:

- magic prefix;
- BOM;
- newline;
- NUL terminator;
- self-described-CBOR tag;
- Record separator;
- embedded ContentIdentity.

Trailing data makes the byte sequence invalid as one standalone native object.

---

## 180. Native Round Trip

For accepted native bytes `B`:

```text
decode(B) = V
```

must imply:

```text
OLP-CIE-1(V) = B
```

exactly.

A noncanonical source representation MUST NOT be accepted merely because it decodes to a value that could later be re-encoded canonically.

---

## 181. Record Serialization Is Not RecordIdentity Preimage

If:

```text
B = OLP-CIE-1(R)
```

then RecordIdentity is not generally:

```text
SHA-256(B)
```

Instead:

```text
RecordIdentity(R).digest =
    SHA-256(
        OLP-CIE-1(
            {
                domain: "record",
                suite: "olp/core/identity/content/v1",
                value: R
            }
        )
    )
```

The identity-domain wrapper MUST NOT be optimized away.

---

## 182. Record Sequence v1

OLP v1 defines Record Sequence v1 as an RFC 8742 CBOR Sequence where every item is exactly one native OLP-CIE-1 encoded Record.

If:

```text
B1 = NativeRecordBytes(R1)
B2 = NativeRecordBytes(R2)
B3 = NativeRecordBytes(R3)
```

then the sequence is exactly:

```text
B1 || B2 || B3
```

No additional separator is added.

A Record Sequence MAY contain zero or more Records.

---

## 183. Record Sequence Semantics

Record Sequence is transport framing, not a Record.

It has no RecordIdentity merely by being a sequence.

Each contained Record retains its normal independent RecordIdentity.

Sequence order means transport order only.

It does not imply:

- chronology;
- causality;
- priority;
- supersession;
- Trust;
- provenance.

---

## 184. Sequence Completeness

A Record Sequence does not prove that a dataset or History is complete.

Receiving:

```text
R1
R2
```

does not prove that:

```text
R3
```

does not exist.

If a protocol requires:

- completeness;
- expected item count;
- authenticated order;
- aggregate integrity;

a higher-level Bundle, manifest, synchronization protocol, or commitment must provide those properties explicitly.

---

## 185. Empty Record Sequence

An empty Record Sequence is valid transport.

It means:

```text
zero Records were transported
```

It does not mean:

```text
no Records exist
```

or:

```text
History is empty
```

---

## 186. Sequence Item Errors

If a CBOR item boundary is reliably known but the item fails OLP Record canonical or schema validation, the item is rejected.

A consumer MAY continue with later items where application policy permits per-item errors.

If malformed or truncated CBOR makes subsequent boundaries unreliable, raw sequence processing SHOULD terminate unless trustworthy external framing provides a recovery point.

---

## 187. Duplicate Records in a Sequence

If a sequence contains:

```text
R1
R2
R1
```

the second R1 occurrence does not create a new immutable Record.

RecordIdentity remains identical.

Repeated transport occurrence does not imply:

- independent Evidence creation;
- increased confidence;
- repeated Attestation;
- increased weight.

Applications MAY deduplicate by RecordIdentity where appropriate.

---

## 188. Heterogeneous Sequences

OLP v1 does not define one generic untyped sequence mixing:

- Records;
- SemanticDefinitionManifests;
- Blobs;
- other artifact classes.

A future multiplexing transport must identify artifact classes explicitly.

---

## 189. JSON

OLP v1 does not define a normative JSON serialization.

Implementation-specific JSON MAY be used for:

- APIs;
- diagnostics;
- storage;
- user interfaces.

Such JSON:

- is not canonical OLP serialization;
- MUST NOT be hashed directly for RecordIdentity;
- MUST NOT be assumed interoperable with another implementation merely because both are JSON.

A future OLP JSON transport must preserve the complete logical OLP value losslessly, including:

```text
null
boolean
full int64
byte string versus text
Unicode value
array order
map values
field presence
empty values
unknown information
```

A future JSON mapping must also safely detect duplicate object names before mapping them to OLP maps.

---

## 190. Future Transports

A future transport serialization MAY differ syntactically from OLP-CIE-1.

It MUST recover the exact logical OLP value.

The identity path remains:

```text
transport representation
        ↓
exact OLP logical value
        ↓
OLP-CIE-1
        ↓
OLP-CI-1
```

A transport MUST NOT redefine:

- integer equality;
- byte/text distinction;
- map equality;
- Unicode equality;
- array order;
- field presence;
- ContentIdentity.

---

## 191. Transport Security

Native serialization provides deterministic representation.

It does not provide:

- confidentiality;
- sender authentication;
- replay protection;
- authenticated sequence completeness;
- transport integrity by itself.

Those properties belong to separate security layers.

---

# Part XIV — Normative Conformance Vectors

## 192. OLP-TV-1

OLP v1 defines:

```text
OLP-TV-1
```

the normative Conformance and Cryptographic Test Vector Suite.

Two independent implementations claiming OLP v1 identity interoperability MUST reproduce the applicable positive:

- bytes;
- SHA-256 digests;
- Base32 identities;

and MUST produce the specified classification for applicable negative vectors.

Lowercase hexadecimal is used below.

Whitespace inserted for readability is not part of the byte sequence.

---

## 193. Primitive OLP-CIE-1 Vectors

| Logical value | Exact OLP-CIE-1 hex |
|---|---|
| `null` | `f6` |
| `false` | `f4` |
| `true` | `f5` |
| `0` | `00` |
| `23` | `17` |
| `24` | `1818` |
| `255` | `18ff` |
| `256` | `190100` |
| `65535` | `19ffff` |
| `65536` | `1a00010000` |
| `4294967295` | `1affffffff` |
| `4294967296` | `1b0000000100000000` |
| `9223372036854775807` | `1b7fffffffffffffff` |
| `-1` | `20` |
| `-24` | `37` |
| `-25` | `3818` |
| `-256` | `38ff` |
| `-257` | `390100` |
| `-65536` | `39ffff` |
| `-65537` | `3a00010000` |
| `-4294967296` | `3affffffff` |
| `-4294967297` | `3b0000000100000000` |
| `-9223372036854775808` | `3b7fffffffffffffff` |
| empty byte string | `40` |
| byte string `00ff` | `4200ff` |
| empty text | `60` |
| text `"a"` | `6161` |
| text `"€"` | `63e282ac` |
| text U+00E9 | `62c3a9` |
| text U+0065 U+0301 | `6365cc81` |
| empty array | `80` |
| `[1,2]` | `820102` |
| empty map | `a0` |

---

## 194. Unicode Non-Normalization Vector

These logical strings MUST remain distinct:

```text
U+00E9
```

encoding:

```text
62c3a9
```

and:

```text
U+0065 U+0301
```

encoding:

```text
6365cc81
```

An implementation normalizing them into one logical value fails OLP-TV-1.

---

## 195. Canonical Map Ordering Vector

Logical map:

```text
{
    "b": 1,
    "aa": 2
}
```

MUST encode exactly as:

```text
a261620162616102
```

The canonical deterministic key encodings are:

```text
"b"  → 6162
"aa" → 626161
```

---

## 196. Decimal Vector

Logical Decimal:

```text
{
    coefficient: "12345",
    exponent: -2
}
```

MUST encode as:

```text
a2686578706f6e656e74216b636f656666696369656e74653132333435
```

It represents exactly:

```text
123.45
```

---

## 197. TimePoint Vector

Logical value:

```text
{
    system:
      "olp/core/time_system/utc/v1",

    value:
    {
        timestamp:
          "2026-08-19T17:11:42.5Z"
    }
}
```

MUST encode as:

```text
a26576616c7565a16974696d657374616d7076323032362d30382d31395431373a31313a34322e355a6673797374656d781b6f6c702f636f72652f74696d655f73797374656d2f7574632f7631
```

---

## 198. TemporalValue Instant Vector

Logical value:

```text
{
    kind: "instant",
    at:
    {
        system:
          "olp/core/time_system/utc/v1",

        value:
        {
            timestamp:
              "2026-08-19T17:11:42.5Z"
        }
    }
}
```

MUST encode as:

```text
a2626174a26576616c7565a16974696d657374616d7076323032362d30382d31395431373a31313a34322e355a6673797374656d781b6f6c702f636f72652f74696d655f73797374656d2f7574632f7631646b696e6467696e7374616e74
```

---

## 199. Definition Manifest Integration Vector

Logical manifest:

```text
{
    manifest_version: 1,

    definitions:
    [
        {
            semantic_id:
              "olp/dns/example.com/predicate/test/v1",

            format:
              "olp/core/definition_format/normative_text/v1",

            definition:
            {
                text:
                  "A zero-argument test predicate."
            }
        }
    ]
}
```

Exact native OLP-CIE-1 bytes:

```text
a26b646566696e6974696f6e7381a366666f726d6174782c6f6c702f636f72652f646566696e6974696f6e5f666f726d61742f6e6f726d61746976655f746578742f76316a646566696e6974696f6ea16474657874781f41207a65726f2d617267756d656e742074657374207072656469636174652e6b73656d616e7469635f696478256f6c702f646e732f6578616d706c652e636f6d2f7072656469636174652f746573742f7631706d616e69666573745f76657273696f6e01
```

Length:

```text
187 bytes
```

---

## 200. DefinitionIdentity Preimage Vector

CI-1 logical preimage:

```text
{
    domain:
      "semantic_definition",

    suite:
      "olp/core/identity/content/v1",

    value:
      <manifest from section 199>
}
```

Exact OLP-CIE-1 bytes:

```text
a3657375697465781c6f6c702f636f72652f6964656e746974792f636f6e74656e742f76316576616c7565a26b646566696e6974696f6e7381a366666f726d6174782c6f6c702f636f72652f646566696e6974696f6e5f666f726d61742f6e6f726d61746976655f746578742f76316a646566696e6974696f6ea16474657874781f41207a65726f2d617267756d656e742074657374207072656469636174652e6b73656d616e7469635f696478256f6c702f646e732f6578616d706c652e636f6d2f7072656469636174652f746573742f7631706d616e69666573745f76657273696f6e0166646f6d61696e7373656d616e7469635f646566696e6974696f6e
```

Length:

```text
257 bytes
```

SHA-256:

```text
201dbc9eef58cad99d81f5fd4ef1a81dee7784c77e835fbad334c24f9b986d2e
```

Unpadded uppercase Base32:

```text
EAO3ZHXPLDFNTHMB6X6U54NIDXXHPBGHP2BV7OWTGTBE7G4YNUXA
```

Canonical textual DefinitionIdentity:

```text
olp-definition-ci1-EAO3ZHXPLDFNTHMB6X6U54NIDXXHPBGHP2BV7OWTGTBE7G4YNUXA
```

---

## 201. Native DefinitionIdentity Vector

Logical native value:

```text
{
    domain: "semantic_definition",
    suite: "olp/core/identity/content/v1",
    digest:
      h'201dbc9eef58cad99d81f5fd4ef1a81dee7784c77e835fbad334c24f9b986d2e'
}
```

Exact encoding:

```text
a3657375697465781c6f6c702f636f72652f6964656e746974792f636f6e74656e742f7631666469676573745820201dbc9eef58cad99d81f5fd4ef1a81dee7784c77e835fbad334c24f9b986d2e66646f6d61696e7373656d616e7469635f646566696e6974696f6e
```

---

## 202. Claim Record Integration Vector

Logical Record:

```text
{
    envelope_version: 1,

    type:
      "olp/core/type/claim/v1",

    content:
    {
        predicate:
          "olp/dns/example.com/predicate/test/v1",

        arguments: {}
    },

    semantic_bindings:
    [
        {
            semantic_id:
              "olp/dns/example.com/predicate/test/v1",

            definition:
            {
                domain:
                  "semantic_definition",

                suite:
                  "olp/core/identity/content/v1",

                digest:
                  h'201dbc9eef58cad99d81f5fd4ef1a81dee7784c77e835fbad334c24f9b986d2e'
            }
        }
    ]
}
```

Exact native Record bytes:

```text
a46474797065766f6c702f636f72652f747970652f636c61696d2f763167636f6e74656e74a269617267756d656e7473a06970726564696361746578256f6c702f646e732f6578616d706c652e636f6d2f7072656469636174652f746573742f763170656e76656c6f70655f76657273696f6e017173656d616e7469635f62696e64696e677381a26a646566696e6974696f6ea3657375697465781c6f6c702f636f72652f6964656e746974792f636f6e74656e742f7631666469676573745820201dbc9eef58cad99d81f5fd4ef1a81dee7784c77e835fbad334c24f9b986d2e66646f6d61696e7373656d616e7469635f646566696e6974696f6e6b73656d616e7469635f696478256f6c702f646e732f6578616d706c652e636f6d2f7072656469636174652f746573742f7631
```

Length:

```text
303 bytes
```

---

## 203. RecordIdentity Preimage Vector

Logical preimage:

```text
{
    domain: "record",
    suite: "olp/core/identity/content/v1",
    value: <Claim Record from section 202>
}
```

Exact bytes:

```text
a3657375697465781c6f6c702f636f72652f6964656e746974792f636f6e74656e742f76316576616c7565a46474797065766f6c702f636f72652f747970652f636c61696d2f763167636f6e74656e74a269617267756d656e7473a06970726564696361746578256f6c702f646e732f6578616d706c652e636f6d2f7072656469636174652f746573742f763170656e76656c6f70655f76657273696f6e017173656d616e7469635f62696e64696e677381a26a646566696e6974696f6ea3657375697465781c6f6c702f636f72652f6964656e746974792f636f6e74656e742f7631666469676573745820201dbc9eef58cad99d81f5fd4ef1a81dee7784c77e835fbad334c24f9b986d2e66646f6d61696e7373656d616e7469635f646566696e6974696f6e6b73656d616e7469635f696478256f6c702f646e732f6578616d706c652e636f6d2f7072656469636174652f746573742f763166646f6d61696e667265636f7264
```

Length:

```text
360 bytes
```

SHA-256:

```text
d0a217641e62ec1d806dac98a1e290133f25fb91cfdfb3b8f26dfe910b52e432
```

Base32:

```text
2CRBOZA6MLWB3ADNVSMKDYUQCM7SL64RZ7P3HOHSNX7JCC2S4QZA
```

Canonical RecordIdentity text:

```text
olp-record-ci1-2CRBOZA6MLWB3ADNVSMKDYUQCM7SL64RZ7P3HOHSNX7JCC2S4QZA
```

---

## 204. Native RecordIdentity Vector

Logical value:

```text
{
    domain: "record",
    suite: "olp/core/identity/content/v1",
    digest:
      h'd0a217641e62ec1d806dac98a1e290133f25fb91cfdfb3b8f26dfe910b52e432'
}
```

Exact encoding:

```text
a3657375697465781c6f6c702f636f72652f6964656e746974792f636f6e74656e742f7631666469676573745820d0a217641e62ec1d806dac98a1e290133f25fb91cfdfb3b8f26dfe910b52e43266646f6d61696e667265636f7264
```

---

## 205. BlobIdentity Vector

Exact Blob bytes:

```text
00010203ff
```

CI-1 preimage logical value:

```text
{
    domain: "blob",
    suite: "olp/core/identity/content/v1",
    value: h'00010203ff'
}
```

Exact preimage bytes:

```text
a3657375697465781c6f6c702f636f72652f6964656e746974792f636f6e74656e742f76316576616c75654500010203ff66646f6d61696e64626c6f62
```

SHA-256:

```text
f84c9f5e0d84a467b3d9aa380c3cb0d5e76f615ada8709ac9e385c3d2f3af712
```

Base32:

```text
7BGJ6XQNQSSGPM6ZVI4AYPFQ2XTW6YK23KDQTLE6HBOD2LZ264JA
```

Canonical BlobIdentity text:

```text
olp-blob-ci1-7BGJ6XQNQSSGPM6ZVI4AYPFQ2XTW6YK23KDQTLE6HBOD2LZ264JA
```

Native BlobIdentity encoding:

```text
a3657375697465781c6f6c702f636f72652f6964656e746974792f636f6e74656e742f7631666469676573745820f84c9f5e0d84a467b3d9aa380c3cb0d5e76f615ada8709ac9e385c3d2f3af71266646f6d61696e64626c6f62
```

---

## 206. RecordReference Vector

Using the RecordIdentity from section 203:

```text
{
    kind: "record",
    identity:
    {
        domain: "record",
        suite: "olp/core/identity/content/v1",
        digest:
          h'd0a217641e62ec1d806dac98a1e290133f25fb91cfdfb3b8f26dfe910b52e432'
    }
}
```

MUST encode as:

```text
a2646b696e64667265636f7264686964656e74697479a3657375697465781c6f6c702f636f72652f6964656e746974792f636f6e74656e742f7631666469676573745820d0a217641e62ec1d806dac98a1e290133f25fb91cfdfb3b8f26dfe910b52e43266646f6d61696e667265636f7264
```

---

## 207. Record Sequence Vector

Let:

```text
R
```

be the exact 303-byte Claim Record from section 202.

The normative two-item Record Sequence is exactly:

```text
R || R
```

with total length:

```text
606 bytes
```

There is no delimiter, newline, array wrapper, or length prefix.

Both extracted Records MUST exactly equal the original 303 native bytes and have the RecordIdentity from section 203.

---

## 208. Negative: Non-Minimal Integer

Input:

```text
1800
```

represents integer zero using a non-minimal CBOR encoding.

Expected result:

```text
native OLP-CIE-1 rejected
```

The implementation MUST NOT silently canonicalize it to:

```text
00
```

while accepting the original as canonical.

---

## 209. Negative: Indefinite Array

Input:

```text
9f01ff
```

is an indefinite-length CBOR array.

Expected:

```text
native OLP-CIE-1 rejected
```

---

## 210. Negative: Floating Point

Input:

```text
f93c00
```

is valid CBOR floating-point `1.0`.

Expected:

```text
CBOR syntax                valid
OLP logical primitive      invalid
```

Floating point is not an OLP v1 primitive.

---

## 211. Negative: CBOR Tag

Input:

```text
c06178
```

is CBOR tag 0 containing text `"x"`.

Expected:

```text
OLP logical primitive model rejected
```

Generic CBOR tags are prohibited.

---

## 212. Negative: Undefined

Input:

```text
f7
```

Expected:

```text
OLP logical primitive model rejected
```

`undefined` is not an OLP v1 value.

---

## 213. Negative: Other Simple Value

Input:

```text
e0
```

Expected:

```text
OLP logical primitive model rejected
```

Only:

```text
false
true
null
```

are permitted CBOR simple values.

---

## 214. Negative: Integer Outside Int64

Input:

```text
1b8000000000000000
```

represents:

```text
9223372036854775808
```

Expected:

```text
CBOR integer              valid
OLP int64                 invalid
```

---

## 215. Negative: Invalid UTF-8

Input:

```text
62c328
```

declares a two-byte CBOR text string containing invalid UTF-8.

Expected:

```text
representation rejected
```

---

## 216. Negative: Duplicate Map Key

Input:

```text
a2616101616102
```

contains key `"a"` twice.

Expected:

```text
OLP logical map rejected
```

An implementation fails this vector if it returns either:

```text
{"a": 1}
```

or:

```text
{"a": 2}
```

as though the original map were valid.

---

## 217. Negative: Noncanonical Map Order

Input:

```text
a262616102616201
```

encodes:

```text
"aa": 2
"b": 1
```

in noncanonical deterministic order.

The exact canonical bytes for the same logical map are:

```text
a261620162616102
```

Expected:

```text
native OLP-CIE-1 rejected
```

The original bytes MUST NOT be silently accepted and reordered.

---

## 218. Negative: Invalid ProtocolKey

Input:

```text
a1614101
```

represents:

```text
{
    "A": 1
}
```

Expected:

```text
deterministic CBOR       valid
OLP map key              invalid
```

---

## 219. Schema-Negative Decimal

Logical structure:

```text
{
    coefficient: "01",
    exponent: 0
}
```

has exact OLP-CIE-1 encoding:

```text
a2686578706f6e656e74006b636f656666696369656e74623031
```

Expected:

```text
OLP-CIE-1                valid
Decimal v1 schema        invalid
```

The canonical encoder MUST NOT rewrite `"01"` to `"1"`.

---

## 220. Schema-Negative UTC Timestamp

Logical TimePoint:

```text
{
    system:
      "olp/core/time_system/utc/v1",

    value:
    {
        timestamp:
          "2026-08-19T17:11:42.500Z"
    }
}
```

Exact deterministic encoding:

```text
a26576616c7565a16974696d657374616d707818323032362d30382d31395431373a31313a34322e3530305a6673797374656d781b6f6c702f636f72652f74696d655f73797374656d2f7574632f7631
```

Expected:

```text
OLP-CIE-1                valid
UTC TimePoint schema     invalid
```

because fractional trailing zeroes violate the canonical UTC lexical form.

The encoder MUST NOT rewrite the timestamp.

---

## 221. Schema-Negative Set Ordering

OLP-TV-1 MUST contain a two-definition SemanticDefinitionManifest where:

```text
A semantic_id =
    olp/dns/example.com/predicate/a/v1

B semantic_id =
    olp/dns/example.com/predicate/b/v1
```

The manifest with:

```text
definitions: [A, B]
```

passes manifest ordering.

The otherwise identical manifest with:

```text
definitions: [B, A]
```

MUST be:

```text
OLP-CIE-1                              valid
SemanticDefinitionManifest v1 schema  invalid
```

The CIE encoder MUST NOT reorder the array.

---

## 222. Negative: Standalone Trailing Data

Input:

```text
f600
```

contains two complete CBOR items:

```text
null
0
```

In standalone-object context the expected result is:

```text
rejected as one standalone OLP object
```

The final `00` MUST NOT be silently ignored.

---

## 223. ContentIdentity Canonical Text Vector

Canonical RecordIdentity:

```text
olp-record-ci1-2CRBOZA6MLWB3ADNVSMKDYUQCM7SL64RZ7P3HOHSNX7JCC2S4QZA
```

A strict canonical parser MUST reject:

```text
olp-record-ci1-2crboza6mlwb3adnvsmkdyuqcm7sl64rz7p3hohsnx7jcc2s4qza
```

and:

```text
olp-record-ci1-2CRBOZA6MLWB3ADNVSMKDYUQCM7SL64RZ7P3HOHSNX7JCC2S4QZA=
```

and any form containing whitespace.

---

## 224. Negative: Base32 Non-Zero Pad Bits

The canonical RecordIdentity ends with:

```text
...QZA
```

A permissive Base32 implementation may decode a noncanonical final symbol such as:

```text
olp-record-ci1-2CRBOZA6MLWB3ADNVSMKDYUQCM7SL64RZ7P3HOHSNX7JCC2S4QZB
```

to the same 32 digest bytes because the differing bits fall in unused Base32 pad bits.

A conforming canonical OLP parser MUST reject this representation.

This vector enforces:

```text
canonical_encode(parse(input)) == input
```

and zero unused Base32 pad bits.

---

## 225. SemanticIdentifier Lexical Vectors

### Valid canonical

```text
olp/core/type/claim/v1
olp/dns/example.com/predicate/shipment_delivered/v1
olp/dns/xn--bcher-kva.example/predicate/test/v2
```

### Lexically valid but potentially unsupported by OLP v1 semantics

For an unknown future method satisfying the generic authority envelope, for example:

```text
olp/key/abc123/type/foo/v1
```

the expected classification is:

```text
lexically valid
namespace method unsupported
```

### Invalid

```text
OLP/core/type/claim/v1
olp/core/type/Claim/v1
olp/core/type/claim/v01
olp/core/type/claim/v0
olp/dns/Example.com/type/foo/v1
olp/dns/example.com./type/foo/v1
olp/dns/foo_bar.example/type/foo/v1
olp/dns/bücher.example/type/foo/v1
```

---

## 226. Identity Mismatch Vector

Given the Claim Record in section 202, the calculated RecordIdentity digest is:

```text
d0a217641e62ec1d806dac98a1e290133f25fb91cfdfb3b8f26dfe910b52e432
```

If an externally supplied expected RecordIdentity differs by one or more bits:

```text
Record parsing             may remain valid
RecordIdentity calculation valid
identity-match property    failed
```

The implementation MUST NOT infer from the mismatch alone that:

- the Claim is false;
- an Issuer is fraudulent;
- the Record schema is invalid;
- the Record is untrustworthy.

Only the expected-identity match failed.

---

## 227. OLP-BP-1 Generated Capability Vectors

Rather than embedding megabytes of test hex, OLP-TV-1 SHALL include deterministic generated tests establishing `OLP-BP-1` capability at the boundaries:

```text
container depth            32
single array               4096 elements
single map                 1024 entries
single byte string         256 KiB
single UTF-8 text string   256 KiB
Decimal coefficient        1024 digits
standalone canonical item  1 MiB
```

provided all applicable baseline limits are simultaneously satisfied.

Values immediately above these numbers are not automatically invalid OLP.

They are simply beyond the `OLP-BP-1` guaranteed minimum.

---

## 228. Test Infrastructure Is Not OLP Serialization

Machine-readable OLP-TV-1 fixture files MAY use:

- JSON;
- CBOR;
- Python structures;
- text;
- other test harness formats.

Such fixture containers are test infrastructure only.

They do not create new normative OLP transport serializations.

---

# Part XV — Security and Privacy Considerations

## 229. Deterministic Identity Is Linkable

ContentIdentity is deterministic.

The same exact Record produces the same RecordIdentity wherever it appears.

Therefore stable identity enables correlation.

If two independent datasets expose:

```text
RecordIdentity(R)
```

an observer can determine that they refer to the same exact Record.

This is useful for independent verification and portability.

It is not unlinkability.

---

## 230. ContentIdentity Is Not Confidentiality

RecordIdentity, DefinitionIdentity, and BlobIdentity are not encryption.

A deterministic digest of low-entropy or guessable content may permit dictionary comparison.

For example, an observer with a small set of candidate Blob values may compute BlobIdentity for each candidate and compare them.

Applications MUST NOT publish deterministic ContentIdentity values for guessable secret content expecting the hash to conceal that content.

---

## 231. BlobIdentity Is Not a Hiding Commitment

BlobIdentity commits to exact bytes for integrity and identity purposes.

It is not a privacy-preserving commitment scheme.

Applications needing hiding or salted commitments require separate cryptographic mechanisms.

---

## 232. EntityReference Linkage

Including multiple Identifiers in one EntityReference explicitly asserts that they refer to the same entity in that occurrence.

Publishing:

```text
Identifier A
Identifier B
```

together can therefore create a privacy-relevant linkage.

Applications SHOULD minimize unnecessary Identifier co-disclosure.

---

## 233. Stable Identifiers and Transport Encryption

Transport encryption protects content in transit.

It does not automatically prevent correlation where stable RecordIdentity or other deterministic identifiers are disclosed to the same or multiple observers.

Privacy-sensitive applications must consider metadata correlation independently of transport confidentiality.

---

## 234. Unicode and Confusables

OLP preserves Unicode exactly and performs no confusable normalization.

User interfaces SHOULD:

- visually distinguish security-sensitive canonical identifiers;
- display escaped or annotated forms where ambiguity is dangerous;
- avoid implying equality from visual similarity.

UI protections MUST NOT alter RecordIdentity.

---

## 235. Internationalized DNS Presentation

Canonical DNS namespace authorities are ASCII.

Software presenting an `xn--` label as Unicode MUST first establish that the label is a valid IDNA A-label under the applicable presentation rules.

A fake or invalid A-label MUST NOT be blindly rendered as though it were an authenticated Unicode domain.

Canonical SID identity remains the ASCII form.

---

## 236. Namespace Takeover

Current control of a DNS name does not retroactively alter historical SemanticBindings.

Historical Records bind non-core semantics to DefinitionIdentity.

Applications evaluating whether a binding was namespace-authorized must use appropriate Evidence about namespace authority at the relevant time.

---

## 237. Malicious Semantic Definitions

A retrieved SemanticDefinitionManifest may be:

- malicious;
- misleading;
- unexpectedly complex;
- unauthorized by the claimed namespace.

DefinitionIdentity verification proves only exact manifest identity.

It does not establish:

- authority;
- safety;
- Trust;
- correctness.

Definitions MUST NOT be automatically executed merely because they verify cryptographically.

---

## 238. Resource Exhaustion

Untrusted OLP input may attempt to exhaust:

- memory;
- CPU;
- stack;
- storage;
- network;
- graph traversal.

Implementations MUST use bounded defensive processing.

Resource exhaustion MUST NOT cause:

- unchecked integer arithmetic;
- ambiguous duplicate-key handling;
- silent truncation;
- semantic guesses.

---

## 239. Reference Amplification

A small Record may reference a very large or deep external graph.

Basic identity and structural validation MUST NOT automatically recursively retrieve References.

Graph traversal requires explicit application intent and resource budgets.

---

## 240. Status Authority Spoofing

Anyone may be able to create a structurally valid StatusChange Record claiming:

```text
actor = E
```

This does not make E an authorized status authority.

Applications MUST evaluate authority separately before deriving status effects.

---

## 241. Issuer Spoofing

Likewise, anyone may construct an Attestation whose declared Issuer is some EntityReference.

The field is declared attribution.

It becomes verified attribution only when sufficient Evidence establishes the necessary connection between the Record, cryptographic/provenance evidence, and the represented Issuer.

---

## 242. Observer Spoofing

Observation `observer` is represented provenance, not proof.

Applications MUST NOT treat an Observer EntityReference as authenticated merely because it appears in Observation content.

---

## 243. Party Misrepresentation

A Party entry represents that an entity occupied a role in an Event or Interaction.

It does not establish:

- participation actually happened;
- consent;
- agreement;
- legal effect.

Applications must evaluate relevant Evidence.

---

## 244. Hash Collisions

OLP-CI-1 relies on SHA-256 collision resistance as a cryptographic security assumption.

Nevertheless, implementation correctness MUST fail closed if distinct complete canonical preimages associated with one ContentIdentity are actually observed.

Digest equality alone MUST NOT authorize destructive merging when complete conflicting preimages are present.

---

## 245. No Silent History Rewriting

Security or policy corrections MUST NOT be implemented by silently mutating historical Records.

Corrections and lifecycle changes should be represented through new explicit Records.

This preserves auditable Evidence of what was previously represented.

---

# Part XVI — Core Semantic Summary

## 246. Core Record Hierarchy

OLP v1 defines:

```text
Record
├── Claim
├── Attestation
├── Observation
├── Event
│   └── Interaction
└── StatusChange
```

This hierarchy expresses semantic specialization, not object-oriented runtime inheritance requirements.

---

## 247. Core Reusable Structures

This specification defines or freezes representation for:

```text
Decimal
ContentIdentity
SemanticBinding
ProfileEntry
RelationshipEntry
ExtensionEntry
Reference
Identifier
EntityReference
ClaimExpression
TimePoint
TemporalValue
Party
```

Proof representation is deliberately deferred.

---

## 248. Conceptual Separation

The semantic distinctions are:

```text
ClaimExpression
    = proposition

Claim Record
    = independently materialized proposition

Attestation
    = declared Issuer asserts proposition(s)

Observation
    = observation process purportedly produced proposition(s)

Event
    = purported occurrence

Interaction
    = multi-entity Event

StatusChange
    = immutable lifecycle/status Evidence
```

These structures can refer to or provide Evidence about one another without collapsing their meanings.

---

## 249. Identity, Reference, Relationship, and Discovery

OLP maintains the distinction:

```text
identity
    → what exact immutable thing?

reference
    → which thing?

relationship
    → how is this Record related to that thing?

discovery
    → where might a copy currently be obtained?
```

These concepts MUST NOT be silently conflated.

---

## 250. Evidence Versus Trust

Nothing in this representation specification defines one universal Trust conclusion.

Records provide independently verifiable structured information.

Applications and Trust Models evaluate that information in Context.

Thus:

```text
Evidence
        ↓
Trust Model + Context
        ↓
contextual reliance conclusion
        ↓
application decision
```

remains outside Record identity.

---

# Part XVII — References

## 251. Normative and Informative Standards

The following external specifications are relevant to OLP v1 representation.

### RFC 2119

**Key words for use in RFCs to Indicate Requirement Levels**

Used for normative requirement terminology.

### RFC 8174

**Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words**

Used together with RFC 2119 for normative requirement terminology.

### RFC 8949

**Concise Binary Object Representation (CBOR)**

Defines CBOR and the deterministic encoding framework narrowed by `OLP-CIE-1`.

### RFC 8742

**Concise Binary Object Representation (CBOR) Sequences**

Defines the framing model used by Record Sequence v1.

### RFC 4648

**The Base16, Base32, and Base64 Data Encodings**

Defines Base32 used by canonical ContentIdentity text.

### RFC 3339

**Date and Time on the Internet: Timestamps**

Provides the timestamp model narrowed by the OLP core UTC Time System.

### RFC 1035

**Domain Names — Implementation and Specification**

Provides relevant DNS label and domain-length foundations.

### RFC 1123

**Requirements for Internet Hosts — Application and Support**

Provides hostname syntax updates including numeric-leading labels.

### RFC 4343

**Domain Name System (DNS) Case Insensitivity Clarification**

Relevant to the distinction between DNS comparison rules and OLP's lowercase canonical authority form.

### RFC 5890

**Internationalized Domain Names for Applications (IDNA): Definitions and Document Framework**

Provides terminology for A-labels and U-labels relevant to OLP DNS namespace presentation.

### FIPS PUB 180-4

**Secure Hash Standard (SHS)**

Defines SHA-256 used by `OLP-CI-1`.

---

# Appendix A — Canonical Core SemanticIdentifiers

The following core SemanticIdentifiers are defined or reserved by this specification:

```text
olp/core/type/claim/v1
olp/core/type/attestation/v1
olp/core/type/observation/v1
olp/core/type/event/v1
olp/core/type/interaction/v1
olp/core/type/status_change/v1

olp/core/identity/content/v1

olp/core/definition_format/normative_text/v1

olp/core/time_system/utc/v1

olp/core/role/participant/v1

olp/core/status_operation/revocation/v1
olp/core/status_operation/supersession/v1
```

Additional core Predicates, Identifier schemes, Profiles, Extensions, Relationships, Proof semantics, or other domain semantics require separate specification.

---

# Appendix B — Canonical Record Envelope Summary

```text
Record {
    envelope_version: 1,
    type: SemanticIdentifier,
    content: map<ProtocolKey, OLPValue>,
    semantic_bindings?: [SemanticBinding, ...],
    profiles?: [ProfileEntry, ...],
    relationships?: [RelationshipEntry, ...],
    extensions?: [ExtensionEntry, ...]
}
```

Mandatory:

```text
envelope_version
type
content
```

Optional and omitted when empty:

```text
semantic_bindings
profiles
relationships
extensions
```

Not universal:

```text
id
issuer
subject
proof
created_at
status
trust
metadata
```

---

# Appendix C — Identity Construction Summary

For Record `R`:

```text
P =
{
    domain: "record",
    suite: "olp/core/identity/content/v1",
    value: R
}

digest =
    SHA-256(OLP-CIE-1(P))

RecordIdentity =
{
    domain: "record",
    suite: "olp/core/identity/content/v1",
    digest: digest
}
```

For SemanticDefinitionManifest `M`:

```text
P =
{
    domain: "semantic_definition",
    suite: "olp/core/identity/content/v1",
    value: M
}
```

For Blob bytes `B`:

```text
P =
{
    domain: "blob",
    suite: "olp/core/identity/content/v1",
    value: B
}
```

The three identity domains are intentionally distinct.

---

# Appendix D — Validation Principle

A conforming implementation should be able to distinguish statements such as:

```text
representation canonical          yes
Record envelope valid             yes
RecordIdentity verified           yes
type semantics supported          no
referenced data available         no
proof verified                    not applicable
status conclusion                 indeterminate
Trust conclusion                  application-specific
```

rather than compressing them into one ambiguous Boolean.

The protocol's fundamental rule is:

> Verification of one property does not silently establish another property.

---

# Appendix E — Final Design Invariants

The following invariants summarize the representation model.

```text
Evidence over reputation.

Record identity over mutable location.

Logical identity over transport bytes.

Declared attribution ≠ verified attribution.

Issuer ≠ signer.

Observer ≠ issuer.

Party ≠ consent.

Identifier ≠ proof of identity.

RecordReference ≠ endorsement.

DefinitionIdentity ≠ namespace authority.

StatusChange ≠ global mutable state.

Revocation ≠ erasure.

Supersession ≠ revocation.

Absence of status Evidence ≠ active status.

Timestamp syntax ≠ trusted time.

RecordIdentity ≠ Truth.

Cryptographic integrity ≠ Trust.

Unknown semantics ≠ invalid representation.

Resource exhaustion ≠ invalid Record.

Transport order ≠ chronology.

Stable hash identity ≠ confidentiality.

One semantic fact → one canonical structural channel.

No silent history rewriting.

No universal Trust score.

No universal Trust Model.

Independent verifiability remains possible without central ownership of Trust.