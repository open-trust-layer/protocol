# Draft v0.3 Integration Report

## Status

Draft v0.3 is the Milestone 25 specification-set integration and conformance-freeze release.

It introduces no new OLP evidence semantics and no new identity-bearing wire-format generation.

Its purpose is to make the repository's accepted executable surface precise, reproducible, and release-addressable after Milestones 19–24 expanded far beyond the original Draft v0.2 eight-capability core.

## Why Draft v0.3 was needed

The post-M24 review found that implementation and conformance evidence had outgrown the release/governance documentation:

- Draft v0.2 release metadata still named only the 62-case core;
- Specification 0013 and the overview still described several higher layers as not independently executed;
- `SECURITY.md` still referred to Draft v0.1;
- `conformance/README.md` stopped at early higher-layer milestones;
- standalone conformance profile JSON files had drifted into two incompatible metadata shapes despite sharing one schema; and
- there was no single exact commitment identifying the full accepted conformance corpus.

These were release-integration defects, not reasons to invent new evidence semantics.

## Milestone decision

M25 therefore freezes one aggregate release profile:

```text
draft-v0.3-interoperable-v1
```

It contains exactly 15 accepted capabilities:

```text
olp.record-identity.v1
olp.record-commitment.sha256.v1
olp.proof-input.v1
olp.proof.eddsa-ed25519.v1
olp.proof-verification.v1
olp.proof-identity.v1
olp.evidence-ref.v1
olp.evidence-relationship.v1
olp.bundle.v1
olp.resolution.v1
olp.identity-authority-lifecycle.v1
olp.privacy-disclosure.v1
olp.transport-encoding.v1
olp.streaming-transport.v1
olp.http-api.v1
```

The aggregate profile selects exactly 180 already-existing conformance cases. No earlier vector expected result is changed by the aggregate profile.

## Independent aggregate evidence

The aggregate candidate passes as one profile rather than as separately orchestrated milestones:

```text
Python 3.11  180 / 180 PASS
Python 3.12  180 / 180 PASS
Python 3.13  180 / 180 PASS
Python 3.14  180 / 180 PASS
Rust 1.85    180 / 180 PASS
```

The complete existing Python↔Rust interoperability suite also passes in the Rust aggregate job.

This matters because a single aggregate run can expose capability-advertisement or profile-composition errors that independent per-profile runs might not reveal.

## Conformance suite commitment

M25 adds `OLP-CONFORMANCE-SUITE-COMMITMENT-V1`, specified normatively in Specification 0014.

The commitment covers:

- the base conformance manifest;
- additive manifest fragments that define the selected profile or contribute selected-capability cases;
- the standalone aggregate profile declaration;
- ordered capability membership;
- ordered selected case IDs; and
- exact bytes of every referenced vector.

Each corpus file is SHA-256 hashed over exact bytes. The outer commitment uses an explicit binary domain and uint32 big-endian length/count framing; it does not depend on JSON object ordering or another JSON canonicalization scheme.

The Draft v0.3 corpus commitment is:

```text
OLP-CONFORMANCE-SUITE-COMMITMENT-V1
SHA-256 62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

The release manifest pins that value and CI independently recomputes it.

The commitment identifies the corpus only:

```text
corpus identity != execution result != signed claim != certification != trust
```

## Commitment-design hardening finding

The first M25 commitment prototype included every additive manifest fragment visible in the repository snapshot.

That would have made a frozen Draft v0.3 digest change in the future merely because an unrelated M26 profile fragment was added. Such behavior would defeat the purpose of a release freeze.

Before acceptance, M25 changed the rule so an additive fragment is committed only when it defines the selected profile or contains a case whose capability is selected by that profile. The complete manifest is still globally validated before selection.

An executable regression copies the conformance tree, adds an unrelated future profile fragment, and requires the Draft v0.3 digest/file inventory to remain unchanged.

The current Draft v0.3 corpus already selects all existing accepted capabilities, so this future-growth correction does not change the pinned digest; it changes the stability rule for later additive repository growth.

## Profile metadata defect fixed

The integration audit found that standalone `olp-conformance-profile-v1` files did not all satisfy one common shape:

- older files carried `status` without `version`;
- newer files carried `version` without `status`; and
- the schema required `status` but did not permit `version`.

M25 normalizes all standalone profile documents to:

```text
schema
id
version
status
capabilities
```

with `version: 1` and `status: draft-v0.3` for the Draft v0.3 repository snapshot.

Executable tests require each standalone profile capability list to exactly match the same profile loaded from the conformance manifest/fragments.

No capability identifier or vector semantics changed as part of this repair.

## Specifications

Specification 0013 remains the general Draft v0.2-era governance baseline for version domains, identifiers, registries, extensions, reason codes, migration, and capability stability.

M25 deliberately did not rewrite its historical narrative to pretend Draft v0.2 had already completed later work.

Instead, new Specification 0014 defines:

- Draft v0.3 aggregate release profiles;
- release-profile case selection;
- profile metadata shape;
- contribution-scoped corpus file selection;
- SHA-256 file commitments;
- binary commitment framing;
- release-manifest pinning; and
- Draft v0.2 → Draft v0.3 compatibility.

Specification 0014 supersedes only stale repository-status statements from the older integration snapshot; it does not replace Specification 0013's general governance rules.

## Compatibility

Draft v0.3 does not require regeneration, rewriting, re-signing, or re-identification of conforming Draft v0.2 v1 objects solely because the specification-set release label changed.

The release manifest explicitly records that Draft v0.3 does not change:

- Record Identity v1;
- ProofInputV1;
- `eddsa-ed25519-v1`;
- Proof Identity v1;
- `EvidenceRefV1`; or
- accepted capability semantics.

A future change that alters those semantics must be explicitly versioned or recorded as errata/breaking change; it cannot be hidden inside a set-release label.

## Security meaning

Draft v0.3 materially strengthens auditability because an implementation can now name both:

1. the aggregate profile it claims; and
2. the exact corpus commitment behind that claim.

It does not certify production deployment security.

Specifically outside the Draft v0.3 conformance claim remain:

- live production HTTP client/server behavior;
- DNS/TLS implementation security;
- production proxies/caches;
- operational key management;
- authentication/authorization frameworks;
- production-scale denial-of-service resistance;
- supply-chain/operations monitoring and incident response; and
- independent external cryptographic/security audit.

## Remaining path toward v1.0

Draft v0.3 closes important release-engineering gaps but should not be mislabeled v1.0.

The highest-value remaining stabilization work is likely to include:

- choosing an explicit stable-profile promotion boundary;
- wider contradiction/errata review of the proposed stable surface;
- independent external security review of that exact boundary;
- final migration/deprecation policy for stable releases; and
- explicit deployment/threat assumptions for any network behavior promoted into a stable profile.

The next milestone should be selected from those stabilization needs rather than by adding unrelated features for momentum.
