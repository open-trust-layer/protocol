# Open Layer Protocol — Roadmap

**Project status:** experimental / pre-0.1  
**Specification-set status:** Draft v0.2  
**Current phase:** Milestone 19 — Evidence Bundle Core

Milestone numbers are project milestones, not protocol version numbers.

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

**Completed.**

Python implementation of Record Identity, commitments, ProofInputV1, mandatory Ed25519 proof creation/verification, deterministic CBOR, and structured verification results.

### Milestone 14 — Executable Conformance Harness

**Completed.**

Implementation-neutral vectors, subprocess adapter contract, CLI, machine-readable reports, and CI.

### Milestone 15 — Independent Second Implementation

**Completed and independently verified.**

Independent Rust implementation reproduces the shared deterministic core and cross-verifies with Python.

### Milestone 16 — Evidence Graph Core

**Completed and independently verified.**

Adds Proof Identity, `EvidenceRefV1`, relationship processing, graph projection/traversal, dangling references, cycle safety, and resource-bound behavior.

### Milestone 17 — Adversarial & Security Review

**Completed, fixed, independently verified, and merged.**

The executable core was attacked for parser differentials, URI ambiguity, recursive/resource exhaustion, policy/cryptography conflation, graph correctness, adapter type confusion, and cross-language drift.

Acceptance:

```text
Python core-v1             62 / 62 PASS
Rust core-v1               62 / 62 PASS
Python <-> Rust interop     9 / 9 PASS
Python 3.11-3.14 CI         PASS
```

See `docs/security-review-milestone-17.md`.

### Milestone 18 — Draft v0.2 Integration Pass

**Completed, independently verified, and merged.**

Goals:

- reconcile implementation/security findings across the specification set;
- separate set-release versioning from protocol object/encoding versions;
- formalize registry and extension governance;
- formalize reason-code semantic distinctions;
- document Draft v0.1 -> Draft v0.2 migration;
- freeze additional independently reproduced Specification 0005 vectors; and
- identify the smallest independently verified core suitable for wider review.

Primary outputs:

- Specification 0013;
- Draft v0.2 release manifest;
- Draft v0.2 integration report;
- promoted Proof Identity and EvidenceRef vectors;
- updated repository status/index documents.

Draft v0.2 intentionally preserves the verified v1 core bytes.

## Phase III — Wider review and executable higher layers

### Milestone 19 — Evidence Bundle Core

**Implementation complete; Python/Rust `bundle-v1` CI is the acceptance gate.**

Make the deterministic reader/validation subset of Specification 0008 executable: manifest identity, root/inventory canonical sets, exact Record/Proof identity recomputation, packaged-resource digests, missing/unexpected evidence, critical extensions, self-contained no-network behavior, and explicit resource limits.

`core-v1` remains frozen at 62 cases. Milestone 19 introduces the separate `bundle-v1` capability/profile with eight shared cases.

### Milestone 20 — Resolution & Discovery Core

Planned next: offline-first explicit resolution, provenance-visible results, identity recomputation, policy-blocked network behavior, redirect/private-address guards, and resolver-loop/resource boundaries.

### Milestone 21 — Identity, Authority & Lifecycle Core

Planned after M20: principal relations, authority grants, lifecycle statements, and policy-separated evaluation without universal identity or authorization truth.

### Milestone 22 — Privacy & Disclosure Core

Planned after M21: whole-object/graph-subset disclosure planning, task-scoped minimization, unresolved dependency reporting, and correlation warnings.

## Path toward v1.0

A stable OLP v1.0 should require at minimum:

1. frozen stable-core normative data models;
2. reproducible canonical vectors;
3. independent interoperable implementations;
4. cross-language proof production and verification;
5. comprehensive malformed/negative/resource testing;
6. no known unresolved core contradictions;
7. stable extension and registry governance;
8. public versioned conformance corpus;
9. security review of all boundaries included in the stable release; and
10. documented migration and deprecation rules.

## Deliberately not on the immediate roadmap

Do not prioritize a marketplace, token, blockchain, universal reputation score, universal identity provider, hosted trust service, or production-scale network before the evidence core and selected higher-layer capabilities are proven interoperable.
