# Open Layer Protocol

An open protocol for portable, verifiable trust between humans, organizations, software agents, services, and other independent participants.

Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

---

## What Open Layer Protocol is

Open Layer Protocol (OLP) is an open protocol for portable, verifiable trust between independent participants.

It defines a common way for humans, organizations, software agents, services, and other actors to exchange portable, independently verifiable records representing claims, attestations, observations, events, interactions, and status changes without requiring trust to be owned or controlled by a single platform.

OLP is designed to make economic and digital history portable across applications, marketplaces, networks, and jurisdictions.

The protocol focuses on evidence, verifiable record identity, provenance, and explicit semantic relationships rather than centralized reputation scores.

Applications remain free to interpret the same evidence differently depending on context, risk, policy, jurisdiction, purpose, and the Trust Model evaluating it.

OLP aims to provide a neutral trust layer that can be used alongside existing commerce, identity, payment, agent, communication, storage, and application protocols.

Its core goals are:

- portable and independently verifiable evidence;
- participant-owned and participant-held history without requiring a single canonical ledger;
- contextual rather than universal trust;
- cryptographically verifiable identity and integrity for protocol records;
- explicit provenance and lifecycle information;
- privacy through data minimization and future selective-disclosure mechanisms;
- interoperability with existing open standards;
- neutrality toward blockchains, marketplaces, payment systems, storage systems, and jurisdictions;
- equal treatment of humans, organizations, software services, autonomous agents, and other actors at the protocol layer;
- permissionless semantic extensibility without requiring one organization to control the meaning of all protocol data.

Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.

---

## What Open Layer Protocol is not

Open Layer Protocol is not a marketplace.

It does not provide product discovery, ordering, delivery, payments, employment, or general commerce infrastructure.

Existing systems and protocols can perform those functions while using OLP as a trust layer.

Open Layer Protocol is not a reputation platform.

It does not define a universal reputation score and does not decide whether a participant is globally "trusted" or "untrusted."

Trust depends on context, evidence, risk, policy, purpose, and the Trust Model evaluating it.

Different applications and Trust Models may legitimately reach different conclusions from the same underlying evidence.

Open Layer Protocol is not an identity provider.

It may reference identifiers, records, credentials, or identity-related information from other systems, but identity, attribution, authority, and trust are intentionally separate concepts.

An identifier does not by itself prove identity.

A signature does not by itself prove that a particular real-world entity made an assertion.

Open Layer Protocol is not a blockchain or cryptocurrency protocol.

Implementations may use distributed ledgers, transparency logs, databases, content-addressed storage, local storage, or other mechanisms.

No blockchain, token, or cryptocurrency is required by the protocol.

Open Layer Protocol is not a payment system, bank, escrow provider, insurer, tax authority, or legal authority.

It can represent or reference verifiable information produced by such systems without replacing them.

Open Layer Protocol is not a global authority for deciding what is legal, moral, acceptable, valid, authoritative, or trustworthy.

Jurisdictions, operators, organizations, applications, and users may apply their own policies.

Where restrictions, status changes, or authoritative decisions are represented through OLP, they should themselves be represented as explicit protocol information with attributable provenance.

Open Layer Protocol is not a mechanism for silently rewriting history.

Corrections, revocations, supersessions, disputes, and other lifecycle changes should be represented through new, explicit, traceable records rather than hidden mutation of existing records.

A record's historical existence, historical validity, and current reliance status are separate concepts.

Most importantly, OLP is not intended to create a new central intermediary.

Its purpose is the opposite:

to enable independent systems to exchange and evaluate verifiable evidence without requiring any single organization to own the underlying trust relationship.

---

## Core architecture

OLP represents protocol information as immutable **Records**.

A Record has a deterministic cryptographic identity derived from its canonical logical representation.

Its identity does not depend on:

- where the Record is stored;
- which service delivered it;
- which database contains it;
- how an application evaluates it;
- whether the Record's contents are ultimately considered trustworthy.

A Record's cryptographic identity establishes what exact immutable Record is being referenced.

It does not establish that the Record is true, authoritative, trustworthy, or currently valid for a particular purpose.

The initial core Record types are:

- **Claim** — an independently materialized proposition;
- **Attestation** — one declared Issuer asserting one or more propositions;
- **Observation** — propositions purportedly produced through observation, sensing, measurement, examination, or detection;
- **Event** — a purported occurrence;
- **Interaction** — a multi-entity Event;
- **StatusChange** — an immutable representation of revocation, supersession, or another lifecycle change.

OLP deliberately separates concepts that are often conflated:

```text
identity != trust

record integrity != truth

issuer != signer

declared attribution != verified attribution

observer != issuer

participation != consent

identifier != proof of identity

reference != endorsement

timestamp syntax != trusted time

status change != mutable global state

revocation != erasure

supersession != revocation

cryptographic verification != application acceptance
```

Applications remain responsible for evaluating evidence according to their own context, policies, risk models, jurisdictional requirements, and Trust Models.

---

## Record identity

OLP v1 defines a serialization-independent logical data model and one normative canonical identity encoding.

A logical Record is deterministically encoded using:

```text
OLP-CIE-1
```

and identified using the domain-separated content identity suite:

```text
OLP-CI-1
```

The result is a stable `RecordIdentity`.

Two independent implementations that possess the same logical Record should therefore be able to determine that they possess the same Record without requiring:

- a central registry;
- a blockchain;
- a mutable web service;
- a shared database;
- interpretation of the Record's domain-specific semantics.

Record identity is intentionally separate from transport encoding.

A future transport may represent the same logical Record differently while preserving exactly the same RecordIdentity.

---

## Semantic extensibility

OLP is designed to support permissionless semantic extension.

Core and non-core semantics use versioned `SemanticIdentifier` values.

For example:

```text
olp/core/type/claim/v1
```

or:

```text
olp/dns/example.com/predicate/shipment_delivered/v1
```

Non-core semantics can be cryptographically bound to immutable Semantic Definition Manifests.

This allows historical Records to preserve the exact semantic definitions they depended on even if:

- a website changes;
- a repository disappears;
- a domain changes ownership;
- a discovery service becomes unavailable;
- newer semantic versions are later published.

Semantic naming, immutable semantic definition, discovery, namespace authority, and Trust are intentionally separate concerns.

This means OLP does not require one global ontology owner or one central semantic registry.

---

## History and lifecycle

OLP does not assume one complete, globally canonical History.

Different participants may possess different subsets of Records.

The absence of a Record from one participant's available History is not proof that the Record never existed.

Records are immutable once finalized.

Corrections and lifecycle changes are represented through new Records rather than mutation of historical Records.

For example:

```text
original Record
      ↓
later StatusChange
      ↓
revocation or supersession
```

The original Record remains part of History.

OLP therefore distinguishes:

```text
historical existence
historical validity
current reliance status
```

These are not the same property.

Current status is derived from available immutable status evidence, applicable authority, effective time, semantic support, and evaluation context.

OLP does not define a global mutable:

```text
record.status
```

field.

---

## Trust remains contextual

OLP does not define a universal Trust algorithm.

Evidence can be portable and independently verifiable while Trust remains contextual.

Conceptually:

```text
Records and Evidence
        ↓
Trust Model + Context
        ↓
reliance conclusion
        ↓
application decision
```

Different Trust Models may legitimately:

- weigh Evidence differently;
- recognize different authorities;
- apply different risk thresholds;
- operate under different jurisdictions;
- disagree about the same participant or event.

That disagreement is not necessarily a protocol failure.

OLP exists to make the underlying evidence portable and independently verifiable, not to impose one universal interpretation of that evidence.

---

## Privacy

Privacy is a protocol-design concern, not an application afterthought.

OLP aims to support privacy through:

- data minimization;
- explicit rather than implicit disclosure;
- separation of identity from trust;
- avoidance of mandatory global identity records;
- avoidance of mandatory global history publication;
- future selective-disclosure mechanisms;
- future privacy-preserving presentation mechanisms.

At the same time, deterministic Record identities are inherently correlatable.

A stable RecordIdentity is not a pseudonym, encryption mechanism, or hiding commitment.

Likewise, placing multiple identifiers inside one EntityReference explicitly reveals that those identifiers are being associated with the same entity in that occurrence.

Applications should therefore disclose only the information required for their purpose.

---

## Specification status

Open Layer Protocol is currently in the specification-design phase.

The following foundational draft milestones have been completed:

### `0001-terminology.md`

Defines the core protocol vocabulary and semantic boundaries, including:

- Participant and Subject;
- Identifier and Reference;
- Claim and Attestation;
- Evidence and Observation;
- Event, Interaction, and Outcome;
- Record, History, and Provenance;
- Context, Trust, and Trust Model;
- Disclosure, Revocation, and Supersession;
- contextual protocol roles.

### `0002-protocol-objects.md`

Defines the core object architecture, including:

- the universal Record envelope;
- core first-class Record types;
- reusable semantic structures;
- Record identity and immutability principles;
- versioning and extension behavior;
- critical semantics;
- composition and references;
- time and proof boundaries;
- validation-layer separation.

### `0003-record-representation.md`

Defines the Record representation and identity model, including:

- the OLP logical primitive model;
- canonical deterministic encoding;
- exact integer and Decimal semantics;
- SemanticIdentifier syntax;
- immutable semantic-definition binding;
- ContentIdentity and RecordIdentity;
- RecordReference, Identifier, and EntityReference;
- Claim, Attestation, Observation, Event, Interaction, and StatusChange v1;
- temporal representation;
- revocation and supersession semantics;
- resource and defensive-processing rules;
- native binary interchange;
- Record Sequence framing;
- baseline processing requirements;
- normative conformance and cryptographic test vectors.

The next planned specification milestone is:

### `0004-proof-verification.md`

Expected to define:

- Proof semantics;
- proof targets;
- proof suites;
- canonical proof input construction;
- signatures and verification material;
- Signer versus Issuer;
- verified attribution;
- delegated authority;
- multiple proofs;
- proof verification outcomes;
- proof lifecycle and key compromise;
- offline verification behavior.

Proof verification will remain explicitly separate from:

- Claim truth;
- authority;
- Trust;
- application acceptance.

---

## Current specification roadmap

```text
0001  Terminology                         ✓ Draft v0.1
0002  Protocol Objects                    ✓ Draft v0.1
0003  Record Representation and Identity  ✓ Draft v0.1

0004  Proofs and Verification             next

0005  Presentation, Disclosure
      and Privacy                         planned

0006  Discovery, Retrieval
      and Synchronization                 planned

0007  Trust Model Interface
      and Evaluation Semantics            planned

0008  Conformance and
      Interoperability Profiles           planned
```

The later roadmap remains subject to change as the protocol evolves.

---

## Design principles

OLP development follows several foundational principles:

- Evidence over reputation.
- Facts and attributable information over opaque judgments.
- Participant-owned history.
- Contextual trust.
- No universal trust score.
- Algorithm plurality.
- Privacy by architecture.
- Identity != trust.
- Actor neutrality.
- No silent history rewriting.
- Blockchain neutrality.
- Jurisdiction neutrality.
- Interoperability before invention.
- Independent verifiability.
- Verification != truth.
- Roles are contextual, not identities.
- Unknown semantics != invalid representation.
- Status change != mutable global state.
- One semantic fact should have one canonical structural representation.

These principles are intended to constrain the protocol itself rather than merely describe implementation preferences.

---

## Project status

**Experimental / pre-0.1**

The foundational terminology, protocol-object model, and Record representation and identity model have reached **Draft v0.1**.

The project is not yet ready for production deployment.

Important areas remain under specification and implementation, including:

- proofs and signatures;
- verified attribution;
- delegated authority;
- privacy-preserving presentation;
- selective disclosure;
- discovery and retrieval;
- synchronization;
- Trust Model interfaces;
- broader interoperability profiles;
- reference implementations;
- independent implementation testing;
- security review.

No production interoperability, security, or stability guarantees should yet be assumed.

OLP is currently being developed openly from first principles toward an independently implementable protocol.

---

## License

License information will be maintained at the repository level.

---

Open Layer Protocol exists to make trust portable and verifiable without making trust centrally owned.