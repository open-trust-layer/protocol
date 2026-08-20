# Changelog

All notable changes to Open Layer Protocol will be documented in this file.

The project is experimental and has not yet made a stable release. The format is inspired by Keep a Changelog, but entries before the first tagged release describe development milestones rather than compatibility guarantees.

## [Unreleased]

### Added

- Non-normative Specification 0000 overview and specification index.
- Draft v0.1 normative specification stack through Specification 0012.
- Project principles document.
- Repository roadmap for the reference implementation and conformance phase.
- Security policy for responsible vulnerability reporting.
- Apache License 2.0 repository license.
- Initial repository placeholders for `docs/`, `src/`, `tests/`, and `vectors/`.
- Milestone 13 Python reference implementation core for Specifications 0003 and 0004.
- Minimal deterministic CBOR encoder implementing the OLP canonical subset.
- OLP-CI-1 Record Identity, Definition Identity, Blob Identity, and canonical textual Record Identity presentation.
- Algorithm-agile RecordCommitment model with mandatory SHA-256 / COSE `-16` support.
- Exact nine-element ProofInputV1 construction and deterministic encoding.
- Mandatory `eddsa-ed25519-v1` proof creation and verification using explicit supplied verification material.
- Structured VerificationResult model preserving malformed, unsupported, unavailable, invalid, mismatch, temporal, and method-status dimensions.
- Reproducible Specification 0003 and 0004 vectors plus a Milestone 13 end-to-end vector.
- Comprehensive Milestone 13 test suite covering canonicalization, mutations, extension criticality, context checks, status separation, and offline verification behavior.
- Milestone 14 executable conformance harness for the currently implemented Specification 0003 and 0004 capabilities.
- Implementation-neutral conformance manifest, now expanded to 57 deterministic positive, negative, malformed, and unsupported vectors.
- Capability-scoped `record-v1`, `proof-v1`, and `core-v1` conformance profiles.
- Python `ConformanceAdapter` protocol plus language-neutral JSON-lines subprocess adapter contract.
- `olp-conformance` CLI with filtering and machine-readable `olp-conformance-report-v1` output.
- Harness self-tests using an intentionally broken implementation to prove false behavior is detected.
- GitHub Actions workflow running repository tests and the complete core conformance profile across supported Python versions.
- Milestone 15 independent Rust implementation of the currently executable Specification 0003/0004 core.
- Standalone Rust `olp-conformance-adapter` implementing the existing JSON-lines subprocess contract without importing Python code.
- Rust normative-vector tests for Record Identity, ProofInputV1, deterministic Ed25519 proof generation, and public-key derivation.
- Bidirectional Python↔Rust interoperability tests for identity, proof-input bytes, proof creation, and cross-verification.
- Dedicated `rust-interoperability` GitHub Actions gate requiring Rust unit tests, full `core-v1` conformance, and cross-language tests.
- Documentation for the independent implementation boundary and Milestone 15 acceptance procedure.
- Milestone 16 executable Evidence Graph Core for Specification 0005.
- Deterministic OLP-PIE-1 Proof Identity derivation and typed `EvidenceRefV1` encoding.
- Immutable relationship statement processing for the seven core relationship types.
- Provenance-preserving evidence graph projection, dangling-reference handling, cycle-safe traversal, and explicit traversal limits.
- `evidence-v1` conformance profile and 16 new implementation-neutral Specification 0005 cases, expanding `core-v1` to 57 cases across eight capabilities.
- Rust implementations of Proof Identity, EvidenceRef, and relationship processing plus three new Python↔Rust evidence interoperability checks.

### Specification foundation

The Draft v0.1 stack currently includes:

- `0001-terminology.md`;
- `0002-protocol-objects.md`;
- `0003-record-representation.md`;
- `0004-proofs-and-verification.md`;
- `0005-evidence-relationships.md`;
- `0006-identity-and-authority.md`;
- `0007-status-and-lifecycle.md`;
- `0008-evidence-exchange-and-bundles.md`;
- `0009-resolution-and-discovery-profiles.md`;
- `0010-privacy-selective-disclosure-and-data-minimization.md`;
- `0011-conformance-and-interoperability.md`; and
- `0012-transport-and-api-profiles.md`.

### Next

- Perform the Milestone 17 adversarial security review.
- Feed findings into the Milestone 18 Draft v0.2 specification pass.

## Release history

No tagged protocol releases yet.
