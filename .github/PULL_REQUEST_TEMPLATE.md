## Summary

Describe the change and why it is needed.

## Scope

Check every surface this PR changes:

- [ ] non-normative/project documentation only
- [ ] normative specification wording
- [ ] Python implementation
- [ ] Rust implementation
- [ ] conformance vectors / expected outcomes
- [ ] interoperability tests
- [ ] promotion evaluator / schemas
- [ ] stabilization / review-target metadata
- [ ] CI / tooling
- [ ] other

## Protocol-semantic impact

Does this PR change any of the following?

- [ ] accepted deterministic bytes
- [ ] Record Identity
- [ ] Proof Identity
- [ ] ProofInput construction
- [ ] cryptographic algorithm or key binding
- [ ] capability semantics
- [ ] conformance corpus membership or commitment
- [ ] candidate/stable promotion meaning
- [ ] none of the above

Explain any checked semantic impact:

## v1.0 review-target impact

Current frozen target:

```text
olp-v1.0-review-2
d470970180bfa128ca14fd01ac920c95dd8ec288
```

- [ ] This PR is operational/editorial and does not change the frozen reviewed source.
- [ ] This PR is a material source-changing fix and may require a new review target.
- [ ] Not applicable.

If a new review target may be required, explain why. Do not silently rebind review evidence from an older target. `olp-v1.0-review-1` and any later superseded targets remain historical evidence for their original source bytes.

## Finding / issue linkage

Related issue or review finding:

## Verification

List the tests, conformance profiles, commitment checks, or manual verification performed.

For deterministic behavior changes, include Python/Rust parity and direct interoperability evidence where applicable. For repository-byte or release-reproducibility changes, include the Windows `core.autocrlf=true` path where relevant.

## Security

- [ ] No security-sensitive details are exposed publicly.
- [ ] `SECURITY.md` was followed for any sensitive finding.

## Checklist

- [ ] The change is narrowly scoped.
- [ ] Documentation and tests match the claimed semantics.
- [ ] Existing accepted vectors were not silently rewritten.
- [ ] JSON object order was not made semantic.
- [ ] Conformance was not described as security certification.
- [ ] Public/internal review was not described as independent external security review.
- [ ] Review evidence was not silently carried across changed source bytes.
