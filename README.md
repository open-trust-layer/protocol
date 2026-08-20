# Open Layer Protocol

**An open protocol for portable, verifiable trust between humans, organizations, software agents, services, and other independent participants.**

> Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

**Project status:** experimental / pre-0.1  
**Specification-set status:** Draft v0.2  
**Current phase:** Post-Milestone 24 integration / next milestone selection

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

The cross-cutting versioning, registry, extension, reason-code, migration, and stable-core rules are defined by [`specification/0013-versioning-registries-and-core-profile.md`](specification/0013-versioning-registries-and-core-profile.md).

The full Milestone 18 integration rationale is documented in [`docs/draft-v0.2-integration.md`](docs/draft-v0.2-integration.md).

---

## Independently verified executable profiles

The frozen `core-v1` interoperability profile contains eight capabilities:

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
Python core-v1 conformance       62 / 62 PASS
Rust core-v1 conformance         62 / 62 PASS
Python <-> Rust interoperability PASS
Python 3.11-3.14 CI              PASS
```

Higher-layer behavior is added through separate profiles rather than silently changing `core-v1`:

```text
bundle-v1                         8 / 8 PASS  (Python + Rust)
resolution-v1                    16 / 16 PASS  (Python + Rust)
identity-authority-lifecycle-v1  18 / 18 PASS  (Python + Rust)
privacy-disclosure-v1            18 / 18 PASS  (Python + Rust)
transport-encoding-v1            22 / 22 PASS  (Python + Rust)
streaming-http-v1                36 / 36 PASS  (Python + Rust)
```

Direct Python↔Rust interoperability gates cover all accepted executable slices. Milestone 23 additionally requires exact deterministic CBOR parity for the single-envelope, Record, and Proof transport cases rather than treating JSON-only success as sufficient. Milestone 24 additionally verifies pinned JSON Text Sequence / CBOR Sequence producer bytes and keeps transport completeness, HTTP/service status, evidence validity, and OLP proof validity as separate dimensions.

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
| 0006 | Identity and Authority Evidence | Executable `identity-authority-lifecycle-v1` subset |
| 0007 | Status, Revocation, and Lifecycle Evidence | Executable `identity-authority-lifecycle-v1` subset |
| 0008 | Evidence Exchange and Bundles | Executable `bundle-v1` subset |
| 0009 | Resolution and Discovery Profiles | Executable `resolution-v1` subset |
| 0010 | Privacy, Selective Disclosure, and Data Minimization | Executable `privacy-disclosure-v1` subset |
| 0011 | Conformance and Interoperability | Executable framework |
| 0012 | Transport and API Profiles | Executable `transport-encoding-v1` and `streaming-http-v1` subsets |
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
transport encoding   != OLP evidence identity
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

Milestones 19–22 independently reproduced bundle, resolution, identity/authority/lifecycle, and privacy/disclosure higher-layer slices without changing the frozen deterministic core.

Milestone 23 independently reproduced canonical textual identities, OJVE-1, and the single-object JSON/CBOR transport envelope. Its acceptance corpus explicitly verifies that transport round trips preserve Record Identity, Proof Identity, proof bytes, and deterministic CBOR output.

Milestone 24 independently reproduced the deterministic streaming/HTTP semantic boundary from Specification 0012: exact producer framing, manifest-first stream processing, truncation/completeness separation, immutable identity-bearing reads, HTTP negotiation/status mapping, parsed `Content-Digest` semantics, redirect policy, cache/range/limit handling, and HTTP-auth/OLP-proof separation without ambient network I/O.

---

## Security status

OLP is still experimental and is **not** a production security certification.

Milestone 17 hardened the executable core against parser differentials, URI ambiguity, recursive/resource exhaustion, policy/cryptography conflation, graph-processing errors, and cross-language representation drift.

Milestone 19 added bounded bundle ingestion. Milestone 20 added deterministic resolver SSRF/redirect/private-address policy. Milestone 21 added exact delegation identity/scope checks and immutable lifecycle conflict handling. Milestone 22 added identity-preserving disclosure minimization and correlation/privacy warnings without field-level redaction or ambient network access. Milestone 23 hardened the deterministic transport boundary against non-canonical textual identities, OJVE type loss, heterogeneous-map-key collapse, wrapper ambiguity, and unproven JSON/CBOR parity. Milestone 24 hardened deterministic streaming and HTTP exchange semantics against transport/evidence conflation, local-404 overclaiming, unsafe redirect behavior, content-digest ambiguity, cache/range misuse, and HTTP-auth/proof-validity conflation.

Live production networking remains outside the accepted interoperability surface: M24 does not certify a production HTTP server/client, DNS/TLS stack, general hostile-input RFC 7464/CBOR parser, raw RFC 8941 parser, HTTP Message Signature implementation, proxy/cache deployment, or authentication framework.

See [`SECURITY.md`](SECURITY.md), [`docs/security-review-milestone-17.md`](docs/security-review-milestone-17.md), and [`docs/streaming-http-api-core.md`](docs/streaming-http-api-core.md).

---

## Roadmap

See [`ROADMAP.md`](ROADMAP.md).

Milestone 24 is accepted and merged. No Milestone 25 scope has been declared yet; the next executable slice will be selected after post-M24 integration review, based on security risk and interoperability value rather than speculative protocol expansion.

---

## License

Open Layer Protocol is licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE).
