# OLP Executable Conformance Harness

**Milestone 14 · Harness v0.1.0**

This directory contains implementation-neutral conformance material for the OLP capabilities currently executable from Specifications `0003` and `0004`.

The harness tests observable protocol behavior. Official vectors do not import or depend on private Python implementation details.

## Current capability IDs

| Capability | Meaning |
|---|---|
| `olp.record-identity.v1` | OLP-CI-1 / OLP-CIE-1 Record Identity |
| `olp.record-commitment.sha256.v1` | SHA-256 (`-16`) record commitment |
| `olp.proof-input.v1` | deterministic-CBOR `ProofInputV1` |
| `olp.proof.eddsa-ed25519.v1` | mandatory Pure Ed25519 proof creation |
| `olp.proof-verification.v1` | structured proof verification semantics |

`core-v1` requires all five capabilities.

## Case categories

- **positive** — a conforming implementation must produce the expected successful result.
- **negative** — the operation is understood and processed, but a security/context property must fail in the specified way.
- **malformed** — the supplied object violates a normative data-model or key-material rule.
- **unsupported** — the input represents a capability/version/algorithm the implementation cannot process; this must remain distinct from cryptographic invalidity.

## Run the Python reference implementation

```bash
python -m pip install -e '.[test]'
olp-conformance run --profile core-v1
```

A machine-readable report is written to `conformance-report.json` by default.

Useful filters:

```bash
olp-conformance run --category negative
olp-conformance run --capability olp.proof-verification.v1
olp-conformance run --case proof.verify.negative.signature.001
olp-conformance list
```

## Adapter contract

The harness supports both an in-process Python `ConformanceAdapter` and a language-neutral subprocess contract.

For an external implementation:

```bash
olp-conformance run \
  --adapter subprocess \
  --adapter-command './my-olp-adapter'
```

For every test case the harness starts the command, writes exactly one JSON request line to stdin, and expects exactly one JSON response line on stdout.

### Request

```json
{
  "protocol": "olp-conformance-adapter-v1",
  "operation": "derive_record_identity",
  "input": {}
}
```

The special `capabilities` operation has an empty input object.

### Successful response

```json
{
  "protocol": "olp-conformance-adapter-v1",
  "ok": true,
  "output": {}
}
```

### Classified error response

```json
{
  "protocol": "olp-conformance-adapter-v1",
  "ok": false,
  "error": {
    "classification": "MALFORMED",
    "reason": "INVALID_CORE_PROPERTY",
    "message": "human-readable detail"
  }
}
```

`classification` is part of the observable conformance contract. Human-readable `message` text is not compared by official vectors.

The included module `python -m olp_conformance.subprocess_reference` implements this contract using the Python reference core and is used by harness self-tests.

## JSON representation of byte strings

Known cryptographic fields use explicit names such as `digest_hex`, `proofValue_hex`, `public_key_hex`, and `challenge_hex`.

Generic OLP values inside records or extensions represent byte strings as:

```json
{"$bytes": "001122aabb"}
```

This projection exists only for conformance JSON. It is not an OLP transport serialization.

## Expectations

A vector expectation is either:

```json
{
  "outcome": "SUCCESS",
  "result": {
    "cryptographic_validity": "INVALID"
  }
}
```

or:

```json
{
  "outcome": "ERROR",
  "classification": "UNSUPPORTED",
  "reason": "UNSUPPORTED_CRYPTOSUITE"
}
```

Successful result objects use subset matching: a vector lists the protocol properties it intends to constrain. Implementations may return additional diagnostic properties without failing that vector.

## Normative anchors and supplemental vectors

`record.identity.spec-vector.001` reproduces the normative `0003` Record Identity vector.

`proof.input.spec-vector.001` reproduces the normative `0004` ProofInputV1 / Ed25519 input vector.

All other cases are deterministic supplemental conformance vectors derived from the same Draft v0.1 rules. They do not create new protocol semantics.

## Harness self-test

`BrokenAdapter` intentionally corrupts Record Identity digests and lies about an invalid signature. The test suite requires that this adapter fail the harness. This guards against a conformance runner that accidentally reports success regardless of observed output.

## Stability

Harness and vector formats are development artifacts while OLP remains Draft v0.1. Changes to a normative vector require a corresponding specification correction; they must never be silently adjusted merely to make an implementation pass.

## Independent Rust adapter

Milestone 15 includes an independent subprocess implementation at `implementations/rust/`. After building it:

```bash
cargo build --release --locked --manifest-path implementations/rust/Cargo.toml

olp-conformance run \
  --profile core-v1 \
  --adapter subprocess \
  --adapter-command implementations/rust/target/release/olp-conformance-adapter
```

The Rust process does not import the Python reference implementation. The repository CI requires this adapter to pass the same `core-v1` corpus and then runs bidirectional Python/Rust interoperability tests.
