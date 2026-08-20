# OLP v1 Review-Binding Hardening

**Status:** pre-review stabilization note  
**Protocol semantics changed:** no  
**Accepted conformance corpus changed:** no

## Purpose

Milestone 26 correctly required durable references before public technical review or independent external security review could satisfy stable promotion. During post-M26 review preparation, one additional fail-closed requirement was identified: a durable review reference must be bound to the exact candidate source snapshot it reviewed.

Without source binding, a legitimate review of an older candidate could be cited after the source changed and could accidentally satisfy a later promotion attempt.

## Resolution

Promotion candidate metadata is revised from schema v1 to schema v2.

The v1 schemas remain checked in as historical contracts. The current v2 candidate adds a review target:

```text
id
status
source_commit
```

Review-target states are:

```text
preparing
frozen
```

While `preparing`, `source_commit` is null. Once the hardening changes themselves are merged and fully verified, the first public review target will be frozen to that exact merge commit in a separate metadata-only change.

Each external gate now contains:

```text
status
reviewed_commit
references
```

A pending gate must carry neither a reviewed commit nor stale references.

A completed gate is valid only when:

1. the review target is frozen;
2. the gate contains at least one durable reference;
3. `reviewed_commit` is a canonical 40-character lowercase Git commit id; and
4. `reviewed_commit` exactly equals the frozen review target's `source_commit`.

A mismatch produces `INVALID`, not ordinary `BLOCKED`.

## Review-round immutability

A frozen review-target identifier must not be rebound to different source bytes merely to reuse review evidence.

If public or security review causes a material source change, the project must create a new review-target identifier and both affected external gates return to pending for that new target.

## Non-effects

This hardening does not change:

- any OLP Record/Proof/Evidence identity construction;
- any cryptosuite;
- any accepted capability semantics;
- any conformance vector or expected result;
- the 62-case `core-v1` corpus commitment;
- the 180-case Draft v0.3 corpus commitment;
- the mandatory/optional candidate profile boundary; or
- the requirement for genuinely independent external security review.

The change only prevents stale or mismatched external-review evidence from satisfying the promotion gate.
