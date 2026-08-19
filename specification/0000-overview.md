# OLP Specification 0000 — Overview and Specification Index

**Status:** Draft  
**Version:** v0.1  
**Role:** Non-normative overview and specification index  
**Filename:** `specification/0000-overview.md`

---

## 1. Purpose

This document is the entry point to the Open Layer Protocol (OLP) specification set.

It explains:

- what OLP is intended to achieve;
- the architectural model shared across the specification set;
- how the individual specifications relate to one another;
- which documents define normative protocol behavior;
- the current maturity of the project; and
- the intended path from Draft v0.1 specifications to interoperable implementations.

This document is **non-normative**.

If this overview conflicts with a numbered normative specification, the normative specification controls.

---

## 2. Project Thesis

Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

OLP provides common structures and processing rules for exchanging independently verifiable evidence between humans, organizations, software agents, services, devices, marketplaces, institutions, and other participants.

OLP does not attempt to define one universal answer to the question:

> Who should be trusted?

Instead, it aims to make the evidence used to answer that question portable, attributable, inspectable, and independently verifiable.

Applications remain free to apply different policies, algorithms, risk models, jurisdictional rules, and contextual interpretations to the same evidence.

The protocol therefore separates:

```text
facts / claims / events
        |
        v
immutable records
        |
        v
cryptographic proofs
        |
        v
evidence relationships and provenance
        |
        v
identity / authority / lifecycle evidence
        |
        v
resolution / disclosure / exchange
        |
        v
application-specific interpretation and policy
```

OLP standardizes the evidence substrate.

It does not standardize universal trust judgments.

---

## 3. Core Architectural Principles

The specification set is built around the following principles.

### 3.1 Evidence over reputation

OLP transports verifiable evidence and provenance rather than defining a universal reputation score.

### 3.2 Facts over judgments

The protocol distinguishes what was asserted or observed from an application's judgment about whether it should be believed or acted upon.

### 3.3 Participant-owned history

Evidence should remain portable across platforms and should not depend on one intermediary continuing to operate.

### 3.4 Contextual trust

The same evidence may legitimately lead to different decisions in different contexts.

### 3.5 No universal trust score

OLP does not define a global participant score, ranking, or binary trusted/untrusted status.

### 3.6 Algorithm plurality

Cryptographic, policy, ranking, and trust-evaluation algorithms may evolve independently where interoperability requirements permit.

### 3.7 Privacy by architecture

Data minimization, selective disclosure, explicit resolution, and avoidance of unnecessary global identifiers are architectural concerns rather than optional presentation features.

### 3.8 Identity is not trust

An identifier, identity claim, verification method, role, authority grant, and trust decision are distinct concepts.

### 3.9 Actor neutrality

Humans, organizations, software agents, services, and other actors are not assigned protocol-level privilege merely because of actor type.

### 3.10 No silent history rewriting

Corrections, disputes, supersession, revocation, compromise, and lifecycle changes are represented by additive evidence rather than destructive mutation of historical objects.

### 3.11 Blockchain neutrality

A blockchain may be used as evidence infrastructure, but no blockchain, token, cryptocurrency, or distributed ledger is required by OLP.

### 3.12 Jurisdiction neutrality

OLP can carry evidence relevant to legal or regulatory decisions without defining one global jurisdiction or legal interpretation.

### 3.13 Interoperability before invention

Where an existing open standard already solves a problem adequately, OLP should interoperate with it rather than create a competing mechanism without strong reason.

### 3.14 Independent verifiability

Core evidence processing should be reproducible by independent implementations and should not require contacting a central OLP authority.

---

## 4. Fundamental Separations

The protocol deliberately preserves the following distinctions:

```text
record identity             != transport serialization
proof validity              != truth
key control                 != identity
identity                    != authority
proof purpose               != authority sufficiency
authority grant             != final authorization decision
status evidence             != cryptographic validity
revocation                  != historical mutation
resolution success          != verification
bundle integrity            != bundle completeness
bundle completeness         != policy sufficiency
selective disclosure        != proof of nonexistence
conformance                 != trustworthiness
transport security          != OLP object proof validity
```

These separations are foundational to the design.

---

## 5. Specification Structure

The current Draft v0.1 specification set is organized as follows.

| Spec | Title | Role | Status |
|---|---|---|---|
| 0000 | Overview and Specification Index | Non-normative entry point and roadmap | Draft v0.1 |
| 0001 | Terminology | Shared vocabulary and conceptual definitions | Draft v0.1 |
| 0002 | Protocol Objects | Foundational object model | Draft v0.1 |
| 0003 | Record Representation | Immutable records, canonical identity representation, Record Identity | Draft v0.1 |
| 0004 | Proofs and Verification | Detached proofs, ProofInputV1, Ed25519 baseline, verification semantics | Draft v0.1 |
| 0005 | Evidence Relationships and Graphs | Proof Identity, EvidenceRef, relationship records, evidence graphs | Draft v0.1 |
| 0006 | Identity and Authority Evidence | Principal identifiers, bindings, roles, grants, delegation | Draft v0.1 |
| 0007 | Status, Revocation, and Lifecycle Evidence | Additive lifecycle evidence and historical/current-status evaluation | Draft v0.1 |
| 0008 | Evidence Exchange and Bundles | Portable evidence packages, manifests, offline/self-contained bundles | Draft v0.1 |
| 0009 | Resolution and Discovery Profiles | Explicit, provenance-visible resolution and discovery | Draft v0.1 |
| 0010 | Privacy, Selective Disclosure, and Data Minimization | Whole-object and graph-subset disclosure; privacy rules | Draft v0.1 |
| 0011 | Conformance and Interoperability | Capability-scoped conformance and cross-implementation testing | Draft v0.1 |
| 0012 | Transport and API Profiles | JSON/CBOR transport, streaming, and HTTP API profiles | Draft v0.1 |

The numbered specifications are intended to be read approximately in order because later layers build on earlier invariants.

---

## 6. Specification Dependency Map

```text
0001 Terminology
       |
       v
0002 Protocol Objects
       |
       v
0003 Record Representation
       |
       v
0004 Proofs and Verification
       |
       v
0005 Evidence Relationships and Graphs
       |
       +--------------------+
       |                    |
       v                    |
0006 Identity & Authority   |
       |                    |
       v                    |
0007 Status & Lifecycle     |
       |                    |
       +---------+----------+
                 |
                 v
0008 Evidence Exchange & Bundles
                 |
       +---------+----------+
       |         |          |
       v         v          v
0009 Resolution 0010 Privacy
       \         /          |
        \       /           |
         +-----+------------+
               |
               v
0011 Conformance & Interoperability
               |
               v
0012 Transport & API Profiles
```

This diagram is explanatory rather than a substitute for each specification's normative dependency declarations.

---

## 7. Architectural Layers

### 7.1 Foundation — Specifications 0001–0003

The foundation defines common terminology, protocol objects, immutable record representation, deterministic identity processing, and Record Identity.

At the end of this layer OLP can answer:

> What exact immutable record are we talking about?

### 7.2 Cryptographic verification — Specification 0004

The proof layer defines detached proofs, deterministic Proof Input construction, record commitments, the mandatory Ed25519 verification baseline, proof purposes, critical extensions, verification-method resolution boundaries, and structured verification results.

At the end of this layer OLP can answer:

> Does this cryptographic proof bind this verification method to exactly this record under the authenticated purpose and context?

It does not answer whether the record is true or trustworthy.

### 7.3 Evidence composition — Specification 0005

The graph layer defines stable Proof Identity, typed evidence references, immutable relationship records, countersignature relationships, anchoring relationships, graph traversal, partial graphs, disputes, corrections, and supersession.

At the end of this layer OLP can represent:

> How are these independent pieces of evidence explicitly related?

### 7.4 Identity and authority — Specification 0006

This layer represents evidence about principals, verification-method control, same-subject claims, roles, membership, authority grants, delegation, constraints, and authority status without turning OLP into an identity provider or authorization server.

### 7.5 Lifecycle — Specification 0007

This layer represents suspension, resumption, retirement, revocation, compromise, deprecation, and related lifecycle events as additive immutable evidence.

Historical cryptographic validity and current policy reliance remain separate dimensions.

### 7.6 Exchange — Specification 0008

Evidence bundles make finite evidence selections portable while preserving the identity and meaning of the objects they contain.

Self-contained profiles support offline verification without making a bundle a universal completeness claim.

### 7.7 Resolution — Specification 0009

Resolution is explicit, replaceable, provenance-visible, and policy-controlled.

Network activity is not hidden inside cryptographic verification.

### 7.8 Privacy — Specification 0010

Native OLP v1 selective disclosure operates primarily by selecting complete immutable objects and graph branches.

Signed/content-addressed records are not silently field-redacted.

External cryptographic selective-disclosure systems retain their native semantics.

### 7.9 Conformance — Specification 0011

OLP conformance is modular and capability-scoped.

Byte-level canonical behavior must be reproducible across independent implementations where a specification defines deterministic encodings.

### 7.10 Transport — Specification 0012

Transport profiles move abstract OLP objects through JSON, CBOR, streams, and HTTP without allowing transport representation to redefine evidence identity.

---

## 8. Core Evidence Model

A simplified OLP evidence graph can be visualized as:

```text
                         Record R
                            ^
                            |
                 +----------+----------+
                 |                     |
              Proof A               Proof B
                 ^                     ^
                 |                     |
         Relationship Record      Lifecycle Record
                 ^                     ^
                  \                   /
                   \                 /
                    +---------------+
                            |
                     Evidence Bundle
                            |
                explicit resolution resources
                            |
                   verifier / policy engine
```

Every arrow that carries evidentiary meaning must itself be represented through defined OLP semantics rather than inferred merely from storage position, array order, or transport packaging.

---

## 9. What OLP Does Not Define

OLP intentionally does not define:

- a universal reputation score;
- a universal trust algorithm;
- a global identity provider;
- a global certificate authority;
- a global authorization server;
- a global revocation authority;
- a global clock;
- a mandatory blockchain;
- a cryptocurrency or token;
- a payment system;
- a marketplace;
- a universal legal interpretation;
- a universal evidence-weighting algorithm;
- a universal graph-ranking algorithm;
- a global resolver;
- a global object registry;
- a central OLP verification service; or
- a requirement that one organization mediate OLP interactions.

Applications and profiles may use such systems where appropriate, but they are not intrinsic protocol authorities.

---

## 10. Current Project Status

The protocol is **experimental and pre-0.1**.

Specifications 0001 through 0012 currently form the Draft v0.1 semantic and exchange stack.

Draft v0.1 is intended to be implementation-tested rather than treated as stable production standard text.

The next project phase is reference implementation and executable conformance work.

The purpose of that phase is to find:

- ambiguous normative language;
- cross-specification contradictions;
- canonicalization disagreements;
- byte-level interoperability failures;
- incomplete error semantics;
- unsafe parser behavior;
- resolver and network-boundary defects; and
- implementation assumptions not captured by the specifications.

Discovered defects should be corrected in the specifications rather than hidden solely inside the reference implementation.

---

## 11. Implementation Roadmap

### Phase II — Reference Implementation Core

The initial implementation should prioritize the deterministic core:

```text
Record
  -> canonical identity representation
  -> Record Identity

Record + proof configuration
  -> ProofInputV1
  -> deterministic CBOR
  -> Ed25519 proof creation / verification
  -> structured VerificationResult
```

The first executable vertical slice should therefore concentrate on Specifications 0003 and 0004.

### Executable conformance

Specification 0011 should then be turned into a versioned test corpus containing:

- positive vectors;
- negative vectors;
- malformed inputs;
- unsupported-version cases;
- critical-extension cases;
- exact canonical-byte vectors;
- security-boundary tests; and
- cross-implementation producer/verifier tests.

### Independent implementation

At least one implementation independent from the reference codebase should reproduce canonical bytes, identities, proof verification, and structured results before the protocol is considered interoperable.

### Security review

The implementation should be attacked with malformed encodings, substitution attempts, downgrade attempts, replay cases, backdating, resolver abuse, SSRF, graph amplification, resource exhaustion, bundle bombs, disclosure ambiguity, and status-conflict cases.

### Draft v0.2

Implementation and security findings should feed a coordinated specification integration pass producing Draft v0.2.

---

## 12. Promotion Toward v1.0

Before a stable OLP v1.0 specification set, the project should require at minimum:

1. frozen core normative data models;
2. reproducible canonical test vectors;
3. at least two independent interoperable implementations of the core;
4. cross-language proof production and verification;
5. comprehensive negative and malformed-input tests;
6. no known unresolved contradictions in core specifications;
7. stable extension and registry governance rules;
8. a public executable conformance corpus;
9. security review of cryptographic and network boundaries; and
10. documented migration/versioning rules.

Specification 0011 contains the normative conformance framework and more detailed promotion criteria.

---

## 13. Reading Guide

For a new implementer:

1. Read `0000-overview.md` for architecture and scope.
2. Read `0001-terminology.md` and `0002-protocol-objects.md` for foundational vocabulary and objects.
3. Implement `0003-record-representation.md` first.
4. Implement `0004-proofs-and-verification.md` second.
5. Add graph semantics from `0005-evidence-relationships.md`.
6. Add identity/authority and lifecycle evaluation only if required by the implementation's declared capabilities.
7. Add bundle and resolution support for portable/offline processing.
8. Apply privacy requirements before exposing exchange interfaces.
9. Validate behavior against `0011-conformance-and-interoperability.md`.
10. Implement transport/API profiles from `0012-transport-and-api-profiles.md` last.

For reviewers interested primarily in OLP's philosophy and boundaries, this overview plus `PRINCIPLES.md` and the Core Invariants sections of the numbered specifications provide the shortest path through the design.

---

## 14. Versioning of This Overview

Because Specification 0000 is non-normative, updates to its explanatory diagrams, roadmap, or index do not by themselves change OLP protocol semantics.

If a normative rule changes, the applicable numbered normative specification must be revised and versioned accordingly.

This overview should be updated whenever:

- a specification is added, removed, renamed, or materially changes scope;
- a specification changes maturity status;
- the implementation phase changes materially; or
- the recommended reading/dependency order changes.

---

## 15. Summary

Open Layer Protocol is designed around a simple proposition:

> **Make evidence portable and independently verifiable; leave trust judgments plural, contextual, and outside central ownership.**

The current Draft v0.1 specification stack establishes:

```text
shared vocabulary
      -> protocol objects
      -> immutable records
      -> cryptographic proofs
      -> evidence graphs
      -> identity / authority evidence
      -> lifecycle evidence
      -> portable bundles
      -> explicit resolution
      -> privacy-aware disclosure
      -> conformance
      -> transport/API profiles
```

The next phase is not another major semantic layer.

It is implementation, interoperability, testing, and refinement.

---

## Repository baseline note

The repository baseline accompanying this overview includes project-level `PRINCIPLES.md`, `ROADMAP.md`, `CHANGELOG.md`, and `SECURITY.md` documents in addition to the numbered specification set.

These project documents do not override normative specification requirements.

The next development phase is the reference implementation and executable conformance work described in `ROADMAP.md`.

---

**End of OLP Specification 0000 — Overview and Specification Index — Draft v0.1**
