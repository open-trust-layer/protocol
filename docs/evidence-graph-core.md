# Evidence Graph Core — Milestone 16

Milestone 16 makes the deterministic core of Specification `0005-evidence-relationships.md` executable while preserving the protocol's central graph invariant:

> A graph edge is evidence with provenance, not protocol-issued truth.

## Executable boundary

The Python reference implementation now provides three deterministic evidence primitives:

1. **Proof Identity (OLP-PIE-1)** — SHA-256 over deterministic CBOR of `['OLP-PROOF-ID', 1, proofInputBytes, proofValue]`.
2. **EvidenceRefV1** — a typed canonical reference `[kind, identityDigest]`, where kind `0` denotes a record and kind `1` denotes a proof.
3. **RelationshipStatementV1** — the seven-element deterministic statement `['OLP-EVIDENCE-RELATIONSHIP', 1, relationType, subject, objects, qualifiers, critical]` carried as the content of an ordinary immutable OLP record.

Relationship records therefore receive ordinary Record Identity. They are not unsigned graph metadata and do not introduce a second identity system.

## Core relationships

The executable core recognizes:

- `references`
- `derivesFrom`
- `supersedes`
- `corrects`
- `disputes`
- `anchors`
- `countersigns`

Relation-specific structural rules remain explicit. `supersedes`, `corrects`, and `disputes` are record-to-record relations; `countersigns` has a null subject and proof targets; `anchors` starts from a record and may target any evidence. Unknown absolute-URI extension relation types are classified as unsupported rather than silently reinterpreted.

Qualifiers use absolute-URI keys. Unknown critical qualifiers fail closed. Non-critical unknown qualifiers remain preserved evidence.

## Graph projection

`EvidenceGraph` indexes records and proofs and derives projected edges from relationship records. Every projected edge retains the relationship record identity that produced it. Duplicate semantic edges from distinct relationship records therefore remain distinct evidence.

The graph layer deliberately permits:

- dangling references;
- cycles;
- conflicting relationship records; and
- multiple independent statements about the same evidence.

None of these conditions rewrites or invalidates the underlying immutable objects.

Traversal is deterministic and cycle-safe. A caller-supplied resource bound may make traversal incomplete; that outcome is reported as incomplete rather than being confused with malformed or invalid evidence.

## Conformance

Milestone 16 adds three capability IDs:

- `olp.proof-identity.v1`
- `olp.evidence-ref.v1`
- `olp.evidence-relationship.v1`

The `evidence-v1` profile contains these capabilities. `core-v1` now contains eight capabilities and 57 implementation-neutral cases total.

The new cases cover deterministic identities/references, relationship ordering and uniqueness, relation-specific type constraints, extension relation handling, critical qualifiers, countersignatures, and ordinary relationship-record identity/projection behavior.

## Cross-language boundary

The independent Rust implementation implements the same three evidence capabilities through the existing JSON-lines subprocess adapter. CI requires:

- Rust unit/normative-vector tests;
- 57/57 `core-v1` conformance;
- Proof Identity equality between Python and Rust;
- EvidenceRef equality between Python and Rust; and
- relationship-processing equality for the shared vector.

No Rust-specific expected output is permitted.

## Deliberate exclusions

Milestone 16 does not implement policy-level trust propagation, universal graph scoring, automatic transitive trust, hidden network resolution, lifecycle/status evaluation, identity/authority evaluation, evidence bundles, or discovery. Those remain separate protocol layers.
