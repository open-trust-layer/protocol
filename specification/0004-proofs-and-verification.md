# OLP Specification 0004 — Proofs and Verification

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 4 — Proofs & Verification  
**Filename:** `specification/0004-proofs-and-verification.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) v1 proof and verification layer.

It defines:

- detached proof semantics;
- the `OLPProof` abstract data model;
- the exact v1 cryptographic Proof Input;
- deterministic CBOR encoding requirements;
- record commitments;
- the mandatory OLP v1 Ed25519 cryptosuite;
- proof purposes;
- verification-method resolution boundaries;
- extension and critical-extension processing;
- multiple-proof semantics;
- time, expiration, key-status, and historical-validity semantics;
- proof creation and verification algorithms;
- structured verification results;
- conformance requirements; and
- security considerations.

The proof layer establishes cryptographic properties. It does not establish truth, trustworthiness, legal effect, authority, reputation, identity, or policy acceptance.

---

## 2. Scope

This specification answers the question:

> How can an independent party cryptographically verify that a proof producer intentionally bound a supported verification method to exactly one immutable OLP record under an explicit proof purpose and proof context?

This specification does **not** define:

- a universal identity system;
- a universal trust model;
- a universal authorization policy;
- a universal reputation score;
- a universal key registry;
- a universal revocation authority;
- a universal timestamp authority;
- a mandatory blockchain;
- a mandatory DID method;
- a mandatory PKI;
- proof chains or general evidence graphs;
- proof identifiers; or
- application-specific trust decisions.

Those concerns may be represented by additional evidence or handled by higher protocol or application layers.

---

## 3. Requirements Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described by BCP 14 when, and only when, they appear in all capitals.

---

## 4. Core Invariants

The following invariants are normative.

### 4.1 Detached proofs

An OLP record has an identity independent of any proof concerning it.

A proof is a logically detached cryptographic artifact that binds to an immutable OLP record.

Adding, removing, transporting, storing, or reordering proofs MUST NOT change the record's identity or canonical representation.

Records and proofs MAY be packaged together for transport without becoming one protocol object.

### 4.2 Cryptographic verification is not truth

Successful proof verification establishes cryptographic properties only.

A successful verification MUST NOT be interpreted by OLP as establishing:

- factual truth;
- accuracy;
- legality;
- legal effect;
- identity;
- authority;
- reputation;
- reliability;
- trustworthiness;
- evidentiary sufficiency; or
- policy acceptance.

Applications MAY make such determinations using local policy and additional evidence.

### 4.3 Deterministic verification, pluralistic interpretation

Given identical:

- record data;
- proof data;
- resolved verification material;
- verification context; and
- supported cryptographic primitives,

conforming implementations MUST reach the same cryptographic result.

Applications MAY legitimately reach different trust or policy conclusions from the same cryptographically verified evidence.

### 4.4 Cryptographic control is not identity

A valid proof establishes control of the private key corresponding to the verification material used for the proof at proof-generation time, subject to the security assumptions of the cryptosuite.

It does not, by itself, establish the real-world identity of the controller.

### 4.5 No silent history rewriting

A later change in key status, cryptosuite recommendation, resolver state, or application policy MUST NOT retroactively alter whether a historical signature mathematically verifies.

Changing current interpretation or reliance policy is distinct from changing historical cryptographic validity.

---

## 5. Terminology

### 5.1 Record

An immutable OLP record conforming to the applicable OLP record specification.

### 5.2 Record Identity

The stable OLP identity of a record as defined by the record-representation specification.

Record Identity and proof `recordCommitment` are related but distinct concepts.

### 5.3 Proof

An `OLPProof` object containing authenticated proof configuration, a record commitment, and cryptographic proof material.

### 5.4 Proof producer

The entity controlling the private key or other proving material used to generate a proof.

This term does not imply a real-world identity.

### 5.5 Verification method

An identifier referring to the public cryptographic material needed to verify a proof.

### 5.6 Resolved verification method

Structured verification material supplied to the cryptographic verifier after resolution.

### 5.7 Cryptosuite

A fully specified cryptographic procedure defining how a proof is generated and verified.

### 5.8 Proof Input

The deterministic abstract structure cryptographically authenticated by an OLP proof.

### 5.9 Proof Input bytes

The deterministic CBOR encoding of the Proof Input.

### 5.10 Record commitment

A self-describing cryptographic digest over the canonical record identity bytes.

### 5.11 Proof purpose

The proof producer's authenticated intent toward the referenced record.

### 5.12 Proof set

An unordered contextual collection of independent proofs concerning the same record.

A proof set is not a proof chain.

---

## 6. `OLPProof` Abstract Data Model

An OLP v1 proof contains the following mandatory core properties:

| Property | Type | Required | v1 rule |
|---|---|---:|---|
| `type` | text string | yes | MUST equal `OLPProof` |
| `version` | integer | yes | MUST equal `1` |
| `cryptosuite` | text string | yes | Fully specifies cryptographic processing |
| `proofPurpose` | text string | yes | Exactly one purpose |
| `verificationMethod` | text string | yes | Absolute URI |
| `recordCommitment` | RecordCommitment | yes | Algorithm identifier + digest bytes |
| `proofValue` | byte string | yes | Suite-defined proof bytes |

The following standardized optional authenticated properties are defined by v1:

| Property | Type | Meaning |
|---|---|---|
| `created` | RFC 3339 date-time string | Proof producer's asserted creation time |
| `expires` | RFC 3339 date-time string | Proof producer's asserted reliance-expiration time |
| `domain` | non-empty text string | Intended security/application domain |
| `challenge` | non-empty byte string | Caller- or protocol-supplied challenge |
| `nonce` | non-empty byte string | Proof-specific nonce |
| `critical` | array of extension identifiers | Extensions that MUST be understood |

A proof MAY contain extension properties as defined in Section 13.

### 6.1 Unknown compact properties

For `version = 1`, an unknown property whose name is not an absolute URI is non-conforming.

Future OLP versions MAY define additional compact core properties.

### 6.2 Duplicate properties

A serialized proof containing duplicate property names MUST be rejected as non-conforming.

An implementation MUST NOT resolve duplicate properties using "first wins", "last wins", merge behavior, or parser-specific behavior.

### 6.3 Abstract value types

Values authenticated by Proof Input v1 are restricted to:

- signed integers in the range `[-2^63, 2^63 - 1]`;
- byte strings;
- Unicode text strings containing valid Unicode scalar values;
- arrays;
- maps;
- `true`;
- `false`; and
- `null`.

Floating-point values, NaN, infinities, CBOR `undefined`, arbitrary CBOR tags, and indefinite-length items are not valid Proof Input v1 values.

For extension-defined nested maps, map keys MUST be text strings and MUST be unique.

Text strings MUST be encoded as UTF-8 for Proof Input. Implementations MUST NOT apply Unicode normalization unless a field specification explicitly requires it.

---

## 7. Core Property Semantics

### 7.1 `type`

`type` MUST equal:

```text
OLPProof
```

`type` is the transport/data-model discriminator.

The cryptographic Proof Input uses the fixed domain separator `OLP-PROOF`, so changing `type` does not create a second cryptographic domain.

### 7.2 `version`

`version` MUST equal integer `1` for this specification.

A verifier receiving a syntactically valid proof with another version MUST report the version as unsupported unless it implements that version.

Unsupported version is not cryptographic invalidity.

### 7.3 `cryptosuite`

`cryptosuite` identifies the complete cryptographic procedure.

Core OLP cryptosuites use compact identifiers reserved by OLP.

Third-party cryptosuites MUST use globally unambiguous absolute URI identifiers.

OLP v1 reserves:

```text
eddsa-ed25519-v1
```

for the mandatory suite defined in Section 12.

A verifier MUST NOT infer a cryptosuite from:

- key shape;
- key length;
- `proofValue` length;
- verification-method scheme; or
- any unauthenticated metadata.

### 7.4 `proofPurpose`

`proofPurpose` MUST contain exactly one purpose identifier.

OLP v1 defines four compact core purposes:

```text
assertion
acknowledgement
witness
authorization
```

Non-core purposes MUST use globally unambiguous absolute URI identifiers.

Purpose semantics are defined in Section 10.

### 7.5 `verificationMethod`

`verificationMethod` MUST be an absolute URI under RFC 3986.

The exact URI string is authenticated.

Implementations reconstructing Proof Input MUST NOT silently:

- change URI case;
- normalize paths;
- add or remove fragments;
- decode and re-encode percent escapes;
- substitute a redirect target;
- replace the identifier with a resolver-preferred alias; or
- otherwise rewrite the authenticated URI.

A resolver MAY apply scheme-specific resolution semantics internally, but the cryptographic Proof Input contains the exact URI authenticated by the proof producer.

### 7.6 `recordCommitment`

`recordCommitment` identifies the exact record bytes protected by the proof.

Its abstract form is:

```text
RecordCommitment {
    algorithm: integer,
    digest: byte string
}
```

Its Proof Input representation is defined in Section 9.

### 7.7 `proofValue`

`proofValue` is an abstract byte string.

Text encodings such as Base64, Base64url, hexadecimal, or multibase are transport concerns and are not proof semantics.

For `eddsa-ed25519-v1`, `proofValue` MUST contain exactly 64 bytes.

### 7.8 `created`

If present, `created` MUST be a syntactically valid RFC 3339 date-time string with an explicit UTC offset.

It means only:

> The proof producer asserted this creation time.

A valid proof containing `created` does not independently establish that the proof existed at that time.

The exact text is authenticated. Implementations MUST NOT normalize the text before reconstructing Proof Input.

### 7.9 `expires`

If present, `expires` MUST be a syntactically valid RFC 3339 date-time string with an explicit UTC offset.

It means:

> The proof producer declares that the proof is not intended to be relied upon after this time.

Expiration changes temporal applicability, not mathematical signature validity.

### 7.10 `domain`

If present, `domain` MUST be a non-empty text string.

Applications MAY require an expected domain.

A cryptographically valid proof whose authenticated domain does not match a required domain MUST report a domain mismatch rather than cryptographic invalidity.

### 7.11 `challenge`

If present, `challenge` MUST be a non-empty byte string.

Applications MAY require an expected challenge.

Challenge mismatch is distinct from cryptographic invalidity.

### 7.12 `nonce`

If present, `nonce` MUST be a non-empty byte string.

A nonce does not automatically provide replay protection. Replay semantics are application- and protocol-context dependent.

### 7.13 `critical`

If present, `critical` is an unordered set represented by an array of absolute URI extension identifiers.

Each identifier:

- MUST be unique;
- MUST name an extension property actually present in the proof; and
- MUST NOT name a core OLP property.

`critical` itself is authenticated.

Before Proof Input encoding, its members MUST be sorted in ascending bytewise lexicographic order of their UTF-8 encodings.

---

## 8. Record Identity and Record Commitments

### 8.1 Canonical commitment input

For records conforming to `specification/0003-record-representation.md`, a proof commitment MUST be computed over the exact OLP-CIE-1 bytes of the OLP-CI-1 identity preimage defined by that specification.

This specification MUST NOT introduce a second record canonicalization algorithm.

Conceptually:

```text
Record
  |
  v
OLP-CI-1 identity preimage
  |
  v
OLP-CIE-1 canonical bytes
  |
  +--> SHA-256 --> Record Identity digest
  |
  +--> selected proof hash --> recordCommitment digest
```

### 8.2 Record Identity is stable

Using a different proof commitment algorithm does not create a new OLP Record Identity.

For example, SHA-256 and SHA-512 commitments MAY both refer to the same record while the record retains one stable identity under the record specification.

### 8.3 Commitment format

The abstract `RecordCommitment` is encoded inside Proof Input v1 as:

```text
[
    hashAlgorithmId,
    digestBytes
]
```

where:

- `hashAlgorithmId` is an integer identifier from the IANA COSE Algorithms registry that identifies a hash algorithm suitable for direct hashing; and
- `digestBytes` is the raw digest output.

The algorithm identifier is itself authenticated because the complete commitment is part of Proof Input.

### 8.4 Mandatory commitment algorithm

Every conforming OLP v1 proof producer and verifier MUST support SHA-256 as identified by COSE algorithm identifier `-16`.

Additional suitable registered hash algorithms MAY be supported.

An implementation MUST NOT infer the hash algorithm from digest length.

### 8.5 Supported is not acceptable

An implementation MAY understand a commitment algorithm while local security policy rejects its use.

Such rejection MUST be represented separately from proof syntax and mathematical signature validity.

If the commitment algorithm is technically supported and all mathematical verification inputs are otherwise available, a local policy rejection MUST NOT by itself prevent recomputing the record commitment or verifying the signature. In that case, an implementation MAY report simultaneously, for example:

```text
commitmentAlgorithmSupport = REJECTED_BY_POLICY
recordBinding = VALID
cryptographicValidity = VALID
```

The application remains free to reject reliance because the policy dimension is not acceptable.

---

## 9. OLP Proof Input v1

### 9.1 Abstract structure

The exact Proof Input v1 structure is the following nine-element array:

```text
ProofInputV1 = [
    "OLP-PROOF",          ; index 0: fixed domain separator
    1,                    ; index 1: proof-input version
    cryptosuite,          ; index 2
    proofPurpose,         ; index 3
    verificationMethod,   ; index 4
    recordCommitment,     ; index 5
    metadata,             ; index 6
    extensions,           ; index 7
    critical              ; index 8
]
```

The array MUST contain exactly nine elements.

`proofValue` MUST NOT appear in Proof Input.

The transport-level `type` is represented cryptographically by the fixed `OLP-PROOF` domain separator rather than by a variable field.

### 9.2 Metadata map

`metadata` is always present in Proof Input.

If no standardized optional metadata is present, it MUST be the empty map.

The following integer labels are defined:

| Label | Proof property | Proof Input value |
|---:|---|---|
| `0` | `created` | exact RFC 3339 text string |
| `1` | `expires` | exact RFC 3339 text string |
| `2` | `domain` | text string |
| `3` | `challenge` | byte string |
| `4` | `nonce` | byte string |

No other metadata labels are valid in Proof Input v1.

A core extension to this map requires a future Proof Input version.

### 9.3 Extension map

`extensions` is always present in Proof Input.

If no extensions are present, it MUST be the empty map.

For each extension property in the `OLPProof` object:

```text
extensions[extensionPropertyName] = extensionPropertyValue
```

The map key MUST be the exact absolute URI property name authenticated by the proof.

All extension properties are authenticated, whether critical or non-critical.

### 9.4 Critical array

`critical` is always present in Proof Input.

If the proof has no critical extensions, it MUST be the empty array.

Its members MUST be sorted as specified in Section 7.13 before encoding.

### 9.5 No hidden associated data

The Proof Input defined here is complete.

An ordinary OLP proof MUST NOT depend on hidden external authenticated data, invisible application bytes, or implicit transport state that is not represented in Proof Input.

A specialized application requiring additional security context MUST represent or commit to that context through an authenticated core field or defined extension.

---

## 10. Proof Purposes

Proof purpose expresses the proof producer's authenticated intent toward the referenced record.

Purposes are semantically distinct and are not ordered by strength.

A conforming implementation MUST NOT automatically substitute, rank, convert, or infer one core purpose from another.

### 10.1 `assertion`

Meaning:

> The proof producer intentionally expresses the referenced record as a statement attributable to the verification method used to create the proof.

An assertion proof does not establish that the record is true or accurate.

### 10.2 `acknowledgement`

Meaning:

> The proof producer intentionally acknowledges receipt of or awareness of the referenced record.

An acknowledgement proof does not, by itself, express:

- agreement;
- acceptance;
- approval;
- consent; or
- belief in the record.

### 10.3 `witness`

Meaning:

> The proof producer intentionally represents that it observed the event, state, interaction, or evidence described by the referenced record.

A witness proof does not establish:

- objective truth;
- impartiality;
- competence;
- physical presence; or
- legally recognized witness status.

### 10.4 `authorization`

Meaning:

> The proof producer intentionally expresses permission, approval, or consent for an action, transition, or consequence represented by the referenced record.

An authorization proof expresses authorization intent.

It does not establish that the proof producer possessed sufficient legal, organizational, contractual, technical, or other authority.

### 10.5 Expected purpose

An application MAY supply an expected purpose.

A cryptographically valid proof with a different authenticated purpose MUST report `PURPOSE_MISMATCH`.

It MUST NOT be treated as satisfying the expected purpose merely because the signature is valid.

### 10.6 Extension purposes

Non-core proof purposes MUST use absolute URI identifiers and MUST have externally defined semantics sufficient for independent implementations to interpret them consistently.

An unsupported purpose does not make the signature cryptographically invalid.

---

## 11. Verification Method Resolution

### 11.1 Resolution boundary

Verification-method resolution is logically separate from cryptographic proof verification.

OLP does not mandate:

- one verification-method scheme;
- one resolver;
- one DID system;
- one certificate infrastructure;
- one blockchain;
- one DNS namespace;
- one registry; or
- one trust root.

### 11.2 Offline verification

A conforming verifier MUST be able to accept already-resolved verification material without performing network access.

The cryptographic verification core MUST NOT require the Internet.

### 11.3 No implicit network dereference

A generic OLP verifier MUST NOT automatically dereference arbitrary network resources solely because an untrusted proof contains a network-capable `verificationMethod` URI.

Applications MAY explicitly enable resolver implementations.

Network resolvers SHOULD enforce security policy including, as applicable:

- allowed URI schemes;
- allowed hosts;
- private-network restrictions;
- redirect limits;
- response-size limits;
- timeouts;
- TLS requirements;
- authentication requirements;
- content-type constraints; and
- cache policy.

### 11.4 Resolved method abstraction

A resolved verification method MUST provide, at minimum:

```text
ResolvedVerificationMethod {
    id
    keyType
    publicKeyMaterial
}
```

It MAY additionally provide:

- resolver provenance;
- controller information;
- method metadata;
- historical version information; or
- status evidence.

The `id` supplied to cryptographic verification MUST correspond to the exact authenticated `verificationMethod` reference.

### 11.5 Compatibility

The declared cryptosuite determines the required key type and key-processing rules.

A resolver MUST NOT select or infer the cryptosuite.

An incompatible resolved method MUST report `VERIFICATION_METHOD_INCOMPATIBLE`.

### 11.6 Resolution failure is not invalidity

Failure to resolve a method MUST NOT be reported as `SIGNATURE_INVALID`.

The verifier MUST distinguish at least:

- unsupported method scheme/type;
- unavailable method;
- method mismatch;
- incompatible method; and
- invalid signature after successful resolution and compatibility checks.

### 11.7 Historical resolution

Current resolver state is not necessarily historical verification state.

Verification-method references SHOULD identify immutable, version-specific, self-certifying, or historically recoverable material where practical.

Deletion or current unavailability does not imply revocation.

---

## 12. Mandatory OLP v1 Cryptosuite

### 12.1 Identifier

The mandatory-to-implement OLP v1 cryptosuite identifier is:

```text
eddsa-ed25519-v1
```

### 12.2 Algorithm

The suite uses Pure Ed25519 as specified by RFC 8032.

### 12.3 Message

The Ed25519 message is exactly the deterministic CBOR encoding of `ProofInputV1`.

The suite MUST NOT apply:

- additional OLP-level prehashing;
- additional application-level canonicalization;
- transport serialization; or
- suite-specific rewriting of Proof Input.

The internal hashing defined by Ed25519 itself is part of Ed25519 and is unaffected by this rule.

### 12.4 Public key

Resolved public verification material MUST identify an Ed25519 public key containing exactly 32 octets.

X25519 keys MUST NOT be coerced, converted, or interpreted as Ed25519 signing keys by this suite.

### 12.5 Signature

`proofValue` MUST contain the native Ed25519 signature of exactly 64 octets.

### 12.6 Verification

The verifier MUST:

1. confirm that the resolved method is compatible with Ed25519;
2. confirm that the public key is exactly 32 octets;
3. confirm that `proofValue` is exactly 64 octets;
4. reconstruct the exact Proof Input bytes; and
5. perform Ed25519 verification according to RFC 8032.

Failure of step 5 after valid prerequisites yields `SIGNATURE_INVALID`.

### 12.7 Additional suites

Implementations MAY support additional cryptosuites.

An additional suite:

- MUST NOT redefine Proof Input v1 semantics;
- MUST NOT redefine deterministic CBOR encoding;
- MUST use its own unambiguous cryptosuite identifier; and
- MUST define all key, proof-value, and verification requirements needed for interoperability.

---

## 13. Extension Model

OLP v1 uses authenticated extensions with explicit criticality.

### 13.1 Extension names

An extension property name MUST be an absolute URI.

Extension names MUST NOT redefine or alias core OLP property names.

### 13.2 Authentication

Every extension property inside `OLPProof` is authenticated.

Unsigned application annotations MUST live outside the proof object.

### 13.3 Non-critical unknown extensions

A verifier MAY cryptographically verify a proof containing an unknown non-critical extension because the extension's raw OLP value can still be included in Proof Input.

The verifier MUST report the extension as not interpreted.

It MUST NOT claim to understand its semantics.

### 13.4 Critical extensions

If an extension's semantics are required for safe interpretation, the proof producer MUST include its identifier in `critical`.

A verifier that does not understand and process a critical extension MUST report:

```text
UNSUPPORTED_CRITICAL_EXTENSION
```

It MUST NOT report the proof as completely processed under its declared semantics.

It MUST NOT silently ignore the extension.

### 13.5 Criticality integrity

`critical` is itself authenticated.

Removing, adding, or changing a critical-extension declaration therefore changes Proof Input and invalidates the original `proofValue`.

### 13.6 Invalid critical declarations

A proof is non-conforming if:

- `critical` contains duplicates;
- `critical` names a core property;
- `critical` names an extension property not present in the proof; or
- a critical identifier is not an absolute URI.

---

## 14. Multiple Proofs

### 14.1 Independent proofs

Multiple proofs MAY concern the same record.

Unless a future explicit dependency mechanism states otherwise, each proof MUST be independently verifiable against:

- the referenced record;
- its own authenticated Proof Input; and
- its own resolved verification method.

### 14.2 Proof sets are unordered

Serialization order, array position, storage order, insertion order, display order, and receipt order MUST NOT imply:

- chronology;
- precedence;
- dependency;
- endorsement;
- authority; or
- countersignature.

A proof set is a collection, not a chain.

### 14.3 Sibling independence

Adding, removing, reordering, or transporting one independent proof MUST NOT alter the cryptographic validity or authenticated meaning of another independent proof.

### 14.4 No implicit countersigning

A proof over a record does not implicitly authenticate, approve, acknowledge, witness, authorize, validate, or countersign any sibling proof.

Proof dependencies MUST be explicit and cryptographically authenticated by a future mechanism.

### 14.5 Proof count has no protocol weight

OLP MUST NOT assign protocol-defined truth, confidence, trust, authority, or evidentiary weight based on the number of proofs associated with a record.

Repeated packaging of an identical proof does not create additional protocol-level evidence.

### 14.6 Mixed algorithms and methods

Independent proofs concerning one record MAY use:

- different commitment algorithms;
- different cryptosuites;
- different proof purposes; and
- different verification-method ecosystems.

---

## 15. Time and Temporal Evidence

### 15.1 Signer-declared time

`created` and `expires` are authenticated statements made by the proof producer.

They are not independent trusted-time evidence.

### 15.2 Independent time evidence

Claims such as:

> Proof P existed no later than time T.

require additional evidence external to the ordinary proof, such as:

- a trusted timestamp token;
- transparency-log evidence;
- blockchain anchoring evidence;
- independent witness evidence; or
- another defined temporal-evidence mechanism.

OLP does not mandate or privilege one temporal-evidence provider.

### 15.3 Backdating

A verifier MUST NOT infer that a proof predates key compromise, revocation, expiry, retirement, or other status change solely because its authenticated `created` value is earlier.

Such an inference requires appropriate independent temporal and status evidence or an explicit application assumption.

### 15.4 Expiration

If `expires` is present and the applicable evaluation time is later than the declared expiration time:

```text
cryptographicValidity = VALID
temporalStatus = EXPIRED
```

is a valid result combination.

Expiration MUST NOT be converted into `SIGNATURE_INVALID`.

---

## 16. Verification-Method Status and Historical Validity

### 16.1 Separate dimensions

Cryptographic validity and verification-method status are independent dimensions.

For example:

```text
cryptographicValidity = VALID
verificationMethodStatus = REVOKED
```

is representable and meaningful.

### 16.2 Status categories

Where status evidence is available, implementations SHOULD preserve distinctions such as:

```text
ACTIVE
RETIRED
EXPIRED
SUSPENDED
REVOKED
COMPROMISED
UNKNOWN
NOT_EVALUATED
```

Not every verification-method ecosystem is required to support every category.

### 16.3 Status provenance

Status information is evidence.

A verifier SHOULD expose:

- source;
- applicable verification method;
- effective time when available;
- retrieval or evidence provenance; and
- status semantics when not self-evident.

OLP does not define a universal revocation authority.

### 16.4 No retroactive signature rewriting

Revocation, suspension, retirement, expiry, compromise evidence, or later method unavailability MUST NOT retroactively change whether an already-created signature mathematically verifies.

Applications MAY reject reliance based on status policy.

### 16.5 Key rotation

Ordinary key rotation does not imply historical compromise.

A retired key and a compromised key MUST NOT be treated as synonymous unless the relevant status system explicitly defines that meaning.

### 16.6 Cryptosuite lifecycle

The same separation applies to cryptosuite lifecycle.

A historical proof may remain:

```text
cryptographicValidity = VALID
cryptosuiteSecurityStatus = DEPRECATED
```

A suite being deprecated for new proof creation does not make historical signatures mathematically invalid.

The same rule applies when local policy rejects a cryptosuite that the implementation can still technically verify. If all verification inputs are available, policy rejection MUST remain distinct from mathematical signature validity. A verifier MAY therefore report both:

```text
cryptosuiteSupport = REJECTED_BY_POLICY
cryptographicValidity = VALID
```

This does not make the proof acceptable under that policy.

---

## 17. Deterministic CBOR Encoding

### 17.1 Required encoding

`ProofInputV1` MUST be encoded using the Core Deterministic Encoding Requirements of RFC 8949, further restricted by this specification.

### 17.2 Additional OLP v1 restrictions

Proof Input v1:

- MUST use definite-length arrays, maps, byte strings, and text strings;
- MUST use preferred serialization for integers and lengths;
- MUST sort map keys in bytewise lexicographic order of their deterministic CBOR encodings;
- MUST NOT contain floating-point values;
- MUST NOT contain NaN or infinities;
- MUST NOT contain CBOR `undefined`;
- MUST NOT contain arbitrary CBOR tags;
- MUST NOT use indefinite-length encoding; and
- MUST NOT contain duplicate map keys.

### 17.3 Semantic map ordering

Map insertion order has no semantic meaning.

Every conforming implementation starting from the same valid abstract Proof Input MUST emit byte-for-byte identical Proof Input bytes.

### 17.4 Array ordering

Array order is semantically significant except where this specification explicitly defines a set-like field.

For `critical`, implementations MUST sort members according to Section 7.13 before CBOR encoding.

### 17.5 No normalization

A verifier MUST reconstruct Proof Input from exact authenticated abstract values.

It MUST NOT invent normalization rules for:

- text;
- URIs;
- timestamps;
- extension identifiers; or
- application context.

---

## 18. Proof Creation Algorithm

A conforming OLP v1 proof producer MUST perform the following steps.

### 18.1 Inputs

Inputs are:

- a valid OLP record;
- a proof purpose;
- a verification-method URI;
- a supported cryptosuite;
- signing key/proving material;
- a supported record-commitment algorithm;
- optional standardized metadata;
- optional extensions; and
- optional critical-extension declarations.

### 18.2 Procedure

1. Validate the record according to the applicable OLP record specification.
2. Validate all mandatory proof properties.
3. Validate all optional standardized metadata.
4. Validate all extension names and values.
5. Validate `critical`:
   - all identifiers are unique absolute URIs;
   - every identifier names a present extension;
   - no identifier names a core property.
6. Construct the exact canonical record identity bytes using the record specification.
7. Hash those bytes using the selected supported commitment algorithm.
8. Construct `recordCommitment = [algorithmId, digestBytes]`.
9. Construct the metadata map using the labels in Section 9.2.
10. Construct the extension map using exact extension names and values.
11. Sort `critical` according to Section 7.13.
12. Construct the exact nine-element `ProofInputV1`.
13. Encode `ProofInputV1` using Section 17.
14. Confirm that the signing key is compatible with the selected cryptosuite.
15. Apply the selected cryptosuite to the exact Proof Input bytes.
16. Store the resulting cryptographic proof bytes as `proofValue`.
17. Construct and return the immutable `OLPProof` object.

### 18.3 No mutation after creation

Changing any authenticated property after step 15 requires generating a new proof.

There is no protocol-level operation for editing an existing proof while preserving its `proofValue`.

---

## 19. Proof Verification Algorithm

A conforming verifier MUST preserve stage distinctions rather than reducing every condition to one boolean.

### 19.1 Inputs

Verification may receive:

- record;
- proof;
- resolved verification method;
- optional expected purpose;
- optional expected domain;
- optional expected challenge;
- optional evaluation time;
- optional verification-method status evidence;
- optional independent time evidence; and
- local security policy.

Resolution MAY occur before invocation or through an explicitly configured resolver layer.

### 19.2 Procedure

1. **Parse and structural validation**
   - Reject duplicate properties.
   - Validate `type`, `version`, core field types, extension names, and `critical`.
   - If structurally non-conforming, later cryptographic stages that depend on the malformed structure are `NOT_EVALUATED`.

2. **Version support**
   - If the proof version is not supported, report `UNSUPPORTED_VERSION`.

3. **Cryptosuite support**
   - If the cryptosuite is not supported, report `UNSUPPORTED_CRYPTOSUITE`.

4. **Extension processing**
   - Preserve and authenticate unknown non-critical extensions.
   - If any critical extension is unsupported, report `UNSUPPORTED_CRITICAL_EXTENSION`.

5. **Record commitment**
   - Construct the canonical record identity bytes using the applicable record specification.
   - If the commitment algorithm is unsupported, report `UNSUPPORTED_COMMITMENT_ALGORITHM`.
   - Compute the digest.
   - Compare algorithm and digest to the authenticated `recordCommitment`.
   - On mismatch, report `RECORD_COMMITMENT_MISMATCH`.
   - Signature verification need not proceed after definitive record-binding failure.

6. **Verification-method resolution state**
   - If required verification material is not supplied or resolved, report the appropriate unavailable/unsupported state.
   - Do not convert resolution failure into signature invalidity.

7. **Verification-method identity and compatibility**
   - Confirm that resolved material corresponds to the exact authenticated `verificationMethod`.
   - Confirm that key type and parameters are compatible with the cryptosuite.
   - On incompatibility, report `VERIFICATION_METHOD_INCOMPATIBLE`.

8. **Proof Input reconstruction**
   - Reconstruct metadata, extensions, sorted `critical`, and the exact nine-element `ProofInputV1`.
   - Encode using deterministic CBOR.

9. **Cryptographic verification**
   - Apply the declared cryptosuite.
   - If verification succeeds, set `cryptographicValidity = VALID`.
   - If verification is actually performed and the proof fails, set `cryptographicValidity = INVALID` and report `SIGNATURE_INVALID`.

10. **Expected-purpose evaluation**
    - If an expected purpose is supplied, compare it to the authenticated purpose.
    - Mismatch yields `PURPOSE_MISMATCH` without changing `cryptographicValidity`.

11. **Expected-domain evaluation**
    - If an expected domain is supplied, compare it to authenticated `domain`.
    - Missing required domain or mismatch yields a domain-specific result.

12. **Expected-challenge evaluation**
    - If an expected challenge is supplied, compare it byte-for-byte to authenticated `challenge`.
    - Missing required challenge or mismatch yields a challenge-specific result.

13. **Temporal evaluation**
    - If an evaluation time is supplied and `expires` is present, evaluate expiration.
    - Do not treat `created` as independent evidence of historical existence.

14. **Verification-method status evaluation**
    - If status evidence is supplied, expose the resulting status separately.
    - Do not alter mathematical signature validity.

15. **Return structured result**
    - Return all evaluated dimensions, warnings, errors, and relevant provenance.

---

## 20. Structured Verification Results

### 20.1 No overloaded boolean

A conforming verifier MUST expose enough structured information to distinguish materially different verification states.

A single boolean MAY be provided as a convenience API only if the structured result remains available and the boolean's derivation is explicitly documented.

### 20.2 Required dimensions

Where applicable, a verification result SHOULD expose at least:

```text
conformance
recordBinding
versionSupport
cryptosuiteSupport
commitmentAlgorithmSupport
criticalExtensionStatus
verificationMethodResolution
verificationMethodCompatibility
cryptographicValidity
purposeStatus
domainStatus
challengeStatus
temporalStatus
verificationMethodStatus
warnings
errors
```

### 20.3 `NOT_EVALUATED`

A condition that was not checked MUST NOT be represented as successful.

Dimensions MUST be capable of representing `NOT_EVALUATED` where evaluation may be skipped or impossible.

### 20.4 Distinct failure classes

Implementations MUST preserve the distinction between:

- **NONCONFORMING** — the object violates this specification;
- **UNSUPPORTED** — the object may be valid OLP but the implementation does not support a required feature;
- **UNAVAILABLE** — a required external input cannot currently be obtained;
- **INVALID** — an operation was performed and produced a definitive negative cryptographic or binding result; and
- **MISMATCH** — a valid authenticated value does not satisfy caller-supplied context.

### 20.5 Warnings

Warnings MUST be non-fatal informational conditions.

A warning MUST NOT silently change a stated verification dimension.

Examples include:

- deprecated cryptosuite;
- deprecated commitment algorithm;
- status evidence unavailable when status was optional;
- unknown non-critical extension not interpreted.

### 20.6 Resolution provenance

Where a verification method was resolved, the result SHOULD expose whether material was:

- supplied directly;
- obtained from a local store;
- obtained from a resolver; or
- recovered from historical evidence,

without treating the source label itself as a trust judgment.

---

## 21. Core Reason Codes

The following machine-readable reason codes are defined for v1.

### 21.1 Structural and version errors

```text
MALFORMED_PROOF
DUPLICATE_PROPERTY
INVALID_CORE_PROPERTY
INVALID_EXTENSION_NAME
INVALID_EXTENSION_VALUE
INVALID_CRITICAL_DECLARATION
UNSUPPORTED_VERSION
```

### 21.2 Cryptosuite and commitment errors

```text
UNSUPPORTED_CRYPTOSUITE
CRYPTOSUITE_REJECTED_BY_POLICY
UNSUPPORTED_COMMITMENT_ALGORITHM
COMMITMENT_ALGORITHM_REJECTED_BY_POLICY
RECORD_COMMITMENT_MISMATCH
```

### 21.3 Extension errors

```text
UNSUPPORTED_CRITICAL_EXTENSION
UNKNOWN_NONCRITICAL_EXTENSION
```

`UNKNOWN_NONCRITICAL_EXTENSION` SHOULD normally be a warning, not a fatal error.

### 21.4 Verification-method errors

```text
UNSUPPORTED_VERIFICATION_METHOD
VERIFICATION_METHOD_UNAVAILABLE
VERIFICATION_METHOD_MISMATCH
VERIFICATION_METHOD_INCOMPATIBLE
VERIFICATION_METHOD_MALFORMED
```

### 21.5 Cryptographic errors

```text
INVALID_PROOF_VALUE_LENGTH
INVALID_PUBLIC_KEY_LENGTH
SIGNATURE_INVALID
```

### 21.6 Context errors

```text
UNSUPPORTED_PROOF_PURPOSE
PURPOSE_MISMATCH
DOMAIN_REQUIRED
DOMAIN_MISMATCH
CHALLENGE_REQUIRED
CHALLENGE_MISMATCH
```

### 21.7 Temporal and status results

```text
PROOF_EXPIRED
VERIFICATION_METHOD_RETIRED
VERIFICATION_METHOD_EXPIRED
VERIFICATION_METHOD_SUSPENDED
VERIFICATION_METHOD_REVOKED
VERIFICATION_METHOD_COMPROMISED
VERIFICATION_METHOD_STATUS_UNKNOWN
```

These status codes MUST NOT be treated as synonyms for `SIGNATURE_INVALID`.

---

## 22. Proof Immutability

A completed proof is an immutable evidence artifact.

Changing any authenticated component, including:

- version;
- cryptosuite;
- proof purpose;
- verification method;
- record commitment;
- standardized metadata;
- extension property;
- critical declaration; or
- extension value,

changes Proof Input.

The original `proofValue` therefore no longer verifies.

Application packaging MAY add external annotations that are not part of the proof object.

Such annotations MUST NOT be presented as cryptographically authenticated by the proof.

---

## 23. Proof IDs, Countersignatures, and Evidence Graphs

This specification intentionally does not define:

```text
proofId
previousProof
proofChain
countersignature
```

Ordinary v1 semantics are:

```text
Proof -> Record
```

A future specification may define explicit cryptographically authenticated relationships such as:

```text
Proof -> Proof
Evidence -> Proof
Evidence -> Evidence
```

Such mechanisms SHOULD be designed as an evidence graph rather than inferred from proof-array order.

Packaging two proofs together MUST NOT be interpreted as creating a dependency between them.

---

## 24. Conformance

### 24.1 OLP v1 proof producer

A conforming OLP v1 proof producer MUST:

- implement the `OLPProof` model defined here;
- construct exact `ProofInputV1`;
- implement deterministic CBOR as restricted here;
- support SHA-256 record commitments using COSE algorithm identifier `-16`;
- support `eddsa-ed25519-v1`;
- enforce extension and critical-extension rules;
- reject malformed proof inputs before signing; and
- emit `proofValue` as raw suite-defined bytes.

### 24.2 OLP v1 proof verifier

A conforming OLP v1 proof verifier MUST:

- parse and validate the `OLPProof` model;
- reconstruct exact `ProofInputV1`;
- implement deterministic CBOR as restricted here;
- support SHA-256 record commitments using COSE algorithm identifier `-16`;
- support `eddsa-ed25519-v1`;
- accept externally supplied resolved verification material;
- distinguish resolution failure from cryptographic invalidity;
- enforce critical-extension semantics;
- expose structured verification results; and
- distinguish `NOT_EVALUATED` from success.

### 24.3 Resolver capability

Network resolution is not required for OLP verifier conformance.

A verifier MAY be fully offline.

### 24.4 Additional algorithms

Supporting additional commitment algorithms or cryptosuites does not reduce the requirement to support the mandatory OLP v1 baseline.

---

## 25. Security Considerations

### 25.1 Record substitution

Verification MUST recompute the record commitment from the exact canonical record identity bytes.

Accepting only an external record identifier without verifying its cryptographic commitment can permit record substitution.

### 25.2 Cross-protocol signature confusion

The fixed `OLP-PROOF` domain separator and versioned Proof Input structure are mandatory.

Implementations MUST NOT sign naked record bytes or a naked record digest as an ordinary OLP v1 proof.

### 25.3 Algorithm confusion

The commitment algorithm and cryptosuite are explicit authenticated values.

Implementations MUST NOT infer them from key or proof length.

### 25.4 Key-type confusion

The mandatory Ed25519 suite MUST reject incompatible key types.

X25519 and Ed25519 material MUST NOT be interchanged merely because they use related curve families.

### 25.5 Extension downgrade

Criticality is authenticated.

A verifier MUST NOT ignore an unsupported critical extension.

### 25.6 Parser differentials

Duplicate properties and duplicate map keys are forbidden.

Proof Input uses a deliberately restricted data model and deterministic CBOR to reduce divergent-parser behavior.

### 25.7 URI rewriting

The exact `verificationMethod` URI is authenticated.

Silent URI normalization can make two implementations reconstruct different Proof Input bytes or resolve different resources.

### 25.8 SSRF and resolver abuse

Network-capable verification-method references are untrusted input.

Generic cryptographic verification MUST NOT automatically dereference them.

### 25.9 Backdating

`created` is signer-controlled authenticated metadata.

It MUST NOT be treated as independent evidence that a proof existed before compromise or revocation.

### 25.10 Replay

A valid proof may be replayed.

Applications requiring replay resistance SHOULD use authenticated `challenge`, `domain`, `nonce`, application state, or a defined extension appropriate to the interaction.

A nonce by itself does not establish replay prevention unless the application checks uniqueness or context.

### 25.11 Secret-key protection

Security of proof creation depends on protection of private signing keys.

This specification does not define private-key storage.

Implementations SHOULD use secure operating-system, hardware, HSM, or equivalent key-protection mechanisms appropriate to their threat model.

### 25.12 Key generation

Ed25519 private keys MUST be generated using a cryptographically secure process conforming to the requirements of the Ed25519 implementation and applicable cryptographic guidance.

Test-vector private keys MUST NOT be reused in production.

### 25.13 Cryptosuite deprecation

Historical cryptographic validity and current security recommendation are separate.

Applications handling long-lived evidence SHOULD preserve independent temporal evidence and cryptographic provenance to support future algorithm migration.

### 25.14 Hash migration

Record commitments are algorithm-agile.

Applications preserving evidence for long periods MAY add new independent proofs using newer commitment algorithms without changing the record or historical proofs.

### 25.15 Proof-count attacks

Applications MUST NOT assume that large numbers of proofs imply independent actors or stronger truth.

Sybil resistance and actor-independence evaluation are outside this cryptographic layer.

### 25.16 Denial of service

Before expensive cryptographic operations, implementations SHOULD perform inexpensive bounded checks such as:

- structure validation;
- version support;
- length limits;
- record-commitment validation; and
- resolver policy checks.

Implementations SHOULD impose resource limits on proof size, extension depth, array size, map size, and resolver activity.

### 25.17 No truth oracle

A valid signature proves a cryptographic binding, not the truth of the record.

Applications MUST NOT present OLP cryptographic verification as an OLP-issued trust or truth judgment.

---

## 26. Interoperability Test Vector 1 — Minimal Ed25519 Proof Input

This vector tests deterministic Proof Input construction and the mandatory Ed25519 cryptosuite independently of record canonicalization.

### 26.1 Inputs

Cryptosuite:

```text
eddsa-ed25519-v1
```

Proof purpose:

```text
assertion
```

Verification method:

```text
urn:example:olp:test-key-1
```

Record commitment algorithm:

```text
-16
```

Record commitment digest:

```text
bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7
```

Metadata:

```text
{}
```

Extensions:

```text
{}
```

Critical:

```text
[]
```

### 26.2 Abstract Proof Input

```text
[
  "OLP-PROOF",
  1,
  "eddsa-ed25519-v1",
  "assertion",
  "urn:example:olp:test-key-1",
  [
    -16,
    h'bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7'
  ],
  {},
  {},
  []
]
```

### 26.3 Deterministic CBOR

Hexadecimal encoding of the exact Proof Input bytes:

```text
89694f4c502d50524f4f46017065646473612d656432353531392d763169617373657274696f6e781a75726e3a6578616d706c653a6f6c703a746573742d6b65792d31822f5820bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7a0a080
```

Length:

```text
106 octets
```

### 26.4 Ed25519 test key

Private seed:

```text
9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60
```

Public key:

```text
d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a
```

The private seed above is for conformance testing only and MUST NOT be used outside test fixtures.

### 26.5 Expected `proofValue`

```text
ea39ac65bdad595f3f79ea315b03545d034dced37c3ed26c5056a3978c6b3f2ee76caac70b914068bf06843ed689dcb41540b344143a23e97dc0d8c74782090d
```

Length:

```text
64 octets
```

A conforming implementation using the inputs above MUST reconstruct the same 106 Proof Input octets and MUST verify the expected 64-octet Ed25519 signature against the listed public key.

---

## 27. Design Summary

OLP v1 proof architecture is:

```text
OLP Record
    |
    v
OLP-CI-1 identity preimage
    |
    v
OLP-CIE-1 canonical bytes
    |
    v
Record commitment
    |
    +------------------------------+
    | cryptosuite                  |
    | proof purpose                |
    | verification method          |
    | authenticated metadata       |
    | authenticated extensions     |
    | critical-extension set       |
    +------------------------------+
                    |
                    v
             ProofInputV1
                    |
                    v
         deterministic CBOR
                    |
                    v
          exact Proof Input bytes
                    |
                    v
          cryptographic suite
                    |
                    v
               proofValue
```

Verification preserves the distinction between:

```text
cryptographic validity
record binding
method resolution
method status
purpose/context matching
temporal evaluation
security policy
trust interpretation
```

OLP verifies evidence.

OLP does not issue universal trust judgments.

---

## 28. References

### Normative

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels.
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
- RFC 3339 — Date and Time on the Internet: Timestamps.
- RFC 3986 — Uniform Resource Identifier (URI): Generic Syntax.
- RFC 8032 — Edwards-Curve Digital Signature Algorithm (EdDSA).
- RFC 8949 — Concise Binary Object Representation (CBOR).
- RFC 9054 — CBOR Object Signing and Encryption (COSE): Hash Algorithms.
- IANA — CBOR Object Signing and Encryption (COSE) Algorithms Registry.
- OLP Specification 0003 — Record Representation.

### Informative

- RFC 9052 — CBOR Object Signing and Encryption (COSE): Structures and Process.
- RFC 9053 — CBOR Object Signing and Encryption (COSE): Initial Algorithms.
- RFC 9338 — CBOR Object Signing and Encryption (COSE): Countersignatures.
- RFC 3161 — Internet X.509 Public Key Infrastructure Time-Stamp Protocol.
- RFC 5280 — Internet X.509 Public Key Infrastructure Certificate and CRL Profile.
- RFC 4998 — Evidence Record Syntax.
- W3C Data Integrity 1.0.
- W3C DID Core.

---

## 29. Deferred Work

The following are intentionally deferred to later OLP specifications:

- canonical proof identifiers;
- proof commitments;
- countersignatures;
- proof-to-proof dependencies;
- evidence graphs;
- timestamp-evidence object models;
- transparency-proof object models;
- blockchain-anchor evidence models;
- universal JSON transport encoding;
- additional mandatory or recommended cryptosuites;
- post-quantum suite profiles;
- cryptosuite registry governance;
- verification-method status evidence schemas; and
- application trust-policy languages.

Deferral of these items is intentional. They are higher-layer structures built on the proof primitive defined here.

---

**End of OLP Specification 0004 — Draft v0.1**
