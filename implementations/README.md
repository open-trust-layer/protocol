# Independent Implementations

This directory contains implementations that are intentionally separate from the Python reference package under `src/olp/`.

Their purpose is interoperability pressure-testing: each implementation is expected to derive behavior from the normative OLP specifications and implementation-neutral conformance corpus, then communicate with the harness only through public OLP data and the `olp-conformance-adapter-v1` subprocess contract.

Current implementations:

- [`rust/`](rust/) — independent Rust implementation of the Specification 0003/0004 core introduced for Milestone 15 and the deterministic Specification 0005 evidence subset added in Milestone 16.

An implementation living here MUST NOT import or link against the Python reference implementation in order to satisfy conformance cases.
