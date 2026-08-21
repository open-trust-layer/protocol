# OLP v1 Review Target Status

The second snapshot-bound OLP v1.0 review target is now frozen.

```text
review target:          olp-v1.0-review-2
status:                 frozen
source commit:          d470970180bfa128ca14fd01ac920c95dd8ec288
public review:          pending
external security:      pending
stable promotion:       BLOCKED
```

Review-2 supersedes review-1 after Issue #21 identified a cross-platform checkout reproducibility defect: exact-byte corpus commitments and required-artifact digests could fail on Git for Windows checkouts with `core.autocrlf=true` because review-1 had no repository line-ending policy.

The frozen review-2 source includes:

- root `.gitattributes` enforcing LF working-tree bytes for text and excluding common binary formats;
- a hash-critical repository-byte regression; and
- a Windows readiness job that enables `core.autocrlf=true` before checkout and reruns the actual reviewer commitment and promotion commands.

The published corpus commitments remain unchanged because the committed conformance corpus bytes did not change.

Historical review-1 remains immutable:

```text
review target:          olp-v1.0-review-1
status:                 historical / superseded
source commit:          877493826d673ccf9bb94e7b6b113b35141ad220
reason superseded:      Issue #21 checkout-byte reproducibility defect
```

No review-1 completion evidence is carried forward automatically.

Public technical review is coordinated in Issue #24. Independent external security review is coordinated in Issue #25. Both gates remain pending and must identify the exact frozen review-2 source commit before either gate can be completed.
