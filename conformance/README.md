# OLP Executable Conformance Harness

**Milestones 14–20 · Harness v0.1.0**

The harness tests observable protocol behavior using implementation-neutral vectors. `core-v1` remains the frozen Draft v0.2 eight-capability core; later capabilities are additive profiles and do not redefine it.

## Current executable profiles

- `core-v1` — frozen Draft v0.2 deterministic core (62 cases).
- `evidence-v1` — Specification 0005 evidence capabilities.
- `bundle-v1` — deterministic Specification 0008 bundle validation (8 cases).
- `resolution-v1` — deterministic offline-first Specification 0009 resolution and network-policy processing (16 cases).

## Run the Python reference implementation

```bash
python -m pip install -e '.[test]'
olp-conformance run --profile core-v1
olp-conformance run --profile bundle-v1
olp-conformance run --profile resolution-v1
```

## Adapter contract

The harness supports an in-process Python adapter and a language-neutral subprocess adapter. Each subprocess request and response is exactly one JSON line under `olp-conformance-adapter-v1`; classified errors preserve `MALFORMED`, `UNSUPPORTED`, unavailable/policy/resource distinctions rather than collapsing them into protocol invalidity.

## Generic OLP values

Known cryptographic fields use explicit hex properties. Generic byte strings use `{"$bytes":"..."}`. Abstract maps that cannot be represented safely as ordinary JSON objects use `{"$map":[[key,value],...]}`. Duplicate abstract keys and duplicate JSON object names are rejected.

## Stability and additive manifest fragments

The original `conformance/manifest.json` and its published checksum remain frozen. Later capability milestones add lexically ordered `manifests/*.json` fragments. A fragment MUST match the base manifest and harness versions, MUST NOT redefine an existing profile incompatibly, and MUST NOT duplicate a case ID. This makes conformance growth append-only at the corpus-file level while preserving global uniqueness and deterministic loading.

Milestone-specific vector indexes and checksum files commit the exact additive corpus. M20 uses `VECTOR-INDEX-M20.md` and `SHA256SUMS-M20.txt`.

## Independent Rust adapter

The Rust implementation under `implementations/rust/` does not import or spawn the Python reference. CI builds it independently, executes every claimed profile against the shared vectors, and runs exact Python↔Rust interoperability comparisons.
