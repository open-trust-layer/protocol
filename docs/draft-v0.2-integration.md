# Draft v0.2 Integration Pass — Milestone 18

**Input baseline:** Milestone 17 merged `main` at `990635d45ecca1c00e02a316ad00377922eacccd`  
**Target:** Open Layer Protocol Draft v0.2

## Purpose

Milestone 18 feeds implementation, conformance, independent-interoperability, and adversarial-review findings back into the specification set.

The governing rule is conservative:

> Do not change identity-bearing or cryptographic bytes unless executable evidence proves the existing construction is wrong.

Milestones 13–17 showed that the current v1 deterministic core can interoperate across independent Python and Rust implementations. Draft v0.2 therefore focuses on cross-spec integration, version/registry governance, migration rules, promoted Specification 0005 vectors, and an explicit boundary between independently verified core behavior and higher layers that remain design-only.

## Integrated findings

Draft v0.2 incorporates these implementation lessons:

- canonical bytes are protocol behavior, not implementation detail;
- transport JSON rejects duplicate member names recursively;
- abstract map projection preserves key type and avoids wrapper collisions;
- authenticated URI identifiers are exact strings and malformed syntax is rejected;
- parser/resource limits exist before unsafe recursive materialization;
- technical algorithm support and local policy acceptance are separate;
- policy rejection does not erase independently computable cryptographic facts;
- graph convergence is not a cycle;
- incremental graph projections do not remain stale;
- bounded traversal reports incompleteness rather than absence;
- unknown noncritical relationship qualifiers remain visible as uninterpreted;
- unknown critical semantics fail closed; and
- cross-language disagreement is a protocol investigation, not a reason to special-case one implementation.

## Cross-spec audit

| Spec | Draft v0.2 result | Executable evidence |
|---|---|---|
| 0000 | Update set status/index from implementation plan to integration result. | Non-normative. |
| 0001 | Core terminology remains sound; 0013 centralizes version/reason-code governance. | Concepts exercised by lower layers. |
| 0002 | Universal immutable Record + detached Proof model remains sound. | Confirmed by M13–M17. |
| 0003 | Preserve `OLP-CIE-1`, Record Identity, Unicode and integer rules. | Python/Rust byte equality. |
| 0004 | Retain M17 policy/math separation and strict identifier rules; no ProofInput byte change. | Python/Rust create/verify + security vectors. |
| 0005 | Promote Proof Identity, EvidenceRefV1, and relationship processing into the verified core. | Python/Rust evidence parity. |
| 0006 | Identity/control/authority/trust separations remain sound; not promoted. | No full executable slice. |
| 0007 | Additive lifecycle model remains sound; not promoted. | No full executable slice. |
| 0008 | Integrity/completeness distinction remains sound; bundle amplification remains deferred. | No full bundle ingestion. |
| 0009 | Explicit no-hidden-network model remains sound; SSRF/redirect behavior remains deferred. | No live resolver stack. |
| 0010 | Whole-object/graph-subset minimization remains sound; privacy behavior remains unproven. | No full disclosure planner. |
| 0011 | Capability-scoped conformance model is validated by the harness. | 62-case shared corpus. |
| 0012 | M17 strict JSON/resource amendments retained. | Python/Rust adapter boundary. |
| 0013 | New versioning, registry, reason-code, migration, and core-profile rules. | Derived from M13–M17 evidence. |

## Byte compatibility decision

Draft v0.2 does not change Record Identity v1, SHA-256 Record Commitment, ProofInputV1, `eddsa-ed25519-v1`, Proof Identity v1, EvidenceRefV1, or RelationshipStatementV1.

Producers therefore do not regenerate existing conforming v1-core evidence merely because the set-release label changes.

## Independently verified core

The Draft v0.2 independently verified core is the current eight-capability `core-v1` profile:

- `olp.record-identity.v1`
- `olp.record-commitment.sha256.v1`
- `olp.proof-input.v1`
- `olp.proof.eddsa-ed25519.v1`
- `olp.proof-verification.v1`
- `olp.proof-identity.v1`
- `olp.evidence-ref.v1`
- `olp.evidence-relationship.v1`

Accepted Milestone 17 evidence:

- Python `core-v1`: 62/62;
- Rust `core-v1`: 62/62;
- Python↔Rust interoperability: 9/9;
- Python 3.11–3.14 CI: pass.

This does not imply that Specifications 0006–0010 are implementation-complete.

## Registry, extension, and reason-code decisions

Compact OLP identifiers are specification-controlled. Third-party extensions use globally unambiguous identifiers, normally absolute URIs. Authenticated identifiers are compared as exact strings. URI syntax does not authorize network access.

Unknown noncritical semantics are preserved where applicable and surfaced as uninterpreted; unknown critical semantics fail closed.

Draft v0.2 preserves semantic distinctions between malformed, unsupported, unavailable, invalid, policy-rejected, resource-limited, and absent outcomes. Existing specification-specific reason codes remain valid.

## Promoted vectors

Milestone 18 promotes independently reproduced Specification 0005 vectors for Proof Identity v1 and EvidenceRefV1 RecordRef/ProofRef encoding into `vectors/`.

This freezes already interoperable behavior; it does not invent new behavior.

## Migration from Draft v0.1

For the v1 verified core there is no record rewrite, proof rewrite, identity change, commitment change, signature change, or EvidenceRef change.

Deployments upgrade parser/security behavior, structured policy/result separation, conformance corpus revision, extension/registry behavior, and release/version governance.

## Deferred executable security work

Milestone 18 deliberately does not declare safe: DID/X.509 method parser ecosystems, authority/delegation evaluation, lifecycle/status conflict processing, bundle amplification behavior, resolver SSRF/redirect/address policy, disclosure-planner correlation behavior, or external selective-disclosure integrations.

## Acceptance gate

Milestone 18 is accepted only after the publication head demonstrates:

- repository tests PASS;
- Python `core-v1` 62/62 PASS;
- Rust crate tests/build PASS;
- Rust `core-v1` 62/62 PASS;
- Python↔Rust interoperability 9/9 PASS.

Because M18 intentionally preserves the executable core, any regression is an integration defect and must be investigated rather than normalized into a new expected value.
