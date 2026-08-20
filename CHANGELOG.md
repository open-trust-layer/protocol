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

### Milestone 24 streaming and HTTP API core

- Add deterministic Specification 0012 sequence and HTTP exchange semantics without introducing ambient network I/O, a universal OLP server, or a mandatory authentication framework.
- Add separate `olp.streaming-transport.v1` and `olp.http-api.v1` capabilities with the combined 36-case `streaming-http-v1` acceptance profile.
- Produce exact RFC 7464 JSON Text Sequence and deterministic CBOR Sequence frame bytes while keeping stream semantic processing on already-parsed frames rather than claiming a general hostile-input sequence decoder.
- Enforce manifest-first streams, exactly one manifest, final `end` behavior, order-independent record/proof/resource semantics, explicit truncation, and preservation of independently addressable present objects.
- Preserve stream completeness independently from evidence validity, including complete transport carrying a resource that fails its committed digest.
- Recompute immutable Record/Proof/manifest identity for identity-bearing HTTP reads and preserve HTTP 404 as a local endpoint result rather than global nonexistence.
- Preserve successful HTTP execution separately from detailed OLP semantic states such as resolution `NOT_FOUND`.
- Preserve HTTP authentication, service authorization, OLP cryptographic validity, and OLP authority evidence as separate dimensions.
- Prevent silent self-contained bundle-query downgrade, HTTPS-to-HTTP redirect downgrade, identity-changing immutable redirects, sensitive-method redirects by default, and cross-origin credential forwarding without explicit policy.
- Model RFC 9530 `Content-Digest` at the parsed RFC 8941 dictionary boundary: the HTTP stack parses Structured Fields, while OLP independently validates algorithm/digest-byte semantics over HTTP content.
- Keep representation-specific cache validators separate from OLP object identity; require explicit policy for public caching of sensitive evidence.
- Keep partial byte ranges separate from full-object verification and keep HTTP 413/429 resource/service states separate from evidence invalidity.
- Add independent dependency-free Rust 1.85 reproduction, source-contract guards forbidding network-client growth, and direct Python↔Rust M24 interoperability coverage.

### Milestone 23 transport encoding core

- Add the deterministic non-network Specification 0012 transport-encoding core without making HTTP, JSON, or any server architecture part of OLP evidence identity.
- Add canonical `r1_`, `p1_`, and `b1_` textual identity presentations with strict unpadded base64url validation, exact 32-octet length checks, typed-context checks, and rejection of non-canonical pad bits.
- Add reversible OLP JSON Value Encoding v1 (`OJVE-1`) for bytes, safe/large integers, arrays, and generic maps.
- Preserve heterogeneous abstract map-key types with pair-based internal representations so host-language dictionary equality cannot collapse integer, text, byte-string, or boolean keys.
- Reject unsafe bare JSON integers, non-canonical decimal integer wrappers, duplicate abstract map keys, malformed wrapper shapes, unsupported OJVE tags, floating-point values, and excessive resource use.
- Add single-object `OLPTransportEnvelopeV1` JSON/CBOR processing with explicit core versus absolute-URI extension message types and distinct malformed/unsupported outcomes.
- Add executable Record and Proof transport-equivalence operations that reconstruct the real object models after OJVE decoding and recompute Record Identity/Proof Identity byte-for-byte.
- Add `olp.transport-encoding.v1` and the separate 22-case `transport-encoding-v1` profile without changing any previously accepted profile.
- Add an independent dependency-free Rust 1.85 implementation with canonical pad-bit checks, pair-preserving abstract values, identity recomputation, source-contract guards, and direct Python↔Rust M23 interoperability coverage.
- Keep streaming, HTTP endpoint/status behavior, content negotiation, `Content-Digest`, HTTP Message Signatures, authentication/authorization, redirects, caching, rate limits, and live network privacy outside M23 for separate review.

### Milestone 22 privacy and disclosure core

- Add the executable Specification 0010 disclosure-planning core without inventing native OLP field-level redaction, zero-knowledge disclosure, a universal privacy score, or a global completeness/minimality proof.
- Process the exact eight-element `DisclosureRequestV1` with explicit caller-supplied planner context rather than introducing a new evidence record or universal policy language.
- Support whole-object disclosure, explicit graph-subset dependency closure, omission of unrelated sibling evidence, and structured unresolved dependencies.
- Recompute Record Identity and Proof Identity for supplied immutable bodies and reject redaction/substitution that does not match the selected `EvidenceRefV1`.
- Verify selected committed resources against `ResourceRefV1` digests before disclosure.
- Preserve the distinction between task-scoped minimized disclosure and global graph completeness; the planner always reports that global completeness is not established and performs no field redaction.
- Model offline/self-contained support as an explicit disclosure tradeoff and surface resolver-interest, manifest, stable-identifier, same-subject, lifecycle, and external-presentation privacy warnings without ambient network I/O.
- Require explicit permission before carrying external native selective-disclosure presentations and preserve their native cryptographic semantics without reconstructing undisclosed claims.
- Defer exact `maxBundleBytes` enforcement to Specification 0008 packaging rather than falsely certifying a size the abstract planner cannot know.
- Add `olp.privacy-disclosure.v1` and the separate 18-case `privacy-disclosure-v1` profile without changing the frozen earlier profiles.
- Add an independent dependency-free Rust 1.85 implementation, source-contract guards, required Python/Rust conformance gates, and direct Python↔Rust M22 interoperability coverage.

### Milestone 21 identity, authority, and lifecycle core

- Add the executable Specifications 0006/0007 core without introducing a global Actor, trust score, authorization boolean, or mutable canonical current state.
- Preserve principal identity, verification-method control, roles, authority, cryptographic validity, lifecycle evidence, and application policy as separate dimensions.
- Add deterministic Principal Relation, Authority Grant, Authority Status, delegation, and Lifecycle Status processing.
- Recompute the exact parent grant Record Identity before any delegation scope evaluation and preserve identity mismatch separately from delegation prohibition or scope mismatch.
- Keep action, resource, context, validity interval, constraints, and delegation provenance explicit; URI hierarchy never creates implicit authority scope.
- Treat every authority constraint as security-critical and fail closed on unsupported constraint semantics.
- Preserve revocation and lifecycle events as immutable additive evidence; absence of lifecycle evidence never implies active status.
- Preserve effective-time, freshness, evidence-completeness, named status-authority, and same-sequence conflict signals without selecting a universal current state.
- Add `olp.identity-authority-lifecycle.v1` and the separate 18-case `identity-authority-lifecycle-v1` profile without changing frozen `core-v1`, `bundle-v1`, or `resolution-v1`.
- Add an independent dependency-free Rust 1.85 implementation, source-contract guards, and direct Python↔Rust M21 interoperability coverage.

### Milestone 20 resolution and discovery core

- Add `ResolutionRequestV1` and deterministic offline-first resolver processing for Specification 0009.
- Resolve exact `EvidenceRefV1` targets from bundle/local-store snapshots only after identity recomputation.
- Resolve committed `ResourceRefV1` content only after digest verification.
- Preserve provenance and distinguish not-found, unavailable, unsupported, policy-blocked, limit-exceeded, freshness failure, and identity mismatch outcomes.
- Model network resolution as caller-supplied deterministic snapshots; the conformance implementation performs zero ambient network I/O.
- Apply network policy before request accounting, including loopback/private-address checks and policy re-checks for redirects.
- Add byte limits, redirect-loop detection, freshness requirements, and unsupported-scheme handling.
- Add `olp.resolution.v1` and the separate 16-case `resolution-v1` profile without changing frozen `core-v1`.
- Add Python↔Rust resolution interoperability coverage.

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
