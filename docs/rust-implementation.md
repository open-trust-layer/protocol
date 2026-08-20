# Independent Rust Implementation

Milestone 15 adds a second implementation of the currently executable OLP core in `implementations/rust/`.

## Scope

The Rust crate implements the same five public capabilities exercised by the Milestone 14 `core-v1` conformance profile:

- `olp.record-identity.v1`
- `olp.record-commitment.sha256.v1`
- `olp.proof-input.v1`
- `olp.proof.eddsa-ed25519.v1`
- `olp.proof-verification.v1`

It covers Specification 0003 Record Identity and the implemented Specification 0004 proof/verification slice. It does not implement later evidence-graph, identity/authority, lifecycle, bundle, discovery, privacy, or transport modules.

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

The Rust test suite directly fixes three foundational interoperability anchors:

1. the Specification 0003 72-byte Record Identity preimage and `r1_...` presentation;
2. the Specification 0004 106-byte ProofInputV1 vector; and
3. the deterministic Ed25519 proof/public-key vector.

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

No Rust-specific vector exceptions are permitted. Milestone 15 acceptance requires the Rust adapter to pass the entire current `core-v1` corpus.

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
- Rust-created proof verification in Python.

## CI

`.github/workflows/conformance.yml` contains a dedicated `rust-interoperability` job. It installs the pinned Rust toolchain, builds and tests the independent crate, runs the Rust adapter against `core-v1`, and executes the bidirectional Python/Rust tests.

A green job is the machine-verifiable acceptance signal for Milestone 15.
