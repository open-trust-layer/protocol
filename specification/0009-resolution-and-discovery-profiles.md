# OLP Specification 0009 — Resolution and Discovery Profiles

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 9 — Resolution & Discovery Profiles  
**Filename:** `specification/0009-resolution-and-discovery-profiles.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) v1 resolution and discovery layer.

It defines:

- explicit resolution requests and structured resolution results;
- separate resolution of immutable OLP evidence, verification methods, principals, lifecycle resources, and external resources;
- package-local, local-store, scheme-specific, and network resolution sources;
- caller-controlled resolution plans rather than hidden resolver precedence;
- discovery hints represented as ordinary immutable OLP records;
- core discovery service types;
- provenance, freshness, authority, and transport success as separate dimensions;
- exact identifier handling and no implicit alias merging;
- safe handling of redirects, network dereferencing, private-address targets, oversized responses, recursive discovery, and resolver loops;
- offline-first processing;
- compatibility with DID, Controlled Identifier, X.509, Web Linking, native registries, and future resolver ecosystems;
- structured reason codes;
- conformance requirements; and
- security and privacy considerations.

OLP does not define one global resolver.

OLP does not define one canonical discovery service.

OLP defines how implementations expose what they resolved, from where, under which rules, and with which unresolved assumptions.

---

## 2. Scope

This specification answers:

> How can an OLP processor obtain referenced evidence and verification resources from bundles, local stores, native identifier systems, or network services while keeping resolution explicit, provenance-visible, policy-controlled, and independent from cryptographic truth?

This specification builds on Specifications 0003 through 0008.

In particular:

- Specification 0004 separates verification-method resolution from cryptographic verification;
- Specification 0005 defines `EvidenceRefV1` and dangling references;
- Specification 0006 defines opaque Principal Identifiers;
- Specification 0007 defines lifecycle collection and native status mechanisms; and
- Specification 0008 defines packaged resolver resources and offline bundles.

This specification does **not** define:

- a global OLP DNS namespace;
- a universal DID method;
- a universal PKI;
- a global object registry;
- a global search engine;
- a mandatory HTTP endpoint;
- automatic trust in DNS, HTTPS, DID, blockchain, certificate, or registry data;
- automatic network access;
- automatic following of redirects;
- automatic alias equivalence;
- one mandatory resolver precedence order;
- a universal freshness interval; or
- a universal definition of authoritative discovery.

---

## 3. Requirements Language

BCP 14 requirement keywords have the meanings defined by RFC 2119 and RFC 8174 when written in all capitals.

---

## 4. Core Invariants

### 4.1 Resolution is not verification

Successfully obtaining bytes or an object does not establish that the object is valid, authentic, current, authoritative, or trustworthy.

### 4.2 Resolution is explicit

A processor MUST NOT perform network resolution merely because untrusted evidence contains a URI.

### 4.3 Offline operation is first-class

A processor MUST be able to resolve from a supplied bundle or local store without network access.

### 4.4 Provenance remains visible

Every successful resolution SHOULD retain enough information to identify the source class and applicable source metadata.

### 4.5 No universal source precedence

OLP does not declare:

```text
network > bundle
bundle > local
DID > X.509
HTTPS > content address
```

or any other universal resolver ranking.

### 4.6 Exact identifiers remain exact

OLP cryptographic and reference semantics use the exact identifier authenticated by the evidence.

A resolver MAY apply scheme-defined processing, but it MUST NOT rewrite the authenticated identifier in verification input.

### 4.7 Redirects do not create identifier equality

A redirect from URI A to URI B does not mean A and B are the same OLP identifier.

### 4.8 Discovery is evidence

A discovery hint is a claim that an endpoint may provide a service.

It is not an automatic delegation of authority to that endpoint.

### 4.9 Absence is not negative evidence

Failure to resolve an object does not establish that the object does not exist.

### 4.10 Resolution failure is not cryptographic invalidity

`UNAVAILABLE`, `NOT_FOUND`, `UNSUPPORTED`, and `POLICY_BLOCKED` MUST remain distinguishable from `INVALID`.

### 4.11 Resolver choice can affect observations

Different resolvers can legitimately return different historical versions, status snapshots, or native representations.

The source and request context MUST remain visible.

### 4.12 Hidden fallback is forbidden

A processor configured for offline-only or bundle-only operation MUST NOT silently fall back to network sources.

### 4.13 Search and resolution are distinct

Resolution starts from a known identifier or reference.

Discovery/search starts from an intent, principal, service type, or other query.

A search result MUST NOT be treated as if it were the uniquely resolved target unless its identity is independently verified.

### 4.14 Resource limits are mandatory

Resolvers MUST operate under finite limits.

---

## 5. Terminology

### 5.1 Resolution target

The exact identifier or evidence reference whose corresponding object or resource is requested.

### 5.2 Resolver

A component that attempts to satisfy a resolution request.

### 5.3 Resolution source

The concrete evidence source used by a resolver, such as a bundle, local store, DID method, PKI store, HTTPS endpoint, transparency service, or other registry.

### 5.4 Resolution plan

Caller-supplied policy describing which resolver classes may be attempted and under what constraints.

### 5.5 Discovery

A process for finding possible endpoints, services, identifiers, or resolution mechanisms.

### 5.6 Discovery hint

An OLP record asserting a possible endpoint for a service associated with a subject.

### 5.7 Resolution provenance

Metadata describing how and from where an object or resource was obtained.

### 5.8 Native resolver

A resolver implementing semantics defined by an external identifier or evidence system.

### 5.9 Network resolver

A resolver that causes network communication.

---

## 6. Resolution Target Classes

OLP v1 defines the following logical target classes:

```text
evidence
verificationMethod
principal
externalResource
lifecycle
service
```

These names describe processor operations, not new identity systems.

### 6.1 Evidence

An evidence target MUST be an `EvidenceRefV1`.

### 6.2 Verification method

The target MUST be the exact Verification Method Identifier authenticated by the proof.

### 6.3 Principal

The target MUST be a Principal Identifier under Specification 0006.

### 6.4 External resource

The target MUST be an absolute URI or a committed `ResourceRefV1`.

### 6.5 Lifecycle

The target MUST identify a lifecycle subject plus optional scope and evaluation time.

### 6.6 Service

The target describes discovery of a service associated with a subject and service type.

---

## 7. `ResolutionRequestV1`

`ResolutionRequestV1` is an abstract processing input, not an OLP evidence record.

```text
ResolutionRequestV1 = [
    "OLP-RESOLUTION-REQUEST",
    1,
    targetClass,
    target,
    accept,
    asOf,
    options
]
```

The array contains exactly seven elements.

### 7.1 Accept

`accept` is an unordered set of media types, object profiles, or native-format identifiers the caller can process.

An empty set means no additional format preference.

### 7.2 `asOf`

`asOf` MAY be null or an RFC 3339 date-time.

It expresses the requested historical observation point.

It does not create trusted chronology.

### 7.3 Options

Core options include:

```text
0 -> offlineOnly : boolean
1 -> maxBytes : non-negative integer or null
2 -> maxResults : non-negative integer or null
3 -> allowRedirects : boolean
4 -> requireFresh : boolean
5 -> networkPolicyId : absolute URI or null
```

Unknown options MUST NOT be silently interpreted.

---

## 8. Resolution Plans

A resolution plan is local configuration describing allowable resolution sources.

Conceptually:

```text
ResolutionPlan {
    sources: ordered list<ResolverDescriptor>
    stopConditions
    networkPolicy
    freshnessPolicy
    conflictPolicy
    limits
}
```

Source ordering is application policy.

OLP does not define one universal order.

A result SHOULD report which source index satisfied the request.

---

## 9. Core Resolver Classes

### 9.1 Bundle resolver

Searches one or more supplied evidence bundles.

Network access: forbidden.

### 9.2 Local-store resolver

Searches application-controlled storage.

Network access: implementation-defined but MUST be declared; a local-store resolver advertised as offline MUST remain offline.

### 9.3 Content-addressed resolver

Retrieves content using a content-addressed storage system and verifies the requested digest.

Content retrieval success does not establish semantic validity.

### 9.4 Scheme-specific resolver

Processes a URI or identifier according to its native scheme.

Examples can include DID methods or other registered identifier systems.

### 9.5 PKI resolver

Obtains certificate/key/status material according to a PKI profile.

### 9.6 Direct network-resource resolver

Dereferences a network URI under explicit security policy.

### 9.7 Composite resolver

Coordinates other resolver classes.

A Composite Resolver MUST retain the provenance of the resolver that actually supplied each result.

---

## 10. Evidence Resolution

For `targetClass = evidence`, a resolver MUST:

1. locate an object of the correct category;
2. recompute its Record Identity or Proof Identity;
3. compare it to the requested `EvidenceRefV1`;
4. return the object only as a matching result if identity matches.

A filename, database key, URL, or server assertion is insufficient by itself.

---

## 11. Verification-Method Resolution

A verification-method resolver MUST return structured verification material sufficient for a cryptosuite compatibility check.

At minimum:

```text
ResolvedVerificationMethod {
    requestedId
    resolvedId
    methodType
    publicVerificationMaterial
    nativeDocument
    provenance
}
```

`resolvedId` MUST NOT silently replace `requestedId` in Proof Input reconstruction.

If native method semantics say that a fragment selects a key from a controller document, the resolver MAY perform that selection, but it MUST preserve both the original requested identifier and the source document identity.

---

## 12. Principal Resolution

Principal resolution can return:

- native identity documents;
- OLP principal-relation records;
- accepted external credentials;
- local account mappings; or
- other evidence.

A Principal Resolver MUST NOT return a single boolean `identityVerified`.

It SHOULD return evidence and provenance for the caller's identity policy.

---

## 13. Lifecycle Resolution

Lifecycle collection MAY resolve:

- OLP lifecycle records;
- CRLs;
- OCSP responses;
- status-list resources;
- native registry status;
- local administrative status; or
- historical snapshots.

The resolver MUST preserve native status semantics and observation metadata.

It MUST NOT flatten all sources to `revoked = true/false`.

---

## 14. External-Resource Resolution

When a request includes `ResourceRefV1`, a successful resolver MUST verify the declared digest before returning a matching result.

When a request is by URI alone, integrity MAY remain unknown until a native authenticity mechanism or separate digest is evaluated.

---

## 15. `ResolutionResultV1`

A resolver SHOULD return:

```text
ResolutionResultV1 {
    status
    request
    matches[]
    provenance[]
    freshness
    conflicts[]
    redirects[]
    warnings[]
    errors[]
}
```

Recommended statuses:

```text
RESOLVED
PARTIALLY_RESOLVED
NOT_FOUND
UNAVAILABLE
UNSUPPORTED
POLICY_BLOCKED
AMBIGUOUS
LIMIT_EXCEEDED
MALFORMED_RESPONSE
IDENTITY_MISMATCH
```

`NOT_FOUND` means only that the attempted resolution sources did not return a matching object under the request context.

---

## 16. Match Semantics

A result is a **matching evidence result** only after identity recomputation.

A result is a **matching URI resource** when it is returned under the requested URI according to the resolver's native rules.

Those are distinct concepts.

Resolvers MUST NOT describe a URI resource as content-addressed unless an explicit digest or content-addressed identifier has been verified.

---

## 17. Multiple Results

Multiple matching or plausible results MAY exist.

Examples:

- historical versions;
- conflicting discovery hints;
- different accepted certificate chains;
- different lifecycle sources;
- multiple same-subject claims.

The resolver MUST preserve ambiguity unless the resolution plan defines a safe selection rule.

---

## 18. Historical Resolution

An `asOf` request asks for material relevant to a historical evaluation point.

A resolver MUST distinguish:

```text
retrieved now
observed at T
effective at T
valid for T
archived from T
```

where the native system provides those concepts.

A current network response MUST NOT be silently represented as a historical snapshot.

---

## 19. Freshness

Freshness is source- and profile-specific.

A resolver MAY classify a result as:

```text
FRESH
STALE
HISTORICAL
UNKNOWN
NOT_APPLICABLE
```

Freshness MUST NOT be inferred solely from HTTP receipt time when the resource defines stronger native semantics.

---

## 20. Discovery Hints

### 20.1 Purpose

A discovery hint makes an attributable statement that a subject may expose a service at an endpoint.

### 20.2 Semantic record profile

`DiscoveryHintStatementV1` is ordinary OLP record content:

```text
DiscoveryHintStatementV1 = [
    "OLP-DISCOVERY-HINT",
    1,
    subjectType,
    subject,
    serviceType,
    endpoint,
    mediaTypes,
    qualifiers,
    critical
]
```

Exactly nine elements are required.

### 20.3 Subject types

Core compact values:

```text
principal
verificationMethod
record
```

`record` uses an `EvidenceRefV1` of kind `0`.

Other subject types MUST be absolute URIs.

### 20.4 Service types

Core compact service types:

```text
evidenceResolution
bundleRetrieval
verificationMethodResolution
lifecycleStatus
```

Third-party service types MUST use absolute URI identifiers.

### 20.5 Endpoint

`endpoint` MUST be an absolute URI.

The endpoint is a discovery claim, not an automatically trusted authority.

### 20.6 Media types

`mediaTypes` is a sorted unique array of media type strings.

Before record construction, members MUST be sorted in ascending bytewise lexicographic order of their UTF-8 encodings.

An empty array means unspecified.

### 20.7 Qualifiers and criticality

Qualifier names MUST be absolute URIs.

`critical` MUST contain unique qualifier identifiers sorted in ascending bytewise lexicographic order of their UTF-8 encodings.

Every critical identifier MUST name a qualifier actually present in the record.

Unknown critical qualifiers make the hint unsupported for safe use.

---

## 21. Proofs over Discovery Hints

A discovery hint MAY have ordinary OLP proofs.

A valid assertion proof demonstrates that the proof producer asserted the hint.

It does not establish:

- that the endpoint is reachable;
- that the endpoint is controlled by the named principal;
- that the endpoint is secure;
- that the endpoint returns authoritative evidence; or
- that the endpoint remains current.

Those propositions require other evidence or policy.

---

## 22. Discovery-Hint Lifecycle

Because a discovery hint is an ordinary record, it MAY receive lifecycle evidence under Specification 0007.

For example:

```text
activate
deprecate
retire
revoke
```

A new hint does not silently delete the old hint.

---

## 23. Web and Native Discovery

Implementations MAY use external mechanisms including:

- Web Linking;
- DID or Controlled Identifier service endpoints;
- DNS-based discovery;
- PKI metadata;
- application configuration;
- local registries; or
- domain-specific service catalogs.

External discovery outputs MUST remain distinguishable from OLP discovery-hint records.

---

## 24. Network Security Policy

Every network-capable resolver MUST have an explicit network security policy.

The policy SHOULD cover:

- allowed URI schemes;
- allowed ports;
- permitted hostnames or domains;
- private-address ranges;
- loopback and link-local addresses;
- redirects;
- maximum redirect count;
- DNS rebinding;
- TLS requirements;
- certificate validation;
- authentication credentials;
- maximum response size;
- content type;
- timeouts;
- connection limits; and
- proxy behavior.

---

## 25. SSRF Protection

A generic OLP library MUST assume network identifiers in untrusted evidence can be attacker-controlled.

Network resolvers SHOULD deny loopback, link-local, private, metadata-service, and other sensitive address ranges by default unless the embedding application explicitly permits them.

Re-resolution after redirect or DNS change MUST reapply policy.

---

## 26. Redirects

Redirect following is disabled unless enabled by the resolution plan.

If followed:

- every target MUST be policy-checked;
- the full redirect chain SHOULD be reported;
- the original requested identifier MUST be preserved;
- redirects MUST NOT establish identifier equality; and
- a redirect target MUST NOT replace authenticated Proof Input fields.

---

## 27. Authentication and Authorization

Access-controlled resolvers MAY require credentials.

Resolver authentication is transport/application behavior.

Possession of credentials to query a resolver does not make the resolver's results trustworthy.

Resolvers SHOULD avoid forwarding ambient credentials to redirected or unrelated hosts.

---

## 28. Privacy

Resolution can leak:

- which participants are interacting;
- which proof is being checked;
- which principal is under investigation;
- which status is being queried;
- which historical event is disputed; and
- which graph branch a verifier is exploring.

Implementations SHOULD prefer:

- bundle-local resources;
- caches;
- privacy-preserving bulk status mechanisms;
- query batching where safe;
- minimal resolver telemetry; and
- explicit user/application consent for sensitive network resolution.

---

## 29. Resolver Caching

Caches MUST retain enough metadata to evaluate freshness and provenance.

A cache entry SHOULD record:

```text
requested identifier
resolved bytes/object identity
source
retrievedAt
native validity/freshness data
```

Cache hits MUST NOT be presented as fresh network observations unless a network request actually occurred.

---

## 30. Resolver Loops

Composite and discovery-driven resolvers MUST detect loops.

Examples:

```text
Hint A -> Resolver B
Resolver B -> Hint C
Hint C -> Resolver A
```

Loop detection should use stable identifiers and bounded recursion.

Loop exhaustion yields `LIMIT_EXCEEDED` or `RESOLUTION_LOOP`, not evidence invalidity.

---

## 31. Determinism Boundary

Given the same:

- request;
- finite supplied source set;
- resolution plan;
- resolver implementations; and
- source snapshots,

result selection SHOULD be deterministic.

Network state itself is not deterministic.

Therefore applications requiring reproducibility SHOULD preserve source snapshots or self-contained bundles.

---

## 32. Resolution Provenance

Provenance SHOULD identify:

```text
sourceClass
sourceIdentifier
requestedAt
retrievedAt
nativeVersion
contentCommitment
transportSecurityState
cacheState
```

where available.

Transport security state MUST NOT be mislabeled as evidence authenticity.

---

## 33. Structured Error Codes

Core codes include:

```text
UNSUPPORTED_TARGET_CLASS
UNSUPPORTED_IDENTIFIER_SCHEME
RESOLUTION_NOT_FOUND
RESOLUTION_UNAVAILABLE
RESOLUTION_POLICY_BLOCKED
RESOLUTION_LIMIT_EXCEEDED
RESOLUTION_LOOP
RESOLUTION_AMBIGUOUS
RESOLVED_IDENTITY_MISMATCH
RESOLVER_RESPONSE_MALFORMED
RESOURCE_DIGEST_MISMATCH
REDIRECT_BLOCKED
NETWORK_ACCESS_DISABLED
FRESHNESS_REQUIREMENT_NOT_MET
```

---

## 34. Conformance Classes

### 34.1 Offline Resolver

MUST support:

- bundle evidence resolution;
- local supplied verification material;
- zero implicit network access;
- identity recomputation; and
- structured results.

### 34.2 Evidence Resolver

MUST support `EvidenceRefV1` resolution and identity verification.

### 34.3 Verification Method Resolver

MUST return typed verification material and preserve exact requested identifiers.

### 34.4 Network Resolver

In addition to applicable resolver requirements, MUST implement explicit network policy, limits, redirect controls, and provenance.

### 34.5 Discovery Processor

MUST process `DiscoveryHintStatementV1`, critical qualifiers, proofs, lifecycle state, and conflicting hints without inventing authority.

---

## 35. Interoperability Test Cases

### 35.1 Bundle hit

Requested RecordRef exists in bundle.

Expected:

```text
status = RESOLVED
sourceClass = bundle
networkRequests = 0
```

### 35.2 Wrong object under lookup key

Local store returns object whose recomputed identity differs.

Expected:

```text
RESOLVED_IDENTITY_MISMATCH
```

### 35.3 Offline miss

No local object.

Expected:

```text
NOT_FOUND or UNAVAILABLE
networkRequests = 0
```

according to local-store semantics.

### 35.4 Network disabled

Resolution plan contains only offline sources.

A URI appears in proof.

Expected:

```text
NETWORK_ACCESS_DISABLED
```

No dereference.

### 35.5 Redirect

A permitted HTTP resolver receives redirect A -> B.

Expected:

```text
requestedId = A
redirectChain includes B
authenticated proof field remains A
```

### 35.6 Private-address target

Untrusted proof references a loopback/private address and policy does not allow it.

Expected:

```text
RESOLUTION_POLICY_BLOCKED
```

### 35.7 Conflicting discovery hints

Two validly proved hints name different lifecycle-status endpoints.

Expected:

```text
both hints preserved
selection = policy-dependent
```

### 35.8 Stale cached status

Cache contains native response past its next-update boundary.

Expected:

```text
freshness = STALE
```

The result MUST NOT be reported as a fresh observation.

---

## 36. Design Summary

```text
known reference / identifier
          |
          v
   ResolutionRequest
          |
          v
   caller ResolutionPlan
          |
    +-----+-----+----------------+
    |           |                |
    v           v                v
 bundle      local store       network/native
    |           |                |
    +-----------+----------------+
                |
                v
       ResolutionResult
                |
       +--------+--------+
       |        |        |
       v        v        v
    object   provenance freshness
       |
       v
verification / graph / lifecycle / policy
```

The essential invariant is:

> **OLP makes resolution replaceable and observable. It never hides a network lookup, resolver trust assumption, or identity rewrite inside cryptographic verification.**

---

## 37. References

### 37.1 Normative OLP references

- OLP Specifications 0003 through 0008.

### 37.2 Normative Internet references

- RFC 2119.
- RFC 8174.
- RFC 3339.
- RFC 3986.

### 37.3 Informative references

- RFC 5280 — X.509 PKI.
- RFC 6960 — OCSP.
- RFC 8288 — Web Linking.
- W3C Decentralized Identifiers.
- W3C Controlled Identifiers.
- W3C Bitstring Status List v1.0.

---

## 38. Deferred Work

Deferred topics include:

- DNS-specific OLP discovery records;
- standardized OLP `.well-known` metadata;
- peer-to-peer discovery;
- distributed hash-table profiles;
- resolver transparency;
- privacy relays;
- oblivious resolution;
- resolver reputation;
- resolver availability proofs;
- subscription and push resolution;
- event streams;
- global indexing; and
- transport-specific endpoints.

---

**End of OLP Specification 0009 — Draft v0.1**
