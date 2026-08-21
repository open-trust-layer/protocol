# Contributing to Open Layer Protocol

Thank you for helping review or improve Open Layer Protocol (OLP).

OLP is currently an **experimental pre-1.0 candidate**. The project is in external review, so precision and source attribution matter more than feature velocity.

## Current review round

The first v1.0 review target is frozen as:

```text
review target:  olp-v1.0-review-1
source commit:  877493826d673ccf9bb94e7b6b113b35141ad220
```

If your contribution is a finding about the v1.0 candidate, identify that exact source commit in the issue or report.

A later `main` commit may contain documentation, review coordination, or other maintenance work. Review evidence for `olp-v1.0-review-1` must still refer to the exact frozen source above.

## Before opening an issue

Please distinguish between:

- **Public technical findings:** specification ambiguity, interoperability disagreement, deterministic-byte disagreement, conformance gaps, governance contradictions, or non-sensitive implementation defects. These may be reported publicly.
- **Security-sensitive findings:** exploitable vulnerabilities, practical attack details, secret material, or information that would materially increase exploitation risk. Do **not** publish these in a public issue; follow `SECURITY.md`.

The public technical-review tracker is Issue #17. Independent security-review coordination is Issue #18.

## High-value review areas

External review is especially useful for:

- cross-specification contradictions;
- Record Identity / Proof Identity / canonicalization disagreement;
- proof-input, algorithm, key, verification-method, record, or proof-purpose substitution;
- identity / authority / lifecycle / authorization confusion;
- bundle completeness, evidence withholding, and nonexistence claims;
- resolver / HTTP success versus cryptographic verification or global existence;
- privacy and correlation assumptions;
- extension, registry, downgrade, migration, deprecation, and errata behavior;
- parser, graph, bundle, and resource-exhaustion boundaries;
- transport, framing, encoding, and content-integrity ambiguity;
- conformance-corpus drift; and
- stale review-evidence reuse during promotion.

## Reproducing the frozen target

Check out the exact source:

```bash
git checkout 877493826d673ccf9bb94e7b6b113b35141ad220
```

Install the Python implementation and tests:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

Run the mandatory candidate core:

```bash
olp-conformance run --profile core-v1
```

Run the Draft v0.3 aggregate profile:

```bash
olp-conformance run --profile draft-v0.3-interoperable-v1
```

Recompute the exact corpus commitments:

```bash
olp-conformance commitment --profile core-v1 --json
olp-conformance commitment --profile draft-v0.3-interoperable-v1 --json
```

Expected commitments:

```text
core-v1
8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e

draft-v0.3-interoperable-v1
62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

## Writing a useful technical finding

A strong finding should include:

1. exact reviewed source commit;
2. affected specification section(s) and/or implementation component(s);
3. expected behavior;
4. observed behavior or conflicting interpretation;
5. a minimal reproduction, test vector, or attack scenario where possible;
6. interoperability or security impact;
7. whether deterministic bytes or capability semantics would need to change; and
8. whether the finding appears editorial, implementation-only, conformance-related, normative, or security-sensitive.

Do not overstate severity. A reproducible ambiguity that causes conforming implementations to disagree is valuable even if it is not exploitable.

## Pull requests

Keep pull requests narrow and explain the semantic surface they touch.

A PR should state whether it changes any of the following:

- normative specification meaning;
- accepted deterministic bytes;
- Record Identity or Proof Identity;
- proof-input construction;
- capability semantics;
- conformance vectors or expected outcomes;
- release/profile corpus commitments;
- promotion evaluator behavior;
- frozen review-target metadata; or
- only non-normative/project documentation.

Passing tests are necessary but do not by themselves prove that a protocol-semantic change is acceptable.

When a bug fix affects protocol semantics, the preferred pattern is:

```text
finding -> reproduction -> regression/conformance case -> specification disposition -> implementation fixes -> cross-language verification
```

## Frozen-review rule

Do not silently mutate the meaning of `olp-v1.0-review-1`.

If a material accepted finding requires a source-changing fix:

1. preserve review-1 as historical evidence for its original source;
2. implement and verify the correction;
3. freeze a new review target;
4. return affected external gates to pending for the new target; and
5. never reuse old review evidence as if it covered changed source bytes.

Editorial or operational changes outside the reviewed source do not automatically create a new review target, but contributors should avoid mixing them with normative changes.

## Cross-language interoperability

Where OLP defines deterministic behavior, Python and Rust disagreement is treated as a protocol/conformance defect, not as an implementation preference.

Changes affecting deterministic behavior should be exercised in both implementations and in direct interoperability tests where applicable.

## Design principles

Contributions should preserve the project principles in `PRINCIPLES.md`, including:

- evidence over reputation;
- facts over judgments;
- contextual trust;
- no universal trust score;
- privacy by architecture;
- identity is not trust;
- no silent history rewriting;
- algorithm, blockchain, and jurisdiction neutrality;
- interoperability before invention; and
- independent verifiability.

## Scope discipline

During the v1.0 review phase, speculative feature expansion is intentionally deprioritized.

A contribution that fixes a finding, clarifies review material, improves conformance evidence, hardens an implementation, or improves project/reviewer usability is generally more valuable than adding a new protocol feature.

## License

By contributing, you agree that your contribution will be licensed under the repository's Apache License 2.0.
