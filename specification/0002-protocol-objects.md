# Open Layer Protocol — Protocol Objects

**Status:** Draft v0.1  
**Milestone:** 2 — Protocol Objects  
**Filename:** `specification/0002-protocol-objects.md`

---

## 1. Purpose

This specification defines the conceptual object model used by Open Layer Protocol (OLP).

It builds on `0001-terminology.md` and establishes which concepts are represented as first-class immutable records, which concepts are reusable embedded structures, and which concepts remain derived or application-specific.

The object model is intentionally small.

OLP should standardize portable evidence, not every possible business or trust concept.

---

## 2. Requirements language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are interpreted as described by RFC 2119 and RFC 8174 when written in all capitals.

---

## 3. Core design rule: one universal Record envelope

OLP has one universal immutable **Record** envelope.

Semantic record types are expressed through the envelope's `type` and `content` rather than through unrelated top-level object formats.

Conceptually:

```text
Record
├── envelope_version
├── type
├── content
├── semantic_bindings? 
├── profiles?
├── relationships?
└── extensions?
```

The exact identity-bearing representation and canonical encoding are defined by Specification 0003.

Proofs are not part of the Record envelope. Specification 0004 defines proofs as detached first-class cryptographic artifacts.

---

## 4. Record envelope fields

### 4.1 `envelope_version`

Required.

Identifies the Record envelope version.

Draft v0.1 defines envelope version `1`.

### 4.2 `type`

Required.

Identifies the semantic type of `content`.

Core OLP semantic types use identifiers reserved by OLP specifications.

Extension semantic types MUST be globally unambiguous.

### 4.3 `content`

Required.

Carries the semantic value represented by the record.

The permitted abstract value model and canonical representation are defined by Specification 0003.

### 4.4 `semantic_bindings`

Optional.

Carries explicit bindings from semantic roles or field meanings to definitions, profiles, schemas, or other identifiers when required for independent interpretation.

Bindings MUST NOT silently override core envelope semantics.

### 4.5 `profiles`

Optional.

Identifies additional profiles that the record claims to conform to.

A profile claim is evidence about intended semantics; it does not replace actual conformance validation.

### 4.6 `relationships`

Optional.

Carries record-local relationship information when a specification explicitly defines such a field.

General evidence-graph relationships are defined later by Specification 0005 as immutable relationship records and SHOULD be preferred when the relationship itself needs provenance, proofs, dispute, or lifecycle handling.

### 4.7 `extensions`

Optional.

Carries namespaced extension data.

Extension names MUST be globally unambiguous.

Security-critical extension semantics require explicit criticality mechanisms in the specification that defines them.

### 4.8 Empty optional fields

Optional envelope fields SHOULD be omitted when empty.

Canonical identity rules MUST define omission and empty values unambiguously so implementations cannot derive different identities from semantically equivalent envelopes.

---

## 5. First-class semantic record types

Draft v0.1 recognizes the following core semantic categories.

### 5.1 Claim

A `Claim` record represents a proposition asserted about one or more subjects.

A Claim is auxiliary in the sense that many specialized record types are themselves claims with more specific semantics.

A Claim does not imply truth.

### 5.2 Attestation

An `Attestation` record represents an attributable assertion by or on behalf of a participant or verification method.

Cryptographic attribution is supplied by detached proofs, not by embedding a signature inside the record.

### 5.3 Observation

An `Observation` record represents an asserted observation, measurement, detection, or inspection.

Observation records SHOULD preserve sufficient context to distinguish what was observed from conclusions derived from the observation.

### 5.4 Event

An `Event` record represents an occurrence or state transition.

Events MAY involve participants, resources, locations, times, inputs, outputs, and outcomes as defined by the applicable semantic profile.

### 5.5 StatusChange

A `StatusChange` record represents an asserted lifecycle or status transition concerning another subject or evidence object.

Later lifecycle specifications MAY define richer status statement profiles while preserving the additive-history model.

---

## 6. Specializations

### 6.1 Interaction

`Interaction` is a specialization of `Event` involving multiple participants or roles.

OLP does not require a separate universal envelope type when an Event profile can express the necessary semantics.

### 6.2 Revocation

`Revocation` is a specialized `StatusChange` operation indicating withdrawal according to the semantics and authority of the status source.

### 6.3 Supersession

`Supersession` is a specialized `StatusChange` or evidence relationship indicating that another object is intended to replace an earlier object for some purpose.

Revocation and supersession MUST remain distinguishable.

---

## 7. Reusable embedded structures

The following concepts are reusable structures rather than mandatory independent top-level objects.

### 7.1 Outcome

An `Outcome` represents the result of an Event or Interaction.

An Outcome MAY be embedded in an Event or represented by a separate record when it requires independent identity, proof, dispute, or lifecycle handling.

### 7.2 EntityReference

An `EntityReference` identifies a participant, resource, subject, account, service, device, or other entity without asserting that OLP itself resolves or authenticates that entity.

### 7.3 Party

A `Party` associates an entity reference with a role in a particular record or event.

A Party role is contextual and does not automatically imply broader organizational or legal authority.

### 7.4 Reference

A `Reference` points to another protocol or external object.

References may be content-addressed or resolver-dependent.

### 7.5 Proof

`Proof` is conceptually reusable evidence of cryptographic attribution or integrity, but proofs are deliberately **not embedded in Record identity**.

Specification 0004 defines `OLPProof` as a detached first-class artifact.

---

## 8. Derived and contextual concepts

The following terms are important to OLP but are not universal first-class record types by default:

### 8.1 Evidence

Evidence is a role that records, proofs, external resources, or relationships may play in an evaluation.

### 8.2 History

History is a selected view over evidence.

### 8.3 Provenance

Provenance is evidence about origin, custody, transformation, or derivation and may itself be represented through ordinary records and relationships.

### 8.4 Context

Context is evaluator- or domain-specific information used to interpret evidence.

### 8.5 Trust

Trust is an application decision, not a universal protocol object.

### 8.6 TrustModel

A TrustModel is an application's assumptions and decision rules.

### 8.7 Verification

Verification is a process/result concerning a defined property.

### 8.8 Status

Status is a derived evaluation over status/lifecycle evidence, not necessarily a mutable field stored on the historical target.

### 8.9 ApplicationDecision

An ApplicationDecision is a local conclusion such as accept, reject, authorize, flag, rank, or request additional evidence.

OLP core does not make such a decision universally authoritative.

---

## 9. Record identity and immutability

Every identity-bearing Record has a stable content-derived Record Identity as defined by Specification 0003.

After identity is established:

- changing `type` changes the record;
- changing identity-bearing `content` changes the record;
- changing an identity-bearing semantic binding, profile, relationship, or extension changes the record; and
- adding or removing a detached proof does **not** change the record.

Records are semantically immutable.

Applications MUST NOT silently mutate stored historical record content while retaining the old Record Identity.

---

## 10. Local metadata is not protocol history

Storage and transport systems commonly maintain metadata such as:

- database primary keys;
- ingestion timestamps;
- cache timestamps;
- source IP addresses;
- local labels;
- indexing fields;
- UI state;
- processing status; or
- filesystem names.

Such metadata is not part of a Record unless explicitly represented as identity-bearing OLP content.

A local system MUST NOT silently inject local metadata into the canonical Record Identity representation.

---

## 11. Unknown semantic types

A parser MAY preserve a structurally valid record whose semantic `type` it does not understand.

However, an implementation MUST NOT claim semantic conformance, verification, or policy satisfaction for an unknown type merely because the envelope parses.

Unknown security-critical semantics MUST fail closed according to the applicable profile.

---

## 12. Extension rules

Core field names and core semantic identifiers are reserved by OLP specifications.

Third-party extensions MUST use globally unambiguous identifiers and MUST NOT redefine the meaning of a core field or type.

Extension mechanisms should preserve forward compatibility without permitting old implementations to silently ignore security-critical semantics.

Specification 0004 defines an explicit critical-extension mechanism for proofs; later specifications define corresponding extension behavior for their own objects.

---

## 13. Actor neutrality

The same Record envelope is used whether a record concerns:

- a human;
- an organization;
- a software agent;
- a service;
- a device;
- an account;
- a document;
- a transaction; or
- another subject.

The envelope MUST NOT encode a universal hierarchy of actor trustworthiness.

---

## 14. Evidence plurality and disagreement

OLP MUST permit multiple records concerning the same event, interaction, subject, or outcome.

Conflicting records are not malformed merely because they conflict.

Dispute, correction, support, contradiction, supersession, and other relationships are represented explicitly rather than resolved by destructive overwrite.

---

## 15. Minimal object taxonomy

The Draft v0.1 taxonomy can be summarized as:

```text
Record                                  first-class immutable envelope
├── Claim                               core semantic category
├── Attestation                         core semantic category
├── Observation                         core semantic category
├── Event                               core semantic category
│   └── Interaction                     specialization
└── StatusChange                        core semantic category
    ├── Revocation                      operation / specialization
    └── Supersession                    operation / specialization

Reusable structures
├── Outcome
├── EntityReference
├── Party
├── Reference
└── Proof                               detached artifact in Spec 0004

Derived / contextual
├── Evidence
├── History
├── Provenance
├── Context
├── Trust
├── TrustModel
├── Verification
├── Status
└── ApplicationDecision
```

---

## 16. Design invariants

```text
one universal Record envelope
record identity is content-derived
records are immutable
proofs do not change record identity
local metadata is not silently identity-bearing
conflicting evidence may coexist
history is derived, not one mutable row
trust and application decisions remain outside the record primitive
```

---

## 17. Deferred representation details

This specification intentionally leaves the following to Specification 0003 and later modules:

- the exact canonical value model;
- byte-level encoding;
- Record Identity hashing and textual forms;
- concrete reference encodings;
- proof format and signature suites;
- evidence graph relationships;
- identity and authority profiles;
- lifecycle evaluation;
- bundle serialization;
- resolution/discovery;
- privacy profiles;
- conformance testing; and
- transport/API profiles.

---

**End of OLP Specification 0002 — Draft v0.1**
