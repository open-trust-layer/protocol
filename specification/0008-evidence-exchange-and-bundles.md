# OLP Specification 0008 — Evidence Exchange and Bundles

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 8 — Evidence Exchange & Bundles  
**Filename:** `specification/0008-evidence-exchange-and-bundles.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) v1 evidence-exchange and bundle layer.

It defines:

- manifested evidence bundles built from existing immutable OLP records and proofs;
- a bundle manifest as an ordinary immutable OLP record rather than a new trust primitive;
- stable bundle identity through the Record Identity of the manifest record;
- explicit roots and inventory;
- packaging of external resolver resources by cryptographic commitment;
- portable and self-contained-verification bundle profiles;
- deterministic duplicate detection and merge behavior;
- partial, dangling, and intentionally minimized bundles;
- object extraction without identity mutation;
- bundle integrity, provenance, completeness, and policy sufficiency as distinct concepts;
- optional proof of the bundle manifest using ordinary OLP proofs;
- offline verification requirements;
- streaming-friendly processing semantics;
- safe handling of untrusted or very large bundles;
- structured ingestion and verification results;
- conformance requirements; and
- security and privacy considerations.

A bundle is a finite transport and disclosure container.

A bundle does not make its contents true.

A bundle does not change the identity or semantics of any object it contains.

A bundle manifest can make a cryptographically addressable statement about exactly which evidence objects and external resources were selected for a particular package.

---

## 2. Scope

This specification answers the question:

> How can one OLP participant package a finite set of records, proofs, graph evidence, lifecycle evidence, identity or authority evidence, and verification resources so another participant can process the same evidence independently without turning the package itself into a hidden source of trust?

This specification builds on:

- OLP Specification 0003 — Record Representation;
- OLP Specification 0004 — Proofs and Verification;
- OLP Specification 0005 — Evidence Relationships and Graphs;
- OLP Specification 0006 — Identity and Authority Evidence; and
- OLP Specification 0007 — Status, Revocation, and Lifecycle Evidence.

Specification 0005 introduced an abstract evidence-bundle concept and deliberately deferred canonical bundle identity, commitments, and transport serialization.

This specification refines that boundary.

This specification does **not** define:

- a universal claim that a bundle contains all relevant evidence;
- a universal evidence-sufficiency algorithm;
- a universal trust score for a bundle;
- a mandatory storage provider;
- a mandatory content-delivery network;
- a mandatory archive;
- a mandatory resolver;
- a universal encryption format;
- a universal compression algorithm;
- a field-level selective-disclosure cryptosystem;
- a mandatory online verification workflow;
- a mutable bundle object;
- a new signature mechanism for bundles; or
- a transport-specific HTTP or JSON encoding.

Transport encodings are defined by later profiles.

---

## 3. Requirements Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described by BCP 14 when, and only when, they appear in all capitals.

---

## 4. Core Invariants

### 4.1 Packaging does not mutate evidence

Putting an OLP record or proof into a bundle MUST NOT change:

- Record Identity;
- Proof Identity;
- proof cryptographic validity;
- proof purpose;
- lifecycle state;
- relationship semantics; or
- authority semantics.

### 4.2 Bundle membership is not endorsement

A sender MAY transmit evidence it disputes, rejects, archives, or does not understand.

Membership in a bundle MUST NOT imply endorsement, acceptance, authorship, witness status, or trust.

### 4.3 Bundle integrity is not object truth

A bundle manifest can establish which object identities were selected.

It cannot establish that those objects are true or trustworthy.

### 4.4 Object integrity is independent of bundle integrity

An individual record or proof can verify correctly even when:

- it was received outside a bundle;
- the bundle manifest is absent;
- the bundle manifest is invalid; or
- the bundle is incomplete.

Conversely, a valid manifest does not make an invalid proof valid.

### 4.5 Completeness is contextual

A bundle MUST NOT be described as containing "all evidence" unless an external rule, authority, closed dataset, or other explicit basis defines the completeness domain.

### 4.6 Sufficiency is policy-specific

A self-contained bundle can contain everything required to perform specified protocol operations while still being insufficient for a particular trust or business decision.

### 4.7 Order is non-semantic

Ordering of records, proofs, resources, roots, inventory entries, or transport frames MUST NOT imply chronology, precedence, trust, dependency, or authority unless another specification explicitly defines such semantics.

### 4.8 Duplicate transmission adds no weight

Repeated transmission of the same identity-bearing object MUST NOT increase protocol-level evidence weight.

### 4.9 Manifest identity reuses Record Identity

OLP MUST NOT define a second bundle-hash namespace when the bundle manifest can be represented as an ordinary OLP record.

The stable identifier of a manifested bundle is the Record Identity of its manifest record.

### 4.10 Manifest proof reuses OLPProof

A party wishing to assert, authorize, acknowledge, or otherwise prove a bundle manifest MUST create an ordinary OLP proof over the manifest record.

No bundle-specific signature primitive is defined.

### 4.11 External resources are committed, not trusted

External resources included for resolution or offline verification MUST be integrity-bound by explicit commitments.

The commitment establishes packaged bytes, not the authenticity or authority of the resource.

### 4.12 Offline verification is first-class

The bundle format MUST permit an implementation to carry enough material for cryptographic verification without mandatory network access.

### 4.13 Partial bundles are valid

A bundle MAY intentionally omit referenced evidence.

Omission creates partial or dangling evidence, not object invalidity.

### 4.14 Merge is additive

Merging bundles MUST NOT silently delete, rewrite, or replace immutable evidence.

### 4.15 Privacy minimization is expected

Bundle producers SHOULD include only evidence reasonably necessary for the declared exchange purpose.

---

## 5. Terminology

### 5.1 Evidence bundle

A finite package containing an optional bundle manifest, OLP records, OLP proofs, and optional external resources.

### 5.2 Manifested bundle

A bundle whose selected OLP objects and external resources are enumerated by a `BundleManifestStatementV1` record.

### 5.3 Bundle ID

The Record Identity of the manifest record.

### 5.4 Root

An `EvidenceRefV1` selected as an entry point for a verification, traversal, disclosure, audit, or application task.

### 5.5 Inventory

The set of OLP evidence identities selected by the manifest.

### 5.6 External resource

A byte sequence that is not itself an OLP record or OLP proof but is carried to support resolution, verification, status processing, native credential processing, archival processing, or another explicitly identified purpose.

### 5.7 Resource commitment

An algorithm identifier and digest that binds to exact external-resource bytes.

### 5.8 Portable bundle

A bundle intended for ordinary exchange that MAY rely on external resolution.

### 5.9 Self-contained verification bundle

A bundle intended to permit the specified OLP cryptographic-verification operations without network resolution.

### 5.10 Bundle closure

The finite set of evidence and resources required by a declared bundle profile or verification task.

### 5.11 Dangling reference

A valid reference whose target is not present in the local bundle or current resolver context.

---

## 6. Architectural Model

```text
                     Bundle Manifest Record
                     Record Identity = Bundle ID
                              |
                     ordinary OLP Proof(s)
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
       roots[]          evidenceInventory[]   resourceInventory[]
          |                   |                   |
          v                   v                   v
      OLP records         OLP proofs        external resources
          \                   |                   /
           \                  |                  /
            +-----------------+-----------------+
                              |
                              v
                     independent verifier
```

The manifest records selection.

The contained evidence retains its own identity and semantics.

---

## 7. Relationship to Specification 0005

Specification 0005 defines an abstract `OLPEvidenceBundleV1` containing roots, records, and proofs.

A bundle satisfying that abstract model remains a valid ad hoc evidence collection.

This specification defines additional conformance profiles for **manifested bundles**.

A processor MUST NOT reinterpret an unmanifested collection as having a bundle identity.

A processor MAY create a new manifest record describing an existing finite collection. Doing so creates a new evidence artifact; it does not alter the contained objects.

---

## 8. `BundleManifestStatementV1`

### 8.1 Semantic record profile

A bundle manifest is an ordinary OLP record conforming to Specification 0003 whose semantic content is exactly one `BundleManifestStatementV1`.

### 8.2 Exact structure

```text
BundleManifestStatementV1 = [
    "OLP-EVIDENCE-BUNDLE-MANIFEST",  ; 0 discriminator
    1,                               ; 1 version
    profile,                         ; 2 bundle profile
    roots,                           ; 3 sorted array<EvidenceRefV1>
    inventory,                       ; 4 sorted array<EvidenceRefV1>
    resourceInventory,               ; 5 sorted array<ResourceRefV1>
    metadata,                        ; 6 map
    extensions,                      ; 7 map
    critical                         ; 8 sorted array
]
```

The array MUST contain exactly nine elements.

### 8.3 Discriminator

Index 0 MUST equal:

```text
OLP-EVIDENCE-BUNDLE-MANIFEST
```

### 8.4 Version

Index 1 MUST equal integer `1`.

### 8.5 Profile

Core v1 profiles are:

```text
portable
selfContainedVerification
```

Other compact strings are reserved.

Third-party profiles MUST use absolute URI identifiers.

### 8.6 Roots

`roots` MUST contain unique `EvidenceRefV1` values.

Roots MUST be sorted by `EvidenceRefCanonicalBytes` from Specification 0005.

Every root SHOULD also appear in `inventory`.

A missing root inventory entry is non-conforming for the core profiles.

### 8.7 Inventory

`inventory` MUST contain unique `EvidenceRefV1` values sorted by `EvidenceRefCanonicalBytes`.

Inventory is a statement about the selected identity set.

It is not a statement that every referenced object is valid, trusted, or available outside this bundle.

### 8.8 Resource inventory

`resourceInventory` MUST contain unique `ResourceRefV1` values sorted by their deterministic CBOR encodings under the restrictions of Specification 0004.

### 8.9 Metadata

The core metadata map MAY contain:

```text
0 -> declaredPurpose : absolute URI or null
1 -> created         : RFC 3339 date-time or null
2 -> expires         : RFC 3339 date-time or null
```

The time fields are producer-declared metadata and do not establish independent chronology.

Unknown integer metadata labels are not permitted in version 1.

### 8.10 Extensions

Extension keys MUST be absolute URIs.

All extension values are part of Record Identity because they are part of the manifest record content.

### 8.11 Critical

`critical` contains extension identifiers that must be understood to safely interpret the manifest.

Unknown critical extensions yield `UNSUPPORTED_CRITICAL_BUNDLE_EXTENSION`.

---

## 9. `ResourceRefV1`

### 9.1 Purpose

`ResourceRefV1` identifies exact external-resource bytes packaged for a known use.

### 9.2 Exact structure

```text
ResourceRefV1 = [
    resourceId,        ; absolute URI or null
    mediaType,         ; normalized media type text
    hashAlgorithmId,   ; COSE hash algorithm identifier
    digestBytes        ; raw digest bytes
]
```

The array MUST contain exactly four elements.

### 9.3 Resource ID

`resourceId` MAY be null.

When non-null, it MUST be an absolute URI.

The exact URI is the identity under which the packaged bytes are being offered to a resolver.

It does not prove that the URI owner published or endorsed those bytes.

### 9.4 Media type

`mediaType` MUST contain exactly a syntactically valid media type `type/subtype` with lowercase type and subtype.

Media type parameters MUST NOT appear in `ResourceRefV1` v1.

A future resource-reference version may define a canonical parameter representation if one is required. This restriction prevents semantically equivalent parameter order or quoting from creating avoidable manifest-identity differences.

### 9.5 Hash algorithm

SHA-256 using COSE algorithm identifier `-16` MUST be supported.

Additional suitable algorithms MAY be supported.

### 9.6 Digest

`digestBytes` is the exact digest of the external-resource payload bytes as packaged.

### 9.7 Equality

Two `ResourceRefV1` values are equal only if all four abstract values are equal.

---

## 10. Abstract Bundle Package

A manifested bundle has the transport-independent abstract model:

```text
ManifestedEvidenceBundleV1 {
    manifestRecord: OLPRecord
    records: collection<OLPRecord>
    proofs: collection<OLPProof>
    resources: collection<PackagedResourceV1>
}
```

Where:

```text
PackagedResourceV1 = [
    resourceRef,
    contentBytes
]
```

Transport specifications MAY add framing metadata that does not alter this abstract model.

---

## 11. Manifest Validation

A bundle processor MUST:

1. validate the manifest record under Specification 0003;
2. confirm that the semantic content is `BundleManifestStatementV1`;
3. compute the manifest Record Identity;
4. validate roots, inventory, resource inventory, extensions, and criticality;
5. index supplied records by recomputed Record Identity;
6. index supplied proofs by recomputed Proof Identity;
7. verify every packaged resource digest;
8. compare supplied identities against the manifest inventory; and
9. report missing, unexpected, conflicting, and malformed items separately.

Manifest validation does not require verifying every contained proof unless the caller requests cryptographic verification.

---

## 12. Bundle Identity

The bundle ID is:

```text
RecordIdentity(manifestRecord)
```

No additional `BundleIdentityDigest` is defined.

Changing:

- profile;
- roots;
- inventory;
- resource inventory;
- manifest metadata;
- manifest extensions; or
- manifest criticality

changes the manifest Record Identity and therefore creates a different bundle ID.

Changing transport order does not.

---

## 13. Manifest Proofs

A proof over the manifest record MAY use any proof purpose valid under Specification 0004.

Examples:

```text
assertion
    "I assert this is the evidence set I selected."

acknowledgement
    "I acknowledge this exact manifest."

authorization
    "I authorize release of this exact manifest."
```

A proof over the manifest MUST NOT be interpreted as recursively asserting the truth of every contained object unless the enclosing record semantics and application policy explicitly establish such a claim.

---

## 14. Portable Bundle Profile

A `portable` bundle:

- MUST include its manifest record;
- MUST include every manifest root;
- MUST include every manifest inventory object that the package claims to carry;
- MAY intentionally omit evidence not listed in inventory;
- MAY contain dangling references from listed objects to unlisted objects;
- MAY omit verification-method resources;
- MAY rely on external resolvers; and
- MUST preserve all missing-reference conditions explicitly during processing.

The profile optimizes finite exchange, not offline closure.

---

## 15. Self-Contained Verification Profile

A `selfContainedVerification` bundle MUST contain enough material to perform all of the following for every included OLP proof whose target record is included:

1. reconstruct the proof target commitment;
2. reconstruct `ProofInputV1`;
3. resolve or otherwise obtain the referenced verification material from packaged content;
4. perform the declared cryptographic suite verification; and
5. report verification-method status as `NOT_EVALUATED` if no status evidence is included rather than performing hidden network access.

A self-contained-verification bundle:

- MUST NOT require network access for OLP cryptographic verification;
- MUST include required verification material as an OLP record, native embedded method, or committed external resource;
- MUST preserve provenance describing how packaged verification material maps to the authenticated `verificationMethod` reference;
- MAY omit identity, authority, lifecycle, or policy evidence not required for raw cryptographic verification;
- MUST NOT claim universal policy sufficiency merely because network access is unnecessary.

---

## 16. Closure

### 16.1 Declared closure

Closure is relative to:

- roots;
- bundle profile;
- supported specifications;
- requested verification operations; and
- caller policy.

### 16.2 No universal graph closure

OLP does not define "all evidence reachable from a root" as the mandatory bundle contents.

Graph expansion can be unbounded, privacy-invasive, circular, or irrelevant.

### 16.3 Core structural closure

When a producer claims closure for a specific processor, every mandatory dependency of that processor MUST either:

- be present; or
- be explicitly listed as intentionally unresolved.

---

## 17. Missing and Unexpected Items

Recommended statuses include:

```text
INVENTORY_ITEM_PRESENT
INVENTORY_ITEM_MISSING
UNEXPECTED_ITEM_PRESENT
ROOT_MISSING
RESOURCE_MISSING
RESOURCE_DIGEST_MISMATCH
EVIDENCE_IDENTITY_MISMATCH
IDENTITY_COLLISION_OR_CONFLICT
```

Unexpected items MAY be retained but MUST NOT silently become manifest members.

---

## 18. Duplicate and Conflict Handling

Two byte-distinct records that recompute to the same Record Identity represent an identity collision or implementation defect and MUST trigger:

```text
IDENTITY_COLLISION_OR_CONFLICT
```

The same applies to Proof Identity.

Exact duplicate copies MAY be deduplicated.

Deduplication MUST NOT change the manifest inventory.

---

## 19. Merge Semantics

Merging bundles means forming a contextual union of independently identified evidence.

A merge operation MUST:

- preserve all distinct records;
- preserve all distinct proofs;
- preserve all distinct external resources;
- preserve source bundle IDs where available;
- preserve conflicts; and
- avoid silently selecting one conflicting resource for the same URI.

A merge MAY create a **new manifest record** for the merged selection.

The new manifest has a new bundle ID.

Original manifests remain valid historical evidence.

---

## 20. Extraction and Subsetting

A processor MAY extract a subset of objects from a bundle.

If the extracted package retains the original manifest but omits manifest inventory members, it MUST report itself as incomplete relative to that manifest.

A producer wishing to create a clean independently verifiable subset SHOULD create a new manifest enumerating the subset.

Creating the new manifest does not mutate or supersede the source manifest unless explicit relationship evidence states so.

---

## 21. Bundle Completeness

The following are distinct:

```text
manifest integrity
inventory presence
reference closure
verification closure
status coverage
authority coverage
application sufficiency
global completeness
```

A processor MUST NOT collapse these dimensions into one boolean named `complete`.

---

## 22. External Resources

External resources MAY include:

- DID or controlled-identifier documents;
- certificates;
- certificate chains;
- CRLs;
- OCSP responses;
- W3C status lists;
- RFC 3161 timestamp tokens;
- transparency receipts;
- native credential presentations;
- policy documents;
- registry snapshots; or
- future resolver artifacts.

The bundle layer treats those bytes as committed resources.

Their semantic and cryptographic validation belongs to the applicable resolver, native format, or application profile.

---

## 23. Resource Provenance

A `ResourceRefV1` with URI `U` means only:

> These exact bytes are packaged for use under identifier U.

It does not prove:

> The authoritative resource currently available at U has these bytes.

Applications requiring that stronger conclusion need native authenticity evidence, an accepted resolver source, transport security plus freshness policy, or separate OLP evidence.

---

## 24. Time and Freshness

Bundle manifest `created` and `expires` fields are producer declarations.

External resource freshness MUST be evaluated according to the resource's native semantics where available.

Packaging a stale resource does not make it fresh.

A bundle MAY intentionally preserve stale historical resolver material for historical verification.

---

## 25. Lifecycle and Historical Verification

A historical evidence package MAY contain:

- historical verification material;
- lifecycle evidence;
- compromise evidence;
- independent time evidence; and
- archival renewal evidence.

The bundle processor MUST keep:

```text
packagedAt
effectiveAt
proof.created
native thisUpdate/nextUpdate
independent timestamp
```

semantically distinct.

---

## 26. Bundle Processing Result

A processor SHOULD return a structured result similar to:

```text
BundleProcessingResult {
    manifestConformance
    bundleId
    profile
    criticalExtensionStatus
    rootResults[]
    inventoryResults[]
    resourceResults[]
    proofVerificationResults[]
    danglingReferences[]
    unexpectedItems[]
    conflicts[]
    closureStatus
    warnings[]
    errors[]
}
```

A failed proof MUST NOT automatically mark unrelated proofs as invalid.

---

## 27. Resource Limits

Processors MUST support configurable limits for untrusted bundles.

Limits SHOULD include:

- total bytes;
- number of records;
- number of proofs;
- number of resources;
- maximum object size;
- maximum resource size;
- maximum nesting depth;
- maximum decompressed size;
- maximum graph traversal depth;
- maximum resolver operations;
- maximum cryptographic operations; and
- wall-clock budget.

Limit exhaustion MUST report incomplete processing, not evidence invalidity.

---

## 28. Compression

Compression is a transport concern.

Bundle identity and OLP object identities MUST NOT depend on compression format or compression level.

Processors MUST defend against decompression bombs and misleading compressed-size assumptions.

---

## 29. Encryption

Bundle encryption is not defined by this specification.

Encryption MAY protect confidentiality during storage or transport.

Encryption MUST NOT be treated as evidence authenticity unless the selected encryption system explicitly provides and verifies authenticity.

Decryption MUST recover the same abstract bundle objects before OLP identity processing.

---

## 30. Streaming

Bundle semantics do not require buffering the complete package.

A streaming transport MAY:

1. deliver the manifest first;
2. deliver records, proofs, and resources in any order;
3. verify each item as it arrives;
4. mark inventory entries present;
5. report unresolved inventory at end-of-stream.

Transport framing is defined by Specification 0012.

Streaming order is not semantic.

---

## 31. Privacy

Bundle construction is a disclosure act.

Producers SHOULD minimize:

- unrelated graph branches;
- unused identity bindings;
- unused authority evidence;
- unnecessary lifecycle history;
- historical verification methods;
- resolver metadata;
- correlation identifiers; and
- external resources not needed by the recipient.

A self-contained bundle often leaks more than an online-resolution bundle.

The privacy specification defines stronger minimization rules.

---

## 32. Security Considerations

### 32.1 Manifest confusion

Implementations MUST bind operations to the exact manifest Record Identity and MUST NOT select a manifest by filename or display label alone.

### 32.2 URI confusion

Packaged resources MUST retain exact resource identifiers. Redirect targets or aliases MUST NOT silently replace the authenticated identifier.

### 32.3 Resource substitution

Resource digest mismatch MUST stop use of that packaged resource.

### 32.4 Zip bombs and parser bombs

Transport implementations MUST enforce resource limits before or during decompression and parsing.

### 32.5 Hidden network access

A self-contained-verification profile MUST NOT silently fall back to network resolution.

### 32.6 Over-bundling

Over-bundling can reveal identity, social-graph, commercial, legal, and lifecycle information unrelated to the verification task.

### 32.7 Malicious but valid evidence

A structurally valid bundle may intentionally contain false claims, invalid proofs, contradictory records, revoked keys, or hostile external documents.

Processors MUST treat bundle syntax and trust interpretation separately.

---

## 33. Conformance Classes

### 33.1 Bundle Reader

A conforming Bundle Reader MUST:

- parse the abstract bundle model;
- validate manifest structure;
- compute bundle ID;
- index records and proofs by recomputed identity;
- validate resource commitments;
- detect missing and unexpected inventory items;
- preserve dangling references; and
- return structured results.

### 33.2 Bundle Producer

A conforming Bundle Producer MUST:

- construct valid manifests;
- sort roots and inventory deterministically;
- compute all evidence identities;
- compute resource commitments;
- avoid duplicate inventory entries; and
- produce a package consistent with its selected profile.

### 33.3 Self-Contained Verification Producer

In addition to Bundle Producer requirements, it MUST include all resources needed for declared offline cryptographic verification.

### 33.4 Streaming Bundle Processor

A conforming Streaming Bundle Processor MUST preserve the same semantic result independent of legal transport-frame ordering.

---

## 34. Interoperability Test Cases

### 34.1 Order independence

Two bundles contain identical manifest and objects in different transport order.

Expected:

```text
same bundleId
same inventory result
```

### 34.2 Missing inventory member

Manifest lists Record A and Proof P; Proof P is omitted.

Expected:

```text
manifestConformance = CONFORMING
Proof P presence = MISSING
```

Record A is not invalidated.

### 34.3 Extra object

Bundle includes Record B not listed in manifest.

Expected:

```text
UNEXPECTED_ITEM_PRESENT
```

B does not become a manifest member.

### 34.4 Resource substitution

Resource bytes do not match committed digest.

Expected:

```text
RESOURCE_DIGEST_MISMATCH
```

Resource MUST NOT be used.

### 34.5 Self-contained no-network rule

Required verification method is absent.

Expected:

```text
SELF_CONTAINED_REQUIREMENT_NOT_MET
```

Processor MUST NOT silently fetch it.

### 34.6 Merge

Bundles X and Y are merged into a new manifested selection.

Expected:

```text
X manifest preserved
Y manifest preserved
new manifest has distinct bundleId
contained object identities unchanged
```

### 34.7 Duplicate transmission

Same proof appears three times.

Expected:

```text
one Proof Identity member
no increased evidentiary weight
```

### 34.8 Manifest proof

A valid assertion proof protects the manifest.

Expected:

```text
manifest proof cryptographicValidity = VALID
contained proof validity = evaluated independently
```

---

## 35. Design Summary

OLP evidence exchange is:

```text
immutable objects
      +
manifest record
      +
optional external-resource commitments
      +
ordinary proofs over the manifest
      =
portable evidence package
```

The design preserves the following distinctions:

```text
object identity       != bundle identity
bundle identity       != bundle endorsement
bundle endorsement    != truth of contents
inventory presence    != reference closure
reference closure     != policy sufficiency
self-contained        != globally complete
resource commitment   != resource authority
```

The essential invariant is:

> **A bundle makes a finite evidence selection portable without changing what the selected evidence means.**

---

## 36. References

### 36.1 Normative OLP references

- OLP Specification 0003 — Record Representation.
- OLP Specification 0004 — Proofs and Verification.
- OLP Specification 0005 — Evidence Relationships and Graphs.
- OLP Specification 0006 — Identity and Authority Evidence.
- OLP Specification 0007 — Status, Revocation, and Lifecycle Evidence.

### 36.2 Normative Internet references

- RFC 2119.
- RFC 8174.
- RFC 3339.
- RFC 3986.
- RFC 8949.
- RFC 9054.

### 36.3 Informative references

- RFC 8742 — CBOR Sequences.
- RFC 3161 — Time-Stamp Protocol.
- RFC 4998 — Evidence Record Syntax.
- RFC 9162 — Certificate Transparency Version 2.0.
- RFC 9943 — SCITT Architecture.
- W3C Verifiable Credentials Data Model v2.0.
- W3C Bitstring Status List v1.0.

---

## 37. Deferred Work

Deferred topics include:

- transport serialization and HTTP framing;
- bundle encryption profiles;
- bundle compression profiles;
- content-addressed archive profiles;
- Merkleized very-large bundle manifests;
- chunk-level resumable transfer;
- erasure coding;
- encrypted disclosure to multiple recipients;
- proof-of-availability systems;
- trusted archival custody profiles;
- domain-specific completeness rules; and
- universal policy sufficiency.

---

**End of OLP Specification 0008 — Draft v0.1**
