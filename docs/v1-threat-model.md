# OLP v1 Candidate Threat Model

**Status:** Milestone 26 candidate-stabilization baseline  
**Applies to:** the future OLP v1.0 candidate boundary defined by Specification 0015  
**Does not imply:** stable release, production certification, or completed external review

## 1. Purpose

This document states the security assumptions and attacker model that must be visible before any Open Layer Protocol profile is promoted from draft/candidate status to stable.

The threat model is intentionally split between protocol semantics and deployment operation. A stable protocol can specify deterministic processing without certifying every DNS resolver, TLS stack, HTTP server, key-management system, proxy, database, or policy engine that may carry or consume OLP evidence.

## 2. Security assets

The candidate boundary protects these protocol-level assets:

1. **Record identity integrity** — the same conforming abstract Record produces the same Record Identity, and a different authenticated Record does not silently acquire another Record's identity.
2. **Proof binding integrity** — proof bytes remain bound to the exact authenticated record, purpose, verification method, suite, and other ProofInputV1 fields.
3. **Proof-result truthfulness** — implementations preserve cryptographic facts separately from availability, lifecycle/status evidence, authority evidence, and local policy.
4. **Evidence-reference integrity** — `EvidenceRefV1` and Proof Identity resolve to the exact evidence object claimed, or fail explicitly.
5. **Graph semantic integrity** — traversal, cycles, convergence, dangling references, incompleteness, and resource limits do not silently change graph meaning.
6. **Authority/lifecycle separation** — identity, control, authority, revocation/status evidence, freshness, and application authorization remain separate dimensions.
7. **Bundle and resource integrity** — packaging does not mutate evidence and committed resources are checked against their declared digests.
8. **Resolution provenance** — resolution source, policy, redirects, freshness, and unavailability remain visible rather than being rewritten as cryptographic validity.
9. **Disclosure integrity and privacy signaling** — withholding does not become proof of absence; disclosed immutable objects preserve identity; known correlation risks remain visible.
10. **Transport semantic integrity** — JSON/CBOR/sequence/HTTP representation does not redefine evidence identity, completeness, proof validity, or authorization.
11. **Conformance/release identity** — a profile claim names a precise capability set and exact committed corpus without implying trust or certification.

## 3. Attacker capabilities

A conforming implementation must assume an attacker may:

- supply arbitrary untrusted JSON, CBOR, OJVE, transport-envelope, sequence-frame, Record, Proof, bundle, relationship, lifecycle, authority, resolver, and disclosure inputs;
- choose pathological nesting, lengths, duplicate names, mixed map-key types, malformed encodings, non-canonical textual identities, invalid Unicode, and oversized values;
- replay valid historical evidence;
- combine individually valid evidence into misleading or incomplete graphs and bundles;
- omit relevant evidence or provide stale/conflicting lifecycle/status evidence;
- provide malicious or attacker-controlled resolver responses, redirects, discovery hints, resource bytes, and HTTP metadata;
- attempt SSRF, loopback/private-address access, redirect downgrade, credential forwarding, recursion, and amplification;
- exploit differences between implementations, parsers, libraries, languages, or policy layers;
- attempt signature/key/purpose/record/verification-method substitution;
- exploit cache, range, content-digest, truncation, and transport-completeness confusion;
- correlate principals or activity through stable identifiers, verification methods, same-subject links, manifests, authority history, lifecycle history, and resolver queries;
- present a passing conformance report or signed self-asserted conformance claim as if it were a security certification; and
- cause resource exhaustion within finite implementation limits.

The model does not assume attackers can break SHA-256 or Ed25519 cryptographically. If those primitives become unsuitable, the versioning and cryptosuite rules require explicit migration rather than silent reinterpretation.

## 4. Trust boundaries

### 4.1 Serialized input -> parser

All externally supplied representations are untrusted before strict parsing, duplicate detection, type/range validation, canonicality checks, and finite resource limits.

### 4.2 Parsed object -> identity/cryptography

Host-language object equality is not OLP identity. Identity and proof input are derived only through the specified deterministic constructions.

### 4.3 Cryptographic result -> policy

Mathematical signature validity does not establish truth, identity sufficiency, authority, freshness, lifecycle acceptability, or local policy acceptance.

### 4.4 Evidence -> graph/application interpretation

Graph reachability, bundle membership, relationship presence, and authority/lifecycle evidence are not universal trust or authorization decisions.

### 4.5 Resolver/network -> protocol processor

URI syntax is not permission to perform I/O. Network access, redirects, address classes, recursion, freshness, and byte limits remain explicit policy inputs.

### 4.6 Bundle/transport -> immutable evidence

Packaging, JSON/CBOR transport, streaming order, HTTP status, TLS, authentication, and HTTP Message Signatures do not alter underlying OLP Record/Proof identity or cryptographic facts.

### 4.7 Conformance -> release/security claims

Passing a committed corpus establishes only the tested interoperability claim. Stable promotion additionally requires review, release governance, and explicit threat assumptions.

## 5. Mandatory candidate-core assumptions

The mandatory v1.0 candidate core is `core-v1`.

For this mandatory core:

- no ambient network access is required for deterministic identity/proof/evidence processing;
- all identity-bearing deterministic bytes are versioned;
- unsupported critical semantics fail closed;
- malformed, unsupported, unavailable, invalid, policy-rejected, and resource-limited states remain distinct where applicable;
- resource limits must not be reported as evidence absence or cryptographic invalidity;
- proof purpose does not itself establish authority;
- graph incompleteness must not be represented as global absence; and
- conformance does not imply trustworthiness.

## 6. Optional candidate-profile risks

Optional candidate profiles add attack surfaces and remain non-mandatory.

### Bundles

Risks include inventory mismatch, duplicate evidence, unexpected content, resource-digest substitution, amplification, and false completeness.

### Resolution

Risks include SSRF, DNS rebinding, private-address targeting, redirect policy bypass, recursion/loops, stale data, source confusion, and resolver privacy leakage.

### Identity / authority / lifecycle

Risks include key-control/identity confusion, scope widening, delegation substitution, unsupported constraints, stale or conflicting status evidence, and accidental conversion of evidence into authorization.

### Privacy / disclosure

Risks include over-disclosure, correlation, hidden dependencies, false global-completeness claims, and incorrect reuse of proofs after field deletion or transformation.

### Transport encoding

Risks include type loss, non-canonical identity strings, heterogeneous-map-key collapse, deterministic-CBOR disagreement, and wrapper ambiguity.

### Streaming / HTTP

Risks include framing/truncation confusion, HTTP-status/OLP-status conflation, redirect downgrade, credential forwarding, cache/range misuse, content-digest confusion, and authentication/proof-validity conflation.

## 7. Security invariants

Stable implementations MUST preserve these distinctions:

```text
proof validity           != truth
key control              != identity
identity                 != authority
authority evidence       != authorization decision
status evidence          != historical mutation
resolution success       != verification
bundle integrity         != completeness
withholding              != nonexistence
transport security       != OLP proof validity
HTTP authorization       != OLP authority evidence
resource limit           != absence
conformance              != trustworthiness
corpus identity          != execution result
candidate status         != stable status
protocol conformance     != deployment certification
```

## 8. Availability and resource exhaustion

OLP requires finite implementation limits but does not prescribe one universal production capacity.

Processors must fail explicitly when configured limits are reached. They must not silently truncate identity-bearing values, silently drop critical evidence, report partial graphs as complete, or convert exhaustion into signature invalidity or global absence.

Production-scale denial-of-service resistance remains deployment-specific and requires separate operational testing.

## 9. Privacy model

OLP does not promise anonymity or unlinkability.

Stable identifiers, proof verification methods, evidence graphs, bundles, lifecycle history, authority chains, and resolver activity may create correlation.

Implementations should minimize disclosure relative to the task, preserve pairwise/context-specific identifier strategies where ecosystems use them, avoid unnecessary network resolution, and surface known correlation warnings. Native external selective-disclosure systems retain their own proof semantics.

## 10. Key compromise and lifecycle

Compromise of signing material is not repaired by rewriting historical evidence.

Lifecycle/status evidence can state compromise, revocation, suspension, retirement, or other events. Verification must preserve the distinction between historical mathematical validity and later status/policy consequences.

Key generation, hardware protection, backup, custody, operator access, recovery, and rotation procedures are deployment concerns and are not certified by OLP conformance.

## 11. Network and deployment assumptions

The Draft v0.3 executable corpus models deterministic network-policy and HTTP semantics but performs no ambient network I/O.

Stable protocol promotion therefore does not certify:

- DNS resolver behavior or DNSSEC deployment;
- TLS libraries, PKI configuration, certificate validation policy, or endpoint identity;
- proxy, CDN, cache, WAF, load-balancer, or service-mesh behavior;
- production redirect following;
- production authentication or authorization frameworks;
- secret storage or operational key management;
- monitoring, incident response, backups, or disaster recovery;
- host/container/cloud hardening;
- dependency and supply-chain security; or
- production-scale availability.

Deployments must threat-model these separately.

## 12. Supply-chain and release assumptions

A stable release must identify an immutable repository snapshot, exact conformance corpus, release manifest, and release provenance according to the v1 release process.

A compromised build, dependency, CI runner, package registry, or release credential can invalidate operational confidence without changing OLP protocol semantics. Release provenance is therefore a separate security boundary.

## 13. Residual risks requiring external review

Before v1.0 promotion, independent external review is required to challenge at least:

- canonicalization and identity constructions;
- proof-input domain separation and substitution resistance;
- Ed25519 key/proof handling;
- graph and bundle resource-amplification behavior;
- authority/delegation and lifecycle/status separation;
- resolver/network policy assumptions;
- privacy/correlation behavior;
- transport/framing/content-integrity boundaries;
- cross-specification contradictions or ambiguous requirement language; and
- whether the conformance corpus materially exercises the claimed stable boundary.

The project must not mark this requirement complete based solely on its own internal review.

## 14. Review consequence

A serious review finding that changes previously conforming deterministic output or materially changes an accepted capability must be versioned under Specifications 0013–0015. It must not be hidden as an editorial stable-release change.

Until the external and public-review gates recorded by the v1 candidate manifest are complete, the promotion evaluator must report the candidate as `BLOCKED`.
