# v1.0 external-review evidence intake

This document defines a **review coordination artifact**, not protocol semantics and not review evidence by itself.
It does not modify the frozen `olp-v1.0-review-4` source.

The only review-4 source that can satisfy either external gate remains:

```text
review target:  olp-v1.0-review-4
source commit:  c293c5524318b342149a80c3e0322e29742f44f7
```

A reviewer may provide a JSON evidence packet conforming to
`stabilization/schemas/v1-external-review-evidence.schema.json` and then run:

```bash
olp-conformance review-evidence-check \
  --candidate stabilization/v1.0-candidate.json \
  --evidence /path/to/reviewer-evidence.json \
  --json
```

The validator is intentionally read-only. A valid packet produces the exact `external_gates` payload that
could be considered for a later reviewed candidate-manifest update. It never edits the candidate or marks a
gate complete.

## Required evidence fields

- gate: public technical review or independent external security review;
- exact review target ID and source SHA;
- reviewer name and organization;
- independence statement (mandatory for the independent security gate);
- methodology and scope;
- final findings and dispositions;
- explicitly excluded areas;
- residual risks;
- one or more durable HTTPS references; and
- `completed: true`.

High/critical findings cannot be accepted merely as residual risk by this intake format. They must be resolved
before the packet can validate. Security-sensitive details still belong in private vulnerability reporting;
public durable references may identify a private/project-verifiable review record without publishing exploit
details.

A successful intake validation is **not** itself a promotion decision. Maintainers must still assess reviewer
independence, scope sufficiency, finding disposition, and durable evidence before changing a gate from pending
to completed. The normal promotion evaluator remains the final source-binding check.
