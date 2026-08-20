# Open Layer Protocol

**An open protocol for portable, verifiable trust between humans, organizations, software agents, services, and other independent participants.**

> Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

**Project status:** experimental / pre-0.1  
**Specification status:** Draft v0.1  
**Current phase:** Milestone 16 Evidence Graph Core complete and independently verified; Milestone 17 adversarial/security review next

---

## What Open Layer Protocol is

Open Layer Protocol (OLP) is an open protocol for portable, independently verifiable evidence between independent participants.

It defines common structures and processing rules for humans, organizations, software agents, services, devices, marketplaces, institutions, and other actors to exchange cryptographically verifiable claims, evidence, attestations, provenance, and outcomes without requiring trust to be owned or controlled by a single platform.

OLP is designed to make economic and digital history portable across applications, marketplaces, networks, organizations, and jurisdictions.

The protocol focuses on **evidence and provenance rather than centralized reputation scores**. Applications remain free to interpret the same evidence differently according to context, risk, policy, jurisdiction, and purpose.

OLP aims to provide a neutral evidence layer that can work alongside existing commerce, identity, payment, authorization, agent, credential, storage, transparency, and communication protocols.

Its core goals include:

- portable and independently verifiable evidence;
- participant-controlled history;
- contextual rather than universal trust;
- cryptographic provenance for important claims;
- explicit evidence relationships and disagreement;
- privacy through data minimization and selective disclosure;
- interoperability with existing open standards;
- neutrality toward blockchains, marketplaces, payment systems, identity systems, and jurisdictions;
- equal protocol treatment of humans, organizations, and autonomous software agents; and
- no requirement for a central OLP authority to verify ordinary evidence.

---

## What Open Layer Protocol is not

**OLP is not a marketplace.**

It does not provide product discovery, ordering, delivery, employment, payments, or general commerce infrastructure. Existing systems can perform those functions while using OLP as an evidence layer.

**OLP is not a reputation platform.**

It does not define a universal reputation score and does not decide whether a participant is globally "trusted" or "untrusted." Trust remains contextual and policy-dependent.

**OLP is not an identity provider.**

It can carry or reference identity evidence from DID, PKI, credential, account, organizational, or other systems, but identity, cryptographic control, authority, and trust remain separate concepts.

**OLP is not a blockchain or cryptocurrency protocol.**

Implementations may use distributed ledgers, transparency logs, databases, archives, or other storage mechanisms. No blockchain, token, or cryptocurrency is required.

**OLP is not a payment system, bank, escrow provider, insurer, or tax authority.**

It can carry verifiable evidence or references produced by such systems without replacing them.

**OLP is not a global authority for deciding what is legal, moral, acceptable, authoritative, or trustworthy.**

Jurisdictions, organizations, applications, and users may apply their own policies. Authoritative or restrictive claims represented through OLP remain evidence with provenance rather than protocol-issued universal truth.

**OLP is not a mechanism for silently rewriting history.**

Corrections, disputes, supersession, revocation, suspension, compromise, and other lifecycle changes are represented as explicit additive evidence rather than hidden mutation of historical objects.

Most importantly, OLP is **not intended to create a new central intermediary**.

Its purpose is the opposite: enable independent systems to exchange and evaluate verifiable evidence without requiring one organization to own the underlying trust relationship.

---

## Core principles

The project is guided by principles including:

- Evidence over reputation.
- Facts over judgments.
- Participant-owned history.
- Contextual trust.
- No universal trust score.
- Algorithm plurality.
- Privacy by architecture.
- Identity != trust.
- Actor neutrality.
- No silent history rewriting.
- Blockchain neutrality.
- Jurisdiction neutrality.
- Interoperability before invention.
- Independent verifiability.

See [`PRINCIPLES.md`](PRINCIPLES.md) for the project principles document.

---

## Specification

Start with [`specification/0000-overview.md`](specification/0000-overview.md).

Specification 0000 is the **non-normative entry point and index**. Normative protocol behavior is defined by the applicable numbered specifications.

| Spec | Document | Status |
|---|---|---|
| 0000 | [`0000-overview.md`](specification/0000-overview.md) — Overview and Specification Index | Draft v0.1 / non-normative |
| 0001 | [`0001-terminology.md`](specification/0001-terminology.md) — Terminology | Draft v0.1 |
| 0002 | [`0002-protocol-objects.md`](specification/0002-protocol-objects.md) — Protocol Objects | Draft v0.1 |
| 0003 | [`0003-record-representation.md`](specification/0003-record-representation.md) — Record Representation | Draft v0.1 |
| 0004 | [`0004-proofs-and-verification.md`](specification/0004-proofs-and-verification.md) — Proofs and Verification | Draft v0.1 |
| 0005 | [`0005-evidence-relationships.md`](specification/0005-evidence-relationships.md) — Evidence Relationships and Graphs | Draft v0.1 |
| 0006 | [`0006-identity-and-authority.md`](specification/0006-identity-and-authority.md) — Identity and Authority Evidence | Draft v0.1 |
| 0007 | [`0007-status-and-lifecycle.md`](specification/0007-status-and-lifecycle.md) — Status, Revocation, and Lifecycle Evidence | Draft v0.1 |
| 0008 | [`0008-evidence-exchange-and-bundles.md`](specification/0008-evidence-exchange-and-bundles.md) — Evidence Exchange and Bundles | Draft v0.1 |
| 0009 | [`0009-resolution-and-discovery-profiles.md`](specification/0009-resolution-and-discovery-profiles.md) — Resolution and Discovery Profiles | Draft v0.1 |
| 0010 | [`0010-privacy-selective-disclosure-and-data-minimization.md`](specification/0010-privacy-selective-disclosure-and-data-minimization.md) — Privacy, Selective Disclosure, and Data Minimization | Draft v0.1 |
| 0011 | [`0011-conformance-and-interoperability.md`](specification/0011-conformance-and-interoperability.md) — Conformance and Interoperability | Draft v0.1 |
| 0012 | [`0012-transport-and-api-profiles.md`](specification/0012-transport-and-api-profiles.md) — Transport and API Profiles | Draft v0.1 |

### Architecture at a glance

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

The specifications intentionally keep several concepts separate:

```text
proof validity       != truth
identity             != trust
authority evidence   != final authorization
status evidence      != historical mutation
resolution           != verification
bundle integrity     != completeness
conformance          != trustworthiness
transport security   != OLP object proof validity
```

---

## Current development phase

The Draft v0.1 semantic and exchange stack is now defined through Specification 0012.

Milestone 13 now provides the first executable reference slice for Specifications 0003 and 0004:

```text
Record
  -> canonical identity representation
  -> Record Identity

Record + proof configuration
  -> ProofInputV1
  -> deterministic CBOR
  -> Ed25519 proof creation / verification
  -> structured VerificationResult
```

The implementation reproduces the normative `0003` and `0004` vectors byte-for-byte, creates and verifies the mandatory Ed25519 proof suite, preserves structured verification outcomes, and performs no implicit network resolution.

Milestone 14 turns Specification 0011 into an executable, implementation-neutral conformance corpus. The current `core-v1` profile now covers the original record/proof capabilities plus the Milestone 16 evidence primitives through positive, negative, malformed, and unsupported cases.

The harness supports both an in-process Python adapter and a JSON-lines subprocess contract suitable for independent implementations in other languages. The Python reference adapter passes the complete current corpus, while an intentionally broken adapter is required to fail as a harness self-test.

Milestone 15 added and verified an independent Rust implementation under `implementations/rust/`. The Rust adapter passed the same implementation-neutral corpus and bidirectional Python↔Rust interoperability gates.

Milestone 16 makes Specification 0005 executable: deterministic Proof Identity, typed `EvidenceRefV1`, ordinary immutable relationship records, provenance-preserving graph projection, dangling-reference handling, cycle-safe traversal, and explicit resource-boundary results. The conformance corpus now contains 57 cases across eight capabilities, including an `evidence-v1` profile exercised by both Python and Rust.

Draft v0.1 remains implementation-test material, not a stable production standard.

---

## Near-term roadmap

1. **Reference implementation core — complete** — Record Identity, ProofInputV1, deterministic CBOR, Ed25519 create/verify, structured verification results, normative vectors, and negative tests.
2. **Executable conformance harness — complete** — implementation-neutral positive, negative, malformed, and unsupported corpus; adapter boundary; CLI; machine-readable reports; harness self-tests; CI.
3. **Second independent implementation — complete and verified** — independent Rust core plus shared-corpus and bidirectional Python↔Rust interoperability gates.
4. **Evidence Graph Core — complete and independently verified** — Proof Identity, EvidenceRef, relationship records, graph projection/traversal, 57-case shared corpus, and Rust parity for deterministic evidence primitives.
5. **Adversarial/security review — next** — cryptographic substitution, parser ambiguity, resolver/network attacks, resource exhaustion, graph/bundle abuse, and privacy failures.
6. **Draft v0.2 integration pass** — feed implementation and security findings back into the specifications.

Before a future stable v1.0 release, the project should require reproducible canonical vectors, independent interoperable implementations, a public conformance corpus, and security review of the core cryptographic and network boundaries.

---

## Design philosophy

OLP is designed so that an implementation can say:

> "Here is the evidence, here is where it came from, here is what cryptographically verifies, here is what could not be evaluated, and here are the assumptions used."

It should not need to say:

> "Trust us; our platform already decided who is trustworthy."

That distinction is the project.

---

## Status

Open Layer Protocol is currently **experimental / pre-0.1**.

The current specifications are **Draft v0.1** and are expected to change as the reference implementation, conformance suite, independent implementations, and security review expose ambiguities or design defects.

---

## Repository documents

- [`PRINCIPLES.md`](PRINCIPLES.md) — architectural principles and project constraints.
- [`ROADMAP.md`](ROADMAP.md) — completed specification milestones and Phase II implementation plan.
- [`CHANGELOG.md`](CHANGELOG.md) — notable project/specification changes before and after releases.
- [`SECURITY.md`](SECURITY.md) — vulnerability reporting and current security-support status.
- [`specification/0000-overview.md`](specification/0000-overview.md) — non-normative specification entry point and dependency map.

The `src/`, `tests/`, and `vectors/` directories now contain the Milestone 13 reference implementation, its test corpus, and reproducible vectors. See [`docs/reference-implementation.md`](docs/reference-implementation.md).

The `conformance/` directory and `olp_conformance` package contain the Milestone 14 executable corpus and runner. See [`conformance/README.md`](conformance/README.md) and [`docs/conformance-harness.md`](docs/conformance-harness.md).

The `implementations/rust/` crate is the independent second implementation and now covers the deterministic Specification 0005 evidence subset as well. See [`implementations/README.md`](implementations/README.md) and [`docs/rust-implementation.md`](docs/rust-implementation.md).

Milestone 16 evidence-graph behavior and boundaries are documented in [`docs/evidence-graph-core.md`](docs/evidence-graph-core.md).

---

## License

Open Layer Protocol is licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE).
