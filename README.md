# Open Layer Protocol

**An open protocol for portable, verifiable trust between humans, organizations, software agents, services, and other independent participants.**

> Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

**Project status:** experimental / pre-1.0 candidate  
**Specification-set status:** Draft v0.3  
**Current phase:** v1.0 candidate — external review round 4

> **OLP v1.0 has not been released.** The current candidate is intentionally blocked from stable promotion until public technical review and independent external security review are completed against the exact same frozen review target.

---

## Moon Company Awareness metadata

The repository includes a root `moon.manifest.yaml` for Moon Company / Moon Core discovery.
This file is non-normative project metadata only: it declares workspace presence and protocol
knowledge domains, with no executable Moon capabilities, actions, endpoints, event contracts, or
runtime-health claim.

The manifest was added after the frozen `olp-v1.0-review-4` source. It does not modify that frozen
source, rebind external review evidence, change protocol semantics or conformance commitments, or
claim that OLP v1.0 has been released.

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

## v1.0 external review — round 4

The active v1.0 external-review target is frozen as:

```text
review target:  olp-v1.0-review-4
status:         frozen
source commit:  c293c5524318b342149a80c3e0322e29742f44f7
```

Reviewers must inspect the exact frozen source commit, not a moving branch tip or later `main`:

- [Frozen review-4 source snapshot](https://github.com/open-trust-layer/protocol/commit/c293c5524318b342149a80c3e0322e29742f44f7)
- [Issue #37 — OLP v1.0 public technical review](https://github.com/open-trust-layer/protocol/issues/37)
- [Issue #38 — Independent external security review needed](https://github.com/open-trust-layer/protocol/issues/38)

The frozen source itself names review-4 in both `SECURITY.md` and the candidate manifest. The later metadata-only freeze binds `olp-v1.0-review-4` to that immutable source SHA.

### Why there is a review round 4

Earlier review targets remain immutable historical evidence:

```text