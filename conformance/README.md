# OLP Executable Conformance Harness

**Milestones 14–25 · Harness v0.1.0 · Draft v0.3 corpus freeze**

The harness tests observable protocol behavior using implementation-neutral vectors. `core-v1` remains the frozen eight-capability deterministic core; later capabilities are additive and do not redefine it.

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

## Run the Python reference implementation

```bash
python -m pip install -e '.[test]'
olp-conformance run --profile core-v1
olp-conformance run --profile draft-v0.3-interoperable-v1
```

## Compute the exact release corpus commitment

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

Specification 0014 defines the exact binary preimage. The commitment covers:

- the base manifest;
- every additive manifest fragment in the repository snapshot;
- the standalone selected profile declaration;
- the ordered profile capability list;
- the ordered selected case IDs; and
- the exact bytes of every vector referenced by those cases.

Each committed file is SHA-256 hashed over exact bytes. File paths are sorted by UTF-8 bytes. The outer commitment uses explicit uint32 big-endian length/count framing, not JSON serialization.

The JSON produced by the CLI is a diagnostic view only; it is not the commitment preimage.

The release manifest [`../specification/releases/draft-v0.3.json`](../specification/releases/draft-v0.3.json) pins the expected digest, and CI recomputes it on every aggregate Python/Rust run.

## Adapter contract

The harness supports an in-process Python adapter and a language-neutral subprocess adapter. Each subprocess request and response is exactly one JSON line under `olp-conformance-adapter-v1`; classified errors preserve `MALFORMED`, `UNSUPPORTED`, unavailable/policy/resource distinctions rather than collapsing them into protocol invalidity.

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

This normalization fixed a release-metadata inconsistency where older profile files used `status` while later files used `version`, despite sharing one profile schema. No capability or vector semantics changed.

## Stability and additive manifest fragments

The original `conformance/manifest.json` remains the base corpus. Later capability milestones add lexically ordered `manifests/*.json` fragments. A fragment MUST match the base manifest and harness versions, MUST NOT redefine an existing profile incompatibly, and MUST NOT duplicate a case ID.

Historical checksum files remain historical snapshots; Draft v0.3 does not rewrite them. The release-level suite commitment in Specification 0014 provides a new exact commitment over the aggregate profile corpus.

## Independent Rust adapter

The Rust implementation under `implementations/rust/` does not import or spawn the Python reference. CI builds it independently and requires:

```text
Python 3.11–3.14 aggregate  180 / 180 PASS
Rust 1.85 aggregate         180 / 180 PASS
Python <-> Rust interop      PASS
```

A corpus commitment identifies test material; it is separate from an implementation result, signed conformance claim, certification, and trust judgment.
