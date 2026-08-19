# OLP Specification 0011 — Conformance and Interoperability

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 11 — Protocol Conformance & Interoperability  
**Filename:** `specification/0011-conformance-and-interoperability.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) v1 conformance and interoperability framework.

It defines:

- modular conformance capability identifiers;
- rules for making precise OLP conformance claims;
- aggregate interoperability profiles;
- mandatory positive, negative, canonicalization, security, and cross-implementation testing categories;
- deterministic test-vector requirements;
- handling of unsupported versions and extensions;
- structured conformance reports;
- a self-asserted conformance-claim record profile;
- test-suite identity and versioning;
- implementation capability discovery;
- requirements for cross-language byte equality where OLP canonical encodings are normative;
- requirements for non-deterministic environmental dependencies to be isolated from deterministic protocol processing;
- compatibility expectations across Specifications 0003 through 0010;
- certification neutrality; and
- security considerations for misleading or incomplete conformance claims.

OLP conformance is modular.

An implementation MUST state **what** it conforms to.

The phrase "OLP compliant" without a version and conformance capability is insufficient for an interoperable claim.

---

## 2. Scope

This specification answers:

> How can independent implementations demonstrate that they interpret OLP records, proofs, evidence graphs, lifecycle evidence, bundles, resolution, and privacy rules consistently enough to interoperate without creating a central certification authority?

This specification does **not** define:

- a mandatory certification organization;
- a trademark program;
- legal certification;
- a universal security rating;
- a guarantee that conforming software is vulnerability-free;
- a guarantee that an implementation's local trust policies are correct;
- a universal implementation language;
- a mandatory network deployment;
- performance benchmarks as protocol correctness; or
- a universal policy engine.

---

## 3. Requirements Language

BCP 14 requirement keywords have the meanings defined by RFC 2119 and RFC 8174 when written in all capitals.

---

## 4. Core Invariants

### 4.1 Conformance is scoped

Every conformance claim MUST identify:

- OLP version or specification version;
- capability or profile;
- implementation version; and
- test basis when a test claim is made.

### 4.2 Conformance is not trust

Passing conformance tests does not establish that an implementation operator, signer, resolver, or evidence source is trustworthy.

### 4.3 Deterministic bytes must agree

Where an OLP specification defines exact canonical bytes, conforming implementations given the same abstract input MUST produce byte-for-byte identical output.

### 4.4 Structured results must preserve distinctions

An implementation MUST NOT pass conformance by collapsing required states such as:

```text
INVALID
UNSUPPORTED
UNAVAILABLE
NOT_EVALUATED
POLICY_BLOCKED
```

into one boolean when the applicable specification requires distinction.

### 4.5 Unknown critical semantics fail closed

Conformance requires safe handling of unknown critical extensions and qualifiers.

### 4.6 Environmental variability is isolated

Network availability, DNS state, resolver output, wall clock, and local policy may vary.

Tests of deterministic protocol logic MUST use fixed inputs or snapshots.

### 4.7 Unsupported is not non-conforming

An implementation may be conforming to a declared capability while not implementing optional modules.

### 4.8 No silent downgrade

Version or capability negotiation MUST NOT silently substitute a weaker unsupported semantic profile when the caller requires a stronger one.

### 4.9 Self-asserted conformance is evidence

A signed conformance claim proves only that the producer made the claim.

Independent certification requires separate evidence.

### 4.10 Test suites are versioned artifacts

Changing expected semantics or test inputs requires a new test-suite identity/version.

---

## 5. Conformance Capability Identifiers

Core OLP v1 capabilities use compact identifiers reserved by this specification:

```text
record-core-v1
proof-producer-v1
proof-verifier-v1
graph-processor-v1
identity-authority-evaluator-v1
lifecycle-evaluator-v1
bundle-reader-v1
bundle-producer-v1
self-contained-bundle-producer-v1
offline-resolver-v1
network-resolver-v1
discovery-processor-v1
privacy-aware-bundle-producer-v1
disclosure-planner-v1
transport-http-reader-v1
transport-http-server-v1
```

Unknown compact capability identifiers are reserved and MUST NOT be minted by third parties.

Third-party capabilities MUST use globally unambiguous absolute URI identifiers.

---

## 6. Capability Dependencies

The following dependency relationships are normative for core v1:

```text
proof-producer-v1
  -> record-core-v1

proof-verifier-v1
  -> record-core-v1

graph-processor-v1
  -> record-core-v1
  -> proof-verifier-v1

identity-authority-evaluator-v1
  -> graph-processor-v1

lifecycle-evaluator-v1
  -> graph-processor-v1

bundle-reader-v1
  -> record-core-v1
  -> proof-verifier-v1
  -> graph-processor-v1

bundle-producer-v1
  -> bundle-reader-v1

self-contained-bundle-producer-v1
  -> bundle-producer-v1
  -> offline-resolver-v1

disclosure-planner-v1
  -> privacy-aware-bundle-producer-v1
  -> bundle-producer-v1
```

A capability claim includes all mandatory semantics of its dependencies.

---

## 7. Aggregate Profiles

### 7.1 OLP v1 Core Verifier

Symbolic profile:

```text
olp-v1-core-verifier
```

Requires:

- `record-core-v1`;
- `proof-verifier-v1`; and
- mandatory Ed25519 cryptosuite support from Specification 0004.

### 7.2 OLP v1 Evidence Processor

```text
olp-v1-evidence-processor
```

Requires:

- `olp-v1-core-verifier`;
- `graph-processor-v1`;
- `bundle-reader-v1`;
- `offline-resolver-v1`.

### 7.3 OLP v1 Full Semantic Processor

```text
olp-v1-full-semantic-processor
```

Requires:

- `olp-v1-evidence-processor`;
- `identity-authority-evaluator-v1`;
- `lifecycle-evaluator-v1`;
- `discovery-processor-v1`;
- privacy warning processing from Specification 0010.

This profile does not require network access.

### 7.4 OLP v1 Exchange Node

```text
olp-v1-exchange-node
```

Requires the Full Semantic Processor plus the applicable transport server profile from Specification 0012.

---

## 8. Precise Conformance Claims

An implementation MUST NOT claim:

```text
OLP compliant
```

without further qualification.

Acceptable forms include:

```text
OLP Draft v0.1 proof-verifier-v1
OLP Draft v0.1 bundle-reader-v1
OLP Draft v0.1 olp-v1-evidence-processor
```

A project MAY use friendlier marketing language only if machine-readable documentation states the exact capabilities.

---

## 9. Test Categories

Every core capability test suite MUST contain applicable cases in these categories:

```text
positive
negative
malformed
unsupported
critical-extension
canonicalization
identity
cryptographic
cross-object
resource-limit
privacy/security
```

A suite SHOULD include regression tests for known past implementation errors.

---

## 10. Positive Tests

Positive tests demonstrate that conforming inputs produce expected semantic outputs.

They MUST NOT be the only tests used for a security-sensitive capability.

---

## 11. Negative Tests

Negative tests MUST cover inputs that are syntactically valid enough to reach the target processing stage but must fail a specific semantic or cryptographic check.

Examples:

- wrong record commitment;
- wrong Ed25519 signature;
- wrong verification-method type;
- purpose mismatch;
- identity mismatch;
- resource digest mismatch;
- critical extension unsupported.

---

## 12. Malformed Tests

Malformed tests cover structural violations such as:

- wrong array length;
- duplicate map key;
- forbidden CBOR type;
- invalid URI syntax;
- incorrect digest length where fixed;
- invalid proof-value length for the mandatory suite;
- unsorted required set representation when canonical sorting is normative.

Processors MUST report malformed input separately from unsupported semantics.

---

## 13. Unsupported Tests

Unsupported tests cover structurally valid future or extension inputs.

Examples:

```text
unknown cryptosuite
unknown proof input version
unknown relationship URI
unknown lifecycle target type
unknown critical bundle extension
```

Expected result MUST preserve `UNSUPPORTED` semantics.

---

## 14. Canonicalization Tests

Canonicalization tests MUST include:

- abstract input;
- exact expected byte encoding;
- byte length;
- digest where applicable; and
- readable diagnostic form.

For Specification 0004 proof input, test suites MUST include the mandatory Ed25519 interoperability vector defined there.

For Proof Identity, suites MUST include vectors from Specification 0005.

For future canonical structures, the defining specification MUST publish equivalent vectors.

---

## 15. Cross-Language Determinism

At least two independent implementations SHOULD reproduce each canonical test vector before a specification is promoted beyond draft maturity.

The implementations SHOULD use different language/runtime stacks where practical.

A single shared serialization library across all "independent" implementations does not provide strong evidence of cross-language interoperability.

---

## 16. Proof Tests

A `proof-verifier-v1` suite MUST cover:

- mandatory SHA-256 record commitment;
- mandatory Pure Ed25519 suite;
- valid proof;
- invalid signature;
- record commitment mismatch;
- wrong key type;
- unavailable verification method;
- unsupported cryptosuite;
- purpose mismatch;
- domain mismatch;
- challenge mismatch;
- expired temporal metadata;
- unknown non-critical extension;
- unknown critical extension;
- proof identity stability under transport reserialization.

---

## 17. Graph Tests

A `graph-processor-v1` suite MUST cover:

- record reference;
- proof reference;
- relationship parsing;
- sorted target set;
- dangling reference;
- cycle;
- countersignature relation;
- dispute/correction/supersession;
- proof-set independence;
- no implicit transitivity;
- no edge ordering semantics.

---

## 18. Identity and Authority Tests

The identity/authority suite MUST cover:

- exact Principal Identifier equality;
- `sameSubjectAs` without automatic merge;
- verification-method control evidence;
- role without automatic authority;
- grant proof without automatic grantor authority;
- delegated grant parent mismatch;
- scope mismatch;
- constraint failure;
- revoked/suspended grant evidence;
- distinct policy result versus cryptographic proof result.

---

## 19. Lifecycle Tests

The lifecycle suite MUST cover:

- additive status evidence;
- activate/suspend/resume/retire/revoke/compromise/deprecate;
- source-local sequencing;
- sequence gap;
- rollback;
- conflict;
- stale evidence;
- no-evidence unknown state;
- effective time versus independent time evidence;
- native status adapter result preservation;
- historical evaluation.

---

## 20. Bundle Tests

The bundle suite MUST cover:

- bundle ID from manifest Record Identity;
- order-independent transport;
- missing inventory item;
- unexpected item;
- duplicate copy;
- same-identity conflict;
- resource digest mismatch;
- self-contained no-network requirement;
- merge producing new manifest;
- extraction producing new manifest;
- valid manifest proof with invalid contained proof.

---

## 21. Resolution Tests

Resolution suites MUST cover:

- bundle hit;
- local miss;
- no-network enforcement;
- identity recomputation;
- redirect policy;
- SSRF/private-address block;
- stale cache;
- ambiguous result;
- resolver loop;
- historical request with no historical snapshot.

Network tests SHOULD use controlled fixtures rather than the public Internet.

---

## 22. Privacy Tests

Privacy-aware tests MUST cover:

- whole-object subsetting;
- no field-redaction identity preservation;
- graph-subset omission semantics;
- same-subject correlation warning;
- stable key correlation warning;
- self-contained over-disclosure warning;
- network-resolution leakage warning;
- external selective-disclosure adapter preserving undisclosed claims.

---

## 23. Resource-Limit Tests

Processors MUST be tested for finite behavior under:

- deeply nested values;
- oversized arrays/maps;
- huge numbers of proofs;
- graph cycles;
- resolver recursion;
- oversized external resources;
- decompression expansion;
- streaming truncation.

A safe resource-limit stop is not test failure if the applicable specification permits configured limits and the result code is correct.

---

## 24. Test Fixture Isolation

Tests of deterministic processing MUST NOT depend on:

- live DNS;
- public websites;
- current certificate status;
- wall-clock current time;
- external blockchains;
- live DID resolvers; or
- third-party API availability.

Such systems MAY be tested in integration suites, but normative deterministic conformance results require fixed fixtures.

---

## 25. Time Fixtures

Whenever time affects expected results, the test input MUST supply the evaluation time explicitly.

Tests MUST NOT assume the machine's current clock.

---

## 26. Policy Fixtures

Where an OLP specification leaves acceptance to local policy, a test MUST state the policy fixture used.

A conformance suite MUST NOT treat one optional trust policy as universal OLP semantics.

---

## 27. Structured Conformance Report

A test runner SHOULD output:

```text
ConformanceReportV1 {
    implementation
    implementationVersion
    protocolDraft
    capabilities[]
    testSuite
    testSuiteCommitment
    startedAt
    completedAt
    environment
    totals
    caseResults[]
    warnings[]
}
```

`startedAt` and `completedAt` are report metadata, not independent temporal evidence.

---

## 28. Case Result

Each case result SHOULD contain:

```text
caseId
capability
status
expected
observed
diagnostics
duration
```

Core statuses:

```text
PASS
FAIL
SKIP_NOT_IMPLEMENTED
SKIP_ENVIRONMENT
ERROR_HARNESS
```

A required case for a claimed capability MUST NOT be counted as passing when skipped.

---

## 29. Test Suite Identity

A conformance suite version SHOULD be identified by:

- stable absolute URI or repository release identifier;
- version;
- cryptographic commitment to the exact test corpus.

Changing expected results requires a new suite version or commitment.

---

## 30. `ConformanceClaimStatementV1`

### 30.1 Purpose

An implementation or testing organization MAY publish a signed OLP record stating a conformance result.

### 30.2 Exact structure

```text
ConformanceClaimStatementV1 = [
    "OLP-CONFORMANCE-CLAIM",
    1,
    implementationId,
    implementationVersion,
    capabilities,
    testSuiteId,
    testSuiteCommitment,
    reportCommitment,
    extensions,
    critical
]
```

Exactly ten elements.

### 30.3 Implementation ID

MUST be an absolute URI.

This is an identifier for the implementation build/product, not necessarily its operator.

### 30.4 Capabilities

Sorted unique set of capability identifiers.

### 30.5 Test commitments

Commitments use:

```text
[
    hashAlgorithmId,
    digestBytes
]
```

SHA-256 support is mandatory.

### 30.6 Semantics

A proof over this record establishes that the proof producer made the conformance claim.

It does not create OLP-wide certification authority.

---

## 31. Third-Party Certification

A third party MAY:

- produce its own Conformance Claim;
- countersign an implementation claim;
- witness a test execution;
- publish a relationship to a test report.

OLP does not rank certifiers.

Applications MAY choose which certification evidence they accept.

---

## 32. Capability Discovery

Transport endpoints MAY advertise capabilities.

A capability advertisement MUST distinguish:

```text
implemented
enabled
configured
temporarilyUnavailable
```

where the transport profile supports those states.

Advertising a capability that is disabled for the current endpoint can cause interoperability failures and SHOULD be avoided.

---

## 33. Version Handling

A processor receiving a future version MUST:

- reject it as malformed only if syntax itself is invalid;
- otherwise report unsupported version;
- preserve unknown input where safe for forwarding;
- never reinterpret the future version as v1 merely because some fields look familiar.

---

## 34. Extension Testing

Every extension defining critical semantics SHOULD publish:

- at least one positive test;
- at least one unknown-critical negative test;
- canonical vectors when it affects canonical bytes;
- security considerations;
- capability identifier.

---

## 35. Interoperability Matrix

Projects SHOULD test not only implementation against its own producer, but:

```text
Producer A -> Verifier B
Producer B -> Verifier A
Producer A -> Bundle Reader C
Bundle Producer C -> Verifier A/B
```

Self-round-trip tests alone are insufficient evidence of interoperability.

---

## 36. Fuzzing

Security-sensitive parsers SHOULD be fuzz tested.

High-value fuzzing targets include:

- deterministic CBOR decoding;
- OLP JSON transport mapping;
- ProofInput reconstruction;
- URI parsing;
- graph traversal;
- bundle streaming;
- HTTP transport envelope parsing.

Fuzz success is not a substitute for conformance vectors.

---

## 37. Differential Testing

Independent implementations SHOULD compare:

- parsed abstract values;
- canonical bytes;
- identities;
- verification result dimensions;
- error classes.

Unexpected differences SHOULD be treated as specification or implementation defects until explained.

---

## 38. Security Test Requirements

A release claiming network-resolver or transport-server capability SHOULD test:

- SSRF defenses;
- redirect policy;
- oversized bodies;
- request smuggling protections supplied by the HTTP stack;
- header/body digest mismatch;
- malformed content type;
- invalid structured fields where used;
- decompression bombs;
- timeout behavior;
- authentication credential leakage across redirects.

---

## 39. Conformance Does Not Override Policy

A verifier can conform perfectly and still reject a proof under local policy.

A policy can be stricter than the protocol baseline.

A policy MUST NOT redefine a mathematically invalid signature as valid.

---

## 40. Interoperability Baseline

For Draft v0.1, a minimal interoperable verification implementation SHOULD target:

```text
record-core-v1
proof-verifier-v1
graph-processor-v1
bundle-reader-v1
offline-resolver-v1
```

This provides:

- immutable record processing;
- mandatory Ed25519 verification;
- evidence references/graphs;
- portable bundle ingestion; and
- network-independent resolution.

---

## 41. Promotion Criteria

Before a future OLP v1.0 release, the project SHOULD require:

1. normative schemas frozen for core structures;
2. all canonical test vectors reproducible by independent implementations;
3. cross-language producer/verifier interoperability;
4. negative test coverage for all critical parsing boundaries;
5. no unresolved specification contradictions across core modules;
6. documented extension registry policy;
7. stable transport profile;
8. public conformance corpus;
9. at least one reference implementation; and
10. security review of cryptographic and network boundaries.

---

## 42. Security Considerations

### 42.1 Fake conformance claims

A valid proof over a conformance claim establishes attribution of the claim, not truth.

### 42.2 Cherry-picked suites

Claims SHOULD identify exact suite commitment to prevent selectively omitting failing tests while retaining a familiar suite name.

### 42.3 Outdated suites

A once-passing result can become stale as specifications or security guidance evolve.

### 42.4 Capability confusion

Applications MUST verify the exact capability needed rather than relying on a generic "supports OLP" flag.

### 42.5 Shared implementation bugs

Multiple products using the same library can all pass the same incorrect interpretation if the test suite is also derived from that library.

Independent vectors and implementations reduce this risk.

---

## 43. Design Summary

```text
specification requirement
        |
        v
capability identifier
        |
        v
versioned test corpus
        |
   +----+----+
   |         |
   v         v
Producer   Consumer
   |         |
   +----+----+
        |
cross-implementation evidence
        |
        v
structured report
        |
        v
optional signed conformance claim
```

The essential invariant is:

> **OLP conformance is specific, testable, modular, and independently reproducible; it is not a central trust badge.**

---

## 44. References

### 44.1 Normative OLP references

- OLP Specifications 0003 through 0010.

### 44.2 Normative Internet references

- RFC 2119.
- RFC 8174.
- RFC 8949.
- RFC 8032.

### 44.3 Informative references

- RFC 8610 — CDDL.
- RFC 9682 — CDDL grammar updates.
- W3C Verifiable Credentials test-suite ecosystem and implementation reports.

---

## 45. Deferred Work

Deferred topics include:

- repository layout of the executable conformance suite;
- official OLP release certification program, if ever desired;
- third-party laboratory requirements;
- performance benchmarking;
- formal verification profiles;
- reproducible-build attestation profiles;
- SBOM integration;
- vulnerability-disclosure program;
- test-suite governance; and
- release-signing infrastructure.

---

**End of OLP Specification 0011 — Draft v0.1**
