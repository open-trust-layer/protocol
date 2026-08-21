# OLP v1 Review Target Status

The OLP v1.0 candidate is preparing its second snapshot-bound external review target.

```text
review target:          olp-v1.0-review-2
status:                 preparing
source commit:          not yet frozen
public review:          pending
external security:      pending
stable promotion:       BLOCKED
```

Review-2 supersedes review-1 after Issue #21 identified a cross-platform checkout reproducibility defect: exact-byte corpus commitments and required-artifact digests could fail on Git for Windows checkouts with `core.autocrlf=true` because review-1 had no repository line-ending policy.

The corrected source now includes:

- root `.gitattributes` enforcing LF working-tree bytes for text and excluding common binary formats;
- a hash-critical repository-byte regression; and
- a Windows readiness job that enables `core.autocrlf=true` before checkout and reruns the actual reviewer commitment and promotion commands.

The published corpus commitments remain unchanged because the committed repository blobs used by the corpus did not change.

Historical review-1 remains immutable:

```text
review target:          olp-v1.0-review-1
status:                 historical / superseded
source commit:          877493826d673ccf9bb94e7b6b113b35141ad220
reason superseded:      Issue #21 checkout-byte reproducibility defect
```

No review-1 completion evidence is carried forward automatically.

After this preparation snapshot is merged and the full repository matrix passes, a metadata-only follow-up will bind `olp-v1.0-review-2` to the exact immutable preparation-source commit. Public technical review and independent external security review must then identify that exact source commit before either gate can be completed.
