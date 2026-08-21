# Open Layer Protocol

**An open protocol for portable, verifiable trust between humans, organizations, software agents, services, and other independent participants.**

> Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

**Project status:** experimental / pre-1.0 candidate  
**Specification-set status:** Draft v0.3  
**Current phase:** v1.0 candidate — external review round 2 in progress

> **OLP v1.0 has not been released.** The current candidate is intentionally blocked from stable promotion until public technical review and independent external security review are completed against the exact same frozen review target.

---

## What Open Layer Protocol is

Open Layer Protocol (OLP) is an open protocol for portable, independently verifiable evidence between independent participants.

OLP standardizes an evidence substrate: immutable records, cryptographic proofs, explicit evidence relationships, identity/authority evidence, lifecycle evidence, exchange bundles, resolution, privacy boundaries, conformance, and transport/API profiles.

It deliberately does **not** define a universal trust score, identity provider, authorization server, marketplace, blockchain, payment system, or central OLP authority.

Applications remain free to interpret the same evidence differently according to context, risk, policy, jurisdiction, and purpose.

See [`PRINCIPLES.md`](PRINCIPLES.md).

---

## Draft v0.3

Draft v0.3 is an **integration and conformance-freeze release**, not a new wire-format generation.

It preserves the already accepted v1 identity-bearing constructions and capability semantics from Draft v0.2 while grouping the executable work accepted through Milestone 24 into one reproducibly committed release profile:

```text
draft-v0.3-interoperable-v1
```

That profile contains 15 capabilities and selects exactly 180 implementation-neutral cases.

The exact corpus is committed by `OLP-CONFORMANCE-SUITE-COMMITMENT-V1`:

```text
SHA-256 62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

The commitment identifies the exact test corpus. It is **not** an OLP evidence identity, implementation result, certification, security rating, or trust judgment.

See [`specification/0014-release-profiles-and-conformance-suite-commitments.md`](specification/0014-release-profiles-and-conformance-suite-commitments.md), [`specification/releases/draft-v0.3.json`](specification/releases/draft-v0.3.json), and [`docs/draft-v0.3-integration.md`](docs/draft-v0.3-integration.md).

---

## v1.0 candidate boundary

Milestone 26 is accepted and merged. It adds stable-promotion governance without publishing OLP v1.0 or changing existing protocol bytes.

The existing eight-capability `core-v1` profile is the **mandatory v1.0 candidate core**. Its exact candidate corpus contains 62 cases and has commitment:

```text
SHA-256 8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e
```

The accepted higher-layer profiles remain optional candidates:

```text
bundle-v1
resolution-v1
identity-authority-lifecycle-v1
privacy-disclosure-v1
transport-encoding-v1
streaming-http-v1
```

Together the mandatory core and optional candidates cover exactly the 15 Draft v0.3 accepted capabilities. Optional behavior is not silently made mandatory.

The machine-readable promotion state is intentionally:

```text
internal readiness:                       PASS
stable promotion:                         BLOCKED
public technical review:                  PENDING
independent external security review:     PENDING
```

The two current blocker codes are:

```text
PUBLIC_TECHNICAL_REVIEW_REQUIRED
INDEPENDENT_EXTERNAL_SECURITY_REVIEW_REQUIRED
```

This is the correct candidate state. Internal conformance cannot self-certify independent review.

See [`specification/0015-stable-profile-promotion-and-readiness.md`](specification/0015-stable-profile-promotion-and-readiness.md), [`stabilization/v1.0-candidate.json`](stabilization/v1.0-candidate.json), [`docs/v1-threat-model.md`](docs/v1-threat-model.md), [`docs/v1-release-process.md`](docs/v1-release-process.md), and [`docs/v1-candidate-readiness.md`](docs/v1-candidate-readiness.md).

---

## v1.0 external review — round 2

The active v1.0 external-review target is frozen as:

```text
review target:  olp-v1.0-review-2
status:         frozen
source commit:  d470970180bfa128ca14fd01ac920c95dd8ec288
```

Reviewers must inspect the **exact frozen source commit**, not a moving branch tip or later `main`:

- [Frozen review-2 source snapshot](https://github.com/open-trust-layer/protocol/commit/d470970180bfa128ca14fd01ac920c95dd8ec288)
- [Issue #24 — OLP v1.0 public technical review](https://github.com/open-trust-layer/protocol/issues/24)
- [Issue #25 — Independent external security review needed](https://github.com/open-trust-layer/protocol/issues/25)

The source snapshot itself contains review-2 in `preparing` state. That is intentional: a Git commit cannot contain its own eventual hash. A later metadata-only commit binds `olp-v1.0-review-2` to the immutable source SHA above.

### Why there is a review round 2

The original review target remains immutable historical evidence:

```text
review target:  olp-v1.0-review-1
source commit:  877493826d673ccf9bb94e7b6b113b35141ad220
status:         historical / superseded
```

Issue #21 identified a release-integrity defect in review-1. Specification 0014 hashes exact repository bytes, but review-1 had no `.gitattributes`; a common Git for Windows checkout using `core.autocrlf=true` could materialize LF text as CRLF and cause the published corpus commitments and required-artifact hashes to fail reproduction.

The correction did **not** change the corpus commitment construction, conformance corpus bytes, protocol semantics, or the two published commitments. The corrected review-2 source adds:

- root `.gitattributes` with deterministic LF text checkout semantics;
- explicit binary exclusions;
- `tests/conformance/test_repository_byte_reproducibility.py`; and
- a Windows readiness job that sets `core.autocrlf=true` before checkout and runs the actual reviewer-facing commitment and promotion commands.

That Windows path passes on the review-2 source.

See [Issue #21](https://github.com/open-trust-layer/protocol/issues/21) and [`docs/v1-review-2-rollover.md`](docs/v1-review-2-rollover.md).

### Reviewer package

- [`docs/v1-review-package-index.md`](docs/v1-review-package-index.md)
- [`docs/v1-public-review-guide.md`](docs/v1-public-review-guide.md)
- [`docs/v1-external-security-review-brief.md`](docs/v1-external-security-review-brief.md)
- [`docs/v1-review-2-rollover.md`](docs/v1-review-2-rollover.md)
- [`docs/v1-review-round-lifecycle.md`](docs/v1-review-round-lifecycle.md)
- [`docs/v1-threat-model.md`](docs/v1-threat-model.md)
- [`docs/v1-release-process.md`](docs/v1-release-process.md)
- [`docs/v1-candidate-readiness.md`](docs/v1-candidate-readiness.md)
- [`stabilization/v1-review-register.json`](stabilization/v1-review-register.json)
- [`SECURITY.md`](SECURITY.md)

High-value review areas include:

- cross-specification contradictions and ambiguous security semantics;
- canonicalization, Record Identity, Proof Identity, and cross-implementation determinism;
- proof-input construction, algorithm/key/verification-method/record/proof-purpose substitution;
- identity, authority, lifecycle, trust, and authorization separation;
- evidence relationships and graph semantics;
- bundle completeness, disclosure withholding, and nonexistence claims;
- resolver/network/HTTP success versus cryptographic verification or existence;
- privacy and correlation assumptions;
- extension, versioning, registry, downgrade, migration, deprecation, and errata behavior;
- malformed input and parser/resource bounds;
- graph and bundle amplification;
- transport, framing, encoding, and content-integrity ambiguity;
- platform, Git checkout, filesystem, locale, newline, and serialization assumptions that could affect deterministic verification; and
- stale conformance or review-evidence reuse during promotion.

### Review evidence is source-bound

Opening a review issue, sending an outreach message, receiving an audit proposal, or publishing a review URL does not by itself satisfy a promotion gate.

A completed external gate must identify the exact frozen source commit and provide durable review evidence for that target.

If a material finding requires a source-changing fix:

1. `olp-v1.0-review-2` remains historically bound to its frozen source;
2. the source is corrected;
3. a new review-target identifier is frozen; and
4. affected external reviews must apply to that new target.

Review evidence is never silently rebound to changed source bytes.

---

## Independently verified executable profiles

The frozen `core-v1` profile contains eight capabilities and remains 62/62 in both implementations.

Higher-layer behavior is additive:

```text
core-v1                          62 / 62 PASS  (Python + Rust)
bundle-v1                         8 / 8 PASS  (Python + Rust)
resolution-v1                    16 / 16 PASS  (Python + Rust)
identity-authority-lifecycle-v1  18 / 18 PASS  (Python + Rust)
privacy-disclosure-v1            18 / 18 PASS  (Python + Rust)
transport-encoding-v1            22 / 22 PASS  (Python + Rust)
streaming-http-v1                36 / 36 PASS  (Python + Rust)
```

Draft v0.3 additionally requires all accepted capabilities in one run:

```text
Python 3.11 draft-v0.3-interoperable-v1  180 / 180 PASS
Python 3.12 draft-v0.3-interoperable-v1  180 / 180 PASS
Python 3.13 draft-v0.3-interoperable-v1  180 / 180 PASS
Python 3.14 draft-v0.3-interoperable-v1  180 / 180 PASS
Rust 1.85 draft-v0.3-interoperable-v1    180 / 180 PASS
Python <-> Rust interoperability          PASS
Windows core.autocrlf=true reproduction   PASS
```

Direct cross-language gates also retain exact byte comparisons where representation bytes are normative, including deterministic CBOR and pinned JSON Text Sequence / CBOR Sequence producer cases.

---

## Specification set

Start with [`specification/0000-overview.md`](specification/0000-overview.md).

| Spec | Document | Current role |
|---|---|---|
| 0000 | Overview and Specification Index | Non-normative entry point |
| 0001 | Terminology | Mandatory v1 candidate foundation |
| 0002 | Protocol Objects | Mandatory v1 candidate foundation |
| 0003 | Record Representation | Mandatory v1 candidate core |
| 0004 | Proofs and Verification | Mandatory v1 candidate core |
| 0005 | Evidence Relationships and Graphs | Mandatory v1 candidate core subset |
| 0006 | Identity and Authority Evidence | Optional `identity-authority-lifecycle-v1` candidate |
| 0007 | Status, Revocation, and Lifecycle Evidence | Optional `identity-authority-lifecycle-v1` candidate |
| 0008 | Evidence Exchange and Bundles | Optional `bundle-v1` candidate |
| 0009 | Resolution and Discovery Profiles | Optional `resolution-v1` candidate |
| 0010 | Privacy, Selective Disclosure, and Data Minimization | Optional `privacy-disclosure-v1` candidate |
| 0011 | Conformance and Interoperability | Mandatory v1 candidate governance |
| 0012 | Transport and API Profiles | Optional transport/streaming candidates |
| 0013 | Versioning, Registries, and Draft v0.2 Interoperable Core | Mandatory cross-cutting governance baseline |
| 0014 | Release Profiles and Conformance Suite Commitments | Mandatory release/corpus governance |
| 0015 | Stable Profile Promotion and Readiness | Mandatory v1 candidate promotion governance |

Individual numbered documents retain their own document revisions. Draft v0.3 remains the current specification-set release; the v1.0 candidate boundary and external-review round sit on top of that set rather than publishing a new specification-set release.

---

## Architecture

```text
Terminology / protocol objects
          |
          v
immutable records
          |
          v
cryptographic proofs
          |
          v
evidence relationships / graphs
          |
          +--> identity / authority evidence
          |
          +--> status / lifecycle evidence
          |
          v
portable evidence bundles
          |
          +--> explicit resolution / discovery
          |
          +--> privacy / selective disclosure
          |
          v
conformance / interoperability
          |
          v
transport / API profiles
          |
          v
release corpus commitment
          |
          v
candidate boundary + promotion gates
          |
          v
source-bound external review
```

Foundational separations include:

```text
proof validity        != truth
identity              != trust
authority evidence    != authorization decision
status evidence       != historical mutation
resolution            != verification
bundle integrity      != completeness
conformance           != trustworthiness
transport security    != OLP object proof validity
transport encoding    != OLP evidence identity
corpus commitment     != conformance result
candidate             != stable
conformance result    != security certification
protocol conformance  != deployment certification
review issue          != completed review
review URL            != source-bound review evidence
```

---

## Implementation, conformance, and readiness tooling

The repository contains:

- Python reference implementation under `src/olp/`;
- executable conformance and promotion tooling under `src/olp_conformance/`;
- implementation-neutral corpus under `conformance/`;
- independent Rust implementation under `implementations/rust/`;
- interoperability tests under `tests/interoperability/`;
- security regressions under `tests/security/`; and
- candidate stabilization metadata under `stabilization/`.

Useful commands:

```bash
olp-conformance run --profile draft-v0.3-interoperable-v1
olp-conformance commitment --profile draft-v0.3-interoperable-v1 --json
olp-conformance promotion-check --candidate stabilization/v1.0-candidate.json --json
```

A release process that requires stable readiness must use:

```bash
olp-conformance promotion-check \
  --candidate stabilization/v1.0-candidate.json \
  --require-ready
```

and it must fail while required external review remains pending.

To reproduce the active frozen review target itself, check out:

```bash
git checkout d470970180bfa128ca14fd01ac920c95dd8ec288
python -m pip install -e '.[test]'
python -m pytest -q
olp-conformance run --profile core-v1
olp-conformance run --profile draft-v0.3-interoperable-v1
olp-conformance commitment --profile core-v1 --json
olp-conformance commitment --profile draft-v0.3-interoperable-v1 --json
olp-conformance promotion-check --candidate stabilization/v1.0-candidate.json --json
```

Expected commitments:

```text
core-v1
8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e

draft-v0.3-interoperable-v1
62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

---

## Security status

OLP remains experimental and is **not** a production security certification.

Milestones 17–24 added adversarial hardening across canonicalization, proof handling, graph traversal, bundles, resolution/SSRF policy, delegation/lifecycle evidence, privacy/disclosure planning, transport encoding, streaming semantics, and modeled HTTP exchange behavior.

Milestone 26 added an explicit candidate threat model, contradiction/review register, release/deprecation/errata process, and a fail-closed promotion gate.

Review round 2 adds a verified cross-platform exact-byte checkout invariant after Issue #21 exposed the review-1 gap. Public technical review is open, and the project is seeking a genuinely independent external security review. Neither external gate is complete yet.

Not certified include production HTTP clients/servers, DNS/TLS behavior, proxy/cache deployments, raw hostile-input parser completeness beyond the tested boundaries, HTTP Message Signature deployment, application authentication/authorization frameworks, operational key management, production-scale denial-of-service resistance, or independent external security review.

See [`SECURITY.md`](SECURITY.md), [`docs/v1-threat-model.md`](docs/v1-threat-model.md), [`docs/v1-external-security-review-brief.md`](docs/v1-external-security-review-brief.md), [`docs/v1-review-2-rollover.md`](docs/v1-review-2-rollover.md), and [`docs/security-review-milestone-17.md`](docs/security-review-milestone-17.md).

---

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

Milestone 26 is accepted and merged. Review round 1 was superseded after Issue #21; the corrected v1.0 external-review target is now frozen as `olp-v1.0-review-2` at `d470970180bfa128ca14fd01ac920c95dd8ec288`.

The current work is **review and disposition**, not speculative feature expansion:

1. public technical reviewers inspect the exact review-2 source;
2. an independent external security reviewer assesses the exact same source;
3. findings are reproduced, classified, and dispositioned;
4. source-changing material fixes trigger another frozen review target; and
5. stable promotion is considered only after all mandatory gates are satisfied for the same exact target.

Until then, the v1.0 candidate remains intentionally **BLOCKED** from stable promotion.

---

## License

Open Layer Protocol is licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE).
