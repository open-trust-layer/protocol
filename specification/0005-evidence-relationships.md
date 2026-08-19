# OLP Specification 0005 — Evidence Relationships and Graphs

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 5 — Evidence Relationships & Graphs  
**Filename:** `specification/0005-evidence-relationships.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) v1 evidence-relationship and evidence-graph layer.

It defines:

- stable proof identity for detached OLP proofs;
- typed references to immutable OLP records and proofs;
- evidence relationships as ordinary immutable OLP records rather than mutable graph metadata;
- the `RelationshipStatementV1` semantic record profile;
- a small core vocabulary for structural and provenance relationships;
- explicit countersignature relationships without introducing linear proof chains;
- anchoring relationships for external time, transparency, ledger, and archival evidence;
- evidence graph construction and projection rules;
- graph traversal and resolution semantics;
- partial and dangling graphs;
- supersession, correction, and dispute semantics without history rewriting;
- evidence bundles as transport containers rather than trust objects;
- extension and critical-qualifier processing;
- structured relationship-processing results;
- conformance requirements; and
- security and privacy considerations.

The evidence graph is a graph of claims and cryptographically attributable statements. It is not a graph of protocol-declared truth.

OLP does not define universal evidence weight, universal trust propagation, universal graph ranking, or a canonical path from evidence to a trust decision.

---

## 2. Scope

This specification answers the question:

> How can independently verifiable OLP records and proofs refer to one another, express explicit provenance and evidence relationships, and be assembled into portable graphs without turning graph structure into a universal trust judgment?

This specification builds directly on:

- OLP Specification 0003 — Record Representation; and
- OLP Specification 0004 — Proofs and Verification.

Specification 0004 establishes the primitive:

```text
Proof -> Record
```

This specification adds explicit evidence relationships while preserving that primitive unchanged.

This specification does **not** define:

- a universal trust score;
- a universal reputation score;
- automatic trust propagation;
- a universal notion of evidence sufficiency;
- a universal causal-inference engine;
- a universal contradiction resolver;
- a universal concept of the "latest" or "correct" record;
- a mandatory blockchain;
- a mandatory transparency log;
- a mandatory timestamp authority;
- a mandatory storage network;
- a mandatory graph database;
- a mandatory evidence resolver;
- a universal ontology for every possible relationship;
- format-specific validation rules for RFC 3161 timestamp tokens, transparency receipts, blockchain receipts, or other external evidence formats; or
- application-specific policy for deciding whether a relationship should be relied upon.

Those concerns MAY be defined by later OLP specifications, external standards, or application policy.

---

## 3. Requirements Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described by BCP 14 when, and only when, they appear in all capitals.

---

## 4. Core Invariants

The following invariants are normative.

### 4.1 Relationships are evidence, not mutable metadata

An OLP evidence relationship is represented by an immutable OLP record containing a relationship statement.

A relationship MUST NOT exist solely as unsigned, mutable graph metadata if it is intended to carry protocol-level evidentiary meaning.

This means a relationship can itself:

- receive OLP proofs;
- be referenced by later records;
- be disputed;
- be corrected;
- be superseded; and
- remain independently inspectable as historical evidence.

### 4.2 No second record object model

This specification does not introduce a second identity-bearing record envelope.

A relationship record is an ordinary OLP record conforming to Specification 0003 whose semantic record content conforms to `RelationshipStatementV1` as defined here.

The enclosing record retains the identity, canonicalization, extension, and immutability rules of Specification 0003.

### 4.3 Proofs remain detached

This specification does not modify the OLP proof primitive defined by Specification 0004.

An ordinary OLP proof continues to bind to exactly one OLP record.

A proof over a relationship record therefore authenticates the relationship statement because the relationship statement is part of that immutable record.

### 4.4 Graph structure is not truth

The presence of a relationship in an OLP evidence graph MUST NOT be interpreted by OLP as establishing that the relationship is objectively true.

For example:

```text
A --corrects--> B
```

means that an immutable OLP relationship record asserts the defined `corrects` relationship.

It does not mean that OLP has determined that B was objectively wrong.

### 4.5 No implicit transitivity

A relationship between A and B and a relationship between B and C MUST NOT automatically create a protocol-level relationship between A and C unless a specification explicitly defines that inference.

In particular, OLP v1 defines no automatic transitivity for:

- `references`;
- `derivesFrom`;
- `supersedes`;
- `corrects`;
- `disputes`;
- `anchors`; or
- `countersigns`.

### 4.6 No implicit trust propagation

Trust, reliability, authority, confidence, and evidentiary weight MUST NOT propagate automatically across graph edges.

A valid proof on A does not make B trusted merely because A references B.

A trusted verifier of one record does not become a trust root for everything reachable from that record.

### 4.7 No graph-count trust

The number of:

- records;
- proofs;
- relationship records;
- graph paths;
- witnesses;
- references; or
- repeated appearances in bundles

MUST NOT create protocol-defined truth, confidence, authority, or evidentiary weight.

### 4.8 History is additive

Supersession, correction, dispute, withdrawal-like semantics, and anchoring are represented by additional immutable evidence.

They MUST NOT rewrite or delete the identity, content, or historical cryptographic validity of existing records or proofs.

### 4.9 Partial graphs are valid

An evidence graph MAY be incomplete.

A relationship record MAY validly reference an object that is not locally available.

Unavailability of a referenced object MUST NOT, by itself, make the relationship record malformed or cryptographically invalid.

### 4.10 Projection never outranks provenance

Implementations MAY project convenient subject-predicate-object edges from relationship records for graph queries.

Every projected edge MUST retain provenance identifying the exact relationship record from which the edge was derived.

A projected edge MUST NOT be treated as stronger evidence than its underlying relationship record and proofs.

---

## 5. Terminology

### 5.1 Evidence object

For this specification, a core OLP evidence object is either:

- an immutable OLP record; or
- an immutable OLP proof.

Relationship records are records and therefore already belong to this set.

### 5.2 Record reference

A typed content-addressed reference to an OLP record using the stable Record Identity digest defined by Specification 0003.

### 5.3 Proof reference

A typed content-addressed reference to an OLP proof using the stable Proof Identity defined by this specification.

### 5.4 Evidence reference

A `RecordRef` or `ProofRef`.

### 5.5 Relationship record

An ordinary OLP record whose semantic content conforms to `RelationshipStatementV1`.

### 5.6 Relationship statement

The immutable semantic value inside a relationship record describing:

- the relationship type;
- its subject when explicit;
- one or more target evidence objects;
- optional qualified extension data; and
- critical qualifiers.

### 5.7 Relationship proof

An ordinary `OLPProof` whose referenced record is a relationship record.

### 5.8 Evidence graph

A contextual graph view constructed from available OLP records, proofs, relationship records, and their resolved references.

An evidence graph is a view over evidence objects, not a new authoritative protocol object.

### 5.9 Projected edge

A convenience graph edge derived from a relationship record.

Projected edges do not replace the underlying relationship record.

### 5.10 Root

An evidence reference selected as a traversal or bundle starting point.

Being a root does not imply trust, priority, authority, or semantic importance beyond the local context selecting it.

### 5.11 Dangling reference

A syntactically valid evidence reference for which the referenced object is not currently available to the processor.

### 5.12 Relationship producer

An entity or verification method that produces a valid proof over a relationship record.

The term does not imply real-world identity or authority.

---

## 6. Architectural Model

OLP v1 uses reified evidence relationships.

Conceptually:

```text
                     +------------------+
                     | Relationship R   |
                     | immutable record |
                     +--------+---------+
                              |
                    relation statement
                              |
                 +------------+------------+
                 |                         |
                 v                         v
            Subject A                 Target B

                     ^
                     |
                 OLP Proof P
```

The important property is that `Relationship R` is itself evidence.

It is not merely an edge inserted into a mutable graph database.

This permits later evidence such as:

```text
Relationship S --disputes--> Relationship R
```

because R has an ordinary Record Identity.

### 6.1 Why relationships are records

Representing relationships as records preserves the architecture established by Specifications 0003 and 0004:

```text
record semantics
      |
      v
immutable Record Identity
      |
      v
ordinary detached proofs
```

No new signature primitive is necessary.

No new mutable relationship identity system is necessary.

No special authority is required to create graph edges.

### 6.2 Graphs are derived views

The authoritative protocol artifacts are the immutable records and proofs.

A graph processor derives a graph view from them.

Different applications MAY:

- load different subsets of the evidence;
- resolve different dangling references;
- apply different local filtering;
- compute different policy results; and
- visualize the same evidence differently.

Those differences do not change object identity.

---

## 7. Proof Identity

Specification 0004 deliberately deferred canonical proof identifiers.

This specification defines a stable transport-independent Proof Identity so that proofs can be referenced by later evidence.

### 7.1 Proof identity requirements

Proof Identity MUST:

- identify one exact OLP proof independently of transport serialization;
- change if the authenticated Proof Input changes;
- change if `proofValue` changes;
- remain stable if transport-only annotations or packaging change;
- remain stable if current resolver state, key status, or local policy changes; and
- be computable without treating the proof as cryptographically valid.

Identity and validity are separate concepts.

### 7.2 Canonical proof identity preimage

For an OLP v1 proof, reconstruct the exact `ProofInputV1` and deterministic Proof Input bytes according to Specification 0004.

Then construct:

```text
ProofIdentityPreimageV1 = [
    "OLP-PROOF-ID",
    1,
    proofInputBytes,
    proofValue
]
```

The array MUST contain exactly four elements.

Where:

- element 0 is the exact text string `OLP-PROOF-ID`;
- element 1 is integer `1`;
- element 2 is a byte string containing the exact deterministic CBOR `ProofInputV1` bytes; and
- element 3 is a byte string containing the exact abstract `proofValue` bytes.

### 7.3 Proof identity encoding

`ProofIdentityPreimageV1` MUST be encoded using the same deterministic CBOR profile defined for Proof Input v1 by Specification 0004.

This proof-identity encoding is referred to as:

```text
OLP-PIE-1
```

Implementations MUST NOT substitute a transport encoding of `OLPProof`.

### 7.4 Proof identity digest

The v1 Proof Identity digest is:

```text
SHA-256(OLP-PIE-1(ProofIdentityPreimageV1))
```

The resulting digest is exactly 32 octets.

This digest is referred to as the:

```text
ProofIdentityDigest
```

### 7.5 Stable identity versus algorithm agility

Proof Identity uses SHA-256 as a stable v1 identity function.

This is distinct from algorithm-agile commitments used for cryptographic anchoring or future proof mechanisms.

Using another hash for an external commitment does not create another identity for the same proof.

This mirrors the distinction between Record Identity and proof `recordCommitment` established by Specification 0004.

### 7.6 Proof identity does not verify the proof

Computing a Proof Identity does not establish:

- signature validity;
- verification-method validity;
- proof-purpose acceptance;
- current key status;
- historical trustworthiness; or
- truth of the referenced record.

A structurally valid but cryptographically invalid proof can still have a stable Proof Identity.

### 7.7 Malformed proofs

A proof for which `ProofInputV1` cannot be deterministically reconstructed according to Specification 0004 does not have a conforming OLP v1 Proof Identity.

Implementations MUST NOT hash an arbitrary received serialization as a fallback.

### 7.8 Proof identity immutability

Changing any authenticated proof property changes `proofInputBytes` and therefore changes Proof Identity.

Changing `proofValue` also changes Proof Identity.

Later changes in:

- key revocation state;
- cryptosuite recommendation;
- resolver availability;
- policy; or
- timestamp evidence

MUST NOT change Proof Identity.

---

## 8. Evidence References

### 8.1 Core evidence-reference representation

`EvidenceRefV1` is a two-element array:

```text
EvidenceRefV1 = [
    kind,
    identityDigest
]
```

The array MUST contain exactly two elements.

### 8.2 Record reference

A record reference is:

```text
[
    0,
    recordIdentityDigest
]
```

Where:

- kind `0` means `record`; and
- `recordIdentityDigest` is the exact 32-octet SHA-256 Record Identity digest defined by Specification 0003.

### 8.3 Proof reference

A proof reference is:

```text
[
    1,
    proofIdentityDigest
]
```

Where:

- kind `1` means `proof`; and
- `proofIdentityDigest` is the exact 32-octet Proof Identity digest defined in Section 7.

### 8.4 Unsupported kinds

No other evidence-reference kinds are defined by `EvidenceRefV1`.

Future OLP object categories SHOULD normally be represented as OLP records where practical, allowing them to use kind `0` without expanding the graph's identity model.

A future specification MAY define a new evidence-reference version if another first-class identity-bearing object category is genuinely required.

### 8.5 Raw digest, not presentation syntax

Evidence references contain raw identity digest bytes.

They MUST NOT contain:

- hexadecimal strings;
- Base64 strings;
- multibase strings;
- database IDs;
- mutable URLs; or
- application aliases

as substitutes for the identity digest.

Transport formats MAY encode byte strings textually according to their own transport specification.

### 8.6 Reference verification

When an object is supplied for an `EvidenceRefV1`, a processor MUST:

1. confirm that the supplied object category matches `kind`;
2. recompute its OLP identity according to the applicable specification; and
3. compare the resulting identity digest byte-for-byte with `identityDigest`.

A mismatch MUST report `EVIDENCE_IDENTITY_MISMATCH`.

A processor MUST NOT trust an externally supplied claimed identifier without recomputation when the object itself is available.

### 8.7 Reference canonical bytes

For sorting and duplicate detection required by this specification, an `EvidenceRefV1` MUST be encoded using deterministic CBOR under the restrictions of Specification 0004.

The resulting bytes are referred to as:

```text
EvidenceRefCanonicalBytes
```

This encoding is used only for deterministic relationship processing and does not replace the underlying Record Identity or Proof Identity algorithms.

### 8.8 Reference equality

Two core evidence references are equal if and only if:

- their `kind` values are equal; and
- their 32-octet identity digests are byte-for-byte equal.

Aliases, storage locations, display names, or resolver metadata MUST NOT affect equality.

---

## 9. Relationship Records

### 9.1 Semantic record profile

An OLP v1 relationship record is an ordinary OLP record conforming to Specification 0003 whose semantic record content is exactly one `RelationshipStatementV1` value.

This specification defines the relationship statement, not a new record envelope.

The enclosing record continues to use Specification 0003 for:

- required record structure;
- canonical identity preimage construction;
- deterministic record encoding;
- Record Identity;
- record-level extensions; and
- immutability.

### 9.2 Relationship statement

The exact abstract `RelationshipStatementV1` is the following seven-element array:

```text
RelationshipStatementV1 = [
    "OLP-EVIDENCE-RELATIONSHIP",  ; index 0: domain/profile discriminator
    1,                            ; index 1: relationship version
    relationType,                 ; index 2
    subject,                      ; index 3: EvidenceRefV1 or null
    objects,                      ; index 4: non-empty sorted array
    qualifiers,                   ; index 5: map
    critical                      ; index 6: sorted array
]
```

The array MUST contain exactly seven elements.

### 9.3 Domain/profile discriminator

Index 0 MUST equal the exact text string:

```text
OLP-EVIDENCE-RELATIONSHIP
```

### 9.4 Version

Index 1 MUST equal integer `1`.

A processor receiving another syntactically valid version MUST report `UNSUPPORTED_RELATIONSHIP_VERSION` unless it implements that version.

### 9.5 Relation type

Index 2 MUST be a non-empty text string.

Core OLP relation types use compact identifiers reserved by OLP.

Extension relation types MUST use absolute URI identifiers under RFC 3986.

Core relation semantics are defined in Section 11.

### 9.6 Subject

Index 3 is either:

- one valid `EvidenceRefV1`; or
- `null` where the selected relation type explicitly defines proof-producer-relative semantics.

In OLP v1, only the core `countersigns` relation permits `null` subject.

### 9.7 Objects

Index 4 MUST be a non-empty array of `EvidenceRefV1` values.

The object array represents a set.

Therefore:

- every reference MUST be unique;
- order has no semantic meaning; and
- producers MUST sort the references in ascending bytewise lexicographic order of `EvidenceRefCanonicalBytes` before the enclosing record identity is computed.

A processor MUST reject a v1 relationship statement containing duplicate objects.

### 9.8 Qualifiers

Index 5 is a map of relationship-specific extension qualifiers.

If no qualifiers are present, it MUST be the empty map.

Each qualifier key MUST be an absolute URI.

Qualifier values MUST use data types permitted by the enclosing OLP record specification.

Compact, unregistered qualifier names are not permitted in v1.

### 9.9 Critical qualifiers

Index 6 is an array of qualifier identifiers whose semantics MUST be understood to safely process the relationship.

If no critical qualifiers exist, it MUST be the empty array.

Each member:

- MUST be an absolute URI;
- MUST be unique;
- MUST name a qualifier actually present in the qualifier map; and
- MUST NOT name a core relationship field.

Before record identity construction, critical members MUST be sorted in ascending bytewise lexicographic order of their UTF-8 encodings.

### 9.10 Unknown non-critical qualifiers

A processor MAY preserve and process the structural relationship while leaving an unknown non-critical qualifier uninterpreted.

It MUST expose that the qualifier was not interpreted.

It MUST NOT claim to understand unknown semantics.

### 9.11 Unknown critical qualifiers

A processor that does not understand a critical qualifier MUST report:

```text
UNSUPPORTED_CRITICAL_RELATIONSHIP_QUALIFIER
```

It MUST NOT report the relationship as fully semantically processed.

### 9.12 Duplicate map keys

Duplicate qualifier keys are non-conforming.

Implementations MUST NOT use first-wins, last-wins, merge, or parser-specific duplicate-key behavior.

### 9.13 Relationship record identity

A relationship record receives an ordinary Record Identity from Specification 0003.

No separate `RelationshipIdentity` is defined.

This is deliberate.

Relationship records are records.

### 9.14 Relationship record proofs

Any ordinary OLP proof MAY concern a relationship record.

For a relationship producer to cryptographically assert the relationship statement, an application SHOULD normally require a cryptographically valid proof with:

```text
proofPurpose = assertion
```

Other proof purposes retain their ordinary meanings.

For example, a `witness` proof over a relationship record does not automatically become an `assertion` proof merely because the record contains a relationship.

---

## 10. Relationship Semantics and Attribution

### 10.1 Statement versus acceptance

A relationship record is an immutable statement.

Its existence establishes that the statement is present in the evidence set.

It does not establish that any application accepts the statement.

### 10.2 Unproved relationship records

A structurally valid relationship record MAY exist without any proof.

A graph processor MAY include it while reporting its attribution state as unproved or not evaluated.

Applications requiring attributable relationship evidence SHOULD require one or more proofs appropriate to their policy.

### 10.3 Assertion proof

A valid `assertion` proof over a relationship record establishes that the verification method authenticated that exact relationship record as an assertion.

It does not establish:

- the real-world identity of the controller;
- authority to make the relationship authoritative;
- objective truth of the relationship; or
- application acceptance.

### 10.4 Multiple proofs

Multiple proofs over one relationship record remain independent according to Specification 0004.

Proof count does not create protocol-defined weight.

### 10.5 Competing relationships

Different relationship records MAY assert incompatible relationships concerning the same evidence objects.

For example:

```text
R1: A --supersedes--> B
R2: B --supersedes--> A
```

or:

```text
R3: C --corrects--> D
R4: E --disputes--> R3
```

OLP preserves both.

It does not choose a winner.

### 10.6 Relationship producers are not graph authorities

Producing a valid proof over a relationship record does not grant the proof producer authority over:

- the referenced records;
- the referenced proofs;
- the subjects of those records;
- unrelated graph regions; or
- future interpretation.

Authority, where relevant, is application- or evidence-specific.

---

## 11. Core Relationship Vocabulary

OLP v1 defines the following compact core relation types:

```text
references
derivesFrom
supersedes
corrects
disputes
anchors
countersigns
```

Core relation types are semantically distinct.

They have no protocol-defined ordering by strength or evidentiary value.

### 11.1 `references`

Form:

```text
subject: EvidenceRefV1
objects: one or more EvidenceRefV1 values
```

Meaning:

> The relationship statement asserts that the subject explicitly refers to the listed evidence objects.

`references` does not imply:

- endorsement;
- agreement;
- derivation;
- truth;
- trust;
- authority; or
- dependency sufficient for application acceptance.

The subject and objects MAY be records or proofs.

### 11.2 `derivesFrom`

Form:

```text
subject: EvidenceRefV1
objects: one or more EvidenceRefV1 values
```

Meaning:

> The relationship statement asserts that the subject was produced using, transformed from, computed from, or otherwise materially derived from the listed evidence objects.

`derivesFrom` does not establish:

- correctness of the derivation;
- completeness of the listed inputs;
- truth of any input;
- truth of the derived object; or
- a protocol-level causal proof.

A derivation relationship MAY be more precisely qualified by an extension qualifier.

OLP v1 defines no automatic transitive `derivesFrom` inference.

### 11.3 `supersedes`

Form:

```text
subject: RecordRef
objects: one or more RecordRef values
```

Meaning:

> The relationship statement asserts that the subject record is intended to replace the listed target records for some purpose or context.

`supersedes` does **not**:

- delete the targets;
- mutate the targets;
- invalidate historical proofs over the targets;
- establish that the subject is objectively more correct;
- establish universal recency; or
- force applications to prefer the subject.

Applications MAY use relationship qualifiers or local policy to define supersession scope.

Competing supersession statements are permitted.

### 11.4 `corrects`

Form:

```text
subject: RecordRef
objects: one or more RecordRef values
```

Meaning:

> The relationship statement asserts that the subject record supplies a correction, amendment, or remedy for an error or omission in the listed target records.

`corrects` does not mean OLP has determined that the target is objectively false.

The target record remains immutable historical evidence.

A correction SHOULD be represented by a new record plus this relationship rather than by editing the original record.

### 11.5 `disputes`

Form:

```text
subject: RecordRef
objects: one or more RecordRef values
```

Meaning:

> The relationship statement asserts that the subject record challenges, contests, or disputes the listed target records or relationship records.

Because relationship records are ordinary records, a dispute can target a relationship statement directly.

`disputes` does not establish that either side is correct.

It does not automatically create a logical contradiction relation.

### 11.6 `anchors`

Form:

```text
subject: RecordRef
objects: one or more EvidenceRefV1 values
```

Meaning:

> The relationship statement asserts that the subject record contains or identifies independent anchoring evidence that cryptographically commits to the listed target evidence objects.

The subject SHOULD contain sufficient format-specific evidence or references for an appropriate verifier to evaluate the claimed anchor.

Examples may include records carrying or referencing:

- RFC 3161 timestamp evidence;
- transparency-log inclusion evidence;
- ledger or blockchain anchoring evidence;
- archival evidence records;
- witness-service receipts; or
- future anchoring mechanisms.

The `anchors` relationship by itself does **not** establish:

- trusted time;
- inclusion in a valid log;
- blockchain finality;
- authority of the anchoring service; or
- acceptance of the anchoring system.

Those properties require validation of the subject evidence under the applicable external or future OLP evidence profile.

### 11.7 `countersigns`

Form:

```text
subject: null
objects: one or more ProofRef values
```

`countersigns` is producer-relative.

A relationship record using `countersigns` MUST have `subject = null` and every object MUST be a `ProofRef`.

The relationship record alone is a countersignature statement template.

For each cryptographically valid OLP proof over that relationship record having:

```text
proofPurpose = assertion
```

the proof establishes:

> The proof producer's verification method cryptographically asserted a countersignature statement over the exact set of target Proof Identities contained in the relationship record.

This construction binds the countersigning proof to the exact target proofs without modifying `OLPProof` itself.

### 11.8 Countersignature is not endorsement of underlying truth

Countersigning an OLP proof authenticates the exact target proof as evidence.

It does not automatically mean that the countersigner:

- independently verified the underlying real-world claim;
- agrees with every semantic implication an application might infer;
- has legal authority; or
- guarantees the target proof producer's identity.

The target proof's own `proofPurpose` remains part of what is being countersigned because it is included in the target Proof Identity.

### 11.9 Countersigning a set

If a `countersigns` relationship record contains multiple target proofs, an assertion proof over that relationship record authenticates the exact set as one countersignature statement.

Applications MAY project a relation to each member for query convenience, but MUST retain the common relationship-record identity and MUST NOT pretend that separate independent countersignature records existed.

For cases where independent countersignatures are required, separate one-target relationship records SHOULD be used.

### 11.10 No core `supports` or `contradicts`

OLP v1 intentionally does not define compact core relations named `supports` or `contradicts`.

Those concepts often require domain-specific interpretation, logical models, confidence assumptions, or evidentiary policy.

An ecosystem MAY define them as absolute-URI extension relation types with precise semantics.

OLP core does not assign universal support or contradiction judgments.

---

## 12. Relation-Type Extensions

### 12.1 Extension relation identifiers

A non-core relation type MUST be identified by an absolute URI.

Example conceptually:

```text
https://example.org/olp/relations/notarizes
```

### 12.2 Required semantics

An extension relation specification SHOULD define:

- permitted subject form;
- permitted target evidence kinds;
- whether `subject = null` is meaningful;
- whether target order is semantically relevant;
- required qualifiers;
- critical qualifiers;
- any expected proof purpose;
- validation rules; and
- security considerations.

### 12.3 Core target ordering remains set-like

`RelationshipStatementV1.objects` remains a sorted set regardless of extension relation type.

An extension requiring ordered inputs MUST encode the ordered structure explicitly in a qualifier or in referenced evidence rather than assigning hidden semantics to array insertion order.

### 12.4 Unknown relation type

A processor that does not understand an extension relation type MAY still:

- validate the enclosing record;
- compute its Record Identity;
- verify proofs over it; and
- preserve its exact relationship statement.

Semantic relationship processing MUST report:

```text
UNSUPPORTED_RELATION_TYPE
```

rather than falsely claiming to understand the relationship.

Unknown relation type is not record invalidity and is not proof cryptographic invalidity.

---

## 13. Relationship Validation

A relationship processor MUST separate structural validation from evidence interpretation.

### 13.1 Structural procedure

For a candidate relationship record:

1. Validate the enclosing record according to Specification 0003.
2. Confirm that the semantic content is a seven-element array.
3. Confirm the exact profile discriminator.
4. Confirm the relationship version.
5. Validate the relation-type identifier.
6. Validate `subject` against the relation-type rules.
7. Validate every object reference.
8. Confirm that objects are unique.
9. Confirm that objects are canonically sorted.
10. Validate qualifier keys and values.
11. Validate critical-qualifier declarations.
12. Apply relation-specific structural constraints.
13. Return a structured relationship-processing result.

### 13.2 Structural invalidity is not relationship falsity

A malformed relationship statement is non-conforming protocol data.

A structurally valid relationship statement that an application does not believe is still conforming evidence.

These conditions MUST NOT be conflated.

### 13.3 Subject-target identity

For core relations other than future explicitly defined exceptions, a relationship statement SHOULD NOT list an object reference equal to its explicit subject reference.

For `supersedes`, `corrects`, and `disputes`, subject-object equality is non-conforming.

### 13.4 Enclosing self-reference

A relationship statement MUST NOT attempt to reference the Record Identity of its own enclosing relationship record from inside the identity-bearing relationship content.

The enclosing Record Identity depends on that content, making ordinary self-reference incompatible with deterministic content-addressed identity.

Implementations MUST NOT attempt fixed-point search or other special behavior to manufacture such a self-reference.

### 13.5 Reference existence is not required at creation

A relationship producer MAY create a relationship record using a valid evidence reference even when the corresponding object is not locally present.

The producer is responsible for obtaining the correct identity digest.

The processor later treats unavailable objects as dangling references.

---

## 14. Evidence Graph Model

### 14.1 Graph nodes

A graph processor MAY construct nodes for:

- OLP records; and
- OLP proofs.

Relationship records are record nodes with additional recognized semantics.

### 14.2 Intrinsic proof-to-record binding

A verified OLP proof has an intrinsic binding to a record commitment under Specification 0004.

When the corresponding record is available and its commitment matches, a graph processor MAY project:

```text
Proof P --proves--> Record R
```

This projected `proves` edge is a graph convenience describing the cryptographic binding.

It is not a new relationship record and MUST NOT be confused with a claim that R is true.

### 14.3 Relationship statement projection

For a relationship record with explicit subject S, relation type T, and target O, a graph processor MAY project:

```text
S --T--> O
```

for query and visualization purposes.

For every projected edge, the processor MUST retain at least:

```text
relationshipRecord = RecordIdentity(R)
```

so that provenance can be recovered.

### 14.4 Reified form is normative

The immutable relationship record is the normative evidence artifact.

The projected edge is derivative.

Deleting a projected edge from a local graph cache does not delete evidence.

Reconstructing the graph from the same evidence objects MUST permit the edge to be projected again.

### 14.5 Multiple relationship records

Two distinct relationship records MAY project the same apparent subject-predicate-object edge.

They remain distinct evidence because they may have:

- different Record Identities;
- different qualifiers;
- different proofs;
- different producers;
- different creation metadata; or
- different surrounding context.

A graph processor MUST NOT collapse them into one evidence artifact merely because the projected edge text is identical.

### 14.6 Semantic multigraph

The resulting evidence graph is therefore a directed labeled multigraph when projected for convenience.

At the evidence level, it is more accurately a reified graph in which relationship statements themselves are addressable record nodes.

### 14.7 Cycles

Projected semantic graphs MAY contain cycles.

For example:

```text
A --supersedes--> B
B --supersedes--> A
```

or:

```text
A --references--> B
B --references--> A
```

A graph processor MUST NOT reject an evidence set merely because the projected graph contains cycles.

### 14.8 No mandatory DAG

OLP v1 does not require the evidence graph to be a directed acyclic graph.

Applications that require a DAG for a specific relation or workflow MAY enforce that requirement locally.

### 14.9 No canonical graph ordering

Nodes, records, proofs, relationship records, and projected edges have no protocol-defined total ordering.

Serialization or retrieval order MUST NOT create semantic chronology.

### 14.10 No canonical "current head"

OLP does not define a universal head record, chain tip, latest state, or canonical branch.

Applications MAY select one or more current candidates using local policy and available relationship evidence.

---

## 15. Supersession, Correction, and Dispute

### 15.1 No mutation through supersession

If A supersedes B:

```text
A --supersedes--> B
```

B remains:

- immutable;
- addressable;
- independently verifiable; and
- historically available if storage permits.

### 15.2 No implicit invalidation

A `supersedes`, `corrects`, or `disputes` relationship MUST NOT change:

- Record Identity of the target;
- Proof Identity of any target proof;
- mathematical validity of historical proofs; or
- previous relationship-record identities.

### 15.3 Multiple successors

A target MAY have multiple records that claim to supersede or correct it.

OLP does not select a canonical successor.

### 15.4 Dispute is evidence

A dispute record is additional evidence about a target.

It MUST NOT be treated as a deletion request.

### 15.5 Resolution is policy

Applications MAY define policies such as:

- prefer a correction proved by the same verification method as the original assertion;
- prefer a regulator-issued supersession;
- display all competing successors;
- require multi-party acknowledgement; or
- ignore unproved corrections.

Such rules are outside OLP core.

### 15.6 "Latest" requires context

A graph relationship alone does not provide trusted wall-clock chronology.

Signer-declared timestamps retain the semantics defined by Specification 0004.

Applications claiming that one record is temporally later than another SHOULD rely on appropriate independent time evidence when chronology matters.

---

## 16. Countersignature Processing

### 16.1 Construction

To countersign one or more existing OLP proofs:

1. Compute the Proof Identity of every target proof.
2. Construct a `RelationshipStatementV1` with:
   - `relationType = "countersigns"`;
   - `subject = null`;
   - `objects =` the sorted unique ProofRefs;
   - desired qualifiers; and
   - critical qualifiers as applicable.
3. Place the relationship statement in a new OLP record conforming to Specification 0003.
4. Produce an ordinary OLP proof over that relationship record according to Specification 0004.
5. Use `proofPurpose = assertion` for the countersigning proof.

### 16.2 Verification

To verify an OLP countersignature:

1. Validate the relationship record.
2. Confirm `relationType = countersigns`.
3. Confirm `subject = null`.
4. Confirm every target is a ProofRef.
5. Verify the countersigning OLP proof against the relationship record.
6. Confirm `proofPurpose = assertion` for countersignature semantics.
7. Resolve target proofs as required by application policy.
8. Recompute each available target Proof Identity and compare it to the referenced ProofRef.
9. Return structured countersignature results.

### 16.3 Target proof need not be valid for countersignature binding

A countersignature may cryptographically bind to a target proof that is itself invalid, unsupported, expired, or currently unresolvable.

These are separate dimensions.

For example:

```text
countersignatureProof = VALID
targetProofIdentity    = MATCH
targetProofValidity    = INVALID
```

is meaningful.

It establishes that the countersigner authenticated the exact target proof artifact, not that the target proof is valid.

### 16.4 Missing target

If the target proof is unavailable:

```text
countersignatureProof = VALID
targetResolution      = UNAVAILABLE
```

is permitted.

The countersigning proof remains cryptographically verifiable because it signs the relationship record, not the remotely fetched target bytes directly.

### 16.5 No countersignature recursion limit in semantics

A proof MAY countersign another proof that itself proves a countersignature relationship record.

This can form explicit evidence chains or graphs.

Processors MUST impose resource limits during recursive traversal but MUST NOT assign hidden semantic meaning to nesting depth.

### 16.6 Relationship to external countersignature formats

OLP countersignature semantics are defined by this specification.

An application MAY additionally carry COSE, CMS, or other external countersignature evidence inside OLP records.

Such external formats require their own verification rules and MUST NOT be silently treated as OLP countersignatures without an explicit mapping profile.

---

## 17. Anchoring and Independent External Evidence

### 17.1 Purpose

The `anchors` relation provides a generic graph connection between an OLP record containing anchoring evidence and one or more OLP evidence objects.

### 17.2 Separation of relationship and anchor validation

Two questions MUST remain separate:

```text
Does relationship record R assert that anchor evidence A concerns target T?
```

and:

```text
Does anchor evidence A validly establish the claimed timestamp, inclusion, ledger, or archival property for T?
```

The first is OLP relationship processing.

The second depends on the anchor evidence format and trust model.

### 17.3 Timestamp evidence

An OLP record MAY carry or identify an RFC 3161 timestamp token or another timestamp-evidence format.

A relationship record MAY then assert:

```text
TimestampEvidenceRecord --anchors--> Proof P
```

Validation of the timestamp token remains subject to the applicable timestamp specification and trust policy.

### 17.4 Transparency evidence

An OLP record MAY carry or identify transparency-log evidence.

A relationship record MAY assert that the transparency evidence anchors a record or proof.

The relationship does not itself establish:

- log consistency;
- inclusion correctness;
- log trustworthiness; or
- operator independence.

### 17.5 Blockchain or ledger evidence

An OLP record MAY carry evidence from a blockchain or other ledger.

OLP core does not privilege such evidence over other anchoring mechanisms.

Blockchain depth, finality, validator assumptions, chain identity, reorganization risk, and related policy remain external to this relationship layer.

### 17.6 Archival evidence

Archive timestamp or evidence-record systems MAY be connected through `anchors` relationships.

This permits long-term preservation evidence to accumulate without modifying historical records or proofs.

### 17.7 Anchor subject should be independently inspectable

The subject of an `anchors` relation SHOULD be an OLP record containing enough immutable information to permit independent inspection or retrieval of the external evidence.

A mutable locator by itself SHOULD NOT be treated as equivalent to preserved anchor evidence.

---

## 18. Evidence Resolution

### 18.1 Resolver boundary

Evidence-object resolution is logically separate from relationship semantics and cryptographic proof verification.

A conceptual resolver interface is:

```text
resolve(EvidenceRefV1, context) -> EvidenceObject | ResolutionResult
```

### 18.2 Offline operation

A conforming relationship and graph processor MUST be capable of operating on already-supplied records and proofs without network access.

### 18.3 No implicit network crawling

A generic OLP graph processor MUST NOT automatically crawl arbitrary network resources merely because graph traversal encounters a missing object.

Applications MAY explicitly configure evidence resolvers.

### 18.4 Resolution outcomes

A processor SHOULD distinguish at least:

```text
RESOLVED
UNAVAILABLE
NOT_FOUND
UNSUPPORTED
TYPE_MISMATCH
IDENTITY_MISMATCH
NOT_EVALUATED
```

### 18.5 Resolved object verification

When a referenced object is resolved, the processor MUST recompute its OLP identity before accepting the resolution as matching the reference.

### 18.6 Resolution provenance

Graph processors SHOULD retain provenance describing how an object was resolved, such as:

- supplied in the current bundle;
- local content-addressed store;
- configured resolver;
- archival repository;
- peer-to-peer system; or
- another explicit mechanism.

Resolution provenance does not imply trust.

### 18.7 Resolver plurality

OLP does not require one global resolver or storage network.

Different applications MAY resolve the same content-addressed evidence through different infrastructures and still obtain identical OLP identities.

---

## 19. Partial and Dangling Graphs

### 19.1 Missing objects

A graph processor MAY encounter:

```text
Relationship R
    |
    +--> RecordRef A  [resolved]
    +--> ProofRef B   [unavailable]
```

R can remain a valid relationship record even when B is unavailable.

### 19.2 No false invalidation

The processor MUST NOT convert target unavailability into:

- malformed relationship;
- invalid relationship proof; or
- target identity mismatch.

Those statuses have different meanings.

### 19.3 Deferred completion

An evidence graph MAY become more complete later when previously dangling references resolve.

Adding the resolved object does not mutate the existing relationship record.

### 19.4 Absence is not evidence of nonexistence

Failure to resolve an evidence reference MUST NOT be interpreted by OLP as proof that the referenced object never existed.

### 19.5 Unresolved semantics

Some relation-specific interpretation MAY require inspecting target content.

If required target content is unavailable, the processor SHOULD report the semantic dimension as `NOT_EVALUATED` or `INCOMPLETE` rather than guessing.

---

## 20. Graph Traversal

### 20.1 Traversal is contextual

OLP does not define one mandatory graph traversal algorithm.

Applications MAY traverse:

- outgoing relationship references;
- incoming relationship indexes;
- proof-to-record bindings;
- countersignature targets;
- supersession candidates;
- dispute branches; or
- application-specific relation types.

### 20.2 Root selection

A traversal begins from one or more locally selected roots.

Root selection is application context, not protocol truth.

### 20.3 No hidden closure requirement

A processor MUST NOT claim that a bundle or graph contains "all evidence" unless it has an external basis for that claim.

OLP content addressing can establish what is present and referenced; it cannot prove that no unreferenced evidence exists elsewhere.

### 20.4 Resource limits

Processors MUST support finite resource limits appropriate to their environment.

Limits SHOULD cover:

- maximum traversal depth;
- maximum resolved nodes;
- maximum relationship records;
- maximum proofs per record;
- maximum outbound resolution attempts;
- maximum object size;
- maximum qualifier depth;
- maximum wall-clock processing time; and
- maximum concurrent resolution operations.

### 20.5 Limit exhaustion

Stopping because of a configured resource limit MUST be reported as incomplete traversal, not as evidence invalidity.

### 20.6 Cycle detection

Processors traversing projected semantic edges MUST detect repeated identities sufficiently to avoid infinite traversal.

Encountering a cycle is not itself a protocol error.

### 20.7 Deterministic local processing

Given the same:

- finite evidence object set;
- supported relationship types;
- relationship qualifier support; and
- graph-processing configuration,

relationship extraction and structural projection SHOULD be deterministic.

Application ranking or trust-policy evaluation MAY remain pluralistic.

---

## 21. Evidence Bundles

### 21.1 Purpose

An evidence bundle is a transport convenience for moving a finite set of related OLP evidence objects together.

A bundle is not a new trust authority and is not an identity-bearing substitute for its contents.

### 21.2 Abstract bundle model

The abstract v1 bundle is:

```text
OLPEvidenceBundleV1 {
    type: "OLPEvidenceBundle"
    version: 1
    roots: array<EvidenceRefV1>
    records: collection<OLPRecord>
    proofs: collection<OLPProof>
}
```

This specification defines bundle semantics but does not define a universal JSON or CBOR transport serialization for the bundle.

A later transport specification MAY do so.

### 21.3 Roots

`roots` MAY be empty for an archival collection but SHOULD normally contain one or more unique evidence references for a task-oriented bundle.

Root ordering has no semantic meaning.

### 21.4 Records and proofs

`records` and `proofs` are contextual collections.

Collection ordering has no semantic meaning.

Repeated copies of the same object do not create additional evidence.

### 21.5 Object verification on ingestion

A bundle processor SHOULD compute:

- Record Identity for every record; and
- Proof Identity for every proof

before indexing them.

### 21.6 Conflicting same-identity objects

If a processor encounters two non-equivalent objects that claim or appear to have the same OLP identity, it MUST NOT silently select one.

It MUST report:

```text
IDENTITY_COLLISION_OR_CONFLICT
```

and preserve the conflict for investigation where feasible.

### 21.7 Bundle incompleteness

A bundle MAY omit objects referenced by included evidence.

Such references become dangling until resolved elsewhere.

### 21.8 Packaging does not create relationships

Placing A and B in the same bundle MUST NOT imply:

```text
A references B
A supports B
A endorses B
A precedes B
```

Relationships require explicit protocol evidence.

### 21.9 Bundle creator is not automatically an endorser

The act of assembling or transmitting a bundle does not, by itself, mean that the bundle creator endorses every included object.

An endorsement or assertion requires explicit signed evidence.

### 21.10 Bundle identity deferred

OLP v1 does not define a canonical bundle identity or bundle commitment.

Applications requiring an immutable statement about a precise object set SHOULD create an OLP record that explicitly references the desired evidence identities and then prove that record.

This avoids turning a convenience container into a second evidence primitive.

---

## 22. Structured Relationship Processing Results

A relationship processor SHOULD return structured results rather than one overloaded boolean.

### 22.1 Recommended dimensions

Conceptually:

```text
RelationshipProcessingResult {
    recordConformance
    relationshipConformance
    relationshipVersion
    relationTypeSupport
    criticalQualifierStatus
    subjectResolution
    objectResolutions[]
    relationshipProofResults[]
    attributionStatus
    projectedEdges[]
    warnings[]
    errors[]
}
```

Exact programming-language representation is implementation-specific.

### 22.2 Core status distinctions

Processors SHOULD distinguish:

```text
CONFORMING
MALFORMED
SUPPORTED
UNSUPPORTED
RESOLVED
UNAVAILABLE
MATCH
MISMATCH
VALID
INVALID
INCOMPLETE
NOT_EVALUATED
```

where applicable.

### 22.3 Reason codes

The following machine-readable reason codes are defined by this specification:

```text
MALFORMED_RELATIONSHIP_STATEMENT
UNSUPPORTED_RELATIONSHIP_VERSION
UNSUPPORTED_RELATION_TYPE
INVALID_RELATION_SUBJECT
INVALID_RELATION_OBJECT
DUPLICATE_RELATION_OBJECT
NON_CANONICAL_RELATION_OBJECT_ORDER
INVALID_RELATION_QUALIFIER
DUPLICATE_RELATION_QUALIFIER
INVALID_CRITICAL_RELATIONSHIP_QUALIFIER
UNSUPPORTED_CRITICAL_RELATIONSHIP_QUALIFIER
RELATION_SUBJECT_OBJECT_CONFLICT
EVIDENCE_REFERENCE_MALFORMED
EVIDENCE_KIND_MISMATCH
EVIDENCE_IDENTITY_MISMATCH
EVIDENCE_UNAVAILABLE
PROOF_IDENTITY_UNAVAILABLE
COUNTERSIGNATURE_TARGET_TYPE_MISMATCH
COUNTERSIGNATURE_PURPOSE_MISMATCH
ANCHOR_VALIDATION_NOT_EVALUATED
GRAPH_TRAVERSAL_LIMIT_REACHED
IDENTITY_COLLISION_OR_CONFLICT
```

### 22.4 Relationship proof validity is separate

A relationship statement can be conforming while a proof over it is invalid.

A proof can be valid while a target object is unavailable.

A target object can resolve correctly while application policy rejects the relationship producer.

The result model MUST preserve these distinctions.

### 22.5 Warnings

Warnings MUST NOT silently change stated validity dimensions.

For example:

```text
relationshipConformance = CONFORMING
warning = UNKNOWN_NON_CRITICAL_QUALIFIER
```

is valid.

---

## 23. No Implicit Inference Rules

### 23.1 No relationship substitution

A processor MUST NOT silently substitute one core relation for another.

For example:

```text
corrects != supersedes
references != derivesFrom
disputes != corrects
anchors != countersigns
```

### 23.2 No proof-purpose substitution

The existence of a relationship record MUST NOT cause proofs over it to acquire a different proof purpose.

An `acknowledgement` proof remains acknowledgement evidence.

It does not become `assertion` merely because the record is a relationship record.

### 23.3 No inferred endorsement

If A references B, OLP MUST NOT infer that the producer of A endorses B.

### 23.4 No inferred chronology

If A references B, OLP MUST NOT infer trusted wall-clock chronology between A and B.

Content-addressed references show that the referenced identity value was available to the producer of the referencing content; they do not constitute an independent timestamp.

### 23.5 No inferred identity equivalence

Two records referring to the same external person, organization, account, key, or object MUST NOT automatically be treated as the same OLP evidence object.

Identity equivalence requires explicit evidence or application policy.

### 23.6 No inferred authority

A valid `supersedes` or `corrects` relationship does not establish that the relationship producer possessed authority to supersede or correct the target for every application.

---

## 24. Privacy Considerations

### 24.1 Graph topology can be sensitive

Even when record content is encrypted, minimized, or pseudonymous, graph structure can reveal:

- repeated interaction;
- organizational relationships;
- dispute patterns;
- shared counterparties;
- key reuse;
- transaction clusters;
- social structure; or
- timing correlations.

Applications SHOULD minimize disclosure of unnecessary graph closure.

### 24.2 Do not bundle the world

An evidence bundle SHOULD contain only evidence necessary for the intended verification or policy task.

Portable history does not require indiscriminate disclosure of every related record.

### 24.3 Resolver privacy

Remote resolution can reveal which evidence objects a verifier is interested in.

Applications SHOULD consider:

- local caches;
- privacy-preserving retrieval;
- batched retrieval;
- content-addressed mirrors;
- anonymizing infrastructure; or
- offline bundles

where appropriate.

### 24.4 Correlation through stable identities

Stable Record Identities and Proof Identities are intentionally correlation-capable for immutable evidence.

Applications handling sensitive evidence SHOULD avoid publishing unnecessary identities to public indexes.

### 24.5 Relationship qualifiers

Qualifiers can leak sensitive context even when the core relation type is innocuous.

Producers SHOULD apply data minimization.

---

## 25. Security Considerations

### 25.1 Reference substitution

A processor MUST recompute the identity of a supplied object before accepting it as the target of an evidence reference.

Failure to do so can permit substitution attacks.

### 25.2 Parser ambiguity

Duplicate map keys, malformed arrays, non-canonical object-set ordering, and ambiguous extension handling can produce divergent graph interpretations.

Processors MUST follow the structural rules in this specification exactly.

### 25.3 Graph amplification attacks

Untrusted evidence can contain many references intended to force expensive traversal or network resolution.

Processors MUST enforce resource limits.

### 25.4 Resolver SSRF and network abuse

Graph processors MUST NOT treat evidence references as permission for arbitrary network access.

Resolver configuration is an explicit application security boundary.

### 25.5 Infinite traversal

Projected graphs may contain cycles.

Processors MUST detect revisited identities or otherwise guarantee traversal termination within configured resource bounds.

### 25.6 Relationship spoofing

An unsigned relationship record can be fabricated by anyone.

Applications requiring attribution MUST evaluate proofs over the relationship record rather than treating record existence as producer identity.

### 25.7 Proof spoofing

A Proof Identity identifies an exact proof artifact but does not establish that the proof is valid.

Applications MUST separately evaluate proof verification results.

### 25.8 Countersignature confusion

A valid countersignature proof establishes that the countersigner authenticated the exact target Proof Identity set.

Applications MUST NOT silently reinterpret this as:

- a new proof directly over the target record;
- agreement with the record's truth;
- legal ratification; or
- successful verification of the target proof.

### 25.9 Supersession hijacking

Anyone capable of producing an OLP record can create a statement claiming to supersede another record.

Applications MUST NOT treat `supersedes` as authoritative without evaluating producer identity, authority evidence, context, and local policy where those matter.

### 25.10 Correction hijacking

The same applies to `corrects`.

A correction relationship is evidence of a correction claim, not protocol-issued authority to rewrite another participant's history.

### 25.11 Dispute flooding

Attackers can create large numbers of dispute records.

Proof count and relationship count carry no protocol-defined weight.

Applications SHOULD use policy, provenance, rate limits, and relevance filters.

### 25.12 Anchor confusion

An `anchors` relationship does not validate the anchor mechanism.

Applications MUST verify the actual timestamp, log, ledger, archival, or witness evidence under the applicable specification.

### 25.13 Hash collisions

Record Identity and Proof Identity v1 rely on SHA-256 collision resistance.

If future cryptographic guidance requires identity migration, a later OLP specification will need an explicit migration strategy.

Applications MUST NOT silently reinterpret existing 32-octet identities under another hash algorithm.

### 25.14 Canonicalization mismatch

Proof Identity depends on the exact deterministic Proof Input bytes defined by Specification 0004.

Implementations MUST NOT derive Proof Identity from transport JSON, serializer-specific CBOR, or another representation.

### 25.15 External relation semantics

Unknown extension relations can carry security-critical meaning.

Applications MUST NOT claim semantic acceptance of an unsupported relation type.

### 25.16 Critical qualifier stripping

Critical qualifiers are identity-bearing record content.

Removing or changing them creates a different relationship record and therefore a different Record Identity.

Processors MUST still verify the structural relationship profile to prevent malformed critical declarations.

### 25.17 Evidence availability attacks

A valid graph can contain dangling references.

An attacker may intentionally withhold referenced evidence.

Applications requiring complete evidence for a decision SHOULD define explicit completeness requirements rather than interpreting availability as truth.

### 25.18 No truth oracle

An evidence graph can make provenance and disagreement inspectable.

It cannot cryptographically convert assertions into universal truth.

---

## 26. Conformance Classes

An implementation MAY claim conformance to one or more of the following classes.

### 26.1 Proof Identity Processor

A conforming Proof Identity Processor MUST:

- reconstruct `ProofInputV1` according to Specification 0004;
- compute exact deterministic Proof Input bytes;
- construct `ProofIdentityPreimageV1`;
- encode it using OLP-PIE-1;
- compute the SHA-256 Proof Identity digest; and
- reject malformed proofs rather than hashing arbitrary transport bytes.

### 26.2 Evidence Reference Processor

A conforming Evidence Reference Processor MUST:

- support record kind `0`;
- support proof kind `1`;
- validate 32-octet identity digests;
- recompute supplied-object identity before accepting a resolution; and
- distinguish type mismatch from identity mismatch.

### 26.3 Relationship Producer

A conforming Relationship Producer MUST:

- produce an ordinary OLP record conforming to Specification 0003;
- place a valid `RelationshipStatementV1` in its semantic record content;
- sort and deduplicate target references;
- validate qualifiers and critical qualifiers;
- obey core relation structural constraints; and
- compute the resulting Record Identity using Specification 0003.

### 26.4 Relationship Processor

A conforming Relationship Processor MUST:

- validate the enclosing record;
- validate `RelationshipStatementV1`;
- support every core relation type in Section 11 structurally and semantically;
- preserve unsupported extension relation types;
- enforce critical-qualifier behavior;
- expose resolution states separately; and
- preserve relationship-record provenance in any projected edges.

### 26.5 Countersignature Processor

A conforming Countersignature Processor MUST additionally:

- support `countersigns` relationship semantics;
- compute and verify target Proof Identities;
- require `subject = null`;
- require ProofRef targets;
- distinguish countersigning-proof validity from target-proof validity; and
- require an assertion-purpose proof for countersignature semantics.

### 26.6 Evidence Graph Processor

A conforming Evidence Graph Processor MUST:

- index records and proofs by recomputed identity;
- retain relationship-record provenance;
- tolerate dangling references;
- avoid implicit trust propagation;
- avoid implicit transitive relation creation;
- handle projected graph cycles safely; and
- expose incomplete traversal caused by resource limits.

### 26.7 Evidence Bundle Processor

A conforming Evidence Bundle Processor MUST:

- preserve contained object identities;
- treat bundle order as non-semantic;
- deduplicate repeated object copies without adding weight;
- detect conflicting same-identity objects; and
- avoid inferring relationships from co-packaging.

---

## 27. Interoperability Test Vector 1 — Proof Identity

This vector derives Proof Identity from the proof test vector in Specification 0004.

### 27.1 Proof Input bytes

Hexadecimal:

```text
89694f4c502d50524f4f46017065646473612d656432353531392d763169617373657274696f6e781a75726e3a6578616d706c653a6f6c703a746573742d6b65792d31822f5820bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7a0a080
```

Length:

```text
106 octets
```

### 27.2 `proofValue`

Hexadecimal:

```text
ea39ac65bdad595f3f79ea315b03545d034dced37c3ed26c5056a3978c6b3f2ee76caac70b914068bf06843ed689dcb41540b344143a23e97dc0d8c74782090d
```

Length:

```text
64 octets
```

### 27.3 Abstract proof identity preimage

```text
[
  "OLP-PROOF-ID",
  1,
  h'89694f4c502d50524f4f46017065646473612d656432353531392d763169617373657274696f6e781a75726e3a6578616d706c653a6f6c703a746573742d6b65792d31822f5820bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7a0a080',
  h'ea39ac65bdad595f3f79ea315b03545d034dced37c3ed26c5056a3978c6b3f2ee76caac70b914068bf06843ed689dcb41540b344143a23e97dc0d8c74782090d'
]
```

### 27.4 OLP-PIE-1 deterministic CBOR

Hexadecimal:

```text
846c4f4c502d50524f4f462d494401586a89694f4c502d50524f4f46017065646473612d656432353531392d763169617373657274696f6e781a75726e3a6578616d706c653a6f6c703a746573742d6b65792d31822f5820bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7a0a0805840ea39ac65bdad595f3f79ea315b03545d034dced37c3ed26c5056a3978c6b3f2ee76caac70b914068bf06843ed689dcb41540b344143a23e97dc0d8c74782090d
```

Length:

```text
189 octets
```

### 27.5 Expected Proof Identity digest

SHA-256:

```text
6d1039805594ca90c67e304ec2c3287e68af391b35dbb82dffd98382fa69af76
```

Length:

```text
32 octets
```

A conforming Proof Identity Processor MUST produce this digest from the listed proof.

---

## 28. Interoperability Test Vector 2 — Evidence References

Using the record digest from the Specification 0004 test vector and the Proof Identity from Section 27:

### 28.1 Record reference

Abstract:

```text
[
  0,
  h'bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7'
]
```

Deterministic CBOR:

```text
82005820bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7
```

### 28.2 Proof reference

Abstract:

```text
[
  1,
  h'6d1039805594ca90c67e304ec2c3287e68af391b35dbb82dffd98382fa69af76'
]
```

Deterministic CBOR:

```text
820158206d1039805594ca90c67e304ec2c3287e68af391b35dbb82dffd98382fa69af76
```

### 28.3 Ordering

For a relationship object set containing both references above, the RecordRef sorts before the ProofRef because its deterministic CBOR encoding is bytewise lexicographically smaller.

A conforming producer representing this two-object set MUST therefore order it as:

```text
[
  RecordRef,
  ProofRef
]
```

---

## 29. Example Relationship Statements

These examples show abstract semantic content only. The enclosing OLP record structure remains defined by Specification 0003.

### 29.1 Reference

```text
[
  "OLP-EVIDENCE-RELATIONSHIP",
  1,
  "references",
  [0, h'<record-A-id>'],
  [
    [0, h'<record-B-id>']
  ],
  {},
  []
]
```

Meaning:

> Record A is asserted to reference Record B.

No endorsement is implied.

### 29.2 Correction

```text
[
  "OLP-EVIDENCE-RELATIONSHIP",
  1,
  "corrects",
  [0, h'<corrected-record-id>'],
  [
    [0, h'<original-record-id>']
  ],
  {},
  []
]
```

The original record remains immutable.

### 29.3 Dispute against a relationship record

```text
[
  "OLP-EVIDENCE-RELATIONSHIP",
  1,
  "disputes",
  [0, h'<dispute-record-id>'],
  [
    [0, h'<relationship-record-id>']
  ],
  {},
  []
]
```

Because the target relationship is itself a record, no special graph-object identity is required.

### 29.4 Countersignature statement

```text
[
  "OLP-EVIDENCE-RELATIONSHIP",
  1,
  "countersigns",
  null,
  [
    [1, h'<target-proof-id>']
  ],
  {},
  []
]
```

A valid assertion-purpose OLP proof over the enclosing relationship record provides the countersignature evidence.

### 29.5 Anchoring statement

```text
[
  "OLP-EVIDENCE-RELATIONSHIP",
  1,
  "anchors",
  [0, h'<timestamp-evidence-record-id>'],
  [
    [1, h'<target-proof-id>']
  ],
  {},
  []
]
```

The relationship identifies the claimed target.

The timestamp evidence itself still requires independent format-specific validation.

---

## 30. Design Summary

The OLP v1 evidence graph is built from a deliberately small set of immutable primitives:

```text
OLP Record
    |
    +--> stable Record Identity
    |
    +<-- ordinary OLP Proof

OLP Proof
    |
    +--> stable Proof Identity

Relationship Record
    |
    +--> ordinary OLP Record
    +--> RelationshipStatementV1
    +--> EvidenceRef(subject)
    +--> EvidenceRef(targets...)
    +<-- ordinary OLP Proof(s)
```

A graph processor may derive:

```text
Subject --relationType--> Target
```

but the relationship-record identity remains attached as provenance.

The architecture therefore supports:

```text
immutable evidence
      +
cryptographic attribution
      +
explicit relationships
      +
partial graph exchange
      +
competing interpretations
```

without requiring:

```text
one chain
one global head
one trust score
one authority
one resolver
one blockchain
one interpretation algorithm
```

The graph preserves evidence.

Applications interpret it.

---

## 31. References

### Normative

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels.
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
- RFC 3986 — Uniform Resource Identifier (URI): Generic Syntax.
- RFC 8949 — Concise Binary Object Representation (CBOR).
- OLP Specification 0003 — Record Representation.
- OLP Specification 0004 — Proofs and Verification.

### Informative

- RFC 6920 — Naming Things with Hashes.
- RFC 9338 — CBOR Object Signing and Encryption (COSE): Countersignatures.
- RFC 3161 — Internet X.509 Public Key Infrastructure Time-Stamp Protocol.
- RFC 4998 — Evidence Record Syntax.
- RFC 9162 — Certificate Transparency Version 2.0.
- RFC 9943 — An Architecture for Trustworthy and Transparent Digital Supply Chains (SCITT Architecture).
- W3C PROV-DM — The PROV Data Model.
- W3C PROV-CONSTRAINTS — Constraints of the PROV Data Model.

---

## 32. Deferred Work

The following are intentionally deferred to later OLP specifications:

- universal textual presentation syntax for RecordRef and ProofRef;
- canonical evidence-bundle serialization;
- canonical evidence-bundle identity or commitments;
- external evidence-object transport profiles;
- RFC 3161 timestamp-evidence record profile;
- transparency-receipt record profile;
- blockchain or ledger-anchor record profiles;
- archival evidence-record profiles;
- selective disclosure of graph substructures;
- encrypted evidence bundles;
- privacy-preserving graph resolution;
- evidence availability proofs;
- application trust-policy languages;
- graph ranking algorithms;
- reputation algorithms;
- domain-specific `supports` or `contradicts` semantics;
- identity and authority relationship profiles;
- schema governance for extension relation types and qualifiers;
- post-quantum identity migration if ever required; and
- protocol-level synchronization or replication between evidence stores.

Deferral is intentional.

These concerns build on the immutable graph primitives defined here and should not be baked into the core relationship model prematurely.

---

**End of OLP Specification 0005 — Draft v0.1**
