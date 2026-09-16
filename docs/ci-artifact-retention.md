# Routine CI artifact retention

Routine conformance and candidate-readiness uploads explicitly expire after
seven days. All nine upload steps keep their existing report sets, names,
failure behavior and full Python/Rust/Windows validation matrix.

This changes future routine CI storage only. Existing artifacts, frozen source
commits, corpus commitments, accepted review evidence and review-target metadata
are unchanged. It is not a new frozen review target or a promotion decision.

Before a routine report is used as durable release or independent-review
evidence, the owner must preserve it in the project-scoped review archive with
its exact source commit, workflow run/attempt, artifact identity and verified
digest. An expiring Actions download is not a durable review reference.

Rollback restores the prior workflow retention settings; it cannot restore
already expired artifacts. No existing artifact is deleted by this change.
