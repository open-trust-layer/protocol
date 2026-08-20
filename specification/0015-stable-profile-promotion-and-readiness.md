# OLP Specification 0015 — Stable Profile Promotion and Readiness

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 26 — v1.0 Candidate Boundary & Promotion Gates  
**Filename:** `specification/0015-stable-profile-promotion-and-readiness.md`

---

## 1. Abstract

This specification defines how Open Layer Protocol (OLP) behavior may be promoted from draft/candidate status toward a future stable v1.0 release without conflating interoperability, security review, deployment safety, or release governance.

It selects the existing eight-capability `core-v1` profile as the **mandatory v1.0 candidate core** and keeps already accepted higher-layer profiles as optional candidates that may be promoted independently.

It also defines machine-checkable stable-promotion gates, threat-model requirements, contradiction/errata review requirements, external-review requirements, and release/migration/deprecation invariants.

This specification adds no new evidence semantics, identity-bearing object format, canonical encoding, cryptosuite, resolver behavior, transport representation, trust algorithm, or authorization decision procedure.

Candidate status is not stable status.

Conformance is not security certification.

---

## 2. Scope

This specification defines:

- stable-promotion terminology;
- the mandatory v1.0 candidate core boundary;
- optional candidate profiles;
- normative-document boundaries associated with those profiles;
- internal promotion gates;
- contradiction and errata review rules;
- threat-model requirements;
- independent external security-review requirements;
- public technical-review requirements;
- migration, deprecation, errata, and release-process requirements;
- machine-readable promotion states; and
- the Milestone 26 candidate-readiness result.

It does not publish OLP v1.0, create a certification authority, certify a production deployment, define a project trademark program, or guarantee absence of vulnerabilities.

---

## 3. Requirements language

BCP 14 requirement keywords have the meanings defined by RFC 2119 and RFC 8174 when written in all capitals.

---

## 4. Promotion vocabulary

### 4.1 Draft

`draft` identifies behavior or a specification-set snapshot that remains subject to compatible or explicitly versioned incompatible change.

### 4.2 Candidate

`candidate` means a boundary has been explicitly selected for stabilization and review.

Candidate status MUST NOT be represented as stable support or production security certification.

### 4.3 Release candidate

`release candidate` means the exact proposed stable snapshot has been frozen and all stable-promotion gates except final publication mechanics have completed successfully.

### 4.4 Stable

`stable` means the project has completed the documented stable-promotion and publication process for a named release/profile.

Stable status does not make evidence true, an implementation trustworthy, or a deployment secure.

---

## 5. Stable promotion does not rewrite protocol versions

Promotion metadata is separate from authenticated OLP object versions and capability semantics.

Promoting a profile from candidate to stable MUST NOT by itself change:

- Record envelope version `1`;
- `OLP-CIE-1` Record Identity bytes;
- the SHA-256 Record Commitment baseline;
- `OLPProof` version `1`;
- `ProofInputV1`;
- `eddsa-ed25519-v1`;
- Proof Identity v1;
- `EvidenceRefV1`;
- accepted relationship semantics; or
- the meaning of any already-published capability identifier.

If promotion review discovers a defect requiring changed deterministic bytes or materially changed capability semantics, the affected object, encoding, cryptosuite, capability, or profile MUST be explicitly versioned under Specification 0013.

A stable label MUST NOT hide a breaking change.

---

## 6. Mandatory v1.0 candidate core

The mandatory v1.0 candidate core is the existing profile:

```text
core-v1
```

Its capabilities are exactly:

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

Selecting `core-v1` as the candidate core does not rename, duplicate, or redefine that profile.

A future stable v1.0 implementation claiming the mandatory core MUST implement the exact stable-promoted revision of every capability in that profile.

---

## 7. Mandatory candidate normative boundary

The mandatory candidate core is governed by these normative specifications:

```text
0001 Terminology
0002 Protocol Objects
0003 Record Representation
0004 Proofs and Verification
0005 Evidence Relationships and Graphs
0011 Conformance and Interoperability
0013 Versioning, Registries, and Core Profile Governance
0014 Release Profiles and Conformance Suite Commitments
0015 Stable Profile Promotion and Readiness
```

Specification 0000 remains the non-normative overview.

Specifications associated only with optional profiles are not implicitly made mandatory by a `core-v1` conformance claim.

---

## 8. Optional v1.0 candidate profiles

The following already-accepted Draft v0.3 profiles are optional v1.0 candidates:

```text
bundle-v1
resolution-v1
identity-authority-lifecycle-v1
privacy-disclosure-v1
transport-encoding-v1
streaming-http-v1
```

Their principal normative specification associations are:

```text
bundle-v1                         -> 0008
resolution-v1                     -> 0009
identity-authority-lifecycle-v1   -> 0006, 0007
privacy-disclosure-v1             -> 0010
transport-encoding-v1             -> 0012
streaming-http-v1                 -> 0012
```

Optional candidate profiles MAY be promoted independently.

A stable release MUST state which optional profiles, if any, were promoted.

An implementation conforming only to the mandatory stable core MUST NOT be called non-conforming merely because it omits an optional profile.

---

## 9. Candidate coverage relationship to Draft v0.3

At Milestone 26, the union of:

- mandatory `core-v1`; and
- the six optional candidate profiles in Section 8

MUST cover exactly the 15 capabilities accepted by `draft-v0.3-interoperable-v1`, with no hidden capability added to the mandatory core.

This coverage rule is a candidate-boundary consistency check. It does not require all optional profiles to be promoted to stable together.

---

## 10. Stable-promotion gate classes

Stable promotion requires both **internal** and **external** gates.

Internal gates are facts the repository can verify from its own specifications, corpus, implementations, review register, and release metadata.

External gates require evidence that the project cannot legitimately self-produce as independent review.

Passing every internal gate while an external gate remains incomplete MUST produce `BLOCKED`, not `READY`.

---

## 11. Internal interoperability gates

Before a candidate may be `READY`, the project MUST demonstrate:

1. an exact candidate profile boundary;
2. an exact conformance corpus commitment;
3. at least two independent implementations of each profile proposed for stable promotion;
4. complete passes of the exact required corpus by those implementations;
5. direct cross-implementation equality where normative bytes are defined;
6. appropriate malformed, negative, unsupported, policy, and resource-limit coverage required by the profile; and
7. no silent required-case skips.

Draft v0.3 provides the baseline execution evidence for the current candidate set, but stable promotion MUST re-check the exact candidate snapshot.

---

## 12. Profile-registry gate

Every candidate profile MUST have one standalone profile declaration whose capability list exactly matches the executable manifest definition.

A profile that exists only in prose, only in the executable manifest, or only in standalone metadata is not sufficient for stable promotion.

Unknown, duplicate, or conflicting capability membership MUST fail the promotion gate.

---

## 13. Corpus-identity gate

The applicable release/profile corpus MUST be reproducibly committed using the current accepted conformance-suite commitment rules.

The project MUST distinguish:

```text
corpus identity != execution result != signed claim != certification
```

A changed selected vector, selected case, selected capability, contributing manifest fragment, or commitment construction changes the corpus identity and requires explicit re-acceptance.

---

## 14. Normative contradiction gate

The proposed stable boundary MUST have an explicit review register covering cross-specification interactions relevant to that boundary.

An unresolved normative contradiction is a stable-promotion blocker.

The absence of an open public issue MUST NOT be treated as proof that no contradiction exists.

A contradiction that changes already accepted deterministic output or materially changes a capability MUST be resolved through explicit versioning rather than wording that silently chooses one incompatible implementation.

Resolved review findings remain historical audit evidence and SHOULD NOT be deleted merely because they are closed.

---

## 15. Threat-model gate

A stable candidate MUST have a documented threat model covering at least:

- protected protocol assets;
- attacker-controlled inputs and capabilities;
- parser/representation boundaries;
- cryptographic and policy boundaries;
- graph/bundle/resource-exhaustion risks;
- authority/lifecycle risks;
- resolution/network risks;
- privacy/correlation risks;
- transport/API risks;
- supply-chain/release boundaries;
- deployment assumptions and exclusions; and
- residual risks requiring external review.

The threat model MUST preserve protocol conformance versus deployment security as separate claims.

---

## 16. Release, migration, deprecation, and errata gate

Before stable promotion, the project MUST document:

- immutable release-snapshot requirements;
- release provenance/tagging rules;
- migration from the preceding candidate/draft release;
- deprecation semantics;
- breaking-change classification;
- stable errata handling;
- vulnerability-fix classification; and
- withdrawal/rollback semantics that do not rewrite historical evidence.

If stable promotion preserves the currently accepted v1 deterministic constructions, existing conforming Draft v0.3 v1 Records and Proofs MUST NOT require regeneration, re-signing, or re-identification solely because the set-release label changes.

---

## 17. Independent external security-review gate

Stable v1.0 promotion MUST require independent external security review of the proposed stable boundary.

The review SHOULD challenge at minimum:

- canonicalization and identity constructions;
- proof-input domain separation and substitution resistance;
- mandatory cryptosuite handling;
- graph/bundle amplification and resource limits;
- identity/authority/lifecycle separation where promoted;
- resolution/network policy where promoted;
- privacy/correlation behavior where promoted;
- transport/framing/content-integrity behavior where promoted;
- cross-specification ambiguity; and
- adequacy of the claimed conformance corpus.

The project MUST NOT satisfy this gate by citing only its own maintainers, its own automated tests, or an internally produced adversarial review.

Completion MUST include one or more durable review references.

---

## 18. Public technical-review gate

Stable v1.0 promotion MUST require public technical review of the exact candidate boundary.

Completion MUST include durable references to the reviewed snapshot and resulting disposition of material findings.

The protocol does not prescribe one universal calendar duration for public review, but a review must be meaningful enough to permit independent inspection of the proposed stable snapshot.

---

## 19. Severity and finding disposition

Known high or critical findings that affect the proposed stable boundary MUST be resolved before promotion or MUST keep promotion blocked.

A finding MAY be classified as outside the promoted boundary only when that exclusion is explicit and does not contradict a capability/profile claim.

Risk acceptance MUST NOT be used to preserve a known cryptographic or identity ambiguity that permits two implementations to produce incompatible authenticated results under the same version.

---

## 20. Promotion evaluator states

A machine-readable promotion evaluator uses these top-level states:

```text
INVALID
BLOCKED
READY
```

### 20.1 `INVALID`

`INVALID` means one or more internal candidate invariants fail, for example profile mismatch, corpus drift, missing required artifact, invalid review metadata, or unresolved normative contradiction.

### 20.2 `BLOCKED`

`BLOCKED` means all internally checkable candidate invariants pass but one or more required external/future promotion gates are incomplete.

`BLOCKED` is the required state while independent external security review or public technical review remains pending.

### 20.3 `READY`

`READY` means every internal and required external promotion gate represented by the evaluator is satisfied.

`READY` is permission to begin final stable publication mechanics; it is not itself the published stable release.

---

## 21. Machine-readable candidate manifest

The repository MAY represent the candidate boundary using a machine-readable manifest.

The manifest SHOULD identify:

- candidate identifier and version;
- baseline Draft/release manifest;
- conformance manifest;
- mandatory profile;
- mandatory normative specifications;
- optional candidate profiles and associated specifications;
- required stabilization artifacts and their exact digests;
- required external gates and current status; and
- the candidate baseline commit.

The evaluator MUST NOT trust a declared `READY` string in the manifest. Readiness is derived from verified gates.

---

## 22. External-gate evidence

An external gate has at minimum:

```text
status
references
```

Current statuses are:

```text
pending
completed
```

A `completed` external gate MUST include at least one durable reference.

A `pending` required external gate produces a blocking reason code.

For Milestone 26 the required external blocker codes are:

```text
PUBLIC_TECHNICAL_REVIEW_REQUIRED
INDEPENDENT_EXTERNAL_SECURITY_REVIEW_REQUIRED
```

---

## 23. Stable publication

Final stable publication MUST follow the project v1 release process after the evaluator reaches `READY`.

A stable release MUST identify an immutable source snapshot and MUST NOT move or reuse a published stable tag for different source bytes.

Release provenance, corpus identity, conformance reports, external review, and security support status remain separate artifacts/facts even when released together.

---

## 24. Relationship to Specifications 0011–0014

Specification 0011 defines modular conformance and certification neutrality.

Specification 0013 defines general version, registry, capability, reason-code, and breaking-change governance.

Specification 0014 defines release profiles and exact conformance-suite commitments.

This specification adds stable-promotion governance on top of those rules. It does not supersede their deterministic or versioning semantics.

---

## 25. Milestone 26 candidate result

Milestone 26 is designed to finish with this state:

```text
mandatory candidate core:       core-v1
optional candidate profiles:    explicit
internal readiness:             PASS
public technical review:        PENDING
independent external review:    PENDING
stable promotion state:         BLOCKED
```

This is intentional.

The correct outcome of internal stabilization is not to self-certify independence. It is to make the remaining external work precise and impossible to bypass accidentally.

---

## 26. Security considerations

Premature stability is itself a security risk because downstream implementers may interpret the label as evidence that semantics, threat assumptions, and deployment boundaries have been independently reviewed.

Promotion tooling MUST therefore fail closed on internal inconsistency and MUST preserve pending external review as an explicit blocker.

A stable label MUST NOT convert:

- valid proof into truth;
- identity into trust;
- authority evidence into a universal authorization decision;
- missing evidence into absence;
- resource exhaustion into invalidity;
- transport success into evidence verification;
- conformance into certification; or
- protocol stability into deployment security.

---

## 27. Summary

OLP v1 stabilization follows one rule:

> **Stabilize the smallest proven mandatory core, keep optional behavior explicit, and never let internal conformance masquerade as independent security review.**

Milestone 26 therefore defines a candidate boundary and promotion gates without publishing v1.0.
