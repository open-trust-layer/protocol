# Open Layer Protocol — Roadmap

**Project status:** experimental / pre-1.0 candidate  
**Specification-set status:** Draft v0.3  
**Current phase:** v1.0 candidate — external review round 2 in progress

Milestone numbers are project milestones, not protocol version numbers.

> **OLP v1.0 has not been released.** Stable promotion remains intentionally blocked until the required public technical review and independent external security review are completed against the same exact frozen review target.

## Current v1.0 review target

The active external-review target is frozen as:

```text
review target:  olp-v1.0-review-2
status:         frozen
source commit:  d470970180bfa128ca14fd01ac920c95dd8ec288
```

Review-2 supersedes review-1 after Issue #21 identified a cross-platform checkout reproducibility defect in the original frozen source. Review-1 remains immutable historical evidence:

```text
review target:  olp-v1.0-review-1
source commit:  877493826d673ccf9bb94e7b6b113b35141ad220
status:         historical / superseded
```

The review-2 source includes repository-enforced LF text checkout bytes, exact-byte regression coverage, and a Windows `core.autocrlf=true` reproduction gate. The published corpus commitments remain unchanged.

Reviewers must inspect the frozen review-2 source commit, not a moving branch tip or later `main`.

Public coordination:

- Issue #24 — public technical review of `olp-v1.0-review-2`
- Issue #25 — independent external security review coordination for `olp-v1.0-review-2`
- Issue #21 — review-1 checkout-byte reproducibility finding and rollover rationale
- `docs/v1-review-package-index.md`
- `docs/v1-public-review-guide.md`
- `docs/v1-external-security-review-brief.md`
- `docs/v1-review-2-rollover.md`
- `docs/v1-review-round-lifecycle.md`

Current promotion state:

```text
internal readiness:                       PASS
stable promotion:                         BLOCKED
public technical review:                  PENDING
independent external security review:     PENDING
```

Required blocker codes:

```text
PUBLIC_TECHNICAL_REVIEW_REQUIRED
INDEPENDENT_EXTERNAL_SECURITY_REVIEW_REQUIRED
```

Opening a tracker, sending outreach, receiving an audit proposal, or publishing a review URL does not itself satisfy either external gate.

---

## Phase I — Specification foundation

Milestones 1–12 are complete at the specification-design level:

- [x] 1 — Terminology
- [x] 2 — Protocol Objects
- [x] 3 — Record Representation
- [x] 4 — Proofs & Verification
- [x] 5 — Evidence Relationships & Graphs
- [x] 6 — Identity & Authority Evidence
- [x] 7 — Status, Revocation & Lifecycle Evidence
- [x] 8 — Evidence Exchange & Bundles
- [x] 9 — Resolution & Discovery Profiles
- [x] 10 — Privacy, Selective Disclosure & Data Minimization
- [x] 11 — Conformance & Interoperability
- [x] 12 — Transport & API Profiles

## Phase II — Make the specification executable

### Milestone 13 — Reference Implementation Core

**Completed.** Python implementation of Record Identity, commitments, `ProofInputV1`, Ed25519 proof creation/verification, deterministic CBOR, and structured verification results.

### Milestone 14 — Executable Conformance Harness

**Completed.** Implementation-neutral vectors, subprocess adapter contract, CLI, machine-readable reports, and CI.

### Milestone 15 — Independent Second Implementation

**Completed and independently reproduced.** Independent Rust implementation reproduces the deterministic core and cross-verifies with Python.

### Milestone 16 — Evidence Graph Core

**Completed and independently reproduced.** Proof Identity, `EvidenceRefV1`, relationship processing, graph projection/traversal, dangling references, cycle safety, and resource-bound behavior.

### Milestone 17 — Internal Adversarial & Security Review

**Completed, fixed, independently reproduced, and merged.**

```text
Python core-v1            62 / 62 PASS
Rust core-v1              62 / 62 PASS
Python <-> Rust interop    PASS
Python 3.11-3.14 CI        PASS
```

This was an internal adversarial review. It is not the independent external security review required for stable promotion.

See `docs/security-review-milestone-17.md`.

### Milestone 18 — Draft v0.2 Integration Pass

**Completed, independently reproduced, and merged.** Added Specification 0013, release/version/registry governance, Draft v0.2 release metadata, promoted evidence vectors, and the frozen eight-capability `core-v1` without changing existing v1 deterministic bytes.

---

## Phase III — Executable higher layers

### Milestone 19 — Evidence Bundle Core

**Accepted and merged.** `bundle-v1` 8/8 in Python and Rust; bounded manifest/inventory/resource validation; frozen `core-v1` unchanged.

### Milestone 20 — Resolution & Discovery Core

**Accepted and merged.** `resolution-v1` 16/16 in Python and Rust; offline-first resolution, provenance, exact identity checks, SSRF/private-address/redirect/freshness/resource policy.

### Milestone 21 — Identity, Authority & Lifecycle Core

**Accepted and merged.** `identity-authority-lifecycle-v1` 18/18 in Python and Rust; exact parent-grant identity/scope, immutable lifecycle/status evidence, conflict/freshness handling, and no protocol authorization boolean or universal current state.

### Milestone 22 — Privacy & Disclosure Core

**Accepted and merged.** `privacy-disclosure-v1` 18/18 in Python and Rust; whole-object/graph-subset minimization, exact immutable identity/resource verification, unresolved dependencies, offline/privacy tradeoffs, and correlation warnings without invented field-level redaction.

### Milestone 23 — Transport Encoding Core

**Accepted and merged.** `transport-encoding-v1` 22/22 in Python and Rust; canonical textual identities, OJVE-1, single-object envelopes, and exact deterministic CBOR parity for accepted Record/Proof/envelope cases.

### Milestone 24 — Streaming & HTTP API Core

**Accepted and merged.** `streaming-http-v1` 36/36 in Python and Rust; exact sequence producer bytes, manifest-first/truncation semantics, immutable HTTP reads, status/negotiation separation, parsed `Content-Digest`, redirect/cache/range/413/429 policy, and HTTP-auth/OLP-proof separation with zero ambient network I/O in conformance.

---

## Phase IV — Release integration and stabilization

### Milestone 25 — Draft v0.3 Integration & Conformance Freeze

**Accepted and merged.**

M25 added no new evidence or wire semantics. It converted independently accepted executable work into one reproducibly committed release-level interoperability claim:

```text
draft-v0.3-interoperable-v1 capabilities   15
Draft v0.3 aggregate cases                180
Python 3.11                               180 / 180 PASS
Python 3.12                               180 / 180 PASS
Python 3.13                               180 / 180 PASS
Python 3.14                               180 / 180 PASS
Independent Rust 1.85                     180 / 180 PASS
Python <-> Rust interoperability           PASS
```

Draft v0.3 corpus commitment:

```text
SHA-256 62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

See `docs/draft-v0.3-integration.md` and `specification/0014-release-profiles-and-conformance-suite-commitments.md`.

### Milestone 26 — v1.0 Candidate Boundary & Promotion Gates

**Accepted and merged.**

M26 added no new evidence semantics or wire-format generation. It selected a conservative stable-candidate boundary and made promotion requirements executable.

Mandatory candidate core:

```text
core-v1
8 capabilities
62 cases
SHA-256 8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e
```

Optional candidate profiles:

```text
bundle-v1
resolution-v1
identity-authority-lifecycle-v1
privacy-disclosure-v1
transport-encoding-v1
streaming-http-v1
```

Mandatory + optional candidates cover exactly the 15 Draft v0.3 accepted capabilities without making optional profiles mandatory.

M26 also added:

- Specification 0015 — Stable Profile Promotion and Readiness;
- `stabilization/v1.0-candidate.json`;
- machine-readable promotion schemas;
- `olp-conformance promotion-check` with `INVALID`, `BLOCKED`, and `READY`;
- a pinned v1 candidate threat model;
- a machine-readable contradiction/review register covering Specifications 0000–0015;
- stable release, migration, deprecation, errata, and rollback rules;
- adversarial promotion-gate tests; and
- Python 3.11–3.14 promotion-readiness CI.

M26 does not publish v1.0. It makes the remaining external work explicit and prevents internal conformance from being misrepresented as independent review.

---

## Phase V — External review and finding disposition

**In progress — review round 2.**

### Review round 1 — historical / superseded

`olp-v1.0-review-1` is permanently bound to source commit `877493826d673ccf9bb94e7b6b113b35141ad220`.

Issue #21 found that a normal Git for Windows checkout with `core.autocrlf=true` could alter hash-critical working-tree text bytes, causing the central reproduction instructions to fail. The source was therefore superseded rather than silently rebound.

### Review round 2 — active

The corrected exact candidate snapshot is frozen as:

```text
olp-v1.0-review-2
d470970180bfa128ca14fd01ac920c95dd8ec288
```

The current legitimate work is:

1. obtain meaningful public technical review of that exact source through Issue #24 and related findings;
2. obtain genuinely independent external security review of that exact source through Issue #25 / external reviewer deliverables;
3. reproduce and classify findings;
4. disposition findings with durable references;
5. add regression/conformance coverage for accepted defects where appropriate; and
6. preserve exact source-binding in all promotion evidence.

### If another material source change is required

A material fix does **not** silently modify the meaning of `olp-v1.0-review-2`.

Instead:

1. review-2 remains historical evidence for its original bytes;
2. the defect is fixed in a new source snapshot;
3. a new review-target identifier is frozen;
4. affected external gates return to `PENDING` for the new target; and
5. earlier review evidence cannot automatically satisfy the new target.

### If no further material source change is required

Once both external gates are legitimately completed for the same exact frozen review-2 source, the promotion evaluator may reach `READY`.

`READY` is permission to begin final stable publication mechanics. It is not itself the stable release.

---

## Path toward v1.0

A stable OLP v1.0 requires, at minimum:

1. an explicitly promoted mandatory stable profile and normative boundary;
2. reproducible canonical vectors and release-level corpus commitments;
3. independent interoperable implementations;
4. cross-language proof production/verification and normative-byte parity;
5. comprehensive malformed/negative/policy/resource testing;
6. no unresolved normative contradictions in the promoted boundary;
7. stable extension, registry, reason-code, migration, deprecation, and errata governance;
8. public versioned conformance corpus and immutable release manifests;
9. meaningful public technical review of the exact promoted source;
10. independent external security review of that exact source; and
11. documented deployment/threat assumptions and release criteria.

Items 1–8 and 11 are internally established for the current candidate boundary. Items 9–10 are the active promotion blockers.

No Milestone 27 protocol-feature scope is declared.

## Deliberately not on the immediate roadmap

Do not prioritize a marketplace, token, blockchain, universal reputation score, universal identity provider, hosted trust service, or speculative protocol features merely to continue the milestone sequence.

The project should remain review-driven until the current candidate has either been dispositioned successfully or superseded by a new frozen review target.
