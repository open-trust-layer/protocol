# Open Layer Protocol

**An open protocol for portable, verifiable trust between humans, organizations, software agents, services, and other independent participants.**

> Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

**Project status:** experimental / pre-0.1  
**Specification-set status:** Draft v0.3  
**Current phase:** Milestone 25 — Draft v0.3 Integration & Conformance Freeze

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

It preserves the already accepted v1 identity-bearing constructions and capability semantics from Draft v0.2 while grouping the executable work accepted through Milestone 24 into one reproducibly committed release profile.

The frozen deterministic `core-v1` remains the smallest OLP core and is not redefined. Draft v0.3 adds the broader release-level profile:

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
```

Direct cross-language gates also retain exact byte comparisons where representation bytes are normative, including deterministic CBOR and pinned JSON Text Sequence / CBOR Sequence producer cases.

---

## Specification set

Start with [`specification/0000-overview.md`](specification/0000-overview.md).

| Spec | Document | Draft v0.3 role |
|---|---|---|
| 0000 | Overview and Specification Index | Non-normative entry point |
| 0001 | Terminology | Shared vocabulary |
| 0002 | Protocol Objects | Foundational object model |
| 0003 | Record Representation | Verified core |
| 0004 | Proofs and Verification | Verified core |
| 0005 | Evidence Relationships and Graphs | Verified core subset |
| 0006 | Identity and Authority Evidence | Executable `identity-authority-lifecycle-v1` subset |
| 0007 | Status, Revocation, and Lifecycle Evidence | Executable `identity-authority-lifecycle-v1` subset |
| 0008 | Evidence Exchange and Bundles | Executable `bundle-v1` subset |
| 0009 | Resolution and Discovery Profiles | Executable `resolution-v1` subset |
| 0010 | Privacy, Selective Disclosure, and Data Minimization | Executable `privacy-disclosure-v1` subset |
| 0011 | Conformance and Interoperability | Executable framework |
| 0012 | Transport and API Profiles | Executable `transport-encoding-v1` and `streaming-http-v1` subsets |
| 0013 | Versioning, Registries, and Draft v0.2 Interoperable Core | General cross-cutting governance baseline |
| 0014 | Release Profiles and Conformance Suite Commitments | Draft v0.3 aggregate profile and corpus commitment |

Individual numbered documents retain their own document revisions. The **Draft v0.3** label identifies the repository-level specification-set release.

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
release profile + exact corpus commitment
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
conformance result    != security certification
```

---

## Implementation and conformance

The repository contains:

- Python reference implementation under `src/olp/`;
- executable conformance harness under `src/olp_conformance/` and `conformance/`;
- independent Rust implementation under `implementations/rust/`;
- interoperability tests under `tests/interoperability/`;
- security regressions under `tests/security/`; and
- normative/promoted construction vectors under `vectors/`.

The conformance CLI can run profiles and independently compute the exact corpus commitment:

```bash
olp-conformance run --profile draft-v0.3-interoperable-v1
olp-conformance commitment --profile draft-v0.3-interoperable-v1 --json
```

The release manifest pins the expected commitment so CI detects accidental corpus drift.

---

## Security status

OLP remains experimental and is **not** a production security certification.

Milestones 17–24 added adversarial hardening across canonicalization, proof handling, graph traversal, bundles, resolution/SSRF policy, delegation/lifecycle evidence, privacy/disclosure planning, transport encoding, streaming semantics, and modeled HTTP exchange behavior.

Draft v0.3 makes the demonstrated surface easier to audit by binding one aggregate profile to one exact corpus. It does not certify live network operation.

Not certified by Draft v0.3 include production HTTP clients/servers, DNS/TLS behavior, proxy/cache deployments, raw hostile-input parser completeness beyond the tested boundaries, HTTP Message Signature deployment, application authentication/authorization frameworks, operational key management, or independent external security review.

See [`SECURITY.md`](SECURITY.md), [`docs/security-review-milestone-17.md`](docs/security-review-milestone-17.md), and [`docs/streaming-http-api-core.md`](docs/streaming-http-api-core.md).

---

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

Milestone 25 is the Draft v0.3 integration/conformance-freeze milestone. The project is deliberately reducing release ambiguity rather than adding speculative protocol scope.

---

## License

Open Layer Protocol is licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE).
