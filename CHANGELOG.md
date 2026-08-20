# Changelog

All notable changes to Open Layer Protocol are documented here.

The project is experimental and has not yet made a stable release. Entries before the first tagged release describe development milestones rather than compatibility guarantees.

## [Unreleased]

### Draft v0.2 — Milestone 18 integration

- Define Draft v0.2 as a specification-set integration release rather than a new wire-format generation.
- Add Specification 0013: versioning, registries, extension governance, reason-code governance, migration rules, capability stability, and the Draft v0.2 independently verified core.
- Preserve existing v1 deterministic core bytes and identifiers.
- Add `specification/releases/draft-v0.2.json`.
- Add `docs/draft-v0.2-integration.md`.
- Promote independently reproduced Specification 0005 Proof Identity and `EvidenceRefV1` vectors into `vectors/`.
- Define the independently verified `core-v1` as eight capabilities.
- Record the accepted Milestone 17 evidence: Python 62/62, Rust 62/62, and Python↔Rust 9/9.
- Distinguish independently verified core behavior from draft-only higher layers in Specifications 0006–0010.
- Document Draft v0.1 -> Draft v0.2 migration with no identity-bearing rewrite for the verified v1 core.
- Formalize that compact OLP identifiers are specification-controlled while third-party extensions use globally unambiguous identifiers.
- Formalize reason-code distinctions between malformed, unsupported, unavailable, invalid, policy-rejected, resource-limited, and absent outcomes.

### Milestone 17 adversarial/security hardening

- Harden absolute-URI syntax validation against whitespace/control injection and malformed percent escapes.
- Add strict JSON duplicate-name, numeric, Unicode, size, and nesting checks at the conformance boundary.
- Bound pre-freeze value recursion and deterministic-CBOR allocation work.
- Enforce cryptosuite policy without conflating policy rejection with mathematical signature validity.
- Preserve record binding and signature validity when a technically supported commitment algorithm is rejected only by local policy.
- Correct evidence-graph cycle detection, incremental projection refresh, and edge-scan resource limits.
- Add reversible `$map` adapter projection for mixed integer/text keys and wrapper-shaped literal maps.
- Harden Rust adapter input handling and deterministic-CBOR map recursion limits.
- Expose uninterpreted noncritical relationship qualifiers.
- Expand `core-v1` from 57 to 62 implementation-neutral cases.
- Amend Specifications 0004 and 0012 for policy/math separation and duplicate-JSON/resource-bound requirements.

### Milestones 13–16

- Add Python reference implementation for Specifications 0003/0004.
- Add deterministic CBOR, Record Identity, commitments, ProofInputV1, Ed25519 create/verify, and structured verification results.
- Add executable implementation-neutral conformance harness and `olp-conformance` CLI.
- Add independent Rust implementation and cross-language interoperability CI.
- Add executable Specification 0005 Evidence Graph Core: Proof Identity, `EvidenceRefV1`, relationship processing, graph projection/traversal, and Rust parity.

### Milestone 19 evidence bundle core

- Add deterministic `BundleManifestStatementV1` and `ResourceRefV1` processing.
- Validate bundle inventory/root identity sets and packaged resource SHA-256 commitments.
- Preserve missing, unexpected, duplicate, and invalid-resource outcomes as separate dimensions.
- Enforce self-contained no-network fallback semantics and fail-closed critical bundle extensions.
- Add `olp.bundle.v1`, `bundle-v1`, eight shared conformance cases, and Python/Rust interoperability coverage.
- Keep frozen `core-v1` unchanged at 62 cases; add eight separate `bundle-v1` cases.

### Specification foundation

Draft v0.2 contains Specifications 0000–0013.

Specifications 0001–0012 originated in the Draft v0.1 design stack. Specification 0013 was added by the Draft v0.2 integration pass.

## Release history

No tagged stable protocol releases yet.
