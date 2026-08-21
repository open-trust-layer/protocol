---
name: Technical review finding
about: Report a public, non-sensitive finding against a frozen OLP review target
title: "[Review finding] "
labels: ""
assignees: ""
---

## Reviewed source

Review target:

```text
olp-v1.0-review-1
```

Exact source commit:

```text
877493826d673ccf9bb94e7b6b113b35141ad220
```

If you reviewed a different source, replace the values above and explain why.

## Finding summary

Describe the issue concisely.

## Affected surface

Specification section(s):

Implementation/component(s), if applicable:

Conformance case/vector(s), if applicable:

## Expected behavior

What should a conforming implementation or reader conclude?

## Observed behavior / conflicting interpretation

What happens instead, or which two plausible interpretations disagree?

## Reproduction or attack scenario

Provide the smallest useful reproduction, input, vector, or scenario.

## Impact

Check all that apply:

- [ ] deterministic-byte disagreement
- [ ] Record Identity / Proof Identity disagreement
- [ ] proof or cryptographic binding issue
- [ ] interoperability defect
- [ ] authority / lifecycle / policy confusion
- [ ] privacy / correlation issue
- [ ] resource-exhaustion / amplification issue
- [ ] transport / resolver / HTTP ambiguity
- [ ] release / promotion / stale-evidence issue
- [ ] editorial ambiguity only
- [ ] other

Suggested severity/priority, with rationale:

## Source-change consequence

Would the proposed resolution change deterministic bytes or capability semantics?

- [ ] no
- [ ] yes
- [ ] unsure

If yes or unsure, explain.

## Sensitive information check

- [ ] I believe this report is safe to discuss publicly.
- [ ] This may contain exploitable or security-sensitive details.

**If the second box applies, stop and do not submit this public issue. Follow `SECURITY.md` and use the private reporting path instead.**
