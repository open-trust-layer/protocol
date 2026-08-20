# Open Layer Protocol — Roadmap

**Project status:** experimental / pre-0.1  
**Specification-set status:** Draft v0.2  
**Current phase:** Milestone 24 — Streaming & HTTP API Core

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

**Accepted and merged.**

Python 3.11–3.14 passed; independent Rust passed; frozen `core-v1` remained 62/62; `bundle-v1` passed 8/8; Python↔Rust bundle interoperability passed.

Make the deterministic reader/validation subset of Specification 0008 executable: manifest identity, root/inventory canonical sets, exact Record/Proof identity recomputation, packaged-resource digests, missing/unexpected evidence, critical extensions, self-contained no-network behavior, and explicit resource limits.

### Milestone 20 — Resolution & Discovery Core

**Accepted and merged.**

Offline-first explicit resolution, provenance-visible results, exact evidence/resource identity recomputation, explicit network policy, redirect/private-address guards, freshness/byte limits, resolver loops, and structured unavailable/not-found/policy outcomes are independently executable in the separate 16-case `resolution-v1` profile.

### Milestone 21 — Identity, Authority & Lifecycle Core

**Accepted and merged.**

Principal/control/role/authority separation, exact delegation-parent identity verification, explicit scope, immutable revocation/lifecycle evidence, conflict/freshness handling, and policy-separated evaluation are independently executable in the separate 18-case `identity-authority-lifecycle-v1` profile.

No global Actor, trust score, mutable canonical current state, or protocol authorization boolean was introduced.

### Milestone 22 — Privacy & Disclosure Core

**Accepted and merged.**

Whole-object and graph-subset disclosure planning, task-scoped minimization, exact immutable identity/resource verification, unresolved dependency reporting, offline/privacy tradeoffs, native external-presentation policy, and correlation warnings are independently executable in the separate 18-case `privacy-disclosure-v1` profile.

No native field-level redaction, zero-knowledge disclosure, global completeness proof, or universal privacy score was introduced.

### Milestone 23 — Transport Encoding Core

**Accepted.**

The deterministic non-network subset of Specification 0012 is independently executable in the separate 22-case `transport-encoding-v1` profile.

Acceptance includes:

```text
Python 3.11-3.14 transport-encoding-v1  22 / 22 PASS
Rust 1.85 transport-encoding-v1         22 / 22 PASS
Python <-> Rust M23 interoperability     PASS
Earlier accepted profiles/regressions   PASS
```

Scope:

- canonical textual Record/Proof/Bundle identity forms;
- strict base64url-no-padding decoding with canonical pad-bit checks;
- reversible OLP JSON Value Encoding v1 (`OJVE-1`);
- byte-string, large-integer, and heterogeneous-map-key preservation;
- strict/unsupported OJVE wrapper handling;
- single-object `OLPTransportEnvelopeV1` processing;
- JSON transport representation using OJVE-1;
- exact deterministic CBOR parity for the accepted envelope/Record/Proof cases;
- transport/object identity separation; and
- implementation-neutral Python/Rust conformance and interoperability.

The final adversarial pass strengthened the original green corpus after detecting that Rust had not actually been required to reproduce Python's deterministic CBOR output. The accepted corpus now makes those bytes explicit rather than inferring JSON/CBOR parity from JSON-only success.

M23 deliberately excludes live sockets, DNS, HTTP authentication/authorization, HTTP Message Signatures, redirects, caching, content-digest handling, and streaming bundle-state semantics.

See `docs/transport-encoding-core.md` and `conformance/VECTOR-INDEX-M23.md`.

### Milestone 24 — Streaming & HTTP API Core

**Next.**

Take the network/API-sensitive remainder of Specification 0012 only after the transport encoding has been independently fixed:

- JSON Text Sequence / CBOR Sequence frame processing;
- truncation and manifest-first behavior;
- immutable object retrieval path validation;
- HTTP content negotiation and structured status mapping;
- `Content-Digest` handling;
- redirects/caching/resource limits;
- separation of HTTP authentication/authorization from OLP proof validity; and
- deterministic HTTP conformance fixtures with no uncontrolled ambient network dependency.

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
