# Security Policy

Open Layer Protocol is currently **experimental / pre-0.1**.

The current specification-set release is **Draft v0.3**. Draft v0.3 has independently reproduced deterministic and exchange semantics, but it is not a production security standard or external security certification.

## Supported versions

There is currently no stable production-supported OLP release.

| Version / branch | Security support |
|---|---|
| Draft v0.3 specification set | Experimental review and coordinated fixes |
| Earlier draft snapshots | Historical/compatibility review only |
| Future tagged pre-releases | As documented with the release |
| Stable v1.0 | Not released |

## Reporting a vulnerability

Please do **not** publish exploitable vulnerability details in a public GitHub issue.

Use GitHub's private vulnerability reporting / Security Advisory workflow for this repository when available. If private vulnerability reporting is unavailable, contact the repository owners privately through the project's GitHub organization before disclosing exploit details publicly.

A useful report should include, where possible:

- the affected specification section or implementation component;
- a minimal reproducible example or test vector;
- expected versus observed behavior;
- security impact;
- whether the issue affects interoperability or canonicalization;
- whether network access or untrusted input is required;
- known mitigations; and
- any proposed specification wording change.

## Executable security evidence

Milestone 17 performed the first systematic adversarial review of the deterministic core. Milestones 19–24 then added independently reproduced higher-layer boundaries for bundles, resolution, identity/authority/lifecycle, privacy/disclosure, transport encoding, and deterministic streaming/HTTP exchange semantics.

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

This is evidence of reproducible conformance against a specific corpus. It is not evidence that every possible input, deployment architecture, or operational threat has been tested.

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

## Residual high-priority risks

Reports are especially valuable for:

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
- corpus/profile drift that permits two release claims to refer to different tests; and
- specification ambiguity that causes implementations to make different security decisions.

## What Draft v0.3 does not certify

Draft v0.3 conformance does **not** certify:

- a production HTTP server or client;
- DNS or TLS implementation/security;
- live redirect following or proxy/cache deployment behavior;
- a complete hostile-input RFC 7464, CBOR, or RFC 8941 parser;
- HTTP Message Signature deployment;
- application authentication or authorization frameworks;
- production key custody/rotation/backup procedures;
- denial-of-service resistance at production scale;
- secure operations, monitoring, incident response, or supply-chain security; or
- completion of an independent external cryptographic/security audit.

Applications MUST perform their own threat modeling and policy review for their deployment context.

## Specification defects are security defects too

If specification ambiguity causes implementations to make different security decisions, the preferred fix is not merely an implementation workaround. The issue should also be reflected in the relevant specification and, where appropriate, in a negative/adversarial conformance vector.

A change that alters accepted deterministic output or capability semantics MUST be handled explicitly under the versioning/breaking-change rules rather than silently folded into a draft release label.

## Disclosure expectations

The project aims to coordinate fixes and specification clarification before public disclosure where practical.

Because no stable v1.0 exists yet, compatibility may still be intentionally broken to correct a serious security design defect, but such a break must be explicit and versioned.

## Cryptographic disclaimer

The presence of standardized primitives such as SHA-256 and Ed25519, independent implementations, and a committed conformance corpus does not mean the overall OLP construction has completed independent cryptographic or security review.

Do not deploy Draft v0.3 as high-assurance production security infrastructure without an appropriate independent review and deployment-specific threat assessment.
