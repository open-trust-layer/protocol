# OLP v1 Public Technical Review Guide

**Status:** open-review guide  
**Candidate:** `olp-v1.0`  
**Review target:** `olp-v1.0-review-4`
**Frozen source commit:** `c293c5524318b342149a80c3e0322e29742f44f7`
**Public review tracker:** Issue #37
**Current mandatory candidate core:** `core-v1`

## Review goal

The public technical review is intended to challenge the proposed OLP v1.0 candidate boundary before stable promotion. It is not a vote on branding or project direction and it is not a substitute for independent security review.

`olp-v1.0-review-4` supersedes `olp-v1.0-review-3` after an external reviewer found that the review-3 source's `SECURITY.md` still named review-2 and the superseded trackers. The correction and rollover rationale are recorded in `docs/v1-review-4-rollover.md`.

Review-2 had earlier superseded review-1, which did not enforce deterministic LF working-tree bytes on Git for Windows checkouts with `core.autocrlf=true`. That defect is recorded in Issue #21 and `docs/v1-review-2-rollover.md`; the review-3 source retains its correction.

Review-1 remains immutable historical evidence for source commit `877493826d673ccf9bb94e7b6b113b35141ad220`. Its review evidence, if any, does not automatically satisfy review-3.

Reviewers must inspect the exact frozen review-4 source above. A branch tip, review-3, later `main`, or another commit is not the review-4 target.

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
- stable-promotion rules that could reuse stale conformance or review evidence;
- migration/deprecation/errata rules that could silently rewrite historical evidence; and
- release/corpus reproduction assumptions that depend on host platform, Git checkout policy, filesystem behavior, locale, or newline conversion.

## Candidate boundary

The mandatory candidate core remains exactly the existing eight-capability `core-v1` profile:

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

## Reproduction invariant

The frozen review-4 source includes a root `.gitattributes` policy that forces LF working-tree bytes for textual files and explicit binary exclusions. The v1 candidate readiness workflow includes a `windows-latest` job that sets `core.autocrlf=true` before checkout, verifies effective Git attributes, and runs the actual reviewer-facing commitment and promotion commands.

Check out exactly:

```text
c293c5524318b342149a80c3e0322e29742f44f7
```

Then run:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
olp-conformance run --profile core-v1
olp-conformance run --profile draft-v0.3-interoperable-v1
olp-conformance commitment --profile core-v1 --json
olp-conformance commitment --profile draft-v0.3-interoperable-v1 --json
olp-conformance promotion-check --candidate stabilization/v1.0-candidate.json --json
```

Expected corpus commitments remain unchanged:

```text
core-v1
8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e

draft-v0.3-interoperable-v1
62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

The promotion state is expected to remain `BLOCKED` throughout review until both public technical review and independent external security review are genuinely completed for this same frozen target.

### Expected `review_target` output at the frozen source

The frozen source necessarily contains the preparation state because a commit cannot contain its own eventual hash:

```text
status:                       BLOCKED
internal_readiness:           PASS
review_target_id:             olp-v1.0-review-4
review_target_status:         preparing
review_target_source_commit:  null
REVIEW_TARGET:                PASS  review target is valid and awaiting an immutable source commit
SECURITY_REVIEW_TARGET:       PASS  SECURITY.md names the active review target olp-v1.0-review-4
```

This is expected. It is not a defect and it does not mean you checked out the wrong commit.

A later metadata-only commit binds `olp-v1.0-review-4` to `c293c5524318b342149a80c3e0322e29742f44f7`. The frozen bytes already name review-4 in `SECURITY.md`, and the evaluator verifies that identifier against the candidate manifest.

That commit changes `review_target.status` and `review_target.source_commit` in `stabilization/v1.0-candidate.json`, the assertions in `tests/conformance/test_promotion.py` and `tests/conformance/test_promotion_schemas.py` that track the checked-in candidate's own state, and reviewer-facing prose. It changes no specification, implementation, conformance vector, corpus commitment, or promotion-gate logic.

Unlike review-3, the preparation snapshot itself already identifies review-4 in `SECURITY.md`. The evaluator verifies that identifier against the candidate manifest before the target can be considered internally ready.

The evaluator's refusal to let an external gate complete while `review_target.status` is `preparing` is deliberate fail-closed behavior: review evidence cannot be bound to a target that has no immutable source commit.

## Finding format

A useful public review finding should identify:

1. exact frozen review-4 source commit;
2. affected specification section(s) or implementation file(s);
3. finding class (`ambiguity`, `interoperability`, `security`, `privacy`, `governance`, `reproducibility`, `editorial`, or other clearly described class);
4. severity or likely impact;
5. a concrete conflicting interpretation, reproduction, or attack scenario where possible; and
6. whether the proposed resolution would change deterministic bytes or capability semantics.

Public findings belong in Issue #37 or a dedicated linked issue. Security-sensitive exploit details should follow `SECURITY.md` rather than being posted publicly when disclosure would create avoidable risk.

## Review completion

Public review is not complete merely because a tracker issue exists or a period of time has elapsed.

Completion requires durable references that identify the exact frozen review-4 source commit and disposition of material findings. If a later material source change results, a new review target must be frozen and review-4 evidence cannot satisfy that new target automatically.
