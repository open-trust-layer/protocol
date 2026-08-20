# Independent Rust Implementation

Milestone 15 added a second implementation of the executable OLP core in `implementations/rust/`; Milestone 16 extends that independent implementation across the deterministic Specification 0005 evidence boundary.

## Scope

The Rust crate implements the eight public capabilities exercised by the current `core-v1` conformance profile:

- `olp.record-identity.v1`
- `olp.record-commitment.sha256.v1`
- `olp.proof-input.v1`
- `olp.proof.eddsa-ed25519.v1`
- `olp.proof-verification.v1`
- `olp.proof-identity.v1`
- `olp.evidence-ref.v1`
- `olp.evidence-relationship.v1`

It covers Specification 0003 Record Identity, the implemented Specification 0004 proof/verification slice, and the deterministic identity/reference/relationship-processing subset of Specification 0005. Higher identity/authority, lifecycle, bundle, discovery, privacy, and transport modules remain outside this crate.

## Independence boundary

The Rust crate does not import, link against, embed, or invoke `src/olp/`. Its protocol behavior is expressed in Rust and its public adapter is a standalone executable.

The only cross-implementation boundary used by conformance is the language-neutral JSON-lines adapter contract from Milestone 14:

```text
olp-conformance
      |
      | JSON request / JSON response
      v
olp-conformance-adapter (Rust process)
```

The crate intentionally has no crates.io dependencies. Deterministic CBOR, SHA-256, OLP-CI-1 Record Identity, ProofInputV1 construction, and structured verification are implemented in the Rust crate. Ed25519 primitive operations are delegated through a narrow FFI boundary to the system OpenSSL `libcrypto` implementation.

## Normative-vector tests

The Rust test suite directly fixes five foundational interoperability anchors:

1. the Specification 0003 72-byte Record Identity preimage and `r1_...` presentation;
2. the Specification 0004 106-byte ProofInputV1 vector; and
3. the deterministic Ed25519 proof/public-key vector;
4. the Specification 0005 Proof Identity vector; and
5. the Specification 0005 record EvidenceRef vector.

Run:

```bash
cargo test --locked --manifest-path implementations/rust/Cargo.toml
```

## Official conformance gate

Build the adapter:

```bash
cargo build --release --locked --manifest-path implementations/rust/Cargo.toml
```

Then run the exact same corpus used for Python:

```bash
olp-conformance run \
  --profile core-v1 \
  --adapter subprocess \
  --adapter-command implementations/rust/target/release/olp-conformance-adapter \
  --report conformance-rust.json
```

No Rust-specific vector exceptions are permitted. Milestone 17 acceptance requires the Rust adapter to pass the entire current 62-case `core-v1` corpus.

## Bidirectional interoperability gate

The repository additionally tests that the implementations can exchange cryptographic artifacts rather than merely reproduce isolated byte vectors:

```bash
OLP_RUN_RUST_INTEROP=1 python -m pytest -q tests/interoperability/test_python_rust.py
```

The tests require:

- identical capability declarations;
- identical Record Identity output;
- identical ProofInputV1 bytes;
- identical deterministic Ed25519 proof creation;
- Python-created proof verification in Rust; and
- Rust-created proof verification in Python;
- identical Proof Identity output;
- identical EvidenceRef output; and
- identical relationship-processing projection for the shared evidence vector.

## CI

`.github/workflows/conformance.yml` contains a dedicated `rust-interoperability` job. It installs the pinned Rust toolchain, builds and tests the independent crate, runs the Rust adapter against `core-v1`, and executes the bidirectional Python/Rust tests.

A green job is the machine-verifiable acceptance signal for the current Milestone 16 cross-language evidence boundary.
