# Open Layer Protocol — Terminology

**Status:** Draft v0.1  
**Milestone:** 1 — Vocabulary  
**Filename:** `specification/0001-terminology.md`

---

## 1. Purpose

This specification defines the shared vocabulary used by Open Layer Protocol (OLP).

The purpose of the terminology layer is to prevent later protocol specifications from silently collapsing concepts that OLP intentionally keeps separate.

The most important separations are:

```text
evidence      != trust
verification  != truth
identity      != trust
history       != reputation
```

Later specifications MAY refine these terms for concrete data structures, but MUST NOT redefine their core meanings incompatibly without an explicit specification-version change.

---

## 2. Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as described by RFC 2119 and RFC 8174 when they appear in all capitals.

---

## 3. Participant and Subject

### 3.1 Participant

A **Participant** is an entity that takes part in an interaction, produces or receives protocol evidence, controls a verification method, or is otherwise represented in an OLP context.

A Participant MAY be:

- a human;
- an organization;
- a software agent;
- a service;
- a device;
- an account-like entity; or
- another actor recognized by an application.

OLP does not assign protocol-level privilege based solely on participant type.

### 3.2 Subject

A **Subject** is the entity, object, event, state, record, proof, resource, or other thing that a statement is about.

A Subject need not be a Participant.

The producer of a statement and the Subject of that statement MAY be different.

---

## 4. Identifier and Reference

### 4.1 Identifier

An **Identifier** is a value used to distinguish or name something within a defined identifier system.

An identifier does not by itself establish:

- identity;
- ownership;
- authority;
- trustworthiness; or
- continued control.

### 4.2 Reference

A **Reference** is a protocol value that points to or identifies another object, resource, participant, or evidence item.

A reference MAY be:

- content-addressed;
- externally resolvable;
- locally resolvable;
- self-certifying; or
- opaque to OLP core.

Resolution success is not the same as verification.

---

## 5. Claim and Attestation

### 5.1 Claim

A **Claim** is a proposition represented as being asserted about one or more subjects.

A claim may be true, false, incomplete, mistaken, disputed, unverifiable, or context-dependent.

The existence of a claim does not imply OLP accepts it as true.

### 5.2 Attestation

An **Attestation** is a claim or set of claims intentionally attributed to a participant or verification method.

An attestation expresses attributable assertion, not protocol-level truth.

A cryptographically valid proof over an attestation can establish cryptographic attribution properties; it does not establish the factual accuracy of the attested content.

---

## 6. Evidence and Observation

### 6.1 Evidence

**Evidence** is information that an evaluator may use when deciding what to believe, trust, permit, rank, investigate, or require.

Evidence is a contextual role rather than a guarantee of correctness.

An OLP object may serve as evidence without OLP declaring it persuasive.

### 6.2 Observation

An **Observation** is a statement representing that a participant, device, service, or process observed some event, state, measurement, artifact, or condition.

An observation records the asserted observation and its provenance.

It does not guarantee sensor accuracy, honesty, completeness, or correct interpretation.

---

## 7. Event, Interaction, and Outcome

### 7.1 Event

An **Event** is a represented occurrence or state transition.

Events may concern one or more participants, resources, systems, or other subjects.

### 7.2 Interaction

An **Interaction** is an Event involving two or more participants or roles whose actions or states are meaningfully related.

Examples include a transaction, delivery, negotiation, service request, handoff, or communication exchange.

An Interaction is a specialization of Event, not a separate universal truth mechanism.

### 7.3 Outcome

An **Outcome** is a represented result associated with an Event or Interaction.

An outcome may be asserted by different participants with different perspectives.

OLP MUST permit disagreement about outcomes to remain explicit evidence rather than requiring one globally authoritative outcome.

---

## 8. Record

A **Record** is an immutable OLP protocol object that carries identity-bearing semantic content.

A record is the primary historical unit of the protocol.

Its identity is derived from its canonical identity representation as defined by Specification 0003.

After a Record Identity is established, changing identity-bearing content creates a different record.

Corrections, disputes, supersession, and status changes are represented through additional records and relationships rather than mutation of the historical record.

---

## 9. History and Provenance

### 9.1 History

**History** is an application- or context-specific view over a set of records, proofs, relationships, and other evidence associated with one or more subjects.

History is derived.

OLP does not define one universal canonical global history.

### 9.2 Provenance

**Provenance** is evidence describing the origin, production, custody, transformation, relationship, or derivation of other evidence.

Provenance may itself be represented by records and proofs and may be disputed or incomplete.

---

## 10. Context

**Context** is information relevant to interpreting evidence or applying a trust or policy decision.

Context may include:

- purpose;
- jurisdiction;
- time;
- transaction value;
- role;
- application policy;
- risk tolerance;
- evidence source;
- business domain; or
- other evaluator-specific information.

Context is not one universal protocol object unless a later specification explicitly defines a concrete context profile.

---

## 11. Trust and Trust Model

### 11.1 Trust

**Trust** is an evaluator's context-dependent willingness to rely on a participant, statement, verification method, evidence source, process, or result for some purpose.

Trust is not a protocol primitive that OLP assigns globally.

### 11.2 Trust Model

A **Trust Model** is a set of assumptions, algorithms, policies, authorities, thresholds, evidence requirements, and decision rules used to evaluate trust in a particular context.

Different trust models MAY reach different conclusions from the same OLP evidence.

This plurality is expected behavior, not protocol inconsistency.

---

## 12. Verification

**Verification** is a process that checks a defined property of evidence according to explicit rules.

Examples include:

- recomputing a content identity;
- validating a cryptographic proof;
- checking a referenced verification method;
- validating a relationship constraint;
- checking a lifecycle statement; or
- evaluating bundle integrity.

Verification MUST NOT be used as an unqualified synonym for truth or trust.

A verification result should identify what property was verified and what could not be evaluated.

---

## 13. Disclosure

**Disclosure** is the act of making selected evidence available to another party or process.

Disclosure may be complete or partial with respect to a larger evidence graph.

Failure to disclose an object does not, by itself, prove that the object does not exist.

Selective disclosure MUST NOT be confused with proof of global completeness.

---

## 14. Revocation and Supersession

### 14.1 Revocation

**Revocation** is an additive statement that a previously issued object, authority, verification method, credential, or other target is withdrawn or should no longer be relied upon according to the revocation source and applicable semantics.

Revocation does not erase the historical target and does not retroactively make a mathematically valid signature fail.

### 14.2 Supersession

**Supersession** is a relationship or status assertion that another object is intended to replace, update, or take precedence over an earlier object for some defined purpose.

Supersession does not delete or mutate the superseded object.

Revocation and supersession are not synonyms.

---

## 15. Issuer and Holder

### 15.1 Issuer

An **Issuer** is a participant or verification method represented as producing or issuing a statement, credential, record, proof, grant, status assertion, or other evidence artifact.

The label `Issuer` is role-specific and does not imply universal authority.

### 15.2 Holder

A **Holder** is a participant or system that possesses, stores, presents, or controls access to evidence.

Possession of evidence does not imply authorship, ownership of the subject, endorsement of the evidence, or authority over it.

---

## 16. Protocol

The **Open Layer Protocol** is the set of interoperable data models, canonicalization rules, cryptographic proof rules, evidence relationships, lifecycle semantics, exchange profiles, and conformance requirements defined by the numbered OLP specifications.

OLP is an evidence interoperability layer.

It is not a universal trust authority.

---

## 17. Intentionally non-core concepts

The following concepts are deliberately not defined as universal OLP core values:

### 17.1 Reputation

Applications MAY derive reputation from OLP evidence, but OLP does not define one universal reputation object or algorithm.

### 17.2 Universal Trust Score

OLP defines no universal trust score.

### 17.3 Canonical Global History

OLP defines immutable records and explicit relationships but does not assert that one globally complete history is always knowable or desirable.

### 17.4 Universal Authority

OLP defines no universal authority that automatically decides identity, truth, legality, status, or trust for all participants.

---

## 18. Foundational invariants

The terminology defined here establishes the following invariants for later specifications:

```text
evidence          != trust
verification      != truth
identifier        != identity proof
key control       != identity
identity          != trust
identity          != authority
history           != reputation
revocation        != deletion
supersession      != mutation
disclosure subset != proof of nonexistence
```

Later OLP specifications MUST preserve these distinctions unless an explicit incompatible protocol version states otherwise.

---

**End of OLP Specification 0001 — Draft v0.1**
