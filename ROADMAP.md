# Open Layer Protocol — Roadmap

**Project status:** experimental / pre-1.0 candidate work  
**Specification-set status:** Draft v0.3  
**Current phase:** Post-Milestone 26 — public technical review / independent external security review

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

M25 added no new evidence or wire semantics. It turned the independently accepted Milestones 17–24 into one precise release-level interoperability claim.

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

Mandatory + optional candidates cover exactly the 15 Draft v0.3 accepted capabilities without making the optional profiles mandatory.

M26 outputs include:

- Specification 0015 — Stable Profile Promotion and Readiness;
- `stabilization/v1.0-candidate.json`;
- machine-readable candidate/review/report schemas;
- `olp-conformance promotion-check` with `INVALID`, `BLOCKED`, and `READY` states;
- a pinned v1 candidate threat model;
- a machine-readable contradiction/review register covering Specifications 0000–0015;
- stable release, migration, deprecation, errata, and rollback rules;
- adversarial promotion-gate tests; and
- Python 3.11–3.14 promotion-readiness CI.

The accepted M26 state is deliberately:

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

M26 does not publish v1.0. It makes the remaining external work explicit and prevents internal conformance from being misrepresented as independent security review.

See `docs/v1-candidate-readiness.md`, `docs/v1-threat-model.md`, `docs/v1-release-process.md`, and `specification/0015-stable-profile-promotion-and-readiness.md`.

## Path toward v1.0

A stable OLP v1.0 should require at minimum:

1. an explicitly promoted mandatory stable profile and normative boundary;
2. reproducible canonical vectors and release-level corpus commitments;
3. independent interoperable implementations;
4. cross-language proof production/verification and normative-byte parity;
5. comprehensive malformed/negative/policy/resource testing;
6. no unresolved normative contradictions in the promoted boundary;
7. stable extension, registry, reason-code, migration, deprecation, and errata governance;
8. public versioned conformance corpus and immutable release manifests;
9. independent external security review of the intended stable boundary; and
10. documented deployment/threat assumptions and release criteria.

M25 materially completed the corpus/release-identity layer. M26 completed the internally satisfiable parts of stable-boundary selection, contradiction review, governance, and threat/release assumptions while making independent external security review and public technical review impossible to bypass accidentally.

The current next legitimate work is review-driven:

1. freeze an exact candidate snapshot for public technical review;
2. obtain independent external security review;
3. disposition material findings through clarification, errata, or explicit version changes;
4. rerun exact conformance/interoperability on the resulting snapshot; and
5. only when promotion state becomes `READY`, perform release-candidate/stable publication mechanics.

No Milestone 27 protocol-feature scope is declared by this roadmap update.

## Deliberately not on the immediate roadmap

Do not prioritize a marketplace, token, blockchain, universal reputation score, universal identity provider, hosted trust service, or speculative protocol features merely to continue the milestone sequence.
