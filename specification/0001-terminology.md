# Open Layer Protocol — Terminology

**Document:** `specification/0001-terminology.md`
**Status:** Draft v0.1
**Milestone:** 1 — Vocabulary

---

## 1. Purpose

This document defines the foundational vocabulary of the Open Layer Protocol (OLP).

Its purpose is to establish precise, implementation-independent meanings for core protocol concepts before schemas, cryptographic mechanisms, transport formats, APIs, trust models, storage systems, or application behavior are specified.

The terms defined here describe **semantic concepts and roles**.

Unless explicitly stated otherwise, a term defined in this document MUST NOT be interpreted as requiring:

* a blockchain;
* a distributed ledger;
* a centralized registry;
* a particular identity system;
* a particular cryptographic suite;
* a particular transport mechanism;
* a particular storage architecture;
* a particular jurisdiction;
* a particular trust algorithm;
* a globally authoritative source of truth.

The vocabulary defined in this document does not by itself determine which concepts become first-class protocol objects.

That question belongs to subsequent protocol specifications.

---

# 2. Normative Language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY**, and related terms are used to express requirements and design constraints within this specification.

Until a formal standards-process document is adopted, these terms should be interpreted according to their ordinary standards-language meanings:

* **MUST / MUST NOT** indicate requirements necessary to preserve protocol semantics.
* **SHOULD / SHOULD NOT** indicate strong recommendations that may be departed from when justified.
* **MAY** indicates permitted behavior.

---

# 3. Fundamental Semantic Boundaries

The following distinctions are foundational to Open Layer Protocol.

## 3.1 Evidence is not Trust

**Evidence** is information that may be evaluated.

**Trust** is a contextual conclusion derived by a Participant, application, organization, algorithm, policy, or other evaluator from available Evidence.

The protocol MAY define how Evidence is represented, authenticated, exchanged, disclosed, referenced, and verified.

The protocol MUST NOT require a universal interpretation of that Evidence.

Two evaluators receiving the same Evidence MAY legitimately reach different Trust conclusions.

---

## 3.2 Verification is not Truth

**Verification** determines whether specified properties of protocol information satisfy defined validation rules.

Verification MAY establish properties such as:

* cryptographic integrity;
* validity of a signature under a particular key;
* consistency with a schema;
* existence of referenced information;
* validity of a proof;
* correspondence to an Identifier under a specified identification mechanism;
* provenance relationships;
* authorization under defined rules.

Verification establishes only the properties actually verified.

Verification alone does not establish that a Claim corresponds to objective reality.

A cryptographically valid false statement remains cryptographically valid.

---

## 3.3 Identity is not Trust

Establishing an Identifier, identity relationship, or provenance relationship does not determine whether the associated Participant should be trusted.

Identity-related Evidence MAY be evaluated by a Trust Model.

Identity MUST NOT be treated by the protocol as equivalent to Trust.

---

## 3.4 History is not Reputation

A History consists of available Records associated with a Subject, Participant, Identifier, or Context over time.

**Reputation**, where calculated, is an interpretation, summary, aggregation, or judgment derived from some subset of that History or other Evidence.

The protocol MUST NOT define a Participant's History as a universal Reputation.

---

## 3.5 Protocol Facts Precede Interpretations

Open Layer Protocol distinguishes between:

1. information that can be represented, attributed, related, or independently verified; and
2. conclusions derived from that information.

Protocol-level representations SHOULD describe Claims, Evidence, provenance, relationships, events, and attributable assertions before describing judgments derived from them.

---

## 3.6 Identification is not Protocol Addressing

Identification and protocol addressing are distinct concepts.

An **Identifier** distinguishes or refers to an entity within an identification system.

A **Reference** locates, addresses, or relates to protocol information or an external resource.

A value MAY serve both purposes in a particular implementation, but the semantic concepts remain distinct.

---

## 3.7 Historical Existence is not Current Validity

The fact that protocol information existed at a particular time is distinct from whether that information:

* was valid at that time;
* is valid now;
* has been revoked;
* has been superseded;
* remains available;
* should currently be relied upon.

OLP MUST preserve these distinctions at the semantic level.

---

## 3.8 Trust is not Authorization

A Trust conclusion is not equivalent to an authorization, permission, legal determination, transaction approval, or policy decision.

A system MAY consider Trust as one input into a broader decision process.

For example:

`Evidence + Context + Trust Model → Trust conclusion`

and separately:

`Trust conclusion + Policy + Context → Decision`

Open Layer Protocol does not require that Trust alone determine whether an action is permitted.

---

# 4. General Vocabulary Rule

Unless explicitly stated otherwise, terms defined in this specification describe **semantic roles or concepts** and MUST NOT be assumed to represent mutually exclusive protocol object types.

A single piece of protocol information MAY satisfy several semantic definitions simultaneously.

For example, information produced by a sensor MAY simultaneously be:

* an Observation;
* represented through a Claim;
* contained in an Attestation;
* used as Evidence;
* stored within a Record.

The mapping between semantic concepts and first-class protocol objects is intentionally deferred to later specifications.

---

# 5. Core Terms

## 5.1 Participant

A **Participant** is an entity that performs, has performed, or is represented as performing one or more active roles within Open Layer Protocol.

A Participant MAY:

* create protocol information;
* receive protocol information;
* hold protocol information;
* present protocol information;
* disclose protocol information;
* verify protocol information;
* store protocol information;
* relay protocol information;
* evaluate Evidence;
* issue Attestations;
* operate through agents, services, interfaces, or delegated mechanisms.

A Participant MAY represent:

* a natural person;
* an organization;
* a software agent;
* an autonomous system;
* a device;
* a service;
* or another entity capable of protocol participation.

A Participant is not required to possess a globally unique real-world identity.

A Participant MUST NOT be assumed to correspond one-to-one with:

* a cryptographic key;
* an Identifier;
* an account;
* a device;
* a process;
* a network endpoint;
* a legal person.

A Participant MAY operate through multiple Identifiers.

A Participant MAY cease to be active while remaining a Participant referenced by existing protocol History.

A Participant is not inherently trusted or untrusted.

---

## 5.2 Subject

A **Subject** is an entity, object, Event, Interaction, Claim, Record, relationship, state, or other thing about which protocol information makes an assertion.

A Participant MAY be a Subject.

A Subject is not necessarily a Participant.

Examples of Subjects MAY include:

* a Participant;
* a natural person who does not participate in OLP;
* an organization;
* a shipment;
* a contract;
* a device;
* a document;
* a dataset;
* an Event;
* an Interaction;
* a physical asset;
* a Claim;
* another protocol object.

Subject describes a semantic role and does not imply active protocol participation.

---

## 5.3 Identifier

An **Identifier** is a value used within an identification system to distinguish or refer to an entity.

An Identifier MAY be:

* globally unique;
* locally unique;
* temporary;
* persistent;
* pseudonymous;
* cryptographically derived;
* externally assigned;
* resolvable;
* non-resolvable.

An Identifier does not necessarily reveal the real-world identity of the entity it references.

An Identifier MUST NOT be assumed to be:

* a public key;
* a DID;
* a URI;
* an account;
* a credential;
* a legal identity;
* a network address.

A Participant MAY have multiple Identifiers.

Multiple Identifiers MAY refer to the same Participant.

An Identifier MUST NOT be assumed to correspond to exactly one real-world entity unless the applicable identification system establishes that property.

Control of an Identifier at a particular time MUST NOT automatically be interpreted as proof of legal ownership, legitimate authority, or real-world identity.

Open Layer Protocol MUST NOT require one universal identification system.

---

## 5.4 Reference

A **Reference** is a value or structure used to locate, address, identify for retrieval purposes, or establish a relationship to protocol information or an external resource.

A Reference MAY point to:

* a Record;
* an Attestation;
* an Event;
* an external document;
* a resource;
* Evidence;
* another protocol-compatible object.

A Reference is conceptually distinct from an Identifier.

A Reference does not necessarily establish:

* identity;
* authorship;
* authority;
* integrity;
* truth;
* ownership.

Those properties require separate Evidence or verification.

---

## 5.5 Claim

A **Claim** is a semantic statement asserting that something is or was the case.

A Claim MAY concern:

* a Participant;
* a Subject;
* an Event;
* an Interaction;
* an Outcome;
* an object;
* a state;
* a capability;
* a relationship;
* another Claim.

A Claim is not inherently attributable.

A Claim is not assumed to be true merely because it exists within the protocol.

A Claim MAY be:

* supported by Evidence;
* contradicted by Evidence;
* unsupported;
* disputed;
* qualified;
* revoked indirectly through revocation of an associated Attestation;
* superseded;
* or otherwise contextualized.

Multiple Attestations MAY assert the same Claim.

Conflicting Claims MAY coexist within OLP.

---

## 5.6 Attestation

An **Attestation** is an attributable assertion of one or more Claims.

Conceptually:

`Attestation = Claim assertion + attributable issuer context`

An Attestation associates a Claim or Claims with an Issuer or Identifier through some attributable mechanism.

An Attestation MAY contain or reference supporting Evidence.

Multiple Attestations MAY assert the same underlying Claim.

Multiple Attestations MAY contradict one another.

Conflicting Attestations MAY coexist within OLP.

The existence of multiple mutually consistent Attestations MUST NOT by itself be interpreted as proof that:

* their Issuers are independent;
* their Claims are true;
* the Attestations were created without coordination;
* the underlying event occurred.

Cryptographic verification of an Attestation MAY establish integrity and attribution relative to an Identifier, key, or other mechanism.

Such verification MUST NOT by itself be interpreted as proof of:

* a real-world identity;
* legitimate authority;
* independence;
* honesty;
* or the truth of the underlying Claim.

---

## 5.7 Evidence

**Evidence** is information that may support, contradict, qualify, contextualize, or otherwise inform evaluation of one or more Claims.

Evidence is defined by its potential role in evaluation, not by its reliability or truthfulness.

Evidence MAY originate from:

* Attestations;
* Observations;
* Events;
* Interactions;
* Outcomes;
* Records;
* documents;
* cryptographic proofs;
* external systems;
* Participants;
* devices;
* services;
* Trust conclusions;
* or other protocol-compatible sources.

Evidence MAY be:

* accurate;
* inaccurate;
* incomplete;
* misleading;
* forged;
* disputed;
* obsolete;
* weak;
* strong;
* independently corroborated;
* or contradicted.

The relevance, reliability, weight, and interpretation of Evidence MAY vary by Context and Trust Model.

Evidence MUST NOT be treated by the protocol as automatically establishing the truth of a Claim.

---

## 5.8 Observation

An **Observation** is Evidence produced through observing or measuring an Event, state, property, condition, or other phenomenon.

An Observation MAY be produced by:

* a natural person;
* a software system;
* a sensor;
* a device;
* a service;
* an autonomous agent;
* another observation mechanism.

An Observation is not inherently objective.

Machine generation does not imply objectivity.

The interpretation or reliability of an Observation MAY depend on:

* the observer;
* measurement methodology;
* equipment;
* calibration;
* environmental conditions;
* available Context;
* provenance;
* data transformation;
* software correctness;
* possible manipulation.

An Observation MAY itself be represented through Claims or Attestations.

---

## 5.9 Event

An **Event** is a representation of something asserted to have occurred.

An Event MAY involve:

* no identifiable entity;
* one entity;
* multiple entities;
* Participants;
* non-Participants;
* Subjects;
* external systems.

An Event MAY reference:

* Participants;
* Subjects;
* Claims;
* Evidence;
* Observations;
* Interactions;
* Outcomes;
* timestamps;
* locations;
* other protocol information.

Representation of an Event within OLP does not itself prove that the represented occurrence happened as described.

Different Claims or Attestations MAY describe the same alleged Event differently.

---

## 5.10 Interaction

An **Interaction** is an Event involving two or more entities in relation to a shared activity, exchange, process, or relationship.

Those entities MAY, but need not, be OLP Participants.

An Interaction MAY involve:

* Participants;
* non-Participants;
* organizations;
* devices;
* external services;
* other Subjects.

Examples MAY include:

* a transaction;
* delivery of a service;
* transfer of an asset;
* fulfillment of an agreement;
* exchange of information;
* execution of a task;
* collaboration;
* negotiation;
* communication.

The protocol MUST NOT assume that every Interaction is:

* financial;
* contractual;
* voluntary;
* successful;
* legally recognized;
* conducted entirely between OLP Participants.

An Interaction MAY produce one or more Outcomes.

---

## 5.11 Outcome

An **Outcome** is an asserted result, consequence, or resulting state associated with an Event or Interaction.

Examples MAY include:

* delivery completed;
* payment failed;
* agreement fulfilled;
* service partially completed;
* transaction disputed;
* requested action rejected.

An Outcome is not assumed to represent an objectively authoritative final state.

Different Participants or other sources MAY assert different Outcomes for the same Event or Interaction.

Multiple conflicting Outcomes MAY coexist.

OLP MUST NOT require a single canonical Outcome merely because multiple assertions concern the same Event or Interaction.

---

## 5.12 Record

A **Record** is a discrete representation containing or referencing protocol information.

A Record MAY contain or reference:

* Claims;
* Attestations;
* Evidence;
* Observations;
* Events;
* Interactions;
* Outcomes;
* Identifiers;
* References;
* provenance information;
* status information;
* other Records.

A Record is not equivalent to truth.

A Record is not equivalent to Reputation.

A Record SHOULD preserve sufficient information to support relevant provenance and verification where the underlying mechanism permits it.

Whether Records are immutable at the byte, storage, or object level is not defined by this vocabulary specification.

---

## 5.13 History

A **History** is an ordered, partially ordered, or otherwise temporally related collection of Records associated with a Participant, Subject, Identifier, relationship, or Context over time.

A History represents available protocol information, not a universal judgment about the subject of that information.

Different Participants, applications, or systems MAY possess different subsets of the same broader History.

OLP does not assume that a single:

* complete;
* globally available;
* canonical;
* centrally stored;
* authoritative

History exists.

Absence of a Record from an available History MUST NOT by itself establish that the corresponding Event, Claim, Evidence, or Interaction never existed.

A Participant's History MUST NOT be silently rewritten in a manner that causes previously represented information to appear never to have existed where that historical distinction is semantically relevant.

Corrections, revocations, disputes, and superseding information SHOULD be represented explicitly.

Preservation of historical semantics does not require:

* perpetual storage;
* universal availability;
* universal disclosure;
* universal replication;
* indefinite retention.

A Record MAY become unavailable because of:

* privacy requirements;
* legal obligations;
* retention policies;
* storage loss;
* deliberate deletion;
* access restrictions;
* selective disclosure.

Such unavailability is distinct from semantically asserting that the Record never existed.

---

## 5.14 Provenance

**Provenance** is information describing the origin and derivation of protocol information.

Provenance MAY include:

* who created or issued information;
* which Identifier was used;
* when information was created;
* which source information was referenced;
* how information was transformed;
* which intermediary systems processed it;
* which signatures or proofs apply;
* which Participants transmitted or presented it;
* which earlier Records influenced it.

Provenance enables evaluators to reason about where information came from without requiring them to accept that information as true.

Provenance does not itself imply:

* truth;
* reliability;
* legitimacy;
* authority;
* independence.

---

## 5.15 Context

**Context** is the set of circumstances, purposes, assumptions, constraints, and relevant information under which Evidence or Trust is evaluated.

Context MAY include:

* purpose;
* requested action;
* interaction type;
* value at risk;
* jurisdiction;
* time;
* domain;
* Participant roles;
* Subject roles;
* historical scope;
* Evidence requirements;
* application policy;
* Trust Model;
* risk tolerance;
* applicable rules.

Evidence considered highly relevant in one Context MAY be irrelevant in another.

The protocol MUST NOT assume that Trust is globally transferable without regard to Context.

OLP MAY define mechanisms for representing Context without requiring a universal ontology covering every possible domain or purpose.

---

## 5.16 Trust

**Trust** is a contextual conclusion about whether reliance on a Participant, Claim, system, service, Subject, or other target is acceptable for a particular purpose.

Trust is derived from interpretation.

Trust is not a primitive protocol fact.

Trust is not an intrinsic property permanently possessed by a Participant.

Trust MAY be determined by:

* a Participant;
* an application;
* an organization;
* an algorithm;
* a policy;
* a Trust Model;
* another decision-making mechanism.

Different evaluators MAY legitimately produce different Trust conclusions from identical Evidence and identical Context.

A Trust conclusion MAY be represented, asserted, exchanged, or attested to.

Once represented in this way, that Trust conclusion MAY itself become Evidence evaluated by another Participant or Trust Model.

Such representation does not transform the Trust conclusion into canonical protocol truth.

The protocol MUST NOT define a universal Trust score.

---

## 5.17 Trust Model

A **Trust Model** is a method, policy, algorithm, process, or decision framework used to evaluate Evidence within a Context and produce Trust-related conclusions.

Conceptually:

`Evidence + Context + Trust Model → Trust conclusion`

A Trust Model MAY consider:

* Provenance;
* historical Interactions;
* Attestations;
* Observations;
* prior Outcomes;
* relationships;
* recency;
* corroboration;
* contradictions;
* external information;
* domain-specific rules;
* risk thresholds;
* identity-related Evidence.

Different Trust Models MAY legitimately produce different conclusions from the same Evidence and Context.

This disagreement is expected behavior and MUST NOT be treated as a protocol inconsistency.

Open Layer Protocol permits algorithm plurality.

No Trust Model becomes authoritative merely because it is compatible with OLP.

OLP MUST NOT define one universal Trust Model.

---

## 5.18 Verification

**Verification** is the process of evaluating whether specified properties of protocol information satisfy defined validation rules.

Verification MAY include checking:

* signatures;
* hashes;
* cryptographic proofs;
* schemas;
* integrity;
* Identifiers;
* References;
* provenance relationships;
* authorization;
* status information;
* temporal conditions.

Successful Verification establishes only the properties that were actually verified.

For example, validation of a signature under a public key may establish that:

* the signature is mathematically valid for that key;
* the signed content has not been modified relative to that signature.

It does not automatically establish:

* who controlled the key at the relevant time;
* the legal or real-world identity of the signer;
* whether the signer was authorized;
* whether the signed Claim is true;
* whether the signer was acting independently;
* whether reliance is appropriate.

Verification MUST NOT be represented as proof of claims beyond the properties actually established.

---

## 5.19 Disclosure

**Disclosure** is the intentional revelation of protocol information, or verifiable information derived from it, to another Participant, system, or audience.

Disclosure MAY be:

* complete;
* partial;
* selective;
* contextual;
* temporary;
* proof-based;
* privacy-preserving.

Disclosure MAY reveal:

* original information;
* selected fields;
* derived information;
* only a verifiable property of underlying information.

Possession of protocol information does not imply automatic public Disclosure.

The ability to verify relevant information SHOULD NOT require universal publication of all underlying information.

---

## 5.20 Revocation

**Revocation** is an attributable indication intended to withdraw, terminate, or limit reliance on previously issued protocol information under specified conditions.

Revocation does not erase the historical existence of the original information.

A Revocation MAY specify:

* effective time;
* scope;
* reason;
* affected Record or Attestation;
* applicable conditions.

The existence of a purported Revocation does not automatically establish that the Revocation is authoritative or effective.

Whether a Revocation is effective MAY depend on:

* provenance;
* authorization;
* applicable protocol rules;
* issuer authority;
* temporal conditions;
* evaluation Context.

A revoked Record MAY remain relevant when evaluating what information existed or was relied upon at an earlier point in time.

Revocation changes reliance status under applicable rules; it does not imply that the original information never existed.

---

## 5.21 Supersession

**Supersession** is the explicit replacement, correction, update, or qualification of earlier protocol information by newer information.

Supersession does not imply deletion of the earlier information.

A superseding Record SHOULD identify the information it supersedes where possible.

Supersession MAY indicate that newer information should be preferred for a particular purpose or time period without implying that the earlier information was invalid when originally created.

Supersession and Revocation are distinct concepts.

For example:

* an outdated address may be superseded by a newer address;
* a credential may instead be revoked;
* an incorrect measurement may be superseded by a correction.

Neither operation semantically erases the historical existence of the earlier Record.

---

## 5.22 Issuer

An **Issuer** is a Participant that creates or authorizes an attributable protocol assertion.

Issuer describes a contextual role.

A Participant MAY act as an Issuer in one context and another role elsewhere.

Being an Issuer does not by itself imply:

* authority;
* truthfulness;
* expertise;
* ownership;
* trustworthiness;
* legal recognition.

Those properties must be established separately where relevant.

---

## 5.23 Holder

A **Holder** is a Participant that possesses protocol information and is capable of storing, presenting, using, or selectively disclosing it.

Holder describes a contextual role.

Possession does not imply:

* authorship;
* ownership;
* endorsement;
* authority;
* truthfulness.

A Holder MAY possess information about itself or about another Subject.

---

# 6. Role Relationships

Participant, Issuer, Holder, and Subject describe different concepts.

A single entity MAY simultaneously perform multiple roles.

For example, a Participant MAY:

* issue an Attestation;
* hold an Attestation issued by another Participant;
* be the Subject of a third Attestation;
* verify Evidence from another system.

A Subject MAY exist without being a Participant.

An Issuer MUST be a Participant under the terminology of this specification because issuing protocol information constitutes an active protocol role.

A Holder MUST be a Participant while acting as a Holder because holding, presenting, or disclosing protocol information constitutes an active protocol role.

No role by itself implies:

* Trust;
* authority;
* ownership;
* correctness;
* legal status;
* truth.

---

# 7. Relationship Between Evidence and Trust

Open Layer Protocol treats Evidence and Trust as separate layers.

A simplified model is:

`Protocol information → Evidence`

`Evidence + Context + Trust Model → Trust conclusion`

`Trust conclusion + Policy + Context → Application decision`

The protocol MAY standardize the interoperable representation and verification of Evidence.

The protocol MUST NOT require all Participants to derive the same Trust conclusion.

Applications MAY:

* ignore certain Evidence;
* weight Evidence differently;
* require additional Evidence;
* apply different Trust Models;
* reject another application's Trust conclusion;
* publish their own Trust conclusions.

This plurality is intentional.

---

# 8. Disagreement and Contradiction

Open Layer Protocol MUST permit disagreement to be represented without requiring the protocol itself to select a universal winner.

For example:

* Participant A attests that an Interaction was completed successfully.
* Participant B attests that the same Interaction failed.
* Participant C provides an Observation supporting part of Participant A's Claim.
* Participant D provides Evidence contradicting both.

All of these MAY coexist.

OLP MAY enable applications to verify:

* provenance;
* attribution;
* signatures;
* timing;
* relationships;
* referenced Evidence.

OLP does not thereby determine which interpretation must be accepted.

Disagreement is protocol information.

It is not necessarily a protocol error.

---

# 9. Information Independence and Collusion

Multiple pieces of Evidence MUST NOT be assumed to be independent merely because they originate from different Identifiers or appear in separate Records.

For example, multiple Attestations MAY:

* share a common source;
* be coordinated;
* originate from the same controlling entity;
* reproduce the same inaccurate information;
* derive from one underlying Observation;
* participate in deliberate collusion.

OLP MAY represent provenance information useful for evaluating independence.

OLP MUST NOT manufacture independence merely from multiplicity.

---

# 10. History and Information Availability

OLP distinguishes:

* historical existence;
* semantic validity;
* current reliance status;
* storage availability;
* disclosure availability.

These concepts MUST NOT be silently collapsed into one another.

A Record may:

* have existed historically;
* later be revoked;
* remain historically relevant;
* no longer be stored by one Participant;
* remain available to another;
* be selectively disclosed;
* be inaccessible because of legal restrictions.

Therefore:

> Absence is not proof of non-existence.

and:

> Unavailability is not equivalent to historical deletion.

The protocol SHOULD preserve enough explicit status information to avoid misleading interpretations where such distinctions are known.

---

# 11. Terms Intentionally Not Defined as Core Protocol Objects

## 11.1 Reputation

Open Layer Protocol does not define **Reputation** as a first-class semantic primitive.

Reputation generally represents an interpretation, aggregation, summary, ranking, or judgment derived from Evidence, History, Trust conclusions, or other information.

Applications MAY construct Reputation systems.

Such systems MAY use OLP-compatible Evidence.

Their outputs MUST NOT become authoritative protocol truth merely because they are derived from OLP data.

Different applications MAY derive incompatible Reputation representations from identical Evidence.

---

## 11.2 Universal Trust Score

Open Layer Protocol does not define a universal **Trust Score**.

Applications and Trust Models MAY calculate:

* numerical scores;
* grades;
* categories;
* probability estimates;
* risk classifications;
* binary recommendations;
* other decision outputs.

Such outputs are contextual results of those systems rather than canonical properties of Participants.

---

## 11.3 Canonical Global History

Open Layer Protocol does not define one mandatory canonical global History containing every Record relevant to every Participant or Subject.

Different Participants MAY hold different subsets.

Applications MUST NOT infer completeness merely because a History is internally valid.

---

## 11.4 Universal Authority

Open Layer Protocol does not define one universally authoritative Participant, registry, Trust Model, ledger, identity provider, or adjudicator.

Specific applications, jurisdictions, ecosystems, or contractual arrangements MAY recognize authorities for particular purposes.

Such authority remains contextual.

---

# 12. Concepts Deferred to Later Specifications

The following concepts are deliberately not fully defined in this vocabulary version unless later protocol design demonstrates that they are necessary:

* Signer;
* Controller;
* Delegate;
* Presenter;
* Verifier as a protocol role;
* cryptographic Proof as a first-class object;
* Policy;
* dispute-resolution mechanisms;
* adjudication;
* appeals;
* identity binding;
* key rotation;
* key recovery;
* delegation chains;
* authorization models;
* schema versioning;
* transport semantics;
* persistence requirements;
* canonical serialization;
* blockchain anchoring;
* consensus mechanisms.

Deferring these concepts prevents implementation assumptions from being introduced prematurely into foundational vocabulary.

---

# 13. Vocabulary Rules for Future Specifications

Future Open Layer Protocol specifications SHOULD follow these rules:

1. Prefer neutral descriptions of observable or attributable information over evaluative labels.

2. Distinguish assertions from truth.

3. Distinguish identity from Trust.

4. Distinguish Verification from truth.

5. Distinguish historical existence from current validity.

6. Distinguish identification from protocol addressing.

7. Identify the source of assertions whenever Provenance permits.

8. Do not imply truth merely from cryptographic validity.

9. Do not imply authority merely from attribution.

10. Do not imply independence merely from multiple sources.

11. Do not imply Reputation merely from History.

12. Do not infer completeness from an available History.

13. Treat Trust as contextual.

14. Permit competing Trust Models.

15. Preserve legitimate disagreement between Claims and Attestations.

16. Represent corrections and status changes explicitly rather than silently rewriting historical semantics.

17. Do not require universal disclosure in order to enable Verification where privacy-preserving alternatives are possible.

18. Avoid unnecessary coupling to a particular:

    * blockchain;
    * ledger;
    * identity system;
    * cryptographic suite;
    * jurisdiction;
    * storage architecture;
    * transport;
    * Trust Model.

19. Keep semantic vocabulary separate from wire-format object design unless a later specification explicitly binds them.

20. Define only the guarantees that a mechanism can actually establish.

---

# 14. Foundational Invariants

The vocabulary defined in this document establishes the following conceptual invariants.

> **Evidence can be portable. Trust remains contextual.**

> **Claims can be attributable without being true.**

> **Information can be verified without being believed.**

> **Identity can be established without implying Trust.**

> **An Identifier is not necessarily an identity.**

> **A valid signature proves only the properties actually validated by that signature mechanism.**

> **History can be preserved without becoming Reputation.**

> **History may be incomplete without being invalid.**

> **Absence of available Evidence is not proof that Evidence never existed.**

> **Revocation changes reliance status; it does not erase historical existence.**

> **Supersession changes which information should be preferred; it does not rewrite the past.**

> **Disagreement can exist without requiring the protocol to select a universal winner.**

> **Multiple Attestations do not automatically imply independent corroboration.**

> **Trust conclusions may themselves become Evidence without becoming canonical truth.**

> **Trust Models may compete while sharing the same interoperable Evidence layer.**

> **Trust is not authorization.**

> **Protocol roles do not inherently imply authority, ownership, truth, or Trust.**

> **OLP verifies relationships between information; it does not manufacture truth from those relationships.**

---

# 15. Conceptual Model Summary

At the vocabulary level, the Open Layer Protocol can be summarized as follows.

A **Participant** may operate through one or more **Identifiers**.

Protocol information may refer to Participants, other entities, or objects as **Subjects**.

A **Claim** states that something is or was the case.

An **Attestation** makes one or more Claims attributable to an **Issuer**.

An **Observation** is a form of **Evidence** produced through observation or measurement.

An **Event** represents something asserted to have occurred.

An **Interaction** is an Event involving multiple entities.

An **Outcome** represents an asserted result or consequence of an Event or Interaction.

Protocol information may be represented within **Records**.

Records may be related using **References**.

A collection of Records over time may form a **History**.

**Provenance** describes where protocol information came from and how it was derived.

Evidence is evaluated within a **Context**.

A **Trust Model** interprets Evidence within that Context.

The result may be a **Trust** conclusion.

That Trust conclusion may influence an application decision, but it does not itself constitute authorization.

Information may later be selectively revealed through **Disclosure**, withdrawn from current reliance through **Revocation**, or replaced or qualified through **Supersession**.

At no point does OLP require a universal authority, universal Reputation, universal Trust score, universal Trust Model, or globally canonical interpretation of the available Evidence.

---

# 16. Scope Boundary

Open Layer Protocol exists to make trust-relevant Evidence portable and independently verifiable without making Trust itself centrally owned.

The protocol therefore concerns itself primarily with:

* representation;
* attribution;
* Provenance;
* relationships;
* Evidence portability;
* status;
* selective Disclosure;
* Verification;
* interoperability.

The protocol does not attempt to become a universal arbiter of:

* truth;
* morality;
* legality;
* reputation;
* authorization;
* risk;
* identity;
* commercial acceptability;
* social standing;
* trustworthiness.

Applications, Participants, policies, jurisdictions, and Trust Models remain responsible for interpreting Evidence within their own Contexts.

---

# 17. Milestone 1 Status

This document represents the vocabulary baseline established during **Milestone 1 — Vocabulary**.

The concepts defined here are intended to constrain future protocol design without prematurely determining implementation details.

The next specification milestone SHOULD determine which of these semantic concepts require first-class protocol representations and which should remain conceptual, derived, embedded, or application-level constructs.

That work belongs to:

**Milestone 2 — Protocol Objects**