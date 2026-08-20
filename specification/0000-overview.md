# OLP Specification 0000 — Overview and Specification Index

**Status:** Draft  
**Specification-set release:** Draft v0.3  
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
corpus commitment           != conformance result
conformance result          != security certification
```

---

## 3. Draft v0.3 integration result

Draft v0.3 is a coordinated integration and conformance-freeze release produced after the executable work from Milestones 13–24.

No new wire-format generation is introduced solely by this set release. The accepted v1 deterministic constructions remain unchanged, including Record envelope version `1`, `OLP-CIE-1`, SHA-256 Record Identity/commitment baseline, `OLPProof` version `1`, `ProofInputV1`, `eddsa-ed25519-v1`, Proof Identity v1, `EvidenceRefV1`, and accepted v1 capability semantics.

Specification 0013 continues to define general version-domain, registry, extension, reason-code, migration, and capability-governance rules.

Specification 0014 defines Draft v0.3 release profiles and deterministic conformance-suite commitments.

---

## 4. Specification index

| Spec | Title | Draft v0.3 role |
|---|---|---|
| 0000 | Overview and Specification Index | Non-normative entry point |
| 0001 | Terminology | Shared vocabulary |
| 0002 | Protocol Objects | Foundational object model |
| 0003 | Record Representation | Independently verified core |
| 0004 | Proofs and Verification | Independently verified core |
| 0005 | Evidence Relationships and Graphs | Independently verified executable subset |
| 0006 | Identity and Authority Evidence | Executable `identity-authority-lifecycle-v1` subset |
| 0007 | Status, Revocation, and Lifecycle Evidence | Executable `identity-authority-lifecycle-v1` subset |
| 0008 | Evidence Exchange and Bundles | Executable `bundle-v1` subset |
| 0009 | Resolution and Discovery Profiles | Executable `resolution-v1` subset |
| 0010 | Privacy, Selective Disclosure, and Data Minimization | Executable `privacy-disclosure-v1` subset |
| 0011 | Conformance and Interoperability | Executable framework |
| 0012 | Transport and API Profiles | Executable `transport-encoding-v1` and `streaming-http-v1` subsets |
| 0013 | Versioning, Registries, and Draft v0.2 Interoperable Core | General cross-cutting governance baseline |
| 0014 | Release Profiles and Conformance Suite Commitments | Draft v0.3 aggregate profile and corpus commitment |

The individual numbered specifications retain independent document revisions. Draft v0.3 identifies the set release.

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
            |
            v
0014 Release Profiles / Corpus Commitment

0013 Versioning / Registries / Core Profile
     governs cross-cutting release, identifier,
     capability, reason-code, and migration rules.
```

---

## 6. Frozen deterministic core

The `core-v1` profile remains the smallest frozen deterministic OLP core:

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

It remains 62/62 in Python and the independent Rust implementation.

Draft v0.3 does not redefine `core-v1`.

---

## 7. Draft v0.3 aggregate interoperability profile

Draft v0.3 additionally defines:

```text
draft-v0.3-interoperable-v1
```

It contains 15 accepted executable capabilities and selects exactly 180 existing conformance cases spanning the deterministic core plus bundles, resolution, identity/authority/lifecycle, privacy/disclosure, transport encoding, streaming, and modeled HTTP exchange semantics.

Acceptance evidence:

```text
Python 3.11 aggregate profile  180 / 180 PASS
Python 3.12 aggregate profile  180 / 180 PASS
Python 3.13 aggregate profile  180 / 180 PASS
Python 3.14 aggregate profile  180 / 180 PASS
Rust 1.85 aggregate profile    180 / 180 PASS
Python <-> Rust interop         PASS
```

The exact corpus commitment is:

```text
OLP-CONFORMANCE-SUITE-COMMITMENT-V1
SHA-256 62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

This commitment identifies the test corpus, not a trust judgment or security certification.

---

## 8. Higher-layer status

Milestones 19–24 made deterministic subsets of Specifications 0006–0012 independently executable without collapsing their designed separations:

- bundle integrity remains distinct from completeness and policy sufficiency;
- resolution remains distinct from verification;
- authority evidence remains distinct from authorization decisions;
- lifecycle evidence remains immutable rather than a silently rewritten current state;
- disclosure minimization remains distinct from proof of global completeness/nonexistence;
- transport encoding remains distinct from evidence identity; and
- HTTP/service state remains distinct from OLP proof validity and authority evidence.

Presence in the Draft v0.3 aggregate profile means the specified executable subset is independently reproduced against the committed corpus. It does not imply that every optional or deployment-specific behavior in a numbered specification has been implemented.

---

## 9. Security lessons integrated

The executable program has incorporated lessons including:

- recursive duplicate-JSON rejection and bounded parsing;
- exact URI and canonical byte semantics;
- technical cryptographic support separated from local policy;
- graph convergence separated from cycles and absence;
- fail-closed critical semantics;
- exact immutable identity recomputation at bundle/resolution/delegation/disclosure/transport boundaries;
- explicit SSRF/private-address/redirect/resource policy;
- privacy/correlation warnings and no hidden field-redaction claims;
- strict transport type preservation and cross-language byte parity; and
- transport completeness, HTTP status, content integrity, proof validity, authority evidence, and policy kept as independent dimensions.

Cross-language disagreement is treated as a protocol/conformance defect, not an implementation preference.

---

## 10. Corpus and vector status

Existing normative-construction vectors remain append-only within a version except for explicitly recorded errata.

The conformance harness uses a frozen base manifest plus additive deterministic fragments. Draft v0.3 adds an aggregate profile that selects the accepted 180 cases without rewriting their expected semantics.

Specification 0014 adds a deterministic SHA-256 commitment over the exact release corpus so a release claim can identify precisely which profile, manifest/fragments, case IDs, and vector bytes were tested.

---

## 11. Migration from Draft v0.2

No identity-bearing migration is required solely because the set release changes from Draft v0.2 to Draft v0.3.

Existing conforming v1 records and proofs are not rewritten, regenerated, re-signed, or re-identified.

Draft v0.3 primarily changes the demonstrated release surface and release metadata: accepted higher-layer capabilities are grouped into one committed aggregate interoperability profile.

Historical evidence remains historical evidence.

---

## 12. Reading guide

For implementers:

1. Read this overview.
2. Read Specifications 0001 and 0002.
3. Implement 0003 and 0004.
4. Add the 0005 evidence primitives.
5. Read 0013 before making versioning, extension, registry, or compatibility claims.
6. Add only the higher-layer capabilities required by the implementation's purpose.
7. Validate each claimed capability against 0011 and the repository conformance corpus.
8. Apply the 0012 transport/API profiles where required.
9. Read 0014 before making a Draft v0.3 aggregate release-profile or corpus-identity claim.

For architectural philosophy, also read `PRINCIPLES.md`.

---

## 13. Promotion toward a stable release

Draft v0.3 materially reduces the distance to a stable release by providing a reproducible 15-capability/180-case aggregate interoperability claim.

It is still not OLP v1.0.

Before a stable release, the project should still require explicit stable-profile promotion criteria, independent external security review of the intended stable boundary, documented operational/deployment threat assumptions, final migration/deprecation procedures, and resolution of any remaining specification contradictions discovered during wider review.

---

## 14. Summary

> **Make evidence portable and independently verifiable; leave trust judgments plural, contextual, and outside central ownership.**

Draft v0.3 records a second major transition: OLP's accepted executable slices can now be named and tested as one independently reproduced release profile, and the exact corpus behind that claim has a deterministic commitment.
