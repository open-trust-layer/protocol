# OLP Specification 0000 — Overview and Specification Index

**Status:** Draft  
**Specification-set release:** Draft v0.3  
**Current stabilization:** Milestone 26 v1.0 candidate boundary  
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
candidate status            != stable status
protocol conformance        != deployment certification
conformance result          != security certification
```

---

## 3. Draft v0.3 integration result

Draft v0.3 is a coordinated integration and conformance-freeze release produced after the executable work from Milestones 13–24.

No new wire-format generation is introduced solely by this set release. The accepted v1 deterministic constructions remain unchanged, including Record envelope version `1`, `OLP-CIE-1`, SHA-256 Record Identity/commitment baseline, `OLPProof` version `1`, `ProofInputV1`, `eddsa-ed25519-v1`, Proof Identity v1, `EvidenceRefV1`, and accepted v1 capability semantics.

Specification 0013 continues to define general version-domain, registry, extension, reason-code, migration, and capability-governance rules.

Specification 0014 defines Draft v0.3 release profiles and deterministic conformance-suite commitments.

Milestone 26 does not create Draft v0.4 or publish v1.0. It adds Specification 0015 and post-Draft-v0.3 stabilization artifacts that define how a future stable boundary may be promoted.

---

## 4. Specification index

| Spec | Title | Current role |
|---|---|---|
| 0000 | Overview and Specification Index | Non-normative entry point |
| 0001 | Terminology | Mandatory v1 candidate foundation |
| 0002 | Protocol Objects | Mandatory v1 candidate foundation |
| 0003 | Record Representation | Mandatory v1 candidate core |
| 0004 | Proofs and Verification | Mandatory v1 candidate core |
| 0005 | Evidence Relationships and Graphs | Mandatory v1 candidate core subset |
| 0006 | Identity and Authority Evidence | Optional `identity-authority-lifecycle-v1` candidate |
| 0007 | Status, Revocation, and Lifecycle Evidence | Optional `identity-authority-lifecycle-v1` candidate |
| 0008 | Evidence Exchange and Bundles | Optional `bundle-v1` candidate |
| 0009 | Resolution and Discovery Profiles | Optional `resolution-v1` candidate |
| 0010 | Privacy, Selective Disclosure, and Data Minimization | Optional `privacy-disclosure-v1` candidate |
| 0011 | Conformance and Interoperability | Mandatory candidate conformance governance |
| 0012 | Transport and API Profiles | Optional transport/streaming candidates |
| 0013 | Versioning, Registries, and Draft v0.2 Interoperable Core | General cross-cutting governance baseline |
| 0014 | Release Profiles and Conformance Suite Commitments | Draft v0.3 release/corpus governance |
| 0015 | Stable Profile Promotion and Readiness | v1.0 candidate boundary and promotion gates |

The individual numbered specifications retain independent document revisions. Draft v0.3 remains the current specification-set release; candidate/stable status is a separate release-governance dimension.

---

## 5. Dependency and governance map

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
            |
            v
0015 Stable Promotion / Readiness

0013 Versioning / Registries / Core Profile
     governs cross-cutting release, identifier,
     capability, reason-code, and migration rules.
```

---

## 6. Mandatory v1.0 candidate core

The `core-v1` profile remains the smallest frozen deterministic OLP core and is now the mandatory v1.0 candidate core:

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

It contains 62 cases and remains independently reproduced in Python and Rust.

The exact candidate core corpus commitment is:

```text
SHA-256 8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e
```

Candidate designation does not rename or redefine `core-v1`, and it does not make it stable yet.

---

## 7. Optional v1.0 candidate profiles

The higher-layer profiles accepted in Draft v0.3 remain optional candidates:

```text
bundle-v1
resolution-v1
identity-authority-lifecycle-v1
privacy-disclosure-v1
transport-encoding-v1
streaming-http-v1
```

They MAY be promoted independently. A future implementation that conforms to the mandatory stable core MUST NOT be called non-conforming merely because it does not implement an optional profile.

The mandatory core plus these six optional profiles cover exactly the 15 capabilities in the Draft v0.3 aggregate profile.

---

## 8. Draft v0.3 aggregate interoperability profile

Draft v0.3 defines:

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

## 9. Higher-layer semantic status

Milestones 19–24 made deterministic subsets of Specifications 0006–0012 independently executable without collapsing their designed separations:

- bundle integrity remains distinct from completeness and policy sufficiency;
- resolution remains distinct from verification;
- authority evidence remains distinct from authorization decisions;
- lifecycle evidence remains immutable rather than a silently rewritten current state;
- disclosure minimization remains distinct from proof of global completeness/nonexistence;
- transport encoding remains distinct from evidence identity; and
- HTTP/service state remains distinct from OLP proof validity and authority evidence.

Presence in the Draft v0.3 aggregate profile means the specified executable subset is independently reproduced against the committed corpus. It does not imply that every optional or deployment-specific behavior in a numbered specification has been implemented or promoted to stable.

---

## 10. Stable-promotion gate

Specification 0015 defines machine-readable promotion states:

```text
INVALID
BLOCKED
READY
```

`INVALID` means an internal candidate invariant failed.

`BLOCKED` means internal candidate invariants pass but one or more required external/future promotion gates are incomplete.

`READY` means all represented internal and required external promotion gates are satisfied; it is permission to begin final stable publication mechanics, not the stable release itself.

The Milestone 26 candidate is intentionally expected to report:

```text
internal readiness:                       PASS
stable promotion:                         BLOCKED
public technical review:                  PENDING
independent external security review:     PENDING
```

The required blocker codes are:

```text
PUBLIC_TECHNICAL_REVIEW_REQUIRED
INDEPENDENT_EXTERNAL_SECURITY_REVIEW_REQUIRED
```

The project MUST NOT satisfy the independent-review gate using only its own maintainers, tests, or internal adversarial review.

---

## 11. Security lessons integrated

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

Milestone 26 additionally consolidates the candidate threat model, stable release/deprecation/errata process, and contradiction/review register.

Cross-language disagreement is treated as a protocol/conformance defect, not an implementation preference.

---

## 12. Corpus and vector status

Existing normative-construction vectors remain append-only within a version except for explicitly recorded errata.

The conformance harness uses a frozen base manifest plus additive deterministic fragments. Draft v0.3 adds an aggregate profile that selects the accepted 180 cases without rewriting their expected semantics.

Specification 0014 adds a deterministic SHA-256 commitment over exact release corpora. Milestone 26 reuses that mechanism for the mandatory `core-v1` candidate corpus.

No accepted vector or expected result is changed merely by candidate designation.

---

## 13. Migration from Draft v0.3 toward stable v1.0

Milestone 26 creates no identity-bearing migration.

If the future stable v1.0 boundary preserves the currently accepted v1 deterministic constructions, existing conforming Draft v0.3 v1 records and proofs are not rewritten, regenerated, re-signed, or re-identified solely because the set-release label becomes stable.

If public or external security review discovers a defect that requires changed deterministic bytes or materially changed capability semantics, the affected version or capability MUST change explicitly under Specifications 0013–0015.

Historical evidence remains historical evidence.

---

## 14. Reading guide

For implementers:

1. Read this overview.
2. Read Specifications 0001 and 0002.
3. Implement 0003 and 0004.
4. Add the 0005 evidence primitives.
5. Read 0013 before making versioning, extension, registry, or compatibility claims.
6. Validate claimed behavior against 0011 and the repository conformance corpus.
7. Add only the optional higher-layer profiles required by the implementation's purpose.
8. Apply the 0012 transport/API profiles where required.
9. Read 0014 before making a release-profile or corpus-identity claim.
10. Read 0015 before making candidate, release-candidate, stable, or readiness claims.

For architectural philosophy, also read `PRINCIPLES.md`.

---

## 15. Promotion toward a stable release

Draft v0.3 materially reduced the distance to a stable release by providing a reproducible 15-capability/180-case interoperability claim.

Milestone 26 reduces release ambiguity further by selecting the smallest mandatory candidate core, keeping higher layers optional, documenting threat and release assumptions, and making promotion blockers executable.

It is still not OLP v1.0.

The remaining promotion work is deliberately external-facing: public technical review of an exact candidate snapshot and independent external security review of the proposed stable boundary, followed by disposition of material findings and a final exact-snapshot rerun.

---

## 16. Summary

> **Make evidence portable and independently verifiable; leave trust judgments plural, contextual, and outside central ownership.**

Draft v0.3 proved a broad interoperable release surface. Milestone 26 converts that evidence into a conservative v1.0 candidate boundary without pretending internal conformance is independent security review.
