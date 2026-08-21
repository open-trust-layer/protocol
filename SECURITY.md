# Security Policy

Open Layer Protocol is currently **experimental / pre-1.0 candidate work**.

The current specification-set release is **Draft v0.3**. OLP v1.0 has not been released.

The first v1.0 external-review target is frozen as:

```text
review target:  olp-v1.0-review-1
status:         frozen
source commit:  877493826d673ccf9bb94e7b6b113b35141ad220
```

The project is actively seeking public technical review and genuinely independent external security review of that exact source snapshot. Neither external promotion gate is complete.

## Supported versions

There is currently no stable production-supported OLP release.

| Version / branch | Security support |
|---|---|
| Frozen `olp-v1.0-review-1` source | Active public/external review and coordinated fixes |
| Draft v0.3 specification set / v1 candidate work | Experimental review and coordinated fixes |
| Earlier draft snapshots | Historical/compatibility review only |
| Future tagged pre-releases | As documented with the release |
| Stable v1.0 | Not released |

Review and support status does not imply production certification.

## Reporting a vulnerability

Please do **not** publish exploitable or security-sensitive vulnerability details in a public GitHub issue.

Use GitHub's private vulnerability reporting / Security Advisory workflow for this repository when available. If private vulnerability reporting is unavailable, contact the repository owners privately through the project's GitHub organization before disclosing exploit details publicly.

For non-sensitive public technical findings, use the public review tracker:

- Issue #17 — `OLP v1.0 public technical review — olp-v1.0-review-1`

For independent external security-review coordination, use:

- Issue #18 — `Independent external security review needed — olp-v1.0-review-1`

The existence of either tracker does not satisfy a promotion gate.

A useful security report should include, where possible:

- exact reviewed source commit;
- affected specification section or implementation component;
- minimal reproducible example or test vector;
- expected versus observed behavior;
- security impact and likely severity;
- whether the issue affects interoperability or canonicalization;
- whether deterministic bytes or capability semantics would need to change;
- whether network access or untrusted input is required;
- known mitigations; and
- any proposed specification wording or conformance-vector change.

## Frozen review target and source binding

Review evidence intended to satisfy a v1.0 promotion gate is source-bound.

For review round 1, the only source commit that can satisfy the current external gates is:

```text
877493826d673ccf9bb94e7b6b113b35141ad220
```

A review of later `main`, a branch tip, or a different commit does not satisfy `olp-v1.0-review-1`.

The authoritative freeze declaration was merged afterward in commit:

```text
7379e3c34a762cf5dbf44075dc47c291e9f0b749
```

That ordering is intentional: the immutable source snapshot must exist before later metadata can bind a review-target identifier to its exact Git hash.

Opening a review issue, sending outreach, receiving an audit proposal, or publishing a review URL is not completed review evidence.

If a material finding requires source changes:

1. `olp-v1.0-review-1` remains historically bound to its original bytes;
2. the defect is fixed in a new source snapshot;
3. a new review-target identifier is frozen;
4. affected external gates are evaluated for the new target; and
5. review evidence is never silently rebound to changed source.

See `docs/v1-review-round-lifecycle.md` and `specification/0015-stable-profile-promotion-and-readiness.md`.

## Executable security evidence

Milestone 17 performed the first systematic **internal** adversarial review of the deterministic core. Milestones 19–24 then added independently reproduced higher-layer boundaries for bundles, resolution, identity/authority/lifecycle, privacy/disclosure, transport encoding, and deterministic streaming/HTTP exchange semantics.

Draft v0.3 groups the accepted executable capabilities into `draft-v0.3-interoperable-v1`:

```text
Python 3.11-3.14 aggregate profile  180 / 180 PASS
Independent Rust 1.85 aggregate     180 / 180 PASS
Python <-> Rust interoperability     PASS
```

The exact release corpus is committed by:

```text
OLP-CONFORMANCE-SUITE-COMMITMENT-V1
SHA-256 62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

The mandatory v1.0 candidate core is the existing eight-capability `core-v1` profile. Its exact 62-case corpus commitment is:

```text
SHA-256 8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e
```

These are evidence of reproducible conformance against specific corpora. They are not evidence that every possible input, deployment architecture, or operational threat has been tested.

## v1 candidate security gate

The candidate includes an explicit threat model, contradiction/review register, release/deprecation/errata process, machine-checkable promotion evaluator, and source-bound external-review governance.

The intended current state is:

```text
internal readiness:                       PASS
stable promotion:                         BLOCKED
public technical review:                  PENDING
independent external security review:     PENDING
```

The required promotion blockers are:

```text
PUBLIC_TECHNICAL_REVIEW_REQUIRED
INDEPENDENT_EXTERNAL_SECURITY_REVIEW_REQUIRED
```

The project MUST NOT mark the independent-review gate complete solely on the basis of its own maintainers, automated tests, internal adversarial review, passing conformance reports, or outreach activity.

See:

- `docs/v1-threat-model.md`
- `docs/v1-candidate-readiness.md`
- `docs/v1-external-security-review-brief.md`
- `docs/v1-review-package-index.md`
- `specification/0015-stable-profile-promotion-and-readiness.md`

## Security boundaries already exercised

Current executable/adversarial coverage includes:

- deterministic CBOR and Record/Proof identity differential testing;
- duplicate-JSON, Unicode, numeric, nesting, and resource-bound parser behavior;
- signature/hash/key-type and proof-binding separation;
- critical-extension fail-closed behavior;
- evidence-graph cycle/convergence/resource-limit handling;
- bundle inventory/resource commitments and bounded ingestion;
- deterministic resolver provenance, SSRF/private-address/redirect/freshness/limit policy;
- exact delegation-parent identity and scope checks;
- immutable lifecycle/status conflict and freshness handling;
- disclosure minimization, unresolved dependencies, and correlation/privacy warnings;
- canonical textual identities and OJVE type preservation;
- exact deterministic JSON/CBOR transport parity for accepted cases;
- stream truncation/completeness versus evidence-validity separation;
- immutable identity-bearing HTTP read semantics;
- parsed RFC 9530 `Content-Digest` semantics over content bytes;
- redirect downgrade/origin/credential policy;
- cache/range/413/429 separation from evidence validity; and
- HTTP authentication/service authorization separated from OLP proof validity and authority evidence.

These tests are important evidence, not a substitute for independent external review.

## Residual high-priority risks

Reports and external review are especially valuable for:

- any collision or identity disagreement across conforming parsers;
- malformed CBOR/JSON/OJVE accepted differently across implementations;
- signature, hash, key-type, proof-purpose, record, or verification-method substitution;
- extension downgrade or ambiguous critical semantics;
- resolver SSRF, DNS rebinding, redirect, recursion, or resource-exhaustion flaws;
- graph/bundle amplification or decompression/allocation attacks;
- authority/lifecycle policy confusion;
- privacy, correlation, or disclosure-minimization failures;
- transport framing or content-integrity confusion;
- cache/proxy/range behavior that changes security meaning;
- corpus/profile drift that permits two release claims to refer to different tests;
- stale review-evidence reuse after source changes;
- specification ambiguity that causes implementations to make different security decisions; and
- weaknesses in the candidate threat model or conformance corpus that internal review did not discover.

## What the current candidate does not certify

Draft v0.3 conformance and v1 candidate readiness do **not** certify:

- a production HTTP server or client;
- DNS or TLS implementation/security;
- live redirect following or proxy/cache deployment behavior;
- a complete hostile-input RFC 7464, CBOR, or RFC 8941 parser;
- HTTP Message Signature deployment;
- application authentication or authorization frameworks;
- production key custody/rotation/backup procedures;
- denial-of-service resistance at production scale;
- secure operations, monitoring, incident response, backup/recovery, or supply-chain security; or
- completion of an independent external cryptographic/security audit.

Applications MUST perform their own threat modeling and policy review for their deployment context.

## Specification defects are security defects too

If specification ambiguity causes implementations to make different security decisions, the preferred fix is not merely an implementation workaround. The issue should also be reflected in the relevant specification and, where appropriate, in a negative/adversarial conformance vector.

A change that alters accepted deterministic output or capability semantics MUST be handled explicitly under the versioning/breaking-change rules rather than silently folded into a draft, candidate, or stable label.

An unresolved normative contradiction inside a proposed stable boundary makes the candidate `INVALID`; it cannot be waived into `READY` by release metadata.

## Disclosure expectations

The project aims to coordinate fixes and specification clarification before public disclosure where practical.

Because no stable v1.0 exists yet, compatibility may still be intentionally broken to correct a serious security design defect, but such a break must be explicit and versioned.

A material change discovered during external review also requires a new frozen review target rather than reuse of review evidence for old source bytes.

The stable release, migration, deprecation, errata, vulnerability-fix, and withdrawal process is documented in `docs/v1-release-process.md`.

## Cryptographic disclaimer

The presence of standardized primitives such as SHA-256 and Ed25519, independent implementations, committed conformance corpora, and machine-checkable promotion gates does not mean the overall OLP construction has completed independent cryptographic or security review.

Do not deploy Draft v0.3 or the current v1 candidate as high-assurance production security infrastructure without appropriate independent review and deployment-specific threat assessment.
