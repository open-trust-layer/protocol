# OLP Specification 0010 — Privacy, Selective Disclosure, and Data Minimization

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 10 — Privacy, Selective Disclosure & Data Minimization  
**Filename:** `specification/0010-privacy-selective-disclosure-and-data-minimization.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) v1 privacy and disclosure layer.

It defines:

- privacy as an architectural requirement rather than an optional presentation concern;
- whole-object and graph-subset selective disclosure for native OLP v1 evidence;
- data-minimized bundle construction;
- explicit disclosure closure relative to a verification task;
- preservation of immutable object identity during disclosure;
- prohibition on silent field redaction of signed or content-addressed OLP records;
- privacy boundaries created by record granularity;
- correlation risks created by Principal Identifiers, verification methods, same-subject evidence, authority graphs, lifecycle history, resolver activity, and bundle manifests;
- pairwise and context-specific identifiers as compatible identifier strategies;
- privacy-preserving resolver and status-processing guidance;
- handling of external selective-disclosure systems such as SD-JWT and BBS-derived presentations without flattening their native semantics;
- disclosure request and result processing models;
- structured privacy warnings;
- conformance requirements; and
- security and privacy considerations.

OLP v1 supports selective disclosure by selecting immutable evidence objects and graph branches.

OLP v1 does not pretend that an arbitrary field can be deleted from an already identified record while preserving that record's identity or proof.

Field-level cryptographic selective disclosure requires a proof system designed for that purpose.

---

## 2. Scope

This specification answers:

> How can OLP participants disclose only the evidence reasonably necessary for a task while preserving verifiability, provenance, immutable identities, and the semantics of external privacy-preserving credential systems?

This specification builds on Specifications 0003 through 0009.

It does **not** define:

- a universal privacy policy;
- a universal lawful basis for processing data;
- a universal consent model;
- a universal anonymity network;
- a universal pairwise-identifier scheme;
- native OLP zero-knowledge proofs;
- native OLP field-level redactable signatures;
- a mandatory BBS cryptosuite;
- a mandatory SD-JWT profile;
- a universal privacy score;
- a global identity-merging prohibition imposed on applications;
- a universal data-retention period; or
- jurisdiction-specific privacy compliance.

Applications remain responsible for applicable law and policy.

---

## 3. Requirements Language

BCP 14 requirement keywords have the meanings defined by RFC 2119 and RFC 8174 when written in all capitals.

---

## 4. Core Invariants

### 4.1 Data minimization is a protocol goal

A producer SHOULD disclose only evidence needed for the declared verification or policy task.

### 4.2 Immutable objects are not redactable by deletion

Removing or altering a field from an OLP record changes its canonical representation and Record Identity.

A processor MUST NOT claim that a redacted value is the same OLP record unless a separate cryptographic mechanism explicitly establishes such semantics.

### 4.3 Proofs remain bound to exact records

A detached OLP proof over Record R cannot be reused as proof over a field-deleted Record R'.

### 4.4 Whole-object selective disclosure is native v1 behavior

A participant MAY disclose Record A while withholding Record B, provided no protocol rule requires B to verify the declared task.

### 4.5 Graph-subset disclosure is native v1 behavior

A participant MAY disclose only selected relationship branches.

Withheld branches MUST NOT be inferred to be absent from the global evidence graph.

### 4.6 Withholding is not falsification

Failure to include an unrelated record is not protocol falsification.

A claim that a bundle is globally complete is a separate proposition.

### 4.7 Completeness claims require a basis

A verifier MUST NOT infer that undisclosed evidence does not exist.

### 4.8 Privacy and offline verification trade off

Self-contained bundles frequently disclose more supporting data than online-resolution bundles.

No profile is universally more private.

### 4.9 Identity evidence is correlation evidence

Identity bindings, `sameSubjectAs` relations, stable verification methods, and repeated Principal Identifiers can create correlation even when each individual record appears harmless.

### 4.10 Resolver queries can disclose interests

Network resolution can reveal which subject, key, status, or evidence branch a verifier is evaluating.

### 4.11 Privacy metadata can itself leak

A manifest describing exactly what was selected can reveal sensitive facts even when the included evidence is encrypted or otherwise access-controlled.

### 4.12 Native privacy mechanisms retain native semantics

OLP MUST NOT convert a selectively disclosed external credential into a statement that reveals undisclosed claims or implies the original undisclosed document was received.

---

## 5. Terminology

### 5.1 Disclosure task

The specific verification, audit, policy, or exchange goal for which evidence is being selected.

### 5.2 Disclosure root

An evidence reference that the recipient is expected to evaluate.

### 5.3 Disclosure closure

The finite supporting evidence selected to make the declared task processable.

### 5.4 Whole-object disclosure

Disclosure of an exact immutable OLP record or proof.

### 5.5 Graph-subset disclosure

Disclosure of a selected subgraph without claiming that undisclosed graph branches do not exist.

### 5.6 Field-level selective disclosure

A cryptographic technique permitting disclosure of selected parts of a protected statement while retaining verifiable proof semantics.

### 5.7 Correlation identifier

Any stable identifier or evidence feature that can help link observations across contexts.

### 5.8 Pairwise identifier

An identifier intentionally scoped to a pair of participants or a bounded context to reduce cross-context correlation.

### 5.9 Over-disclosure

Disclosure of evidence not reasonably needed for the declared task.

---

## 6. Privacy Threat Model

OLP implementations SHOULD consider at least:

- passive recipients correlating stable identifiers;
- active recipients requesting excessive evidence;
- resolvers observing verification queries;
- status services observing credential or key checks;
- bundle intermediaries enumerating evidence graphs;
- malicious graph nodes attempting correlation through relationship records;
- timing correlation;
- repeated verification-method reuse;
- authority-chain disclosure;
- lifecycle-history disclosure;
- metadata and filename leakage;
- access logs;
- cache logs;
- content-length leakage;
- re-identification from combinations of otherwise non-identifying facts; and
- collusion between recipients.

OLP cannot eliminate all such risks.

It can avoid making them unnecessarily mandatory.

---

## 7. Record Granularity as Privacy Boundary

Because native OLP v1 proofs bind to complete immutable records, record design strongly affects later disclosure.

Producers SHOULD prefer semantically coherent, reasonably granular records over unnecessarily monolithic records when selective future disclosure is expected.

For example, rather than one record containing:

```text
legal identity
home address
bank account
shipment history
employment history
```

an application SHOULD consider separate records if those claims can be independently meaningful and independently disclosed.

Granularity MUST NOT be manipulated to misrepresent context.

A record must still contain enough context to preserve the intended meaning of the statement.

---

## 8. Native OLP v1 Selective Disclosure

Native v1 selective disclosure consists of:

```text
select exact records
select exact proofs
select exact relationship records
select exact identity/authority evidence
select exact lifecycle evidence
select exact resolver resources
```

and package them according to Specification 0008.

No field deletion is required.

---

## 9. No Silent Field Redaction

If a producer receives:

```text
Record R = {A, B, C}
Proof P -> R
```

it MUST NOT transmit:

```text
{A, C}
Proof P
```

and label the result as the same record.

The recipient would be unable to reconstruct the authenticated record commitment.

A redacted presentation MUST use:

- a different record and explicit derivation/provenance evidence;
- an external selective-disclosure mechanism;
- a future OLP-native selective-disclosure profile; or
- another cryptographically defined method.

---

## 10. Derived Records

An application MAY create a new OLP record containing a subset, summary, or derived claim from source evidence.

The new record:

- has its own Record Identity;
- requires its own proof if attribution is needed; and
- MAY reference source evidence using Specification 0005.

A derivation relationship does not make the derived claim semantically equivalent to the source.

---

## 11. External Selective-Disclosure Evidence

OLP can carry external evidence systems that support field-level selective disclosure.

Examples include:

- SD-JWT presentations; and
- BBS-derived proof presentations in ecosystems that implement the applicable W3C cryptosuite.

Such presentations SHOULD be packaged as:

- committed external resources under Specification 0008; or
- OLP records whose semantics explicitly preserve the native presentation and verification result.

OLP MUST NOT reconstruct undisclosed claims or imply they were revealed.

---

## 12. Disclosure Request Model

`DisclosureRequestV1` is an abstract processing input, not an evidence record.

```text
DisclosureRequestV1 = [
    "OLP-DISCLOSURE-REQUEST",
    1,
    purpose,
    roots,
    requiredCapabilities,
    evidenceRequirements,
    resolverPolicy,
    options
]
```

### 12.1 Purpose

`purpose` MUST be an absolute URI or null.

It is application-declared context, not legal consent.

### 12.2 Roots

Roots are `EvidenceRefV1` values the recipient requests to evaluate.

### 12.3 Required capabilities

A sorted set of OLP capability identifiers as defined by Specification 0011.

### 12.4 Evidence requirements

Application-defined requirements such as:

```text
specific proof purpose
specific authority action
specific lifecycle scope
specific relationship type
historical verification time
```

OLP core does not define a universal policy language here.

### 12.5 Resolver policy

The request MAY express whether external resolution is permitted.

### 12.6 Options

Core options include:

```text
0 -> preferMinimalDisclosure : boolean
1 -> preferOfflineVerification : boolean
2 -> maxBundleBytes : integer or null
3 -> permitExternalNativePresentations : boolean
```

---

## 13. Disclosure Planning

A Disclosure Planner SHOULD:

1. identify the requested roots;
2. identify mandatory protocol dependencies;
3. identify caller-declared policy dependencies;
4. reuse already included evidence where possible;
5. exclude unrelated sibling evidence;
6. prefer exact needed relation paths over broad graph export;
7. select the least revealing suitable verification material when multiple equivalent options exist under policy;
8. avoid unnecessary same-subject links;
9. avoid unrelated lifecycle history;
10. record unresolved dependencies rather than fetching them when network access is disallowed;
11. produce a new bundle manifest for the selected set.

---

## 14. Disclosure Closure

Closure is relative to the declared task.

A processor MUST NOT claim globally minimal disclosure unless it has a formal basis for that claim.

The recommended term is:

```text
task-scoped minimized disclosure
```

rather than:

```text
minimum possible disclosure
```

because multiple incomparable evidence sets can satisfy the same policy.

---

## 15. Whole-Object Dependency Rules

A producer SHOULD include a whole object when it is required to:

- verify a selected proof;
- evaluate a selected relationship;
- establish an authority path requested by policy;
- establish lifecycle state requested by policy;
- verify a native external presentation; or
- resolve a verification method without network access.

It SHOULD NOT automatically include all objects merely sharing:

- a principal;
- a verification method;
- a relationship target;
- a lifecycle target; or
- a bundle of origin.

---

## 16. Proof Disclosure

A record can be disclosed with:

- no proofs;
- one selected proof;
- multiple selected proofs.

Withholding sibling proofs MUST NOT imply those proofs do not exist.

A recipient requiring a particular proof purpose SHOULD request that purpose explicitly.

---

## 17. Relationship Disclosure

A graph-subset bundle MAY contain:

```text
A -> B
B -> C
```

while omitting:

```text
B -> D
```

The recipient MUST NOT infer that B has no relationship to D.

A relationship record included in the subset retains its exact provenance and identity.

---

## 18. Identity and Authority Minimization

Identity and authority graphs can be especially sensitive.

Producers SHOULD avoid disclosing:

- legal names when a pseudonymous principal identifier suffices;
- organization memberships unrelated to the action;
- unrelated roles;
- parent grants beyond the path needed for authority evaluation;
- same-subject links not required by the verifier;
- historic verification methods not needed for the evaluated proof.

---

## 19. Pairwise and Contextual Principal Identifiers

Specification 0006 permits opaque absolute-URI Principal Identifiers.

An ecosystem MAY define pairwise or context-specific identifier schemes.

OLP core MUST NOT require that two pairwise identifiers be globally linkable.

Evidence asserting `sameSubjectAs` between pairwise identifiers can defeat unlinkability and SHOULD be disclosed only when required.

---

## 20. Verification-Method Correlation

Reusing one long-lived verification method across unrelated contexts creates a strong correlation handle.

Applications MAY use:

- context-specific keys;
- rotating verification methods;
- pairwise keys;
- delegated keys; or
- privacy-preserving external credential systems

where appropriate.

Key rotation does not itself erase historical correlation from evidence already disclosed.

---

## 21. Lifecycle Privacy

Lifecycle data can reveal:

- employment changes;
- account suspension;
- compromise events;
- organizational disputes;
- security incidents;
- business relationships;
- regulatory actions.

A disclosure planner SHOULD include only lifecycle evidence required by the requested evaluation.

A current-status task does not automatically require disclosure of the complete lifecycle history.

---

## 22. Status-Checking Privacy

Status queries can identify the object being checked.

Implementations SHOULD prefer mechanisms that reduce per-subject query leakage where suitable.

Bulk status-list systems can provide privacy advantages because one shared resource can cover many subjects, but they introduce their own correlation, caching, and freshness considerations.

---

## 23. Resolver Privacy

A network resolver MAY learn the exact URI, principal, proof target, or status source being queried.

Resolution plans SHOULD support:

```text
offlineOnly
bundleFirst
cacheAllowed
privacyRelay
batching
```

where implemented.

A privacy relay is outside core v1 semantics and MUST NOT be assumed trustworthy merely because it hides the client network address.

---

## 24. Bundle Manifest Privacy

A manifested bundle explicitly lists evidence identities.

Even without record bodies, those identities can enable correlation if previously observed.

Applications MAY choose an unmanifested transient collection when no durable exact-set statement is needed.

If a manifest is required, producers SHOULD avoid adding descriptive metadata that is not necessary.

---

## 25. Self-Contained versus Online Privacy

Self-contained verification can reduce resolver-query leakage but can increase disclosed payload.

Online resolution can reduce bundle payload but reveal lookup behavior.

Applications SHOULD choose based on threat model.

OLP MUST NOT label one as universally privacy-preserving.

---

## 26. Audience Binding

OLP v1 does not define a universal audience-encryption mechanism.

Where disclosure is intended for a bounded recipient, transport or storage encryption SHOULD be used.

If a proof itself must be restricted to a context, the authenticated `domain`, `challenge`, or a critical extension under Specification 0004 can be used according to the application protocol.

Encryption and proof-purpose semantics remain separate.

---

## 27. Replay and Reuse

A recipient may retain and redisclose evidence unless technical, contractual, legal, or policy controls prevent it.

OLP proofs are portable by design.

Applications requiring one-time or context-bound presentations SHOULD use authenticated challenges, domains, short-lived native presentations, or other explicit mechanisms.

A confidentiality statement alone does not cryptographically prevent redisclosure.

---

## 28. Disclosure Logging

An application MAY record disclosure events.

Such logging is itself sensitive.

A disclosure log SHOULD NOT be required by OLP core.

If represented as OLP evidence, it SHOULD:

- clearly identify what the logger claims occurred;
- avoid implying recipient consent unless separately evidenced;
- minimize sensitive manifest details; and
- remain subject to ordinary proof and lifecycle semantics.

---

## 29. `DisclosureResultV1`

A Disclosure Planner SHOULD return:

```text
DisclosureResultV1 {
    status
    purpose
    selectedRoots[]
    selectedEvidence[]
    selectedResources[]
    unresolvedDependencies[]
    privacyWarnings[]
    policyWarnings[]
    producedBundleId
    errors[]
}
```

Recommended statuses:

```text
READY
PARTIAL
UNSATISFIABLE
POLICY_BLOCKED
LIMIT_EXCEEDED
UNSUPPORTED
```

---

## 30. Privacy Warning Codes

Core warning codes include:

```text
STABLE_PRINCIPAL_CORRELATION
STABLE_VERIFICATION_METHOD_CORRELATION
SAME_SUBJECT_LINK_DISCLOSED
UNRELATED_ROLE_DISCLOSURE
UNRELATED_AUTHORITY_DISCLOSURE
EXCESS_LIFECYCLE_HISTORY
NETWORK_RESOLUTION_LEAKAGE
BUNDLE_MANIFEST_CORRELATION
SELF_CONTAINED_OVERDISCLOSURE
EXTERNAL_PRESENTATION_UNLINKABILITY_UNKNOWN
GLOBAL_COMPLETENESS_NOT_ESTABLISHED
```

Warnings do not automatically make a disclosure invalid.

---

## 31. External SD-JWT Interoperability

RFC 9901 defines selective disclosure for JSON Web Tokens.

When an SD-JWT presentation is used as OLP-supporting evidence:

- the SD-JWT verification algorithm remains authoritative for its native cryptographic semantics;
- OLP MUST NOT interpret undisclosed claims;
- OLP SHOULD preserve the exact presentation bytes when those bytes are required for native verification;
- OLP MAY relate the presentation to OLP records using explicit evidence relationships;
- derived native presentation validity is separate from OLP record proof validity.

---

## 32. External BBS Interoperability

A BBS-derived presentation can provide selective disclosure and unlinkable derived-proof properties under its native cryptosuite.

OLP SHOULD preserve:

- disclosed messages;
- native proof bytes;
- cryptosuite identifier;
- verification method or issuer context;
- nonce/challenge semantics; and
- native verification result.

OLP MUST NOT imply unlinkability if the surrounding OLP bundle includes stable correlation identifiers that defeat it.

---

## 33. Security Considerations

### 33.1 Redaction substitution

Processors MUST reject claims that a field-deleted record retains the original Record Identity.

### 33.2 Context stripping

Removing qualifiers, relationship records, or scope information can make a technically valid subset misleading.

Disclosure planning MUST preserve semantic context required for correct interpretation.

### 33.3 Selective evidence bias

A sender can intentionally disclose favorable evidence and withhold unfavorable evidence.

OLP selective disclosure does not solve this problem.

Applications requiring completeness need an explicit closed-domain or completeness mechanism.

### 33.4 Correlation through hashes

Content-addressed identifiers can correlate repeated disclosure of identical objects.

### 33.5 Small anonymity sets

Pairwise identifiers provide little privacy when associated metadata uniquely identifies the subject.

### 33.6 Resolver side channels

Timing, DNS, TLS, request size, and cache behavior can leak more than the resolver payload itself.

### 33.7 Native proof misuse

External selective-disclosure systems MUST be verified using their native security requirements.

---

## 34. Conformance Classes

### 34.1 Privacy-Aware Bundle Producer

MUST:

- support task-scoped evidence selection;
- avoid implicit graph closure;
- preserve object identity;
- create a new manifest for a manifested subset;
- expose unresolved dependencies; and
- return privacy warnings.

### 34.2 Disclosure Planner

MUST process `DisclosureRequestV1` and produce structured results.

### 34.3 Native Selective-Disclosure Adapter

MUST preserve external format semantics and MUST NOT synthesize undisclosed claims.

### 34.4 Privacy-Aware Resolver

MUST expose network activity and MUST support a no-network mode.

---

## 35. Interoperability Test Cases

### 35.1 Whole-object proof

Record A and Record B exist; only A is required.

Expected disclosure:

```text
A included
B omitted
```

No inference that B does not exist.

### 35.2 Invalid redaction

Original record contains fields X and Y and has proof P.

Sender removes Y and supplies P.

Expected:

```text
record commitment mismatch
```

### 35.3 Relationship subset

Graph contains A->B and A->C; task needs B only.

Expected:

```text
A->B may be included
A->C may be omitted
```

### 35.4 Same-subject minimization

Authority verification succeeds using Principal P without a `sameSubjectAs` relation to Q.

Expected:

```text
sameSubjectAs evidence omitted
```

### 35.5 Self-contained tradeoff

Offline mode requires verification-method document.

Expected:

```text
resource included
privacy warning may indicate additional disclosure
```

### 35.6 SD-JWT

Native presentation discloses claim A and withholds B.

Expected:

```text
OLP processes A according to native presentation
B remains undisclosed
```

### 35.7 BBS correlation defeat

Native BBS proof is unlinkable, but OLP bundle includes stable Principal Identifier P.

Expected warning:

```text
STABLE_PRINCIPAL_CORRELATION
```

---

## 36. Design Summary

OLP v1 privacy architecture is:

```text
large evidence graph
        |
        v
declared disclosure task
        |
        v
task-scoped dependency analysis
        |
        +--> exact records
        +--> selected proofs
        +--> selected relationships
        +--> selected identity/authority evidence
        +--> selected lifecycle evidence
        +--> selected resolver resources
        |
        v
new minimized evidence bundle
```

The key distinctions are:

```text
withheld evidence        != nonexistent evidence
subset bundle            != globally complete graph
record granularity       != field-level ZK disclosure
native SD proof          != ordinary OLP proof
pairwise identifier      != guaranteed anonymity
offline verification     != minimum disclosure
```

The essential invariant is:

> **OLP v1 minimizes disclosure by selecting exact evidence objects and graph branches, never by pretending an altered record is the same immutable record.**

---

## 37. References

### 37.1 Normative OLP references

- OLP Specifications 0003 through 0009.

### 37.2 Normative Internet references

- RFC 2119.
- RFC 8174.
- RFC 3986.

### 37.3 Informative privacy/interoperability references

- RFC 9901 — Selective Disclosure for JSON Web Tokens.
- W3C Verifiable Credentials Data Model v2.0.
- W3C Data Integrity.
- W3C Data Integrity BBS Cryptosuites v1.0.
- W3C Bitstring Status List v1.0.

---

## 38. Deferred Work

Deferred work includes:

- native OLP field-level selective disclosure;
- Merkleized record commitments;
- BBS-native OLP cryptosuites;
- zero-knowledge relationship proofs;
- zero-knowledge authority proofs;
- anonymous credentials;
- private set membership;
- unlinkable OLP proof profiles;
- pairwise principal-identifier standards;
- oblivious resolver protocols;
- encrypted bundle manifests;
- disclosure receipts;
- data-retention protocols; and
- jurisdiction-specific privacy profiles.

---

**End of OLP Specification 0010 — Draft v0.1**
