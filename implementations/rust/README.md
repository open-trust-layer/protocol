# OLP Rust Core — Milestone 15

This crate is an **independent second implementation** of the Open Layer
Protocol core currently covered by Specifications `0003` and `0004`.

It is intentionally derived from the normative specifications and the public,
implementation-neutral Milestone 14 conformance corpus rather than from Python
implementation internals.

## Implemented capabilities

- `olp.record-identity.v1`
- `olp.record-commitment.sha256.v1`
- `olp.proof-input.v1`
- `olp.proof.eddsa-ed25519.v1`
- `olp.proof-verification.v1`

The crate has no crates.io dependencies. Deterministic CBOR, SHA-256, record
identity, ProofInputV1, proof construction, and the structured verification
state machine are implemented in Rust. Ed25519 primitive operations use the
system OpenSSL EVP implementation through a narrow FFI boundary.

### Requirements

- Rust 1.85.0 (pinned by `rust-toolchain.toml`) or a compatible newer toolchain
- OpenSSL 1.1.1 or newer development/runtime library providing `libcrypto`
- Linux for the repository CI profile

## Build and test

```bash
cargo test --manifest-path implementations/rust/Cargo.toml
cargo build --release --manifest-path implementations/rust/Cargo.toml
```

## Run the implementation-neutral conformance suite

From the repository root:

```bash
olp-conformance run \
  --profile core-v1 \
  --adapter subprocess \
  --adapter-command implementations/rust/target/release/olp-conformance-adapter
```

The adapter speaks exactly `olp-conformance-adapter-v1` JSON-lines. No Python
module is imported by the Rust process.

## Independence boundary

The Rust crate does not link to, import, embed, or invoke the Python OLP
reference implementation. The cross-language tests deliberately interact only
through public OLP data and the Milestone 14 subprocess adapter contract.

## Repository acceptance gate

The root GitHub Actions workflow contains a `rust-interoperability` job that:

1. installs Rust 1.85.0 and `libssl-dev`;
2. runs `cargo test --locked`;
3. builds the release subprocess adapter;
4. runs that adapter against all 41 cases in the official `core-v1` corpus; and
5. runs the bidirectional Python↔Rust interoperability tests.

Milestone 15 should be considered accepted only when that job is green.
