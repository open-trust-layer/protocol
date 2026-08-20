# OLP Specification 0000 — Overview and Specification Index

**Status:** Draft  
**Specification-set release:** Draft v0.2  
**Role:** Non-normative overview and specification index  
**Filename:** `specification/0000-overview.md`

---

## 1. Purpose

This document is the non-normative entry point to the Open Layer Protocol (OLP) specification set.

Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

OLP standardizes portable evidence and provenance. It does not standardize universal trust judgments.

If this overview conflicts with a numbered normative specification, the numbered specification controls.

---

## 2. Fundamental separations

OLP preserves these distinctions:

```text
record identity             != transport serialization
proof validity              != truth
key control                 != identity
identity                    != authority
proof purpose               != authority sufficiency
authority grant             != authorization decision
status evidence             != cryptographic validity
revocation                  != historical mutation
resolution success          != verification
bundle integrity            != bundle completeness
bundle completeness         != policy sufficiency
selective disclosure        != proof of nonexistence
conformance                 != trustworthiness
transport security          != OLP object proof validity
```

---

## 3. Draft v0.2 integration result

Draft v0.2 is a coordinated specification-set release produced after:

- Milestone 13 — Python reference implementation;
- Milestone 14 — executable conformance harness;
- Milestone 15 — independent Rust implementation;
- Milestone 16 — executable Evidence Graph Core; and
- Milestone 17 — adversarial/security review.

The integration pass found no need to change the existing v1 deterministic core bytes.

Therefore Draft v0.2 preserves Record envelope version `1`, `OLP-CIE-1`, SHA-256 Record Identity/commitment baseline, `OLPProof` version `1`, `ProofInputV1`, `eddsa-ed25519-v1`, Proof Identity v1, `EvidenceRefV1`, and `RelationshipStatementV1`.

Specification 0013 defines how set releases, document revisions, object versions, canonical encodings, cryptosuites, capabilities, registries, reason codes, and migration rules remain separate.

---

## 4. Specification index

| Spec | Title | Draft v0.2 role |
|---|---|---|
| 0000 | Overview and Specification Index | Non-normative entry point |
| 0001 | Terminology | Shared vocabulary |
| 0002 | Protocol Objects | Foundational object model |
| 0003 | Record Representation | Independently verified core |
| 0004 | Proofs and Verification | Independently verified core |
| 0005 | Evidence Relationships and Graphs | Independently verified executable subset |
| 0006 | Identity and Authority Evidence | Draft design; not yet in verified core |
| 0007 | Status, Revocation, and Lifecycle Evidence | Draft design; not yet in verified core |
| 0008 | Evidence Exchange and Bundles | Draft design; not yet in verified core |
| 0009 | Resolution and Discovery Profiles | Draft design; not yet in verified core |
| 0010 | Privacy, Selective Disclosure, and Data Minimization | Draft design; not yet in verified core |
| 0011 | Conformance and Interoperability | Executable framework |
| 0012 | Transport and API Profiles | Transport/API design plus hardened JSON boundary |
| 0013 | Versioning, Registries, and Draft v0.2 Interoperable Core | Cross-cutting governance |

The individual numbered specifications retain independent document revisions. Draft v0.2 identifies the set release.

---

## 5. Dependency map

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
       \         /
        \       /
         +-----+
            |
            v
0011 Conformance & Interoperability
            |
            v
0012 Transport & API Profiles

0013 Versioning / Registries / Core Profile
     governs cross-cutting release, identifier,
     capability, reason-code, and migration rules.
```

---

## 6. Independently verified Draft v0.2 core

The current repository `core-v1` profile contains:

```text
olp.record-identity.v1
olp.record-commitment.sha256.v1
olp.proof-input.v1
olp.proof.eddsa-ed25519.v1
olp.proof-verification.v1
olp.proof-identity.v1
olp.evidence-ref.v1
olp.evidence-relationship.v1
```

Accepted Milestone 17 evidence:

```text
Python core-v1                        62 / 62 PASS
Rust core-v1                          62 / 62 PASS
Python <-> Rust interoperability       9 / 9 PASS
Python CI                              3.11-3.14 PASS
```

This is the smallest currently demonstrated interoperable OLP core. It is not a claim that OLP is production-ready or that every higher-layer specification has two independent implementations.

---

## 7. Higher-layer status

Specifications 0006–0010 remain part of Draft v0.2 because their conceptual boundaries are important to the architecture, but they are not yet part of the independently verified core.

Executable work remains necessary for identity/authority ecosystem parsing and delegation evaluation; lifecycle/status collection and conflict evaluation; bundle ingestion and amplification limits; resolver SSRF, redirect, recursion, and private-address policy; and disclosure planning/privacy correlation behavior.

A specification being present in the Draft v0.2 set MUST NOT be interpreted as independent implementation evidence for behavior that has not yet been executed and tested.

---

## 8. Security lessons integrated

Milestone 17 fed these lessons back into the specification set:

- duplicate JSON names are rejected recursively;
- authenticated URI identifiers are exact strings and malformed syntax is rejected;
- parser/resource limits exist before unsafe recursive materialization;
- technical algorithm support and local policy acceptance are separate;
- cryptographic facts are not rewritten by local policy;
- graph convergence is not a cycle;
- graph traversal limits report incompleteness, not absence;
- unknown noncritical semantics remain visible as uninterpreted where applicable;
- unknown critical semantics fail closed; and
- cross-language disagreement is treated as a protocol/conformance defect.

---

## 9. Vector status

Draft v0.2 retains the existing Specification 0003 and 0004 normative-construction vectors unchanged.

Milestone 18 additionally promotes independently reproduced Specification 0005 vectors for Proof Identity v1 and `EvidenceRefV1` RecordRef/ProofRef encoding.

Normative vectors are append-only within a version except for explicitly recorded errata.

---

## 10. Migration from Draft v0.1

For the independently verified v1 core, no identity-bearing migration is required solely because the set release changes from Draft v0.1 to Draft v0.2.

Existing conforming records and proofs are not rewritten. Deployments upgrade parser/security behavior, policy/result separation, conformance corpus revision, extension/registry behavior, and release/version governance.

Historical evidence remains historical evidence.

---

## 11. Reading guide

For implementers:

1. Read this overview.
2. Read Specifications 0001 and 0002.
3. Implement 0003.
4. Implement 0004.
5. Add the executable 0005 evidence primitives.
6. Read 0013 before making versioning, extension, registry, or compatibility claims.
7. Validate against 0011 and the repository conformance corpus.
8. Add 0006–0010 capabilities only when needed and test them explicitly.
9. Apply 0012 transport profiles last.

For architectural philosophy, also read `PRINCIPLES.md`.

---

## 12. Promotion toward a stable release

Draft v0.2 is suitable for wider technical review, but it is not OLP v1.0.

Before a stable release, the project should require frozen stable-core models, reproducible vectors, independent interoperable implementations, comprehensive malformed/negative/policy/resource testing, no unresolved stable-core contradictions, stable registry procedures, a versioned public conformance corpus, security review of all included boundaries, and documented migration/deprecation rules.

---

## 13. Summary

> **Make evidence portable and independently verifiable; leave trust judgments plural, contextual, and outside central ownership.**

Draft v0.2 records a major transition: OLP is no longer only a prose design. A small deterministic core has been implemented independently, tested across languages, attacked adversarially, and integrated back into the specification set.

The next work should expand executable evidence only where it materially improves interoperability or reduces risk.
