# OLP v1.0 Candidate Readiness — Milestone 26

**Status:** candidate-stabilization report  
**Baseline release:** Draft v0.3  
**Baseline commit:** `5acc4b8934305a5215379c480db32bd0fd22f3ae`  
**Stable release published:** no

## 1. Result

Milestone 26 defines a candidate boundary and stable-promotion gates without publishing OLP v1.0.

The intended accepted readiness state is:

```text
internal readiness:                       PASS
stable promotion:                         BLOCKED
public technical review:                  PENDING
independent external security review:     PENDING
```

`BLOCKED` is a successful Milestone 26 outcome. It means the repository is internally coherent enough to name the remaining external gates precisely, not that the protocol has failed conformance.

## 2. Mandatory candidate core

The mandatory v1.0 candidate core is the existing `core-v1` profile. It contains eight capabilities and 62 implementation-neutral cases.

```text
olp.record-identity.v1
olp.record-commitment.sha256.v1
olp.proof-input.v1
olp.proof.eddsa-ed25519.v1
olp.proof-verification.v1
olp.proof-identity.v1
olp.evidence-ref.v1
olp.evidence-relationship.v1
```

Milestone 26 does not rename or redefine that profile.

The exact `core-v1` candidate corpus commitment is:

```text
SHA-256 8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e
```

## 3. Why the mandatory core stays small

Draft v0.3 demonstrates a broader 15-capability interoperable release surface. That fact alone is not a reason to force every deployment to implement bundles, network resolution, authority/lifecycle evaluation, disclosure planning, or HTTP exchange semantics.

The stable-candidate rule is therefore:

> Mandatory core behavior should be the smallest independently reproduced foundation needed for portable evidence identity, proof verification, and evidence relationships; higher-layer behavior remains explicit and separately claimable.

This preserves algorithm/profile plurality and prevents feature breadth from becoming accidental mandatory coupling.

## 4. Optional candidate profiles

The following accepted Draft v0.3 profiles remain optional v1.0 candidates:

```text
bundle-v1
resolution-v1
identity-authority-lifecycle-v1
privacy-disclosure-v1
transport-encoding-v1
streaming-http-v1
```

Together they contribute seven capabilities. Combined with `core-v1`, the candidate boundary covers exactly the 15 capabilities accepted by `draft-v0.3-interoperable-v1`.

No optional profile is promoted merely by being included in the Draft v0.3 aggregate run.

## 5. Draft v0.3 release continuity

Milestone 26 preserves the Draft v0.3 committed release corpus unchanged:

```text
Draft v0.3 cases:             180
Draft v0.3 capabilities:       15
SHA-256:
62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

The promotion evaluator independently recomputes that commitment from repository bytes and checks it against `specification/releases/draft-v0.3.json`.

No accepted vector or expected result is changed by Milestone 26.

## 6. Internal stabilization artifacts

The candidate manifest pins three review artifacts byte-for-byte.

```text
Threat model
2300a6100d99378c7b4c34abb5b99f26672a0263e930a986665a33e478ff6b38

Review / contradiction register
ad925eab6ac7fa9a8dc87b0b256fa029e4e4eb72d8171a350df271e7b72329a1

Release / migration / deprecation / errata process
9cc20b7ef427af8d185fa138ba41a03f701d9bdf3dc69f375ad6c043de21a58b
```

A byte change in one of these artifacts without updating the candidate metadata makes the evaluator `INVALID`.

## 7. Cross-specification review

The Milestone 26 review register covers Specifications **0000 through 0015** and the highest-risk semantic/governance boundaries, including:

- proof purpose versus authority sufficiency;
- identity/control versus authority;
- lifecycle/status evidence versus historical cryptographic validity;
- bundle integrity/completeness versus policy sufficiency;
- disclosure withholding versus global nonexistence;
- resolution success versus verification;
- HTTP status versus OLP semantic status;
- transport security/authentication versus OLP object proof validity;
- transport representation versus evidence identity;
- conformance/corpus identity versus certification or trust; and
- candidate/stable promotion metadata versus object/capability/corpus versioning.

The existing numbered specifications preserve these distinctions. The review found governance/documentation gaps but no semantic contradiction requiring a new Record, Proof, encoding, cryptosuite, or accepted capability version.

The machine-readable review register retains the findings and resolutions rather than deleting closed findings from history. Finding `M26-R011` explicitly verifies that Specification 0015 cannot use candidate/stable labels to reinterpret the existing version domains defined by Specifications 0013–0014.

## 8. Promotion evaluator

`olp-conformance` now exposes:

```bash
olp-conformance promotion-check --candidate stabilization/v1.0-candidate.json
```

The evaluator has three possible states:

```text
INVALID   internal candidate invariant failed
BLOCKED   internal invariants pass, required external gate pending
READY     all represented internal and external gates satisfied
```

For release automation:

```bash
olp-conformance promotion-check \
  --candidate stabilization/v1.0-candidate.json \
  --require-ready
```

must return non-zero until the candidate is genuinely `READY`.

## 9. Fail-closed promotion behavior

The M26 test suite verifies that the candidate becomes `INVALID` if, among other things:

- the mandatory core is silently widened or swapped;
- an optional candidate profile is silently dropped;
- mandatory + optional coverage no longer equals the Draft v0.3 15-capability set;
- standalone profile metadata differs from executable manifest definitions;
- the Draft v0.3 corpus commitment drifts;
- a pinned threat-model/review/release-process byte changes;
- an internal normative contradiction remains unresolved; or
- an external gate is marked completed without a durable reference.

JSON object member order is explicitly not treated as semantic.

## 10. Required external blockers

The candidate currently has exactly these promotion blockers:

```text
PUBLIC_TECHNICAL_REVIEW_REQUIRED
INDEPENDENT_EXTERNAL_SECURITY_REVIEW_REQUIRED
```

They are not implementation failures and they must not be cleared by maintainers simply changing a status flag.

Public review must identify the reviewed snapshot and material finding disposition.

Independent external security review must be performed independently of the project's own internal adversarial work and must provide durable review references.

## 11. Threat-model boundary

The candidate threat model explicitly includes protocol assets, hostile parser/input behavior, substitution attacks, resource exhaustion, graph/bundle amplification, authority/lifecycle confusion, resolver/SSRF/redirect risks, privacy/correlation risks, transport ambiguity, release/corpus claims, and supply-chain boundaries.

It also explicitly excludes claims that OLP conformance certifies production DNS, TLS, HTTP implementations, proxies/caches, key custody, operational authorization frameworks, host/cloud hardening, monitoring, incident response, or production-scale denial-of-service resistance.

## 12. Migration consequence

Milestone 26 creates no identity-bearing migration.

If a future v1.0 release preserves the currently accepted v1 deterministic constructions, existing conforming Draft v0.3 v1 Records and Proofs do not need regeneration, re-signing, or re-identification merely because the repository release label becomes stable.

If external review finds a defect requiring changed deterministic bytes or materially changed capability semantics, the affected version/capability must change explicitly under the versioning rules.

## 13. What M26 does not claim

Milestone 26 does not claim:

- OLP v1.0 is released;
- the candidate is `READY`;
- independent external review is complete;
- production deployments are certified;
- optional higher-layer profiles are mandatory;
- conformance proves trustworthiness; or
- there are no unknown vulnerabilities.

## 14. Next legitimate work

After Milestone 26, the next meaningful stable-promotion work is external-facing rather than feature expansion:

1. publish/freeze an exact review candidate snapshot for public technical review;
2. obtain independent external security review of the candidate boundary;
3. disposition material review findings through clarifications, errata, or explicit version changes;
4. rerun exact conformance/interoperability gates on the resulting candidate snapshot; and
5. only when the evaluator reaches `READY`, perform final release-candidate and stable publication mechanics.

New protocol features are not required merely to continue the milestone sequence.
