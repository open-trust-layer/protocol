# Open Layer Protocol

**An open protocol for portable, verifiable trust between humans, organizations, software agents, services, and other independent participants.**

> Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

**Project status:** experimental / pre-0.1  
**Specification-set status:** Draft v0.2  
**Current phase:** Milestone 18 — Draft v0.2 integration and wider technical review

---

## What Open Layer Protocol is

Open Layer Protocol (OLP) is an open protocol for portable, independently verifiable evidence between independent participants.

OLP standardizes the evidence substrate: immutable records, cryptographic proofs, explicit evidence relationships, identity/authority evidence, lifecycle evidence, exchange bundles, resolution, privacy boundaries, conformance, and transport profiles.

It deliberately does **not** define a universal trust score, identity provider, authorization server, marketplace, blockchain, payment system, or central OLP authority.

Applications remain free to interpret the same evidence differently according to context, risk, policy, jurisdiction, and purpose.

See [`PRINCIPLES.md`](PRINCIPLES.md).

---

## Draft v0.2

Draft v0.2 is an **integration release**, not a new wire-format generation.

The independently verified v1 deterministic core remains byte-compatible with Draft v0.1:

- Record envelope version `1`;
- `OLP-CIE-1` Record Identity encoding;
- SHA-256 Record Commitment baseline;
- `ProofInputV1`;
- `eddsa-ed25519-v1`;
- Proof Identity v1;
- `EvidenceRefV1`; and
- `RelationshipStatementV1`.

Cross-cutting versioning, registry, extension, reason-code, migration, and stable-core rules are defined by [`specification/0013-versioning-registries-and-core-profile.md`](specification/0013-versioning-registries-and-core-profile.md).

The integration rationale is documented in [`docs/draft-v0.2-integration.md`](docs/draft-v0.2-integration.md).

---

## Independently verified core

The current `core-v1` interoperability profile contains eight capabilities:

```text
olp.record-identity.v1
olp.record-commitment.sha256.v1
olp.proof-input.v1
olp.proof.eddsa-ed25519.v1
olp.proof-verification.v1
olp.proof-identity.v1
olp.evidence-ref.v1
olp.evidence-relationship.v1
```

Milestone 17 acceptance demonstrated:

```text
Python core-v1 conformance        62 / 62 PASS
Rust core-v1 conformance          62 / 62 PASS
Python <-> Rust interoperability   9 / 9 PASS
Python 3.11-3.14 CI                PASS
```

This does **not** imply that every higher-layer behavior in Specifications 0006–0010 has been independently implemented and security-tested.

---

## Specification set

Start with [`specification/0000-overview.md`](specification/0000-overview.md).

| Spec | Document | Draft v0.2 role |
|---|---|---|
| 0000 | Overview and Specification Index | Non-normative entry point |
| 0001 | Terminology | Shared vocabulary |
| 0002 | Protocol Objects | Foundational object model |
| 0003 | Record Representation | Verified core |
| 0004 | Proofs and Verification | Verified core |
| 0005 | Evidence Relationships and Graphs | Verified core subset |
| 0006 | Identity and Authority Evidence | Draft design |
| 0007 | Status, Revocation, and Lifecycle Evidence | Draft design |
| 0008 | Evidence Exchange and Bundles | Draft design |
| 0009 | Resolution and Discovery Profiles | Draft design |
| 0010 | Privacy, Selective Disclosure, and Data Minimization | Draft design |
| 0011 | Conformance and Interoperability | Executable framework |
| 0012 | Transport and API Profiles | Draft transport/API profile |
| 0013 | Versioning, Registries, and Draft v0.2 Interoperable Core | Cross-cutting v0.2 governance |

The individual numbered documents retain their own document revisions. The **Draft v0.2** label identifies the repository-level specification-set release.

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
```

Foundational separations include:

```text
proof validity       != truth
identity             != trust
authority evidence   != authorization decision
status evidence      != historical mutation
resolution           != verification
bundle integrity     != completeness
conformance          != trustworthiness
transport security   != OLP object proof validity
```

---

## Implementation and conformance

The repository contains:

- Python reference implementation under `src/olp/`;
- executable conformance harness under `src/olp_conformance/` and `conformance/`;
- independent Rust implementation under `implementations/rust/`;
- interoperability tests under `tests/interoperability/`;
- security regressions under `tests/security/`;
- promoted normative-construction vectors under `vectors/`.

Milestones 13–17 established executable identity/proof/evidence behavior, independent implementation parity, and adversarial hardening.

Draft v0.2 integrates those findings back into the specification set without changing already verified core bytes.

---

## Security status

OLP is still experimental and is **not** a production security certification.

Milestone 17 hardened the currently executable core against parser differentials, malformed URI inputs, recursive/resource exhaustion, policy/cryptographic conflation, graph-processing errors, and cross-language representation drift.

Higher-layer executable review remains necessary for resolver SSRF, bundle ingestion/amplification, authority evaluation, lifecycle/status conflict handling, and privacy/disclosure behavior.

See [`SECURITY.md`](SECURITY.md) and [`docs/security-review-milestone-17.md`](docs/security-review-milestone-17.md).

---

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

The immediate post-v0.2 goal is wider technical review and selecting the next executable higher-layer slice based on risk and interoperability value rather than adding speculative protocol scope.

---

## License

Open Layer Protocol is licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE).
