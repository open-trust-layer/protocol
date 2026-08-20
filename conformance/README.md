# OLP Executable Conformance Harness

**Milestones 14–26 · Harness v0.1.0 · Draft v0.3 corpus freeze + v1 candidate gates**

The harness tests observable protocol behavior using implementation-neutral vectors. `core-v1` remains the frozen eight-capability deterministic core; later capabilities are additive and do not redefine it.

Milestone 26 adds release-readiness tooling alongside conformance. Promotion readiness is deliberately separate from protocol conformance.

## Accepted executable profiles

```text
core-v1                          62 cases
bundle-v1                         8 cases
resolution-v1                    16 cases
identity-authority-lifecycle-v1  18 cases
privacy-disclosure-v1            18 cases
transport-encoding-v1            22 cases
streaming-http-v1                36 cases
```

Draft v0.3 adds one aggregate release-level profile:

```text
draft-v0.3-interoperable-v1     180 cases / 15 capabilities
```

The aggregate profile selects the already accepted cases; it adds no new evidence or wire semantics.

## v1 candidate boundary

The mandatory v1.0 candidate core is the existing `core-v1` profile. Its exact corpus commitment is:

```text
SHA-256 8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e
```

The following profiles remain optional candidates:

```text
bundle-v1
resolution-v1
identity-authority-lifecycle-v1
privacy-disclosure-v1
transport-encoding-v1
streaming-http-v1
```

Together mandatory + optional candidates cover exactly the 15 Draft v0.3 accepted capabilities. Optional profiles are not silently made mandatory.

## Run conformance

```bash
python -m pip install -e '.[test]'
olp-conformance run --profile core-v1
olp-conformance run --profile draft-v0.3-interoperable-v1
```

## Compute an exact corpus commitment

```bash
olp-conformance commitment \
  --profile draft-v0.3-interoperable-v1 \
  --json
```

The accepted Draft v0.3 suite commitment is:

```text
OLP-CONFORMANCE-SUITE-COMMITMENT-V1
SHA-256 62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

Specification 0014 defines the exact binary preimage. The commitment covers the selected profile/capabilities/case IDs and exact contributing manifest/vector bytes while excluding unrelated future profile growth.

The release manifest [`../specification/releases/draft-v0.3.json`](../specification/releases/draft-v0.3.json) pins the expected Draft v0.3 digest, and CI recomputes it on every aggregate Python/Rust run.

## Evaluate stable-promotion readiness

Milestone 26 adds:

```bash
olp-conformance promotion-check \
  --candidate stabilization/v1.0-candidate.json \
  --json
```

Promotion reports use three top-level states:

```text
INVALID   internal candidate invariant failed
BLOCKED   internal invariants pass; required external gate pending
READY     all represented internal and required external gates satisfied
```

The current candidate is intentionally expected to report:

```text
internal readiness: PASS
status:             BLOCKED
blockers:
  PUBLIC_TECHNICAL_REVIEW_REQUIRED
  INDEPENDENT_EXTERNAL_SECURITY_REVIEW_REQUIRED
```

For final release automation, use:

```bash
olp-conformance promotion-check \
  --candidate stabilization/v1.0-candidate.json \
  --require-ready
```

This returns non-zero while promotion is `BLOCKED` or `INVALID`.

A conformance pass cannot clear external-review blockers.

## What the promotion evaluator verifies

The evaluator independently checks:

- the global conformance manifest/fragments load cleanly;
- the Draft v0.3 release manifest matches the candidate baseline;
- the Draft v0.3 180-case corpus commitment recomputes exactly;
- the mandatory candidate core is exactly `core-v1` with eight capabilities;
- the six optional candidate profiles/specification associations are exact;
- mandatory + optional capabilities cover exactly the 15 Draft v0.3 capabilities without overlap or omission;
- standalone profile metadata exactly matches executable profile definitions;
- the candidate threat model, review register, and release process match pinned SHA-256 values;
- no recorded internal normative contradiction/release blocker remains unresolved; and
- completed external gates have durable references.

JSON object member order is not semantic.

## Promotion metadata

Candidate and review metadata live under `../stabilization/`:

```text
v1.0-candidate.json
v1-review-register.json
schemas/v1-promotion-candidate.schema.json
schemas/v1-promotion-report.schema.json
schemas/v1-review-register.schema.json
```

The candidate manifest is release-governance metadata. It is not an OLP Record, Proof, EvidenceRef, conformance claim, or trust judgment.

## Adapter contract

The conformance harness supports an in-process Python adapter and a language-neutral subprocess adapter. Each subprocess request and response is exactly one JSON line under `olp-conformance-adapter-v1`; classified errors preserve `MALFORMED`, `UNSUPPORTED`, unavailable/policy/resource distinctions rather than collapsing them into protocol invalidity.

## Generic OLP values

Known cryptographic fields use explicit hex properties. Generic byte strings use `{"$bytes":"..."}`. Abstract maps that cannot be represented safely as ordinary JSON objects use `{"$map":[[key,value],...]}`. Duplicate abstract keys and duplicate JSON object names are rejected.

## Profile metadata

Standalone `profiles/*.json` documents use schema `olp-conformance-profile-v1` with exactly:

```text
schema
id
version
status
capabilities
```

At the Draft v0.3 freeze they use `version: 1`, `status: draft-v0.3`, and their capability lists must exactly match the executable profile definitions loaded from the manifest/fragments.

## Stability and additive manifest fragments

The original `conformance/manifest.json` remains the base corpus. Later capability milestones add lexically ordered `manifests/*.json` fragments. A fragment MUST match the base manifest and harness versions, MUST NOT redefine an existing profile incompatibly, and MUST NOT duplicate a case ID.

Historical checksum files remain historical snapshots. Release-level suite commitments include only fragments that contribute to the selected profile/case set, making a frozen release stable under unrelated future profile growth.

## Independent Rust adapter

The Rust implementation under `implementations/rust/` does not import or spawn the Python reference. Existing CI independently requires:

```text
Python 3.11–3.14 aggregate  180 / 180 PASS
Rust 1.85 aggregate         180 / 180 PASS
Python <-> Rust interop      PASS
```

The M26 promotion evaluator is release-governance tooling in Python; it does not introduce a new protocol capability that Rust must implement. The protocol behaviors inside the candidate boundary remain governed by the existing cross-language conformance gates.

A corpus commitment identifies test material; it is separate from an implementation result, promotion-readiness result, signed conformance claim, certification, and trust judgment.
