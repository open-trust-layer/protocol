# Milestone 25 — Draft v0.3 Integration & Conformance Freeze

Milestone 25 is a release-integration milestone. It adds no new OLP evidence semantics or wire-format generation.

The milestone exists to reconcile the independently accepted Milestones 19–24 with the repository's release/versioning/conformance layer and to create one reproducible release-level interoperability claim.

Acceptance boundary:

- one aggregate `draft-v0.3-interoperable-v1` profile covering every currently accepted executable capability;
- exactly 180 existing conformance cases, with no silent modification of earlier vectors;
- Python 3.11–3.14: 180/180 PASS;
- independent Rust 1.85: 180/180 PASS;
- existing direct Python↔Rust interoperability gates remain green;
- a deterministic SHA-256 commitment to the exact aggregate profile, manifest fragments, and referenced vectors;
- a Draft v0.3 specification-set release manifest recording compatibility with Draft v0.2;
- Specification 0013, SECURITY.md, README.md, ROADMAP.md, and conformance documentation reconciled with the accepted executable surface;
- no claim that live network deployment, TLS, external security audit, or production operations are certified.

Milestone 25 MUST preserve the already accepted v1 Record Identity, ProofInputV1, Ed25519 suite, Proof Identity, EvidenceRefV1, bundle, resolution, authority/lifecycle, privacy/disclosure, and transport behavior. Any discovered contradiction that would require changing existing deterministic output or published semantics must be treated as a separate breaking/errata decision rather than hidden inside the release integration pass.
