# OLP v1 Public Technical Review Guide

**Status:** review guide; review target not yet frozen  
**Candidate:** `olp-v1.0`  
**Current mandatory candidate core:** `core-v1`

## Review goal

The public technical review is intended to challenge the proposed OLP v1.0 candidate boundary before stable promotion. It is not a vote on branding or project direction and it is not a substitute for independent security review.

The exact source commit will be inserted into the machine-readable candidate metadata only after the review-binding hardening itself is merged and verified. Reviewers should not treat an unfrozen branch tip as the review target.

## Primary questions

Reviewers are especially asked to identify:

- normative contradictions across Specifications 0001–0015;
- ambiguous canonicalization or identity rules that could produce cross-implementation disagreement;
- proof-input or proof-purpose ambiguity;
- places where identity, authority, lifecycle, trust, or authorization are accidentally conflated;
- bundle/disclosure semantics that could overclaim completeness or nonexistence;
- resolver/HTTP semantics that could overclaim verification or global existence;
- privacy/correlation risks that are understated or internally inconsistent;
- extension/versioning rules that could permit silent downgrade or semantic drift;
- stable-promotion rules that could reuse stale conformance or review evidence; and
- migration/deprecation/errata rules that could silently rewrite historical evidence.

## Candidate boundary

The mandatory candidate core is exactly the existing eight-capability `core-v1` profile:

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

The following remain optional candidates:

```text
bundle-v1
resolution-v1
identity-authority-lifecycle-v1
privacy-disclosure-v1
transport-encoding-v1
streaming-http-v1
```

Optional profiles are not silently required for a mandatory-core conformance claim.

## Reproduction

From the eventual frozen review commit, reviewers can run:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
olp-conformance run --profile core-v1
olp-conformance run --profile draft-v0.3-interoperable-v1
olp-conformance commitment --profile core-v1 --json
olp-conformance commitment --profile draft-v0.3-interoperable-v1 --json
olp-conformance promotion-check --candidate stabilization/v1.0-candidate.json --json
```

Expected corpus commitments are:

```text
core-v1
8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e

draft-v0.3-interoperable-v1
62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

The promotion state is expected to remain `BLOCKED` throughout review until both public technical review and independent external security review are genuinely completed for the same frozen review target.

## Finding format

A useful public review finding should identify:

1. the frozen source commit;
2. affected specification section(s) or implementation file(s);
3. finding class (`ambiguity`, `interoperability`, `security`, `privacy`, `governance`, `editorial`, or other clearly described class);
4. severity or likely impact;
5. a concrete conflicting interpretation, reproduction, or attack scenario where possible; and
6. whether the proposed resolution would change deterministic bytes or capability semantics.

Security-sensitive exploit details should follow `SECURITY.md` rather than being posted publicly when disclosure would create avoidable risk.

## Review completion

Public review is not complete merely because an issue exists or a period of time has elapsed.

Completion requires durable references to the exact frozen source commit and disposition of material findings. If a material source change results, a new review target must be frozen and review evidence for the older commit cannot satisfy the new target automatically.
