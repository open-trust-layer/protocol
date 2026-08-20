# Open Layer Protocol — Roadmap

**Project status:** experimental / pre-0.1  
**Specification-set status:** Draft v0.2  
**Current phase:** wider technical review after Milestone 18 integration

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

**Completed.** Python implementation of Record Identity, commitments, ProofInputV1, Ed25519 create/verify, deterministic CBOR, and structured verification results.

### Milestone 14 — Executable Conformance Harness

**Completed.** Implementation-neutral vectors, subprocess adapter contract, CLI, reports, and CI.

### Milestone 15 — Independent Second Implementation

**Completed and independently verified.** Independent Rust implementation reproduces the shared deterministic core and cross-verifies with Python.

### Milestone 16 — Evidence Graph Core

**Completed and independently verified.** Adds Proof Identity, `EvidenceRefV1`, relationship processing, graph projection/traversal, dangling references, cycle safety, and resource-bound behavior.

### Milestone 17 — Adversarial & Security Review

**Completed, fixed, independently verified, and merged.**

Acceptance:

```text
Python core-v1             62 / 62 PASS
Rust core-v1               62 / 62 PASS
Python <-> Rust interop      9 / 9 PASS
Python 3.11-3.14 CI          PASS
```

See `docs/security-review-milestone-17.md`.

### Milestone 18 — Draft v0.2 Integration Pass

**Integration output complete; repository PR/CI is the acceptance gate.**

Outputs:

- Specification 0013;
- Draft v0.2 release manifest;
- Draft v0.2 integration report;
- promoted Proof Identity and EvidenceRef vectors;
- updated repository status/index documents.

Draft v0.2 intentionally preserves the verified v1 core bytes while formalizing release/version domains, registry and extension governance, reason-code distinctions, migration rules, capability stability, and the independently verified core boundary.

## Phase III — Wider review and executable higher layers

The next milestone should be selected after Draft v0.2 acceptance and review feedback.

Priority should go to the highest-risk or highest-interoperability-value executable slice rather than adding speculative protocol scope.

Strong candidates include:

1. **Resolver security profile execution** — explicit network fixtures, SSRF/private-address policy, redirects, recursion, provenance, and offline behavior.
2. **Bundle ingestion execution** — manifested bundle parsing, streaming/resource limits, amplification resistance, integrity/completeness separation.
3. **Identity/authority execution** — principal/method bindings, grants, delegation, status interaction, and policy separation.
4. **Lifecycle/status execution** — conflicting sources, freshness/completeness, rollback/equivocation, historical/current evaluation.
5. **Disclosure/privacy execution** — object/graph minimization, disclosure closure, correlation warnings, external selective-disclosure boundaries.

## Path toward v1.0

A stable OLP v1.0 should require frozen stable-core models, reproducible canonical vectors, independent interoperable implementations, cross-language proof production and verification, comprehensive malformed/negative/resource testing, no unresolved core contradictions, stable extension/registry governance, a public versioned conformance corpus, security review of all included boundaries, and documented migration/deprecation rules.

## Deliberately not on the immediate roadmap

Do not prioritize a marketplace, token, blockchain, universal reputation score, universal identity provider, hosted trust service, or production-scale network before the evidence core and selected higher-layer capabilities are proven interoperable.
