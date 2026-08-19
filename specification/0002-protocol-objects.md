# Open Layer Protocol — Protocol Objects

**Document:** `specification/0002-protocol-objects.md`
**Status:** Draft v0.1
**Milestone:** 2 — Protocol Objects
**Depends on:** `0001-terminology.md`

---

# 1. Purpose

This document defines the conceptual object model of the Open Layer Protocol (OLP).

It determines:

* which semantic concepts defined by OLP require first-class protocol representation;
* the responsibilities of the core Record types;
* the common structure shared by Records;
* how Records are identified, related, extended, verified, and evolved;
* which concepts remain embedded, derived, contextual, transport-level, or application-level rather than first-class protocol objects.

This document deliberately does **not** define:

* a concrete serialization format;
* canonical JSON, CBOR, or other encoding;
* a specific hashing algorithm;
* a specific signature algorithm;
* a specific Identifier system;
* transport protocols;
* storage APIs;
* database schemas;
* concrete cryptographic proof suites;
* application Trust Models;
* domain-specific profiles.

Those concerns belong to later specifications.

The purpose of this milestone is to establish the **stable conceptual architecture** upon which those later mechanisms can be built.

---

# 2. Normative Language

The key words **MUST**, **MUST NOT**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **MAY**, and related terms express protocol requirements and design constraints.

Until OLP adopts a formal standards-process document, these terms should be interpreted according to their ordinary standards-language meanings.

---

# 3. Governing Design Rule

A vocabulary concept becomes a first-class protocol object only where independent interoperability requires it.

A concept is a strong candidate for first-class representation when it needs to be independently:

* serialized;
* identified;
* referenced;
* exchanged;
* verified;
* related to other protocol information;
* assigned provenance;
* subjected to status changes;
* preserved across implementations.

Not every important semantic concept requires its own Record type.

OLP therefore distinguishes between:

1. **first-class Records;**
2. **reusable semantic structures;**
3. **specializations and profiles;**
4. **derived or contextual concepts;**
5. **transport, presentation, and implementation-local structures.**

---

# 4. Core Object Model

The universal first-class carrier of independently representable OLP information is the **Record**.

The initial OLP core defines the following Record types:

```text
Record
│
├── Claim
│
├── Attestation
│
├── Observation
│
├── Event
│
└── StatusChange
```

Among these:

* **Claim** is an auxiliary core Record type used when an otherwise unattributed proposition requires independent identity or referencing.
* **Attestation**, **Observation**, **Event**, and **StatusChange** are the primary operational core Record types.

The following remain reusable semantic structures rather than mandatory independent Record families:

```text
Outcome
EntityReference
Party
Reference
Proof
```

The following remain semantic specializations:

```text
Interaction → Event specialization

Revocation   → StatusChange operation
Supersession → StatusChange operation
```

The following remain derived or contextual concepts:

```text
Evidence
History
Provenance
Context
Trust
TrustModel
Verification
Status
ApplicationDecision
```

The following remain outside the semantic Record model unless a later specification explicitly promotes them:

```text
Bundle
Presentation
Encryption wrapper
Selective-disclosure package
Transport metadata
Local storage metadata
```

---

# 5. Record

## 5.1 Definition

A **Record** is the universal first-class envelope for independently representable OLP information.

A Record provides the common protocol-level structure required to identify, type, preserve, relate, extend, and verify independently meaningful protocol information.

The semantic meaning of a Record is determined by:

* its declared Record type;
* the applicable type version;
* its type-specific content;
* applicable intrinsic relationships;
* applicable profiles;
* applicable critical semantics.

The mere fact that information is represented as a valid Record does not imply that the information is:

* true;
* accurate;
* trusted;
* authoritative;
* independent;
* current;
* legally valid;
* acceptable for a particular purpose.

---

## 5.2 Universal Envelope

The mandatory OLP Record envelope SHALL remain minimal.

Every Record SHALL unambiguously identify:

1. the applicable core Record envelope version;
2. its semantic Record type;
3. the version of that type's interpretation rules;
4. its type-specific semantic content.

Conceptually:

```text
Record
├── envelope_version
├── type
├── type_version
└── content
```

The exact serialized field names and encoding are not defined by this specification.

A version may be encoded separately from its type identifier or incorporated into an unambiguous versioned type identifier.

---

## 5.3 Optional Generic Machinery

The Record envelope SHALL support generic optional mechanisms for:

```text
relationships
profiles
extensions
criticality declarations
```

A Record is not required to use any of these mechanisms unless the applicable Record type, profile, or extension requires them.

The universal envelope SHALL NOT require every Record to contain:

* an Issuer;
* a Subject;
* a timestamp;
* a signature;
* a proof;
* mutable status;
* a Trust value;
* a Reputation value;
* a universal provenance field.

Such information belongs to type-specific semantics or later protocol layers when required.

---

# 6. Record Identity

## 6.1 Stable Identity

Every Record SHALL possess a stable cryptographically bound **Record Identity**.

Record Identity SHALL bind to the identity-relevant representation of the Record.

The exact identity mechanism is deferred to later specifications.

Possible future mechanisms MAY include content hashes or other cryptographically bound content identifiers, but this document does not mandate any particular algorithm.

---

## 6.2 Derived Identity

Record Identity MAY be deterministically derived rather than stored as an intrinsic field.

The protocol SHALL NOT require a Record to contain its own Record Identity as part of the material from which that same identity is calculated.

---

## 6.3 Semantic Immutability

A Record SHALL be semantically immutable once issued or otherwise finalized as an identifiable protocol Record.

Any change to identity-relevant information SHALL produce a distinct Record Identity.

A Record MUST NOT be silently rewritten while retaining its prior Record Identity.

For example:

```text
R1
Claim:
    shipment weight = 1,240 kg
```

must not silently become:

```text
R1
Claim:
    shipment weight = 1,420 kg
```

A correction instead requires new protocol information, such as:

```text
R1
Claim:
    shipment weight = 1,240 kg

R2
Claim:
    shipment weight = 1,420 kg

S1
StatusChange:
    operation: supersede
    target: R1
    successor: R2
```

---

## 6.4 Identity-Relevant Information

Information intrinsic to the meaning of a Record SHALL participate in its immutable identity boundary.

This normally includes:

* envelope version;
* semantic Record type;
* type version;
* type-specific content;
* intrinsic semantic relationships;
* applicable profiles;
* identity-relevant extensions;
* required critical-semantic declarations;
* intrinsic proof material where the applicable mechanism defines it as part of the Record.

The precise canonical identity representation is deferred to a later specification.

---

## 6.5 Local Metadata

Implementation-local metadata MUST remain outside the Record identity boundary.

Examples include:

* receipt time;
* database row identifiers;
* storage location;
* cache status;
* UI labels;
* search indexes;
* local annotations;
* synchronization state;
* transport routing information.

Conceptually:

```text
StoredRecord
├── Record
│     └── cryptographic Record Identity
│
└── LocalMetadata
      ├── received_at
      ├── database_id
      ├── cache_state
      └── ui_metadata
```

Modification of LocalMetadata MUST NOT alter Record Identity.

---

## 6.6 Replication

Copies of the same immutable Record MAY retain the same Record Identity across:

* Participants;
* storage systems;
* transports;
* applications;
* jurisdictions.

Copying, caching, storing, or relaying a Record does not create a new protocol assertion merely because another system now possesses a copy.

---

## 6.7 Semantic Equivalence

Record Identity applies to the represented Record, not to semantic similarity.

Two Records MAY contain Claims that appear semantically equivalent while remaining distinct Records.

OLP core SHALL NOT require general semantic deduplication or natural-language equivalence detection.

---

## 6.8 Identity Verification Without Semantic Understanding

Computing or verifying Record Identity MUST NOT require understanding the application-specific semantic meaning of the Record type.

An implementation that does not understand a future Record type SHOULD still be able, where supported by the envelope and identity mechanism, to:

* preserve the Record;
* calculate or verify its Record Identity;
* compare it with another purported copy;
* inspect generic envelope information.

This property is essential for forward compatibility.

---

# 7. Claim Record

## 7.1 Purpose

A **Claim Record** independently materializes an otherwise unattributed proposition so that the proposition can be:

* independently identified;
* reused;
* referenced;
* related to other Records;
* discussed by multiple Attestations.

A Claim Record represents a proposition.

It does not represent somebody asserting that proposition merely because the Claim exists as a Record.

---

## 7.2 Embedded Claims

Claims do not always need independent Record identity.

A Claim MAY be embedded inside another Record, particularly an Attestation.

For example:

```text
Attestation
    claims:
        - shipment X was delivered
```

This embedded Claim is semantically meaningful but does not automatically become a separate Record.

---

## 7.3 Independently Materialized Claims

Where independent reference is useful, the Claim MAY be represented as a Claim Record.

For example:

```text
C1
type: Claim
content:
    shipment X was delivered
```

Then:

```text
A1
type: Attestation
issuer: Alice
claim: ref(C1)
```

and:

```text
A2
type: Attestation
issuer: Bob
claim: ref(C1)
```

may assert the same independently identified proposition.

---

## 7.4 No Implicit Issuer

Creating, storing, transporting, or materializing a Claim Record MUST NOT automatically make that actor the Issuer of the proposition.

Attributable assertion belongs to the **Attestation** model.

---

## 7.5 No Truth Semantics

Standalone representation of a Claim MUST NOT imply:

* truth;
* attribution;
* authority;
* agreement;
* Trust.

---

# 8. Attestation Record

## 8.1 Purpose

An **Attestation Record** represents an attributable assertion of one or more Claims.

Its primary semantic question is:

> **Who is asserting what?**

Attestation SHALL be a core first-class Record type.

---

## 8.2 Issuer Requirement

An Attestation SHALL identify its **declared Issuer** according to the applicable type rules.

Declared Issuer semantics and verified attribution are separate concepts.

For example:

```text
issuer: Alice
```

may be structurally valid even when verification of Alice's control or authorization is:

```text
indeterminate
```

---

## 8.3 Claims

An Attestation MAY:

* embed one or more Claims;
* reference one or more independently materialized Claim Records;
* combine these mechanisms where the applicable profile permits it.

OLP SHALL NOT require one Attestation per Claim.

---

## 8.4 Issuer vs Signer

The semantic Issuer MUST remain distinct from:

* cryptographic signer;
* hardware key;
* timestamp authority;
* witness;
* storage provider;
* Holder;
* relay;
* presenter.

A mechanism MAY explicitly bind one of these actors to Issuer semantics, but such equivalence MUST NOT be assumed by default.

---

## 8.5 Validity Boundary

A valid Attestation Record does not imply that its Claims are:

* true;
* authoritative;
* independent;
* complete;
* trusted.

Cryptographic verification may establish attribution relative to a particular Identifier or mechanism without establishing real-world identity or truth.

---

# 9. Observation Record

## 9.1 Purpose

An **Observation Record** represents structured information purportedly produced through observation or measurement.

Its primary semantic question is:

> **What was purportedly observed or measured, and under what observational circumstances?**

Observation SHALL be a core first-class Record type.

---

## 9.2 Structural Specialization

Observation exists as a separate core type because interoperable observational data commonly requires structured semantics such as:

* observed Subject;
* property;
* value;
* unit;
* method;
* sampling conditions;
* uncertainty;
* observed time;
* location;
* instrument;
* calibration context;
* derivation information.

The exact schema is deferred.

---

## 9.3 No Epistemic Privilege

Observation is a structural specialization, not a privileged fact object.

An Observation MAY be:

* inaccurate;
* forged;
* miscalibrated;
* incomplete;
* manipulated;
* misinterpreted.

Machine generation MUST NOT imply objectivity.

The existence of an Observation Record does not itself establish that an actual observation or measurement took place as described.

---

## 9.4 Attribution

An Observation MAY carry or reference sufficient attribution or Provenance to identify its purported source without requiring an additional Attestation wrapper.

An Attestation MAY separately make Claims about an Observation.

---

## 9.5 Direct and Derived Observations

Observation MAY represent direct or derived observational information.

Derivation SHOULD be represented through appropriate Provenance or relationships where relevant.

A derived Observation MUST NOT be assumed to have been calculated correctly merely because its lineage is represented.

---

# 10. Event Record

## 10.1 Purpose

An **Event Record** is an independently referenceable protocol representation of a **purported occurrence**.

Its primary semantic question is:

> **Which occurrence is being represented?**

Event SHALL be a core first-class Record type.

---

## 10.2 Neutral Occurrence Anchor

The existence of an Event Record does not itself assert, without attribution, that the occurrence actually happened.

An Event Record MAY serve as a neutral common referent for other Records.

For example:

```text
E1
type: Event
content:
    delivery of shipment X
```

may then be referenced by:

```text
A1
issuer: Alice
claim:
    E1 occurred successfully
```

and:

```text
A2
issuer: Bob
claim:
    E1 did not occur as described
```

The protocol can therefore preserve disagreement around a shared Event reference.

---

## 10.3 Independent Materialization

An Event SHOULD normally be independently materialized where the occurrence itself requires:

* stable identity;
* multiple references;
* relationships to other Events;
* Observations;
* Attestations;
* lifecycle;
* reusable Evidence.

A simple event-like proposition that requires no independent identity MAY remain embedded inside a Claim.

---

# 11. Interaction

An **Interaction** is a specialization of Event.

Interaction represents a purported occurrence involving two or more entities in a shared:

* activity;
* exchange;
* process;
* relationship.

Interaction SHALL NOT form a separate parallel core object family.

Interaction-specific semantics MAY be expressed through:

* an Event subtype;
* profile;
* schema;
* specialized content.

The participating entities MAY, but need not, be OLP Participants.

---

# 12. Outcome

**Outcome** remains a reusable semantic structure rather than a mandatory core Record type.

An Outcome represents an asserted result, consequence, or resulting state associated with an Event or Interaction.

Outcomes SHOULD normally be represented through:

* Claims;
* Attestations;
* Event content where appropriate;
* domain profiles.

Where an Outcome requires independent identity, OLP core SHOULD normally represent it through an independently materialized Claim concerning the relevant Event or Interaction.

For example:

```text
C2
type: Claim
content:
    subject: ref(E1)
    outcome: fulfilled
```

OLP core SHALL NOT require a generic standalone Outcome Record type.

Domain extensions MAY define specialized Outcome-oriented Record types where interoperability requirements justify doing so.

OLP MUST NOT imply that one canonical Outcome exists for every Event or Interaction.

---

# 13. StatusChange Record

## 13.1 Purpose

A **StatusChange Record** represents an attributable assertion intended to change the reliance status or preferred interpretation of one or more existing Records.

Its primary semantic question is:

> **How is existing protocol information asserted to have changed in status or preferred interpretation?**

StatusChange SHALL be a core first-class Record type.

---

## 13.2 Required Attribution

A StatusChange SHALL identify the Participant or Identifier to whom the status assertion is attributed.

Declared attribution and verified authority remain separate.

---

## 13.3 Target

A StatusChange SHALL reference the Record or Records to which the asserted status change applies.

A StatusChange MAY itself become the target of another StatusChange.

---

## 13.4 Core Operations

The initial core status semantics SHALL include at least:

```text
Revocation
Supersession
```

These are semantic operations within the StatusChange model rather than separate unrelated object families.

---

## 13.5 Revocation

Revocation indicates an attributable intention to withdraw, terminate, or limit reliance on previously issued protocol information under specified conditions.

Revocation MAY include:

* target;
* effective time;
* scope;
* reason;
* applicable conditions.

A Revocation does not erase the historical existence of the target Record.

---

## 13.6 Supersession

Supersession indicates that newer information replaces, corrects, updates, or qualifies earlier protocol information for an applicable purpose.

Supersession SHOULD be capable of identifying successor Record or Records where applicable.

Supersession does not imply that the earlier Record never existed or was necessarily invalid when created.

---

## 13.7 Status Is Derived

The existence of a StatusChange does not by itself establish that its asserted effect is authoritative.

Current status SHOULD be derived from relevant information including:

```text
target Record
+
StatusChange Records
+
attribution and Provenance
+
authorization or authority rules
+
effective time
+
Context
```

Different evaluators MAY derive different status conclusions.

OLP SHALL NOT require one universally authoritative mutable `status` field on the original Record.

---

## 13.8 Conflicting Status Information

Conflicting StatusChange Records MAY coexist.

For example:

```text
S1: revoke R1
S2: S1 was unauthorized
S3: supersede S1
```

The protocol represents the relevant information.

The evaluator determines applicable status according to its rules and Context.

---

# 14. Core Type Responsibility Rule

Record type selection SHOULD be based on the Record's **primary semantic responsibility**, not on every role that its information may later play.

Use:

* **Claim** when an unattributed proposition requires independent identity;
* **Attestation** when attributable assertion is primary;
* **Observation** when structured purported observation or measurement is primary;
* **Event** when an independently referenceable purported occurrence is primary;
* **StatusChange** when standardized status interpretation of existing Records is primary.

Semantic overlap MAY exist.

Overlap alone MUST NOT make a representation invalid.

Profiles SHOULD guide domains toward consistent representations where multiple semantically reasonable choices would otherwise harm interoperability.

---

# 15. No Generic Evidence Record

OLP core SHALL NOT define a universal `Evidence` Record type.

Evidence is a semantic role that information plays during evaluation.

Any of the following may function as Evidence:

* Claim;
* Attestation;
* Observation;
* Event;
* StatusChange;
* external document;
* external resource;
* Trust conclusion represented through another Record.

Whether information functions as Evidence depends on the evaluation Context.

---

# 16. No Core History, Trust, Reputation, or TrustScore Record

OLP core SHALL NOT define universal Record types for:

* History;
* Trust;
* Reputation;
* TrustScore.

A History is a derived collection or view over Records.

Trust is a contextual conclusion.

Reputation is an interpretation or aggregation.

A Trust conclusion MAY itself be represented through an Attestation or suitable extension type, but OLP MUST NOT elevate such a conclusion into canonical protocol truth.

---

# 17. Relationships

## 17.1 Generic Relationships

The universal Record envelope SHALL support generic typed relationships to:

* other Records;
* external resources.

Conceptually:

```text
relationships:
    - relation: <relationship identifier>
      target: <Reference>
```

The exact syntax and initial relationship vocabulary are deferred.

---

## 17.2 Type-Specific Relationships

Relationships necessary to define the intrinsic semantics of a Record type SHOULD remain within that type's content.

Examples include:

* Attestation Issuer;
* Observation Subject;
* StatusChange target.

The universal Record envelope SHOULD NOT grow to understand every semantic relationship used by every Record type.

---

## 17.3 Relationship Assertions

A relationship represented within a Record is itself protocol information.

Its presence does not automatically establish that the relationship is objectively true.

For example:

```text
certified_by → Authority X
```

does not prove actual certification merely because the relationship is encoded.

The relationship's reliability depends on attribution, Provenance, Verification, and Context.

---

## 17.4 Critical Relationships

Any extensible relationship whose semantics are necessary for safe interpretation MUST be capable of being declared critical or otherwise required by the applicable type/profile rules.

An implementation MUST NOT silently ignore an unknown relationship if understanding that relationship is required for safe interpretation.

---

## 17.5 Graph Structure

Generic Record relationships MAY form cycles.

OLP SHALL NOT assume that the global Record graph is:

* a tree;
* a DAG;
* centrally ordered.

Implementations MUST handle graph traversal without assuming global acyclicity.

Individual relationship definitions MAY impose stricter graph constraints.

---

# 18. Provenance

Provenance SHALL emerge from:

* attributable Record information;
* derivation relationships;
* source relationships;
* type-specific attribution;
* proofs;
* other explicit protocol relationships.

OLP SHALL NOT require a single monolithic provenance field.

For example:

```text
O1  raw Observation
O2  derived_from O1
A1  references O2
```

may provide part of a provenance chain.

A declared derivation relationship does not by itself prove that the transformation was performed correctly.

---

## 18.1 Transport Is Not Provenance

Copying, transmitting, caching, routing, or relaying a Record MUST NOT implicitly change its semantic origin or Issuer.

For example:

```text
Alice → Relay A → Relay B → Bob
```

does not make Relay A or Relay B the Issuer of Alice's Attestation.

Transport history and semantic Provenance are distinct.

A transport actor becomes semantically relevant only where it:

* performs a transformation;
* creates a new assertion;
* adds independently meaningful protocol information.

---

## 18.2 Provenance and Privacy

OLP SHOULD permit:

* partial provenance;
* selectively disclosed provenance;
* privacy-preserving provenance proofs;

where supported by applicable mechanisms.

Independent verifiability SHOULD NOT require universal disclosure of every actor in a provenance chain.

---

# 19. Reference

## 19.1 Purpose

A **Reference** is a reusable semantic structure used to locate, address, or bind to another Record or external resource.

References SHALL remain conceptually distinct from Identifiers.

---

## 19.2 Locator vs Target Identity

A Reference MAY act as a **locator**, identifying where information may be retrieved.

For example:

```text
https://example.com/report
```

A locator alone MUST NOT automatically be interpreted as an immutable identity for the retrieved content.

Mutable resources may change while retaining the same locator.

---

## 19.3 Immutable Binding

Where semantics depend upon the exact contents of an external resource, OLP SHOULD permit an immutable identity or cryptographic commitment to accompany the locator.

Conceptually:

```text
Reference
├── locator
└── target_identity
```

The exact mechanism is deferred.

A retrieval locator and immutable target binding are distinct concepts.

---

## 19.4 Availability

A Reference does not imply:

* current availability;
* public availability;
* perpetual storage;
* universal dereferenceability.

A Record referencing unavailable information MAY remain structurally valid.

The inability to obtain required referenced information MAY instead result in an **indeterminate** evaluation.

---

# 20. Record Composition

OLP SHALL support both:

* embedded semantic structures;
* References to independent Records.

The governing rule is:

> Information that is small and semantically local MAY be embedded.
> Information requiring independent identity or lifecycle SHOULD normally be a Record and be referenced.

---

## 20.1 Embedded Structures

Reusable structures such as:

* Claim;
* Outcome;
* EntityReference;
* Party;
* Proof;

MAY be embedded where their meaning exists primarily within the containing Record.

Embedding such a structure MUST NOT implicitly create an independent nested Record.

---

## 20.2 Independently Identified Records

Information requiring independent:

* identity;
* provenance;
* Verification;
* reuse;
* status;
* lifecycle;

SHOULD be represented as a separate Record and referenced.

---

## 20.3 Nested Complete Records

A Record SHOULD NOT normally embed another complete independently identified Record inside its immutable semantic content where a Reference can express the relationship.

Composition by Reference is preferred.

---

## 20.4 Bundling

Transport bundling is conceptually separate from semantic Record composition.

A future Bundle may carry:

```text
Bundle
├── Record A
├── Record B
└── Record C
```

without making B or C semantically nested inside A.

The addition or removal of Records from a transport Bundle MUST NOT change the identities of the contained Records.

Bundle syntax belongs to a later specification.

---

## 20.5 Recursive Structures

Core schemas SHOULD avoid unnecessary recursive embedding.

Implementations MUST NOT assume that externally referenced Record graphs are acyclic.

Resource limits and denial-of-service protections belong primarily to implementation/security specifications.

---

# 21. EntityReference and Subjects

OLP SHALL define a reusable semantic representation for referring to Subjects and other entities involved in Records.

For purposes of this document, this structure is referred to conceptually as **EntityReference**.

The final serialized name is not fixed.

An EntityReference MAY use:

* one Identifier;
* multiple Identifiers;
* a Record Reference;
* an appropriate combination thereof.

---

## 21.1 No Mandatory Participant Record

A Subject or Participant MUST NOT be required to possess a dedicated Participant Record merely in order to be referenced.

OLP core SHALL NOT require a first-class `ParticipantRecord`.

This avoids turning OLP into an identity registry.

---

## 21.2 No Universal Identifier Requirement

A Subject MUST NOT be required to possess one globally unique OLP Identifier.

Entity representation SHOULD support:

* local identifiers;
* pseudonymous identifiers;
* external identification systems;
* privacy-preserving mechanisms.

---

## 21.3 Multiple Identifiers

Multiple Identifiers MAY be associated with one represented entity.

Doing so constitutes an assertion that those Identifiers refer to the same entity.

Such co-location does not independently prove the identity relationship.

---

## 21.4 Identity Is Not Proven by Reference

An EntityReference expresses the intended referent of protocol information.

It MUST NOT by itself be interpreted as proof of:

* real-world identity;
* ownership;
* control;
* authority;
* legal status;
* Trust.

---

# 22. Party

A **Party** is a reusable semantic structure associating an EntityReference with a role in an Event or Interaction.

Conceptually:

```text
Party
├── entity
└── role
```

Role identifiers SHOULD be extensible and unambiguous.

OLP core SHOULD NOT hardcode every possible domain-specific party role.

For example:

```text
buyer
seller
carrier
service_provider
client
witness
```

may be defined by profiles or domain vocabularies.

Party-role assertions MUST NOT automatically imply external legal authority, ownership, or authorization.

---

# 23. Time Semantics

OLP SHALL distinguish different semantic roles of time.

The protocol MUST NOT collapse all temporal information into one universal timestamp.

Relevant time concepts MAY include:

* Record creation time;
* issuance time;
* assertion time;
* Event occurrence time;
* Observation time;
* StatusChange effective time;
* validity start;
* validity end;
* expiry;
* independently established temporal proofs.

---

## 23.1 Claimed Time

A time value contained within a Record is an assertion unless a Verification mechanism establishes stronger temporal guarantees.

For example:

```text
created_at: T
```

does not automatically prove that the Record objectively came into existence at exactly T.

---

## 23.2 Record Time vs Event Time

Record creation time MUST NOT be assumed to equal Event occurrence time.

A Record created today MAY represent an Event purported to have occurred:

* yesterday;
* years ago;
* in the future.

---

## 23.3 Observation Time

Observation time is distinct from:

* Record creation time;
* transport time;
* receipt time;
* storage time.

Receipt and storage times SHOULD normally remain implementation-local unless intentionally represented as attributable protocol information.

---

## 23.4 Effective Time

StatusChange MAY specify effective time distinct from Record creation time.

A claimed retroactive or future effective time is representable without the protocol automatically establishing that the actor has authority to impose that effect.

---

## 23.5 Validity Intervals

Applicable Record types MAY represent:

* `valid_from`;
* `valid_until`;
* expiry;
* other temporal constraints.

These constraints express intended semantics but do not themselves establish universal authority.

---

## 23.6 Verified Time Properties

A temporal Verification mechanism MUST state the specific property it establishes.

For example:

* existed before T;
* existed after T;
* was witnessed at T;
* was included in structure S before T.

OLP MUST NOT reduce all such guarantees to an undefined generic concept of “verified timestamp.”

---

## 23.7 Approximation and Uncertainty

OLP SHOULD permit representation of:

* intervals;
* approximate time;
* uncertainty;
* partial temporal knowledge.

The protocol SHOULD NOT force false precision.

---

## 23.8 Ordering

Protocol ordering and wall-clock time SHALL remain distinct concepts.

Relationships MAY establish partial ordering even where exact wall-clock timestamps are unavailable or unreliable.

---

# 24. Record Types and Versioning

## 24.1 Envelope Version

The core Record envelope SHALL be versioned independently.

Envelope evolution SHOULD occur only where generic Record mechanics require incompatible change.

---

## 24.2 Record Type

Every Record SHALL declare an unambiguous semantic Record type.

Core types defined by this specification are:

```text
Claim
Attestation
Observation
Event
StatusChange
```

---

## 24.3 Type Version

Every Record SHALL unambiguously identify the version of its type semantics.

Type evolution SHALL remain independent from envelope evolution.

Changing an Observation schema, for example, SHOULD NOT require a new Record-envelope version unless generic Record mechanics also change.

---

## 24.4 Stable Historical Semantics

Existing type-version semantics MUST NOT be silently redefined.

The same requirement applies to versioned:

* profiles;
* extensions;
* relationships;
* other semantic declarations.

Incompatible semantic change requires a new version or identifier.

Historical interpretation MUST NOT depend on mutable external content currently published under an otherwise stable identifier.

---

## 24.5 Unsupported Types and Versions

An implementation encountering a structurally valid but unsupported:

* Record type;
* type version;
* profile;
* critical extension;
* critical relationship;

SHOULD classify the relevant semantics as **unsupported**, not automatically **invalid**.

---

## 24.6 Unknown Envelope Versions

A detectable but unsupported envelope version SHOULD likewise be classified as **unsupported**.

A malformed Record claiming to use a supported envelope version may instead be structurally invalid.

---

# 25. Decentralized Type Identification

Type, profile, extension, and relationship identifiers MUST be unambiguous within the applicable protocol context.

The identifier model SHOULD permit decentralized definition.

OLP SHOULD NOT require one central authority to approve every future:

* Record type;
* profile;
* extension;
* relationship vocabulary.

Core OLP types MAY use an OLP-defined namespace.

The exact identifier syntax is deferred.

---

# 26. Profiles

A **Profile** refines a core Record type with domain-specific semantics or constraints.

For example:

```text
Event
    profile: ShipmentDelivery
```

may preserve generic Event semantics while adding logistics-specific meaning.

Profiles allow an implementation to understand:

> “This is an Event”

even when it does not understand:

> “This is a specialized maritime refrigerated-shipping Event profile.”

Profiles SHOULD be preferred over uncontrolled creation of new core types where the underlying semantic responsibility remains unchanged.

---

## 26.1 Critical Profiles

A profile whose semantics must be understood for safe interpretation MUST be capable of being declared required or critical.

An implementation that does not understand such a profile MUST NOT claim full semantic understanding of the Record.

---

# 27. Extensions and Critical Semantics

OLP SHALL distinguish between **critical** and **non-critical** extensible semantics.

---

## 27.1 Non-Critical Extensions

A non-critical extension adds information that may be ignored without changing the safe interpretation of the Record's core semantics.

An unknown non-critical extension MAY be ignored for semantic interpretation where safe.

However, identity-relevant unknown extension data SHOULD be preserved when an implementation claims to preserve or relay the same immutable Record.

---

## 27.2 Critical Extensions

A critical extension changes, constrains, or adds semantics that must be understood before the Record can be safely interpreted.

An unknown critical extension MUST NOT be silently ignored.

If an implementation does not understand a required critical extension, it MUST NOT claim full semantic understanding of the affected Record.

---

## 27.3 Criticality Beyond Extensions

Criticality applies conceptually to any extensible semantic component where ignorance could change safe interpretation.

This includes, where applicable:

* profiles;
* relationships;
* extension fields;
* other declared semantic mechanisms.

---

## 27.4 No Hidden Redefinition

Critical extensions MAY refine or constrain core Record semantics.

They SHOULD NOT redefine the fundamental semantic responsibility of a core Record type.

A mechanism that fundamentally changes the meaning of an Attestation into something that is no longer an attributable assertion SHOULD use a new type, version, or appropriate profile rather than an opaque extension.

---

## 27.5 Stable Extension Semantics

The semantics associated with a versioned extension identifier MUST NOT be silently redefined.

Incompatible change requires a distinct version or identifier.

---

# 28. Unknown-Type Processing

Unknown Record types SHOULD remain generically processable to the extent permitted by the envelope.

An implementation MAY be able to:

* identify Record Identity;
* identify type;
* identify envelope version;
* preserve content;
* inspect generic relationships;
* route the Record;
* store the Record;
* verify generic integrity properties;

without understanding type-specific semantics.

The implementation MUST NOT pretend to understand semantics it does not support.

---

# 29. Proof

## 29.1 Reusable Semantic Structure

**Proof** is a reusable semantic structure.

Proof material MAY be:

* embedded inside a Record;
* externally associated;
* independently represented where its lifecycle and interoperability require it.

OLP does not yet require one universal first-class `Proof` Record type.

---

## 29.2 Intrinsic Proof

Proof material necessary to establish intrinsic attribution or other intrinsic semantics of a Record MAY belong inside the Record's immutable identity boundary.

For example, an Attestation mechanism MAY define an Issuer proof as intrinsic.

---

## 29.3 External Proof

Proofs created:

* later;
* independently;
* by third parties;

SHOULD normally be associated with the existing Record without modifying that Record.

Examples MAY include:

* later timestamp proofs;
* archive witnesses;
* countersignatures;
* inclusion proofs.

---

## 29.4 Binding

External proofs MUST bind unambiguously to the specific:

* Record;
* Record Identity;
* representation;
* property

to which they apply.

---

## 29.5 Property-Scoped Guarantees

Every proof mechanism MUST define the specific property or properties it is capable of establishing.

Examples include:

```text
integrity under mechanism X
signature validity under key K
existence before time T
inclusion in structure S
authorization under rule P
selective-disclosure consistency
```

Successful proof Verification MUST NOT automatically imply:

* truth;
* Trust;
* real-world identity;
* authority;
* correctness beyond the verified property.

---

## 29.6 Multiple Proofs

A Record MAY have multiple proofs establishing different properties.

Verification results SHOULD therefore remain property-specific.

---

# 30. Issuance

Issuance SHALL remain semantically distinct from:

* serialization;
* storage;
* transport;
* possession;
* cryptographic signing.

**Issuance** is the act by which a Participant adopts an attributable assertion as its own under an applicable mechanism.

A cryptographic signer MAY act on behalf of an Issuer without becoming semantically identical to that Issuer.

The applicable mechanism MAY define how issuance is established.

---

# 31. Validation and Verification Layers

OLP SHALL distinguish the following layers:

1. structural conformance;
2. Record Identity and integrity;
3. semantic support;
4. reference completeness;
5. proof Verification;
6. status interpretation;
7. Trust evaluation;
8. application decision.

A positive result at one layer MUST NOT automatically imply a positive result at another.

---

# 32. Structural Conformance

Structural conformance determines whether a representation satisfies applicable:

* envelope rules;
* supported schema rules;
* required type constraints.

Structural invalidity MAY include:

* malformed encoding;
* missing mandatory data;
* invalid required field structure;
* malformed supported Reference format;
* impossible representation under the applicable schema.

Structural validity says nothing about truth or Trust.

---

# 33. Record Identity and Integrity Verification

This layer determines whether the Record's identity-relevant representation satisfies its applicable cryptographic identity mechanism.

Failure MAY indicate:

* corruption;
* modification;
* incorrect canonicalization;
* incorrect Record Identity.

Successful integrity Verification does not establish the truth of Record contents.

---

# 34. Semantic Support

Semantic support determines whether an implementation understands the applicable:

* envelope version;
* type;
* type version;
* required profiles;
* critical extensions;
* critical relationships;
* other required semantics.

Possible conceptual outcomes include:

```text
supported
partially supported
unsupported
```

A structurally valid Record may remain unsupported.

---

# 35. Reference Completeness

Completeness is relative to a particular Verification or evaluation task.

A Record MAY be structurally valid while some referenced information is unavailable.

For example:

```text
Attestation A1
    evidence: ref(O1)
```

may remain structurally valid if O1 cannot currently be retrieved.

An evaluation requiring O1 may instead become **indeterminate**.

---

# 36. Proof Verification

Proof Verification SHALL remain property-specific.

OLP implementations SHOULD avoid a universal:

```text
verified = true
```

where different properties were actually evaluated independently.

Conceptually:

```text
record_identity       = satisfied
issuer_signature      = satisfied
timestamp_property    = indeterminate
hardware_origin       = unsupported
```

is preferable to one undifferentiated Boolean.

---

# 37. Status Interpretation

Status SHALL be derived from applicable protocol information rather than assumed to be an intrinsic mutable property of the target Record.

Evaluation MAY consider:

* StatusChange Records;
* attribution;
* authority;
* effective time;
* conflicting Evidence;
* applicable rules;
* Context.

Different evaluators MAY derive different status conclusions.

---

# 38. Trust Evaluation

Trust evaluation is outside generic Record validity.

A Record may be:

* structurally valid;
* integrity-verified;
* semantically supported;
* correctly attributed;

and still not be trusted for a particular purpose.

Trust remains contextual.

---

# 39. Application Decision

Application decisions remain outside generic protocol validity.

A system MAY reject an action even where:

* the Record is structurally valid;
* required proofs succeed;
* applicable Trust conclusions are positive.

Other constraints may include:

* policy;
* law;
* contractual rules;
* risk thresholds;
* operational considerations.

Trust is not authorization.

---

# 40. Common Evaluation Outcomes

Where appropriate, OLP implementations SHOULD distinguish at least:

* **satisfied / valid** — the evaluated rule succeeded;
* **failed / invalid** — the rule was evaluated and failed;
* **unsupported** — the implementation does not understand the required mechanism or semantics;
* **indeterminate** — the implementation understands the rule but lacks sufficient information to establish the result;
* **not applicable** — the rule does not apply.

---

## 40.1 Unsupported vs Indeterminate

These concepts MUST remain distinct.

Example:

> “I do not support this signature algorithm.”

is **unsupported**.

> “I support the signature algorithm, but the required verification key is unavailable.”

is **indeterminate**.

---

## 40.2 Unsupported vs Invalid

A future Record using an unknown but potentially legitimate type or envelope version is not automatically invalid.

Unsupported semantics MUST NOT be silently converted into invalidity.

---

## 40.3 Evaluation Independence

Failure or unsupported status at one layer SHOULD NOT erase independently obtainable results at another layer.

An implementation MAY report:

```text
structure               valid
Record Identity         verified
critical semantics      unsupported
signature               verified cryptographically
semantic interpretation unsupported
```

without contradiction.

---

# 41. Time-Dependent Verification and Key Compromise

Record Verification MUST remain capable of distinguishing:

```text
signature validates under key K
```

from:

```text
the legitimate Participant controlled key K at time T
```

These are different properties.

If a key is later compromised, revoked, or disputed, historical Record interpretation MAY depend on:

* key status Evidence;
* issuance time;
* compromise time;
* Context;
* applicable authority rules.

Later changes in key or proof acceptability MUST NOT silently rewrite the historical Record.

---

# 42. Selective Disclosure

Selective disclosure is outside the core Record object model but SHALL respect Record Identity semantics.

A partial representation of a Record MUST NOT silently present itself as the complete original Record unless an applicable proof mechanism explicitly preserves a verifiable relationship to that original Record.

Selective disclosure MAY later be expressed through:

* presentation structures;
* derived representations;
* proofs;
* new Records linked to existing Records.

---

# 43. Encryption and Confidentiality

Encryption is not defined as a core semantic Record type in this milestone.

An encrypted representation may function as:

* transport protection;
* storage protection;
* disclosure packaging;
* presentation protection.

An encrypted or transformed representation MUST NOT silently claim the identity of the original Record unless the applicable mechanism preserves the required cryptographic binding.

Concrete confidentiality mechanisms are deferred.

---

# 44. Offline Operation

The object model SHOULD support meaningful offline processing.

An implementation in possession of a Record and relevant local Verification material MAY evaluate whatever properties can be established locally.

Unavailable external material MAY result in:

```text
indeterminate
```

without making the Record structurally invalid.

Core interpretation SHOULD NOT require constant access to:

* central registries;
* schema websites;
* online ledgers;
* global status servers.

Specific profiles or applications MAY require online dependencies, but OLP core should not.

---

# 45. External Schemas and Definitions

Core Record interpretation MUST NOT depend on successfully retrieving a mutable external schema URL merely to determine the fundamental meaning of a core type and version.

External schema or definition locations MAY assist discovery.

However, historical semantic interpretation requires stable versioned semantics.

If external definitions disappear, an implementation that already possesses the relevant definitions should remain capable of interpreting historical Records.

If the semantics are unavailable to an implementation, the Record SHOULD be treated as unsupported rather than automatically invalid.

---

# 46. Resource Limits

The protocol object model permits Records and Record graphs of varying complexity.

Implementations SHOULD enforce appropriate limits against:

* excessive Record size;
* excessive relationship count;
* pathological nesting;
* graph traversal attacks;
* decompression attacks;
* computationally expensive proof verification;
* memory exhaustion.

Exceeding an implementation resource limit MUST NOT necessarily be interpreted as proof that the Record is semantically invalid.

Operational resource-limit failures belong primarily to implementation and security specifications.

---

# 47. Domain Specialization

Core Record types define protocol-level semantic responsibilities.

Domain specialization SHOULD occur through:

* profiles;
* schemas;
* extensions;
* additional type vocabularies where genuinely necessary.

OLP core SHOULD avoid uncontrolled proliferation of domain-specific types such as:

```text
PaymentEvent
ShippingEvent
MedicalEvent
EmploymentEvent
CourtEvent
```

where those semantics can instead refine the generic Event model.

A new Record type is justified where the semantic responsibility is genuinely different, not merely because the application domain is different.

---

# 48. Transport and Presentation Boundary

The semantic object model SHALL remain separate from transport and presentation concerns.

The following SHOULD NOT automatically become semantic Records merely because they carry Records:

* Bundle;
* network packet;
* API response;
* encrypted envelope;
* presentation;
* storage container.

A Record maintains its identity independently of how it is transported or packaged.

---

# 49. Conceptual Processing Model

A generic OLP implementation may process a Record conceptually as follows:

```text
receive representation
        │
        ▼
identify envelope version
        │
        ├── unsupported
        │       → unsupported envelope
        │
        ▼
parse supported envelope
        │
        ├── malformed
        │       → structurally invalid
        │
        ▼
verify Record Identity / integrity
        │
        ├── failure
        │       → integrity failure
        │
        ▼
identify type + type version
        │
        ├── unsupported
        │       → preserve generically where possible
        │
        ▼
check required profiles / critical semantics
        │
        ├── unsupported
        │       → semantic interpretation unsupported
        │
        ▼
resolve information required for requested evaluation
        │
        ├── unavailable
        │       → indeterminate where appropriate
        │
        ▼
verify requested proof properties
        │
        ▼
derive applicable status
        │
        ▼
evaluate Evidence under Context / Trust Model
        │
        ▼
application policy decision
```

These stages MUST NOT be collapsed into one universal validity result.

---

# 50. Initial Core Architecture Summary

The initial OLP object model can be summarized as:

```text
                        ┌──────────────┐
                        │    Record    │
                        └──────┬───────┘
                               │
           ┌───────────────────┼─────────────────────┐
           │                   │                     │
           ▼                   ▼                     ▼
        Claim             Attestation           Observation
           │
           │
           └───────────────┐
                           │
                           ▼
                         Event
                           │
                           └── Interaction

                        StatusChange
                         ├── Revocation
                         └── Supersession
```

A more precise non-hierarchical view is:

```text
Core Records
------------
Claim
Attestation
Observation
Event
StatusChange

Semantic specializations
------------------------
Interaction → Event
Revocation → StatusChange
Supersession → StatusChange

Reusable structures
-------------------
Outcome
EntityReference
Party
Reference
Proof

Generic Record machinery
------------------------
Relationships
Profiles
Extensions
Criticality declarations

Derived / contextual concepts
-----------------------------
Evidence
History
Provenance
Context
Trust
TrustModel
Verification
Status
ApplicationDecision

Transport / presentation concepts
---------------------------------
Bundle
Presentation
Selective disclosure
Encryption wrapper
Transport metadata
Local metadata
```

---

# 51. Foundational Object Invariants

The object model defined by this document establishes the following invariants:

> **Record is the universal carrier, not a universal truth object.**

> **A Record's existence does not establish the truth of its content.**

> **Record Identity is stable and cryptographically bound to identity-relevant information.**

> **Identity-relevant mutation creates a new Record.**

> **Local metadata does not alter Record Identity.**

> **Copies of the same Record remain the same protocol Record.**

> **Record Identity can be verified without understanding application-specific Record semantics.**

> **Claim represents a proposition; Attestation represents someone attributably asserting a proposition.**

> **Materializing a Claim does not create an implicit Issuer.**

> **Observation represents purported observation or measurement, not objective fact.**

> **Event represents a purported occurrence, not an unattributed assertion that the occurrence happened.**

> **Interaction specializes Event.**

> **Outcome is not assumed to be singular or canonical.**

> **StatusChange represents a status assertion; it does not create universal mutable state.**

> **Revocation and Supersession do not erase historical existence.**

> **Current status is derived.**

> **References may locate information without immutably identifying its contents.**

> **Mutable locators and immutable target bindings are distinct.**

> **Provenance is represented through explicit attributable information and relationships, not a single opaque value.**

> **Transport does not alter semantic provenance.**

> **Generic Record graphs may contain cycles.**

> **Unknown critical semantics cannot be silently ignored.**

> **Unsupported is not invalid.**

> **Indeterminate is not failure.**

> **Stable Record interpretation requires stable versioned semantics.**

> **Proofs establish specific properties, not generic truth or Trust.**

> **Issuance is not the same thing as cryptographic signing.**

> **Structural validity, integrity, semantic understanding, Verification, Trust, and application decisions are distinct layers.**

> **A Record may be valid and verified while still being untrusted or unusable for a particular purpose.**

> **Evidence is a role information plays, not a core Record type.**

> **History is a derived view, not a mandatory globally canonical object.**

> **Trust is a contextual conclusion, not a protocol primitive.**

> **OLP's core object layer remains independent of any blockchain, ledger, storage system, identity provider, jurisdiction, or Trust Model.**

---

# 52. Design Consequence

The Milestone 2 architecture intentionally creates a small semantic core.

OLP does not attempt to standardize every possible fact, transaction, business object, risk score, reputation calculation, or application decision.

Instead, it standardizes the minimum interoperable machinery required to make independently meaningful trust-relevant information:

* identifiable;
* immutable;
* attributable where applicable;
* referenceable;
* composable;
* extensible;
* versionable;
* verifiable;
* portable across systems.

This allows different applications and Trust Models to operate over a shared Evidence layer without requiring a shared universal interpretation.

---

# 53. Deferred Questions

The following questions are intentionally deferred to later milestones:

* concrete serialization;
* canonicalization;
* Record Identity algorithm;
* hash agility;
* signature suites;
* proof suite representation;
* proof attachment syntax;
* key representation;
* Identifier resolution;
* schema representation;
* profile packaging;
* extension identifier syntax;
* relationship identifier syntax;
* Bundle format;
* presentation format;
* selective-disclosure mechanisms;
* encryption;
* key rotation;
* key compromise signaling;
* delegation;
* authorization;
* storage APIs;
* retrieval protocols;
* replication;
* synchronization;
* discovery;
* indexing;
* status discovery;
* consensus mechanisms;
* blockchain anchoring;
* external registry integration.

Deferral of these concerns is deliberate.

Milestone 2 defines the **object architecture**, not its complete implementation.

---

# 54. Milestone 2 Status

This document represents the conceptual protocol-object baseline established during:

**Milestone 2 — Protocol Objects**

The resulting initial OLP core consists of:

```text
Record

Core Record types:
    Claim
    Attestation
    Observation
    Event
    StatusChange
```

with:

```text
Interaction
    as an Event specialization

Revocation
Supersession
    as StatusChange operations

Outcome
EntityReference
Party
Reference
Proof
    as reusable semantic structures
```

The next milestone SHOULD build upon this architecture without reopening these object boundaries unless implementation analysis exposes a concrete contradiction.

The object model is now sufficiently defined to begin specifying the representation and integrity rules required to make these Records interoperable between independent implementations.