# OLP v1 Review-Round Lifecycle

**Status:** review-process guidance

The OLP v1 candidate uses explicit review rounds so public/security review evidence cannot be silently reused after the reviewed source changes.

## States

A review target begins as:

```text
preparing
```

with no source commit.

After all pre-review hardening changes pass the full repository matrix, a metadata-only follow-up freezes the target:

```text
frozen
```

and records one exact immutable Git source commit.

## Completion binding

Public technical review and independent external security review remain separate gates. Each completed gate must contain:

- `status = completed`;
- `reviewed_commit` equal to the frozen target commit; and
- one or more durable references.

A completed review against any other commit is invalid for that target.

## Findings after freeze

Editorial discussion alone does not require a new round when the frozen source bytes remain unchanged.

If finding disposition changes source bytes within the reviewed candidate boundary, the project must:

1. keep the old review target as historical evidence;
2. create a new review-target identifier;
3. freeze the corrected source under the new identifier after CI passes; and
4. return affected external gates to pending for the new target.

The old review may remain relevant background evidence, but it cannot automatically satisfy completion for changed source.

## Relationship to stable publication

A review round is not a stable release tag and does not change OLP evidence identity. It is release-governance metadata used to prove which exact source was independently examined.
