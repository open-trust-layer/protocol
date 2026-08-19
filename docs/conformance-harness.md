# Executable Conformance Harness

Milestone 14 implements the executable portion of Specification 0011 for the capabilities currently provided by the Python reference implementation.

The harness is intentionally separated from the `olp` implementation package:

```text
conformance vectors
       |
       v
olp_conformance runner
       |
       v
ConformanceAdapter
   |            |
   v            v
Python       external process
adapter      (any language)
```

The harness judges only externally observable results. It does not inspect private implementation state.

## Install

```bash
python -m pip install -e '.[test]'
```

## Run

```bash
olp-conformance run --profile core-v1
```

The command exits `0` only for a complete `PASS`. A failed case, adapter crash, or unsupported required capability yields a non-zero exit status.

`conformance-report.json` is generated for automated consumers.

## Profiles

- `record-v1` — Record Identity and mandatory SHA-256 Record Commitment.
- `proof-v1` — ProofInputV1, mandatory Ed25519 proof creation, and proof verification.
- `core-v1` — all currently executable Specification 0003/0004 capabilities.

## Language-neutral adapters

An external implementation can be tested without Python imports:

```bash
olp-conformance run \
  --adapter subprocess \
  --adapter-command './olp-adapter'
```

The process contract is specified in [`../conformance/README.md`](../conformance/README.md). The repository includes `python -m olp_conformance.subprocess_reference` as a working example.

## Harness self-test

`BrokenAdapter` is intentionally incorrect. The repository tests require the harness to reject it. This protects against a false-positive runner and gives future changes a simple sanity check:

```bash
olp-conformance run --adapter broken --profile core-v1
```

The command must fail.

## Normative-vector discipline

The Specification 0003 and 0004 normative vectors are anchors. If implementation work exposes a contradiction, the project must resolve the specification issue explicitly rather than silently rewriting a vector to match code.

Supplemental conformance vectors may expand test coverage but cannot create new normative semantics.
