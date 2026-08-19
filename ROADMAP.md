# Open Layer Protocol — Roadmap

**Project status:** experimental / pre-0.1  
**Specification status:** Draft v0.1  
**Current phase:** Phase II — reference implementation and executable conformance

This roadmap describes the intended development sequence. Milestone numbers are project milestones, not protocol version numbers.

## Phase I — Specification foundation

Completed.

- [x] **Milestone 1 — Terminology**  
  Shared vocabulary, semantic boundaries, and foundational invariants.

- [x] **Milestone 2 — Protocol Objects**  
  Core object taxonomy, universal record envelope, and separation of first-class versus derived concepts.

- [x] **Milestone 3 — Record Representation**  
  Immutable records, OLP-CIE-1 deterministic encoding, OLP-CI-1 Record Identity, references, semantic bindings, and base conformance rules.

- [x] **Milestone 4 — Proofs & Verification**  
  Detached proofs, ProofInputV1, deterministic CBOR, algorithm-agile commitments, Ed25519 baseline, verification semantics, extensions, and structured results.

- [x] **Milestone 5 — Evidence Relationships & Graphs**  
  Proof Identity, EvidenceRef, immutable relationship records, graph semantics, countersignatures, and anchoring relationships.

- [x] **Milestone 6 — Identity & Authority Evidence**  
  Principal identifiers, verification-method bindings, roles, memberships, grants, delegation, and authority evaluation boundaries.

- [x] **Milestone 7 — Status, Revocation & Lifecycle Evidence**  
  Additive lifecycle evidence, revocation/suspension/compromise/retirement semantics, current and historical evaluation.

- [x] **Milestone 8 — Evidence Exchange & Bundles**  
  Portable manifested bundles, offline/self-contained verification packages, merge/extraction semantics, and bundle integrity boundaries.

- [x] **Milestone 9 — Resolution & Discovery Profiles**  
  Explicit caller-planned resolution, provenance-visible discovery, resolver security boundaries, and offline behavior.

- [x] **Milestone 10 — Privacy, Selective Disclosure & Data Minimization**  
  Whole-object and graph-subset disclosure, correlation risks, disclosure planning, and external selective-disclosure interoperability.

- [x] **Milestone 11 — Conformance & Interoperability**  
  Capability-scoped conformance, positive/negative/malformed vectors, cross-implementation testing, and conformance evidence.

- [x] **Milestone 12 — Transport & API Profiles**  
  JSON/CBOR transport mappings, streaming envelopes, HTTP API profiles, capability advertisement, and transport security boundaries.

## Phase II — Make the specification executable

### Milestone 13 — Reference Implementation Core

**Next.**

Build the smallest rigorous executable vertical slice from Specifications 0003 and 0004:

```text
Record
  -> OLP-CI-1 identity preimage
  -> OLP-CIE-1 deterministic bytes
  -> Record Identity

Record + proof configuration
  -> ProofInputV1
  -> deterministic CBOR
  -> Pure Ed25519 proof creation
  -> proof verification
  -> structured VerificationResult
```

Initial implementation goals:

- deterministic data models;
- exact canonical-byte reproduction;
- SHA-256 Record Identity;
- record commitments;
- mandatory `eddsa-ed25519-v1` suite;
- local verification-method resolution;
- strict malformed/unsupported/invalid distinctions;
- no implicit network access; and
- unit tests built directly from specification vectors.

### Milestone 14 — Executable Conformance Harness

Turn Specification 0011 into a public, versioned test corpus containing:

- positive vectors;
- exact-byte vectors;
- negative vectors;
- malformed inputs;
- unsupported-version/suite cases;
- critical-extension cases;
- parser-differential tests;
- resource-boundary tests; and
- machine-readable conformance reports.

### Milestone 15 — Independent Second Implementation

Create or coordinate at least one implementation independent of the reference codebase.

The decisive interoperability tests are:

- identical Record Identity digests;
- identical canonical record bytes;
- identical ProofInputV1 bytes;
- proofs produced by implementation A verify in implementation B;
- proofs produced by implementation B verify in implementation A; and
- structured failure classifications agree for required vectors.

A second language is preferred because it exposes hidden assumptions more effectively than a second copy of the same code.

### Milestone 16 — Adversarial & Security Review

Attack the executable design rather than reviewing prose alone.

At minimum test:

- duplicate/ambiguous encodings;
- non-deterministic CBOR;
- algorithm and key-type confusion;
- record, verification-method, and proof-purpose substitution;
- unknown critical extensions;
- replay and backdating;
- resolver SSRF and redirect abuse;
- compromised/rotated verification methods;
- graph cycles and amplification;
- bundle bombs and decompression/resource exhaustion;
- status conflicts and stale evidence;
- disclosure/completeness ambiguity; and
- downgrade behavior.

Security or interoperability defects discovered here must feed back into the specifications, not only into implementation patches.

### Milestone 17 — Draft v0.2 Integration Pass

Revise the complete specification set using implementation, conformance, interoperability, and security findings.

Goals include:

- remove ambiguities exposed by code;
- reconcile cross-spec terminology and reason codes;
- freeze additional test vectors;
- clarify registries and extension governance;
- document migration/versioning rules; and
- identify the smallest stable core suitable for wider review.

## Path toward v1.0

A stable OLP v1.0 should not be declared solely because the prose specifications look complete.

Before v1.0, the project should require at minimum:

1. frozen core normative data models;
2. reproducible canonical vectors;
3. at least two independent interoperable implementations of the core;
4. cross-language proof production and verification;
5. comprehensive malformed and negative testing;
6. no known unresolved contradictions in the core specifications;
7. stable extension and registry governance;
8. a public executable conformance corpus;
9. security review of cryptographic, resolver, graph, bundle, and transport boundaries; and
10. documented migration and compatibility rules.

## Deliberately not on the immediate roadmap

The project should not prioritize a marketplace, token, blockchain, universal reputation score, universal identity provider, hosted trust service, or production-scale network before the evidence core is proven interoperable.

The next pressure test is code.
