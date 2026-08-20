# OLP Specification 0013 — Versioning, Registries, and the Draft v0.2 Interoperable Core

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 18 — Draft v0.2 Integration Pass  
**Filename:** `specification/0013-versioning-registries-and-core-profile.md`

---

## 1. Abstract

This specification defines cross-cutting versioning, registry, extension-governance, reason-code, capability, migration, and interoperability-profile rules for Open Layer Protocol (OLP).

Draft v0.2 is an integration release, not a new wire-format generation. Milestones 13–17 produced executable evidence that the deterministic v1 core defined by Specifications 0003, 0004, and the executable subset of 0005 interoperates across independent Python and Rust implementations without changing the published Record Identity, Proof Input, proof, Proof Identity, or EvidenceRef encodings.

This specification therefore separates repository release labels from protocol object and encoding versions, defines stability rules for compact OLP identifiers and third-party extensions, governs reason-code semantics, and identifies the smallest currently demonstrated interoperable core.

It does not create a central OLP registry service.

---

## 2. Version domains

OLP has independent version domains. Implementations MUST NOT treat them as interchangeable.

### 2.1 Specification-set release

A specification-set release is a repository-level snapshot such as `Draft v0.1` or `Draft v0.2`. It groups documents, vectors, conformance material, and project status.

A set-release label does not itself appear in Record Identity bytes, ProofInputV1, Proof Identity, EvidenceRefV1, or another identity-bearing object unless a specific profile explicitly places it there.

### 2.2 Document revision

An individual specification has its own document revision. A document revision may change independently from the set-release label.

### 2.3 Protocol object version

A protocol object version is authenticated or interpreted as part of a protocol object, for example Record `envelope_version = 1`, `OLPProof version = 1`, or `RelationshipStatementV1`.

Changing the set-release label MUST NOT silently change the meaning of an existing object version.

### 2.4 Canonical encoding version

Canonical encoding versions identify deterministic bytes used for identity or cryptographic processing, including `OLP-CIE-1`, `ProofInputV1`, Proof Identity v1, `EvidenceRefV1`, and `OJVE-1`.

If the same previously conforming abstract input would produce different canonical bytes after a change, the applicable encoding version MUST change unless the previous behavior was unambiguously invalid and the correction is explicitly recorded as an erratum.

### 2.5 Cryptosuite version

Changing a signing input, prehashing rule, key interpretation, signature primitive, domain separation, or proof-byte interpretation that changes cryptographic behavior MUST use a new cryptosuite identifier.

### 2.6 Capability/profile version

A capability identifier names concrete interoperable behavior. An implementation MUST NOT claim an existing capability identifier while implementing an incompatible semantic variant.

---

## 3. Draft v0.2 compatibility statement

Draft v0.2 preserves the independently verified v1 deterministic core from Draft v0.1.

The following remain unchanged:

- Record envelope version `1`;
- `OLP-CIE-1`;
- SHA-256 Record Identity and commitment baseline;
- `OLPProof` version `1`;
- `ProofInputV1`;
- `eddsa-ed25519-v1`;
- Proof Identity v1;
- `EvidenceRefV1`;
- `RelationshipStatementV1`; and
- the current `core-v1` capability identifiers.

A conforming implementation MUST NOT rewrite, re-sign, or re-identify an otherwise conforming Draft v0.1 v1-core object solely because the specification-set release label changes to Draft v0.2.

Historical evidence remains historical evidence. Later policy, deprecation, status, or security decisions MUST NOT silently rewrite historical identity bytes or cryptographic facts.

---

## 4. Change classification

Every normative protocol change SHOULD be classified before publication.

### 4.1 Editorial

Editorial changes do not alter conforming behavior and do not require protocol-version changes.

### 4.2 Clarifying

A clarifying change makes an already intended rule explicit without making two previously conforming implementations disagree. Clarifications MAY retain existing object/capability versions when they preserve intended interoperable meaning. The change MUST be recorded.

### 4.3 Additive compatible

An additive compatible change introduces a new optional capability, profile, extension, or registry entry without changing existing canonical bytes or semantics. A new capability identifier SHOULD be used when independently testable behavior is added.

### 4.4 Breaking

A breaking change alters interpretation or deterministic output of previously conforming input. Examples include changing Record Identity bytes, changing ProofInputV1 bytes, changing the meaning of an existing compact proof purpose or relationship type, or changing a cryptosuite's signing input.

A breaking change MUST use an appropriate new object, encoding, suite, capability, or profile version.

---

## 5. Identifier governance

### 5.1 Compact OLP identifiers are specification-controlled

Short identifiers whose interpretation depends on the OLP namespace are controlled by numbered OLP specifications. Third parties MUST NOT mint new compact identifiers and assume they are globally understood by OLP.

### 5.2 Third-party extensions use globally unambiguous identifiers

Unless a numbered specification defines another collision-resistant namespace, third-party semantic identifiers MUST use absolute URIs.

Authenticated identifiers are exact strings. Processors MUST NOT silently trim, lowercase, percent-decode/re-encode, Unicode-normalize, follow redirects, resolve aliases, or otherwise rewrite an authenticated identifier before comparison.

### 5.3 URI syntax is not network permission

An absolute URI is identifier syntax. Its presence MUST NOT by itself authorize network access. Resolution remains explicit and policy-controlled under Specification 0009.

### 5.4 No registration by observation

Receiving an unknown extension identifier does not register it. Local registries MAY exist, but local registration MUST NOT be represented as universal OLP registration.

---

## 6. Core registry entries in Draft v0.2

### 6.1 Mandatory cryptosuite

`eddsa-ed25519-v1`

### 6.2 Core proof purposes

`assertion`, `acknowledgement`, `witness`, `authorization`

Proof purpose authenticates intent/context; it does not by itself establish authority sufficiency.

### 6.3 Core evidence relationship types

`references`, `derivesFrom`, `supersedes`, `corrects`, `disputes`, `anchors`, `countersigns`

### 6.4 Commitment baseline

SHA-256 remains the mandatory interoperable commitment baseline. Policy acceptance of an algorithm is separate from technical support and mathematical verification.

---

## 7. Extension governance

Unknown noncritical semantics MUST be preserved where the applicable object model requires preservation, and processors MUST NOT falsely report that they understand their meaning.

Unknown critical semantics MUST fail closed with an unsupported state.

If criticality participates in canonical or proof-authenticated input, a transport or resolver MUST NOT add or remove critical markers as a presentation convenience.

A new extension definition MUST NOT retroactively assign a conflicting meaning to an identifier already used by another specification or owner.

---

## 8. Reason-code governance

Reason codes communicate machine-readable processing facts; they are not trust scores.

New OLP reason codes SHOULD use uppercase ASCII snake case. Published reason codes MUST NOT be silently repurposed to mean a materially different condition.

The following distinctions are cross-specification invariants:

`malformed != unsupported != unavailable != invalid != policy-rejected != resource-limited != absent`

A stage that was not evaluated because a prerequisite was unavailable MUST NOT be reported as invalid.

Reasons ending in `REJECTED_BY_POLICY` record local policy rejection and MUST NOT rewrite independently computable cryptographic facts.

Resource-limit outcomes MUST be explicit. An implementation MUST NOT silently truncate identity-bearing values, return a partial graph as complete, convert resource exhaustion into signature invalidity, or claim absence merely because a configured traversal limit was reached.

---

## 9. Capability governance

The independently verified Draft v0.2 core contains:

- `olp.record-identity.v1`
- `olp.record-commitment.sha256.v1`
- `olp.proof-input.v1`
- `olp.proof.eddsa-ed25519.v1`
- `olp.proof-verification.v1`
- `olp.proof-identity.v1`
- `olp.evidence-ref.v1`
- `olp.evidence-relationship.v1`

These are grouped by the repository `core-v1` profile.

Once a capability has public cross-implementation vectors, its identifier MUST NOT be reused for incompatible behavior. Supporting one capability does not imply support for all OLP specifications.

---

## 10. Draft v0.2 interoperable core

A capability belongs in the independently verified core only when the repository demonstrates implementation-neutral vectors, a reference implementation, an independent implementation, deterministic agreement where applicable, appropriate malformed/negative/unsupported coverage, and relevant security regressions.

At the Milestone 17 acceptance point the project demonstrated:

- Python repository tests: PASS;
- Python `core-v1`: 62/62 PASS;
- Rust crate tests/build: PASS;
- Rust `core-v1`: 62/62 PASS; and
- Python↔Rust interoperability: 9/9 PASS.

These results are evidence of interoperability, not a claim that OLP is generally secure or production-ready.

---

## 11. Higher-layer draft status

Specifications 0006–0010 remain part of Draft v0.2 as design specifications, but their major processing models are not yet part of the independently verified core.

Deferred executable attack surfaces include identity/authority ecosystem parsing and delegation evaluation, lifecycle/status conflict processing, bundle ingestion and amplification limits, resolver SSRF/redirect/address policy, and disclosure/privacy correlation behavior.

A specification being included in Draft v0.2 MUST NOT be represented as independent implementation evidence for behavior that has not been implemented and tested.

---

## 12. Promotion of additional capabilities

Before a capability from Specifications 0006–0010 is added to the independently verified core, it SHOULD have a precise capability identifier, positive/malformed/unsupported/negative cases as applicable, resource-limit coverage, at least one security-focused case, and cross-implementation comparison.

Capabilities involving live network or time dependencies MUST isolate those dependencies through fixed snapshots, explicit resolver inputs, or other reproducible fixtures.

---

## 13. Vector governance

A published normative vector for a versioned deterministic construction MUST NOT be silently changed to produce different expected bytes. Corrections MUST be recorded explicitly as errata and SHOULD use a new vector identifier where ambiguity would otherwise result.

Published test keys are public test material and MUST NOT be reused for production authority or confidentiality.

Draft v0.2 promotes independently reproduced Specification 0005 vectors for Proof Identity v1 and `EvidenceRefV1` alongside the existing 0003 and 0004 vectors.

---

## 14. Migration from Draft v0.1

For the independently verified v1 core, migration is intentionally minimal.

Producers do not need to regenerate conforming Draft v0.1 records or proofs solely for Draft v0.2.

Verifiers MUST preserve the existing v1 deterministic bytes and SHOULD adopt the stricter parser, resource-boundary, extension-interpretation, and policy-separation requirements integrated through Milestones 16 and 17.

Stored immutable evidence SHOULD remain stored under its existing Record Identity or Proof Identity.

Implementations claiming the Draft v0.2 interoperable core SHOULD run the current `core-v1` corpus and identify the exact corpus/repository revision used.

---

## 15. Security rules for version/registry processing

Implementations MUST NOT silently downgrade required capabilities, treat an unknown version as the nearest known version, reinterpret extension URIs as compact core identifiers, normalize authenticated identifiers before equality comparison, infer network permission from URI syntax, convert local policy into cryptographic fact, treat resource-limit truncation as completeness, or ignore unsupported critical semantics.

---

## 16. Conformance requirements

An implementation claiming the Draft v0.2 interoperable core MUST:

1. identify the exact core capability/profile revision used;
2. preserve all existing v1 deterministic encodings;
3. preserve malformed/unsupported/unavailable/invalid/policy/resource distinctions required by applicable specifications;
4. fail closed on unknown critical semantics;
5. avoid silent downgrade;
6. use extension identifiers according to this specification; and
7. not claim unimplemented higher-layer capabilities by implication.

---

## 17. Summary

Draft v0.2 freezes the implementation lesson that protocol release numbers, identity bytes, cryptographic truth, local policy, and implementation capability are different things and must remain different things.

The independently verified core is deliberately small. Its strength comes from reproducible bytes, independent implementations, explicit unsupported states, and executable security regressions rather than from claiming that the entire future OLP stack is already production-ready.
