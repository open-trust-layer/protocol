# OLP v1 Release, Migration, Deprecation, and Errata Process

**Status:** Milestone 26 candidate-stabilization process  
**Applies to:** promotion from Draft v0.3/candidate status toward a future stable OLP v1.0

## 1. Purpose

This document defines release mechanics that are intentionally separate from OLP evidence semantics.

A release label must never silently rewrite Record Identity, ProofInputV1, Proof Identity, EvidenceRefV1, cryptosuite semantics, or an already-published capability identifier.

## 2. Candidate stages

The project uses these conceptual stages:

```text
draft -> candidate -> release candidate -> stable
```

A stage name is repository/release metadata. It is not an authenticated field in existing OLP v1 evidence unless a specific future profile explicitly makes it one.

`candidate` means a boundary has been selected for stabilization. It does not mean the boundary has completed independent review.

`release candidate` means all promotion gates except final publication mechanics have been satisfied and the exact release snapshot is frozen for final verification.

`stable` means the documented stable-promotion gates have been satisfied and an immutable release has been published.

## 3. Mandatory stable core

The mandatory v1.0 core candidate is the existing `core-v1` profile.

Stable promotion must not silently add an optional higher-layer profile to the mandatory core. Such a change requires an explicit release-profile decision and review.

Optional profiles may be promoted independently and must be named explicitly by implementations that claim them.

## 4. Pre-release gates

Before a release candidate may be described as ready for stable publication:

1. the mandatory candidate profile and every optional profile proposed for stable promotion must be identified exactly;
2. the exact conformance corpus must have a reproducible suite commitment;
3. at least two independent implementations must pass the exact claimed corpus;
4. normative-byte constructions must have direct cross-implementation equality evidence where applicable;
5. malformed, negative, unsupported, policy, and resource-limit behavior required by the claimed boundary must remain tested;
6. no unresolved normative contradiction may remain inside the proposed stable boundary;
7. the candidate threat model must be current;
8. migration, deprecation, errata, and release procedures must be documented;
9. independent external security review must be completed and referenced;
10. public technical review must be completed and referenced; and
11. high/critical findings affecting the stable boundary must be resolved or cause promotion to remain blocked.

A conformance pass cannot waive gates 6–11.

## 5. Release snapshot

A stable release must identify an immutable source snapshot.

The release record must name:

- the stable release identifier;
- the exact source commit;
- the exact mandatory and optional stable profiles;
- the exact capability lists;
- the conformance suite commitment(s);
- the implementation versions used for acceptance;
- external-review references;
- public-review references;
- migration/deprecation status; and
- any accepted errata.

The release manifest must be committed before or as part of the release snapshot without creating self-referential hash requirements.

## 6. Tag and provenance

A stable release must use an immutable annotated Git tag identifying the release source commit.

The project should cryptographically sign the release tag or otherwise provide cryptographically verifiable release provenance through the project-controlled release process.

Published stable tags must never be moved or reused for different source bytes.

If a release credential is compromised, the incident must be documented and repaired with new provenance rather than silently moving the old tag.

## 7. Conformance artifacts

Stable-release acceptance should retain machine-readable conformance reports and suite-commitment diagnostics for the independent implementations used for promotion.

The corpus commitment identifies test material. Reports identify observed execution. Neither is a security certification.

## 8. Migration from Draft v0.3

If the v1.0 stable core preserves the currently accepted v1 deterministic constructions, Draft v0.3 conforming v1 Records and Proofs do not need regeneration, re-signing, or re-identification merely because the set-release label changes.

An implementation migration may require:

- stricter validation;
- new supported/unsupported capability declarations;
- updated reason-code handling;
- updated registry metadata;
- new release-profile declarations; or
- updated deployment/security policy.

Historical immutable evidence remains under its existing identity.

If external review finds a defect that requires changed deterministic bytes or materially different capability semantics, the affected version/capability must change explicitly and migration instructions must state the break.

## 9. Deprecation

Stable objects, encodings, cryptosuites, capabilities, and compact identifiers must not disappear silently.

A deprecation notice must identify:

- the deprecated identifier/version;
- the reason;
- security impact where applicable;
- replacement, if any;
- whether verification of historical evidence remains required; and
- the release in which production or generation support changes.

Deprecation does not rewrite historical evidence.

Security-driven deprecation may recommend immediate cessation of new use while retaining explicit historical verification behavior when safe.

## 10. Breaking changes after stable release

A breaking change includes a change that causes previously conforming deterministic input to produce different identity/proof bytes or materially changes an existing capability's meaning.

Breaking changes require the appropriate new object, encoding, cryptosuite, capability, or profile version.

A stable release label, erratum, implementation patch version, or editorial specification update must not be used to hide a breaking semantic change.

## 11. Clarifications and errata

An erratum may retain an existing version only when the previous text was unambiguously inconsistent with the already-defined interoperable behavior and correcting the text does not create two legitimate conforming interpretations.

Every stable erratum must record:

- an identifier;
- affected document/section;
- classification (`editorial`, `clarifying`, `security`, or `breaking`);
- old interpretation;
- corrected interpretation;
- effect on vectors/capabilities; and
- release applicability.

A breaking erratum is not merely an erratum for versioning purposes; it must trigger explicit version migration.

## 12. Vulnerability fixes

Security fixes follow the coordinated disclosure process in `SECURITY.md`.

When a vulnerability affects stable protocol semantics, the project must determine whether the fix is:

- implementation-only;
- clarifying without semantic break;
- additive compatible; or
- breaking.

The classification and any vector/capability changes must be public when disclosure permits.

## 13. Optional-profile promotion

Optional profiles are promoted independently.

A stable release manifest must distinguish:

```text
mandatory stable core
optional stable profiles
candidate/draft profiles not promoted
```

An implementation claiming only the mandatory stable core must not be described as non-conforming merely because it omits an optional profile.

## 14. Rollback

Evidence history is not rolled back by moving release metadata.

If a release is withdrawn, the project publishes a new status/advisory identifying the affected release and replacement guidance. Stable tags and old release manifests remain immutable historical artifacts.

## 15. Final stable publication checklist

Before stable publication, release automation or maintainers must verify:

- promotion evaluator status is `READY`;
- source commit and tag target are exact;
- release manifest is complete;
- suite commitments recompute;
- required conformance reports pass with no required skips;
- external and public-review references are present;
- unresolved high/critical release blockers are absent; and
- repository status/security documentation matches the published release.

If any item fails, stable publication is blocked.
