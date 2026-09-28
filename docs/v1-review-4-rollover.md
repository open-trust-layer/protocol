# OLP v1 Review-4 Rollover

**Status:** review-governance record
**Previous target:** `olp-v1.0-review-3`
**Previous source:** `f0dd778f09f904e334477bb1d6294f78d3d466f0`
**New target:** `olp-v1.0-review-4`
**New source:** not yet frozen

## Why review-3 was superseded

An external reviewer examining the exact review-3 source reported a source-binding consistency defect in Issue #35. The frozen checkout's `SECURITY.md` still identified `olp-v1.0-review-2` and routed reviewers to Issues #24 and #25, while the later freeze metadata and trackers identified review-3 and Issues #34 and #35.

The two-commit freeze lifecycle intentionally prevents a source snapshot from containing its own eventual Git hash. It does not require the snapshot to carry a stale review-target identifier. A reviewer must be able to determine from the reviewed bytes which review round the source was prepared for.

## Correction

Review-4 adds a repository invariant with three parts:

1. the preparation snapshot names `olp-v1.0-review-4` in both `SECURITY.md` and the candidate manifest;
2. Specification 0015 requires those active target identifiers to agree before and after freeze; and
3. the promotion evaluator fails closed with `SECURITY_REVIEW_TARGET = FAIL` if they disagree.

The candidate begins in `preparing` state with `source_commit = null`. After the full repository matrix passes, a later metadata-only commit binds review-4 to the immutable preparation commit. The frozen source therefore contains the correct review-target identifier even though, necessarily, it cannot contain its own eventual hash.

## Invariants preserved

This rollover changes review governance and its executable validation only. It does not alter:

- OLP evidence or wire semantics;
- Record Identity, Proof Identity, `ProofInputV1`, or any identity-bearing construction;
- candidate capability membership;
- conformance vectors, expected outcomes, or accepted case selection;
- the `core-v1` corpus commitment; or
- the `draft-v0.3-interoperable-v1` corpus commitment.

Both external gates remain pending. Review-3 evidence and discussion remain historical and are not rebound to review-4.

## Finding provenance

The finding was reported publicly by Shxnque (Quelum Wilson) in Issue #35 after review of the exact review-3 source commit. The project records the finding as source-level review evidence, not as completion of the independent external security-review gate.
