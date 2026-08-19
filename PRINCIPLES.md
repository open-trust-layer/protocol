# Open Layer Protocol — Principles

**Status:** Project principles  
**Applies to:** protocol design, specifications, reference implementations, conformance work, and project governance

Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

These principles are architectural constraints, not marketing slogans. When a proposed protocol feature conflicts with them, the conflict should be explicit and the burden of proof lies with the proposal.

## 1. Evidence over reputation

OLP should make evidence portable, attributable, inspectable, and independently verifiable.

The protocol must not require a universal reputation score or a centrally owned reputation profile in order to function.

Applications may derive reputation or risk assessments from evidence, but those judgments remain application-specific.

## 2. Facts over judgments

OLP should distinguish claims, observations, events, proofs, provenance, and status evidence from judgments made about them.

A cryptographically valid statement is not automatically true. A verified identity is not automatically trustworthy. A valid authority grant is not automatically sufficient for every action.

Protocol data should preserve the evidence needed for later interpretation rather than silently embedding one evaluator's conclusion as universal fact.

## 3. Participant-owned history

Participants should be able to retain and move relevant evidence about their interactions without remaining dependent on the platform that originally mediated those interactions.

Portability must not require the original intermediary to remain online indefinitely.

## 4. Contextual trust

Trust is contextual.

The same evidence may reasonably lead to different conclusions in different applications, jurisdictions, risk environments, and time periods.

OLP should standardize evidence interchange, not one mandatory trust decision.

## 5. No universal trust score

OLP must not define a protocol-level global score that collapses a participant's history into one universal ranking, number, or trusted/untrusted state.

Applications may compute local scores, but those algorithms and their assumptions must remain separable from the protocol evidence itself.

## 6. Algorithm plurality

Cryptographic algorithms, resolution mechanisms, policy engines, ranking systems, trust models, and storage technologies should be replaceable where protocol interoperability permits.

OLP should define mandatory interoperability baselines when necessary without treating those baselines as permanent monopolies.

## 7. Privacy by architecture

Privacy must be considered in record granularity, identifier use, evidence resolution, bundle construction, disclosure, and verification—not added only as a user-interface feature.

Implementations should minimize unnecessary disclosure and correlation while preserving the context required to avoid misleading evidence.

## 8. Identity is not trust

An identifier is not an identity proof.

Cryptographic key control is not identity.

Identity is not authority.

Authority is not trust.

These concepts may be related by evidence, but OLP must not collapse them into one protocol primitive.

## 9. Actor neutrality

Humans, organizations, software agents, services, devices, accounts, and other participants should be treated as protocol actors without receiving automatic evidentiary privilege merely because of actor type.

Applications and law may legitimately distinguish them; the core evidence layer should not invent a universal hierarchy among them.

## 10. No silent history rewriting

Historical records and proofs are immutable evidence artifacts.

Corrections, disputes, supersession, suspension, revocation, compromise, retirement, and other lifecycle changes should be represented as additive evidence rather than destructive mutation of prior history.

## 11. Blockchain neutrality

OLP does not require a blockchain, token, cryptocurrency, distributed ledger, or consensus network.

Such systems may provide useful anchoring, timestamping, transparency, settlement, or storage evidence, but they remain optional infrastructure.

## 12. Jurisdiction neutrality

OLP may carry evidence relevant to legal or regulatory decisions, but it should not embed one jurisdiction as the universal legal authority for all protocol participants.

Legal effect, compliance, admissibility, and policy remain context-dependent.

## 13. Interoperability before invention

Where an established open standard already solves a problem adequately, OLP should interoperate with it rather than create a competing mechanism without a strong technical reason.

New OLP mechanisms should exist because the evidence layer needs semantics that existing standards do not provide cleanly—not merely because OLP can invent them.

## 14. Independent verifiability

Core OLP evidence should be verifiable by independent implementations from explicit inputs.

Verification should not require contacting a central Open Layer Protocol authority, hidden resolver, proprietary scoring service, or privileged database.

Network resolution may be used when explicitly selected, but cryptographic verification itself should remain reproducible and inspectable.

## Architectural consequence

These principles imply a recurring separation throughout OLP:

```text
record identity             != transport serialization
proof validity              != truth
key control                 != identity
identity                    != authority
proof purpose               != authority sufficiency
authority evidence          != final authorization decision
status evidence             != cryptographic validity
revocation                  != historical mutation
resolution                  != verification
bundle integrity            != bundle completeness
bundle completeness         != policy sufficiency
selective disclosure        != proof of nonexistence
conformance                 != trustworthiness
transport security          != OLP object proof validity
```

## Changing these principles

The principles may evolve as the project matures, but changes should be deliberate, documented, and reviewed against the protocol's long-term goal:

> **Make evidence portable and independently verifiable while keeping trust judgments plural, contextual, and outside central ownership.**
