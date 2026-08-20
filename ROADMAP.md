# Open Layer Protocol — Roadmap

**Project status:** experimental / pre-0.1  
**Specification-set status:** Draft v0.3  
**Current phase:** Post-Milestone 25 stabilization / stable-profile review

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

**Completed.** Python implementation of Record Identity, commitments, ProofInputV1, Ed25519 proof creation/verification, deterministic CBOR, and structured verification results.

### Milestone 14 — Executable Conformance Harness

**Completed.** Implementation-neutral vectors, subprocess adapter contract, CLI, machine-readable reports, and CI.

### Milestone 15 — Independent Second Implementation

**Completed and independently verified.** Independent Rust implementation reproduces the deterministic core and cross-verifies with Python.

### Milestone 16 — Evidence Graph Core

**Completed and independently verified.** Proof Identity, `EvidenceRefV1`, relationship processing, graph projection/traversal, dangling references, cycle safety, and resource-bound behavior.

### Milestone 17 — Adversarial & Security Review

**Completed, fixed, independently verified, and merged.**

```text
Python core-v1            62 / 62 PASS
Rust core-v1              62 / 62 PASS
Python <-> Rust interop    PASS
Python 3.11-3.14 CI        PASS
```

See `docs/security-review-milestone-17.md`.

### Milestone 18 — Draft v0.2 Integration Pass

**Completed, independently verified, and merged.** Added Specification 0013, release/version/registry governance, Draft v0.2 release metadata, promoted evidence vectors, and a frozen eight-capability `core-v1` without changing existing v1 deterministic bytes.

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

See `docs/streaming-http-api-core.md` and `conformance/VECTOR-INDEX-M24.md`.

## Phase IV — Release integration and stabilization

### Milestone 25 — Draft v0.3 Integration & Conformance Freeze

**Accepted and merged.**

M25 added no new evidence or wire semantics. It turns the independently accepted Milestones 17–24 into one precise release-level interoperability claim.

Acceptance evidence:

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

The exact release corpus is committed with `OLP-CONFORMANCE-SUITE-COMMITMENT-V1`:

```text
SHA-256 62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

M25 outputs:

- aggregate `draft-v0.3-interoperable-v1` profile;
- deterministic corpus-commitment algorithm and CLI;
- Specification 0014;
- `specification/releases/draft-v0.3.json`;
- normalized standalone conformance-profile metadata/schema;
- Python/Rust aggregate CI that recomputes and verifies the pinned corpus commitment;
- Draft v0.3 overview/security/conformance documentation;
- explicit Draft v0.2 → Draft v0.3 migration with no identity-bearing rewrite; and
- a regression proving unrelated future profile growth does not perturb a frozen Draft v0.3 corpus commitment.

M25 deliberately does **not** claim production network security, TLS correctness, operational security, or completion of an independent external security audit.

See `docs/draft-v0.3-integration.md` and `specification/0014-release-profiles-and-conformance-suite-commitments.md`.

### Next milestone selection

No Milestone 26 scope has been declared.

The next step should be selected from the remaining stabilization path toward a credible stable profile: explicit stable-boundary promotion criteria, contradiction/errata review, independent external security review, deployment/threat assumptions, and final migration/deprecation policy. New protocol features should not be invented merely to continue the milestone sequence.

## Path toward v1.0

A stable OLP v1.0 should require at minimum:

1. an explicitly promoted stable profile and normative data-model boundary;
2. reproducible canonical vectors and release-level corpus commitment;
3. independent interoperable implementations;
4. cross-language proof production/verification and normative-byte parity;
5. comprehensive malformed/negative/policy/resource testing;
6. no known unresolved contradictions in the promoted stable boundary;
7. stable extension, registry, reason-code, migration, and deprecation governance;
8. public versioned conformance corpus and immutable release manifests;
9. independent external security review of the intended stable boundary; and
10. documented deployment/threat assumptions and release criteria.

Draft v0.3 materially advances items 2, 3, 4, 5, 7, and 8. It does not by itself complete items 1, 6, 9, or 10.

## Deliberately not on the immediate roadmap

Do not prioritize a marketplace, token, blockchain, universal reputation score, universal identity provider, hosted trust service, or production-scale network before the evidence core and promoted release capabilities are proven interoperable and independently reviewed.
