# OLP v1 Review Package Index

**Status:** review-2 package preparing  
**Review target:** `olp-v1.0-review-2`  
**Source commit:** not yet frozen

This index collects the materials for the second public/external review round of the OLP v1.0 candidate.

Review-2 supersedes review-1 because the review-1 source did not enforce deterministic LF working-tree bytes for Git for Windows checkouts with `core.autocrlf=true`. The defect and rollover rationale are recorded in Issue #21 and `docs/v1-review-2-rollover.md`.

## Candidate and promotion state

- `stabilization/v1.0-candidate.json`
- `specification/0015-stable-profile-promotion-and-readiness.md`
- `docs/v1-candidate-readiness.md`
- `docs/v1-release-process.md`
- `docs/v1-review-round-lifecycle.md`
- `docs/v1-review-preparation-status.md`

## Security context

- `docs/v1-threat-model.md`
- `SECURITY.md`
- `docs/security-review-milestone-17.md`
- `docs/v1-external-security-review-brief.md`

## Public technical review

- `docs/v1-public-review-guide.md`
- `stabilization/v1-review-register.json`

## Review-2 rollover and cross-platform reproduction

- `docs/v1-review-2-rollover.md`
- `.gitattributes`
- `tests/conformance/test_repository_byte_reproducibility.py`
- `.github/workflows/v1-candidate-readiness.yml`

The readiness workflow includes a Windows job that sets `core.autocrlf=true` before checkout and then runs the exact-byte regressions plus the reviewer-facing corpus commitment and promotion commands.

## Conformance and interoperability

- `specification/0011-conformance-and-interoperability.md`
- `specification/0014-release-profiles-and-conformance-suite-commitments.md`
- `conformance/README.md`
- `specification/releases/draft-v0.3.json`

Expected corpus commitments remain unchanged:

```text
core-v1
8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e

draft-v0.3-interoperable-v1
62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

## Normative candidate boundary

Mandatory candidate specifications:

```text
0001
0002
0003
0004
0005
0011
0013
0014
0015
```

Optional candidate profile specifications:

```text
0006, 0007  identity-authority-lifecycle-v1
0008        bundle-v1
0009        resolution-v1
0010        privacy-disclosure-v1
0012        transport-encoding-v1 / streaming-http-v1
```

Specification 0000 is the non-normative overview and should also be reviewed for misleading summaries.

## Source binding

Review-2 is currently in `preparing` state and therefore has no source commit yet.

After the preparation snapshot is merged and fully verified, a metadata-only follow-up will freeze:

```text
id:             olp-v1.0-review-2
source commit:  <exact immutable SHA>
```

Reviewers must then inspect that exact commit. A branch tip, later commit, or review of different source does not satisfy the promotion gate for this target.

Historical review-1 remains bound to:

```text
id:             olp-v1.0-review-1
source commit:  877493826d673ccf9bb94e7b6b113b35141ad220
```

Review evidence for review-1 does not automatically satisfy review-2.
