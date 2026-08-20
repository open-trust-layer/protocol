# OLP v1 Review Package Index

**Status:** preparation index; source snapshot not yet frozen

This index collects the materials intended to accompany the first public/external review round for the OLP v1.0 candidate.

## Candidate and promotion state

- `stabilization/v1.0-candidate.json`
- `specification/0015-stable-profile-promotion-and-readiness.md`
- `docs/v1-candidate-readiness.md`
- `docs/v1-release-process.md`

## Security context

- `docs/v1-threat-model.md`
- `SECURITY.md`
- `docs/security-review-milestone-17.md`
- `docs/v1-external-security-review-brief.md`

## Public technical review

- `docs/v1-public-review-guide.md`
- `stabilization/v1-review-register.json`

## Conformance and interoperability

- `specification/0011-conformance-and-interoperability.md`
- `specification/0014-release-profiles-and-conformance-suite-commitments.md`
- `conformance/README.md`
- `specification/releases/draft-v0.3.json`

Expected corpus commitments:

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

The first review target is named:

```text
olp-v1.0-review-1
```

Its exact source commit is intentionally not written here until the snapshot-binding hardening is merged and fully verified. The next metadata-only step will freeze that identifier to the exact merge commit and open the public review tracker against that SHA.

Reviewers should not treat a moving branch tip as the review target.
