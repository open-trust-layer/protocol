# Milestone 20 — Resolution & Discovery Core

Milestone 20 makes the deterministic, security-sensitive subset of Specification 0009 executable without introducing hidden network access.

## Executable capability

`olp.resolution.v1` is exposed through the separate `resolution-v1` conformance profile. Draft v0.2 `core-v1` remains frozen at eight capabilities / 62 cases.

The executable slice supports two target classes:

- `evidence` — exact `EvidenceRefV1` lookup with identity recomputation;
- `externalResource` — absolute URI or committed `ResourceRefV1` lookup.

Other Specification 0009 target classes remain explicitly `UNSUPPORTED_TARGET_CLASS` until their dependent executable models exist.

## Deterministic resolver snapshots

The conformance adapter consumes caller-supplied resolver snapshots. It never performs DNS, HTTP, DID resolution, filesystem lookup, or other ambient I/O.

This lets Python and Rust prove the same processing rules for:

- bundle and local-store hits;
- source provenance;
- exact identity recomputation;
- resource digest verification;
- offline-only policy;
- network-policy preflight;
- redirect policy;
- private/loopback address blocking;
- redirect-chain loop detection;
- response/resource byte limits;
- freshness requirements;
- `NOT_FOUND`, `UNAVAILABLE`, `UNSUPPORTED`, `POLICY_BLOCKED`, `LIMIT_EXCEEDED`, and `IDENTITY_MISMATCH` separation.

A real network resolver may perform I/O outside this pure core, but it must feed an equivalent explicit result/provenance model into verification. URI syntax never grants network permission.

## Security properties

Network request accounting remains zero until target, redirect, and private-address policy checks have passed. Redirect targets are policy-checked again rather than inheriting permission from the original URI.

Identity mismatch, resolver unavailability, resource limits, and local policy rejection are never relabeled as cryptographic or evidence invalidity.

## Acceptance gate

Milestone 20 requires:

- all repository tests on Python 3.11–3.14;
- frozen `core-v1` 62/62 on Python and Rust;
- `bundle-v1` 8/8 on Python and Rust;
- `resolution-v1` 16/16 on Python and Rust;
- exact Python↔Rust resolution interoperability.
