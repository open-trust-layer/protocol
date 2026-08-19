# OLP Specification 0007 — Status, Revocation, and Lifecycle Evidence

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 7 — Status, Revocation & Lifecycle Evidence  
**Filename:** `specification/0007-status-and-lifecycle.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) v1 status, revocation, and lifecycle-evidence layer.

It defines:

- a generic immutable lifecycle-status record profile;
- a generic target model for OLP records, OLP proofs, verification methods, principals, and extension-defined targets;
- the core lifecycle event vocabulary `activate`, `suspend`, `resume`, `retire`, `revoke`, `compromise`, and `deprecate`;
- explicit status-authority attribution without creating a universal status authority;
- source-local sequence semantics that do not depend on a universal clock;
- scoped status assertions;
- authenticated effective-time and next-update assertions;
- separation of cryptographic validity, lifecycle evidence, lifecycle authority, freshness, completeness, and local policy;
- current-status and historical-status evaluation semantics;
- conflict, equivocation, rollback, stale-evidence, and missing-evidence handling;
- interaction with the status records already defined by OLP Specification 0006;
- interoperability boundaries for X.509 CRLs, OCSP, W3C Bitstring Status List, DID/native status mechanisms, short-lived credentials, transparency systems, archival evidence, and future external status systems;
- structured processing and evaluation results;
- conformance requirements; and
- security and privacy considerations.

OLP does not maintain mutable status fields on historical records or proofs.

OLP does not define a global revocation server, global status registry, global clock, global certificate authority, global issuer, or universal algorithm for determining the current state of every object.

Status is evidence.

Revocation is evidence.

Lifecycle is represented by additive immutable evidence rather than destructive mutation of history.

---

## 2. Scope

This specification answers the question:

> How can OLP represent portable evidence that an existing record, proof, verification method, principal identifier, authority grant, or other target has become active, suspended, resumed, retired, revoked, compromised, deprecated, or otherwise changed lifecycle state, without modifying the target and without pretending that one status source is universally authoritative?

This specification builds directly on:

- OLP Specification 0003 — Record Representation;
- OLP Specification 0004 — Proofs and Verification;
- OLP Specification 0005 — Evidence Relationships and Graphs; and
- OLP Specification 0006 — Identity and Authority Evidence.

Specification 0003 establishes immutable record identity.

Specification 0004 establishes detached proofs, structured verification results, verification-method status as a dimension separate from cryptographic validity, and the principle that later status does not rewrite historical signature validity.

Specification 0005 establishes stable Proof Identity, `EvidenceRefV1`, immutable relationship records, explicit correction/dispute/supersession relationships, partial evidence graphs, and resolution boundaries.

Specification 0006 establishes Principal Identifiers, authority evidence, authority-status records, verification-method-status records, and the separation between cryptographic control, identity, authority, status, and policy.

This specification generalizes lifecycle evidence across OLP object categories while preserving all of those invariants.

This specification does **not** define:

- a mutable `status` field on OLP records;
- a mutable `revoked` flag on OLP proofs;
- a universal current-state database;
- a universal revocation authority;
- a universal certificate authority;
- a universal principal-status authority;
- a mandatory online status service;
- a mandatory status URL;
- a mandatory DID method;
- a mandatory PKI;
- a mandatory W3C credential-status mechanism;
- a mandatory blockchain;
- a mandatory transparency log;
- a universal status precedence algorithm;
- a universal meaning of “latest” based solely on timestamps;
- a universal status freshness period;
- a universal sequence namespace;
- a universal state machine for all target types;
- a universal rule that revocation can never be corrected;
- a universal rule that retirement means compromise;
- a universal rule that absence of status evidence means active;
- a universal rule that a cryptographically valid status statement is authoritative;
- automatic trust in a status producer; or
- automatic network dereferencing during lifecycle evaluation.

Applications MAY use OLP lifecycle evidence together with external status systems.

Where a native status mechanism already defines suitable semantics, implementations SHOULD preserve and evaluate those native semantics rather than flattening them into a lossy OLP boolean.

---

## 3. Requirements Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described by BCP 14 when, and only when, they appear in all capitals.

---

## 4. Core Invariants

The following invariants are normative.

### 4.1 Lifecycle evidence is additive

A lifecycle event MUST be represented as new evidence.

It MUST NOT be represented by mutating the Record Identity, Proof Identity, canonical content, proof value, or historical representation of the target.

For example:

```text
Grant G
    |
    +-- Status S1: suspend
    |
    +-- Status S2: resume
    |
    +-- Status S3: revoke
```

The original Grant G remains unchanged.

### 4.2 Status does not rewrite history

A later revocation, retirement, suspension, compromise claim, deprecation claim, or status-source decision MUST NOT retroactively change:

- Record Identity;
- Proof Identity;
- whether a historical signature mathematically verifies;
- the bytes that were originally signed; or
- the fact that a status assertion itself existed as an immutable OLP record.

Historical cryptographic validity and later reliance status are separate dimensions.

### 4.3 Status evidence is not universal truth

A conforming lifecycle-status record establishes that a particular immutable status statement exists.

A valid proof establishes cryptographic attribution to a verification method under Specification 0004.

Neither, by itself, establishes that the lifecycle event objectively occurred or that every application must rely on the statement.

### 4.4 No universal current status

OLP v1 does not define one protocol-global function:

```text
currentStatus(target) -> ACTIVE | REVOKED
```

A current-status conclusion depends on at least some combination of:

- which status sources are accepted;
- whether their authority is established;
- whether the relevant evidence set is complete enough;
- whether the evidence is sufficiently fresh;
- whether event ordering is established;
- whether scope matches;
- whether effective-time assertions are accepted;
- whether conflicts exist;
- whether native external status rules apply; and
- local policy.

### 4.5 Absence is not positive status

The absence of a revocation, suspension, compromise, or other negative status record MUST NOT, by itself, be interpreted as:

```text
ACTIVE
GOOD
VALID
NOT_REVOKED
UNCOMPROMISED
```

unless an accepted status mechanism explicitly defines and cryptographically supports such negative-information semantics.

An open OLP evidence graph is not inherently complete.

### 4.6 Event vocabulary is not a universal state machine

Core lifecycle event names have stable semantics, but OLP v1 does not define one automatic transition table for every target type.

For example:

```text
resume
```

means that a producer asserts that an applicable suspension no longer applies.

It does **not** automatically undo:

```text
revoke
compromise
retire
deprecate
```

Similarly:

```text
activate
```

MUST NOT automatically erase previously accepted revocation or compromise evidence.

### 4.7 No timestamp-only “latest wins” rule

Producer-asserted timestamps are not a universal ordering oracle.

OLP MUST NOT define:

```text
largest effectiveAt wins
```

as a universal status-resolution rule.

### 4.8 Status authority is separate from status syntax

Anyone can create a structurally conforming lifecycle-status record.

Applications MUST separately determine whether the record's proof producer or named status authority is an acceptable source for the target and scope.

### 4.9 Effective time is not independent chronology

`effectiveAt` is an authenticated semantic time assertion made by the status producer.

It does not independently prove:

- when the status record was created;
- when the status event objectively occurred;
- when another participant learned of the event; or
- that the status record existed at the asserted time.

Stronger historical conclusions require appropriate independent temporal evidence.

### 4.10 Sequence is not a global clock

A source-local `sequence` can express issuer-declared ordering within a narrowly defined lifecycle stream.

It MUST NOT be compared across unrelated status authorities, targets, scopes, or status mechanisms as though it were a global time value.

### 4.11 Expiration is distinct from revocation

If a target has an intrinsic `validUntil`, `expires`, or equivalent validity boundary defined by another OLP or external specification, reaching that boundary does not require a `revoke` lifecycle event.

Expiration and revocation remain semantically distinct.

### 4.12 Retirement is distinct from compromise

`retire` means the target is no longer intended for new use according to the status producer.

It does not imply unauthorized private-key disclosure, hostile takeover, forgery, or other compromise.

### 4.13 Compromise is distinct from cryptographic failure

A proof may legitimately be represented as:

```text
cryptographicValidity = VALID
lifecycleEvidence      = COMPROMISE_REPORTED
```

These are not contradictory.

### 4.14 Conflicts remain evidence

If accepted lifecycle evidence conflicts, a processor MUST preserve the conflict.

It MUST NOT silently discard inconvenient evidence merely to manufacture one clean status value.

### 4.15 Corrections do not delete erroneous status history

A mistaken status statement may later be corrected, disputed, or superseded using Specification 0005 relationships or additional lifecycle evidence.

The original status record remains part of history.

### 4.16 External status semantics remain external

When status originates in X.509, OCSP, a W3C status list, a DID method, a hardware system, a package registry, or another external mechanism, OLP MUST NOT silently redefine the source mechanism's semantics.

### 4.17 Verification and status collection are separable

A cryptographic verifier MUST be capable of verifying a proof without implicitly performing arbitrary status network lookups.

Lifecycle evidence collection and proof verification remain separate operations.

### 4.18 Offline evaluation is first-class

An implementation MUST be able to evaluate supplied lifecycle evidence without mandatory network access.

The resulting evaluation MAY be incomplete or stale; that condition must remain visible.

### 4.19 Status provenance remains visible

A lifecycle conclusion SHOULD retain sufficient provenance to determine:

- which lifecycle records were evaluated;
- which proofs supported them;
- which status authority was named;
- how identity/authority binding was evaluated;
- which external mechanisms were consulted;
- when external evidence was observed;
- whether source-supplied freshness information existed; and
- which local policy produced any collapsed operational state.

### 4.20 Status quantity is not status quality

A larger number of lifecycle records does not create greater protocol-defined truth.

Ten thousand untrusted revocation claims do not automatically outweigh one accepted authoritative status source.

OLP does not define status by vote count.

---

## 5. Terminology

### 5.1 Lifecycle target

The object or identifier about which a lifecycle-status statement is made.

### 5.2 Lifecycle status record

An immutable OLP record whose semantic content conforms to `LifecycleStatusStatementV1`.

### 5.3 Lifecycle event

The producer-asserted status event named by a lifecycle-status record.

### 5.4 Status producer

A verification method that produces a valid proof over a lifecycle-status record.

### 5.5 Status authority

A Principal Identifier named by the lifecycle-status statement as the principal on whose behalf the status assertion is claimed to be made.

A named status authority is not automatically authoritative merely because it is named.

### 5.6 Status source

A broader term for the source from which lifecycle evidence is obtained.

A status source MAY be:

- an OLP proof producer;
- a named OLP status authority;
- a certificate authority;
- an OCSP responder;
- a W3C credential-status issuer;
- a DID/native resolver;
- a hardware or device-management authority;
- a package registry;
- an organizational security service;
- a transparency service;
- a local administrator; or
- another domain-defined source.

### 5.7 Effective time

The time from which the status producer asserts that a lifecycle event should be considered semantically effective.

### 5.8 Observation time

The local time at which an evaluator, collector, or resolver observed or retrieved status evidence.

Observation time is not a field of `LifecycleStatusStatementV1` unless independently represented by additional evidence.

### 5.9 Next update

A producer-asserted time by which the source expects status information to be refreshed or reconsidered.

`nextUpdate` is a freshness signal, not an automatic inverse lifecycle event.

### 5.10 Sequence

A non-negative source-local ordinal that can express producer-declared ordering of status events within the same target, status authority, and scope.

### 5.11 Scope

An optional absolute URI identifying the lifecycle context in which a status assertion is intended to apply.

### 5.12 Status freshness

An evaluation of whether lifecycle evidence is recent enough for the relying application's current purpose.

### 5.13 Status completeness

An evaluation of whether the evidence source or supplied evidence set provides sufficient coverage for the lifecycle conclusion being attempted.

Completeness is not implied merely because no additional records are known.

### 5.14 Current-status evaluation

An evaluation of lifecycle evidence for reliance at or near an evaluation time considered “current” by the application.

### 5.15 Historical-status evaluation

An evaluation concerning lifecycle state at a past time.

### 5.16 Native status mechanism

A status mechanism defined outside this specification by the target's identity, credential, certificate, registry, hardware, or application ecosystem.

### 5.17 Operational state

A local policy result such as `ALLOW`, `BLOCK`, `ACTIVE`, `SUSPENDED`, or `REVOKED_FOR_USE`.

Operational state is not an OLP-global fact.

---

## 6. Architectural Model

The normative architecture is:

```text
                         Target T
                            ^
                            |
                 immutable target reference
                            |
                 +----------+----------+
                 |                     |
                 v                     v
        Lifecycle Status S1   Lifecycle Status S2
          event=suspend          event=revoke
                 ^                     ^
                 |                     |
             Proof P1              Proof P2
                 |                     |
                 +----------+----------+
                            |
                            v
                 source/authority evidence
                            |
                            v
                    lifecycle evaluator
                            |
           +----------------+----------------+
           |                |                |
           v                v                v
        freshness        conflicts       local policy
           |                |                |
           +----------------+----------------+
                            |
                            v
                  Structured Result
```

The lifecycle records themselves are immutable evidence.

The evaluator MAY derive a current or historical operational view, but that derived view is not another mutable truth field on the target.

### 6.1 Relationship to Specification 0005

Lifecycle status is represented using ordinary OLP records, not special graph edges.

A graph processor MAY project:

```text
StatusRecord --statusOf--> Target
```

for convenience, but the reified lifecycle-status record is normative.

Corrections, disputes, supersession, anchors, and references continue to use Specification 0005 relationship records.

### 6.2 Relationship to Specification 0006

A status statement may name a `statusAuthority` Principal Identifier.

Binding the proof-producing verification method to that principal uses identity evidence under Specification 0006 or an accepted external identity mechanism.

Authority to issue the lifecycle statement is separately evaluated.

### 6.3 No mutable status service required

A conforming OLP lifecycle implementation can operate entirely from:

- immutable records;
- immutable proofs;
- supplied external status artifacts; and
- explicit local policy.

A network status service MAY improve freshness or completeness but is not required by the protocol core.

---

## 7. `LifecycleTargetV1`

### 7.1 Representation

`LifecycleTargetV1` is the following two-element array:

```text
LifecycleTargetV1 = [
    targetType,      ; index 0
    reference        ; index 1
]
```

The array MUST contain exactly two elements.

### 7.2 Core target types

OLP v1 defines the compact target types:

```text
record
proof
verificationMethod
principal
```

Other compact strings are reserved for future OLP specifications.

Third-party target types MUST use globally unambiguous absolute-URI identifiers.

### 7.3 `record`

For:

```text
targetType = "record"
```

`reference` MUST be an `EvidenceRefV1` with:

```text
kind = 0
```

as defined by Specification 0005.

Any OLP record can therefore receive lifecycle evidence, including:

- ordinary domain records;
- relationship records;
- authority grants;
- principal relation records;
- prior lifecycle-status records; and
- future OLP record profiles.

### 7.4 `proof`

For:

```text
targetType = "proof"
```

`reference` MUST be an `EvidenceRefV1` with:

```text
kind = 1
```

as defined by Specification 0005.

Lifecycle evidence about a proof does not change its Proof Identity or cryptographic validity.

### 7.5 `verificationMethod`

For:

```text
targetType = "verificationMethod"
```

`reference` MUST be an exact absolute URI satisfying the Verification Method Identifier requirements of Specification 0004.

The URI MUST be preserved exactly for cryptographic and semantic processing.

### 7.6 `principal`

For:

```text
targetType = "principal"
```

`reference` MUST be a Principal Identifier under Specification 0006.

A lifecycle event targeting a principal refers to the lifecycle of the **identifier or participation representation**, not to the physical or legal existence of a human or organization.

For example, revoking an account-like principal identifier does not mean the person represented by that account has ceased to exist.

### 7.7 Extension target types

An extension target type MUST:

- use an absolute URI;
- define the allowed type and canonical semantics of `reference`;
- define equality rules;
- define any lifecycle-event compatibility rules;
- define whether resolver interaction is required; and
- define security considerations.

A processor that does not understand an extension target type MUST report `UNSUPPORTED_LIFECYCLE_TARGET_TYPE`.

### 7.8 Equality

Core lifecycle targets are equal only if:

- `targetType` values are exactly equal; and
- references are equal according to the target type's rules.

For `record` and `proof`, equality follows `EvidenceRefV1` equality.

For URI-based target types, equality is exact string equality under the applicable OLP identifier specification.

### 7.9 No implicit aliasing

OLP MUST NOT treat two targets as equal merely because:

- one URI redirects to another;
- two identifiers are asserted `sameSubjectAs`;
- two keys have similar display labels;
- two records contain similar semantics; or
- local databases map them to one account.

Any broader equivalence is policy-dependent and MUST retain provenance.

---

## 8. `LifecycleStatusStatementV1`

### 8.1 Semantic record profile

An OLP v1 lifecycle-status record is an ordinary OLP record conforming to Specification 0003 whose semantic record content is exactly one `LifecycleStatusStatementV1` value.

The enclosing record continues to use Specification 0003 for:

- canonical record representation;
- Record Identity;
- record-level extensions;
- immutability; and
- any record-level metadata.

### 8.2 Exact statement

`LifecycleStatusStatementV1` is the following twelve-element array:

```text
LifecycleStatusStatementV1 = [
    "OLP-LIFECYCLE-STATUS",  ; index 0: profile discriminator
    1,                       ; index 1: version
    target,                  ; index 2: LifecycleTargetV1
    event,                   ; index 3: lifecycle event identifier
    statusAuthority,         ; index 4: PrincipalIdentifier or null
    effectiveAt,             ; index 5: RFC 3339 date-time or null
    sequence,                ; index 6: non-negative integer or null
    scope,                   ; index 7: absolute URI or null
    nextUpdate,              ; index 8: RFC 3339 date-time or null
    reason,                  ; index 9: absolute URI or null
    qualifiers,              ; index 10: map
    critical                 ; index 11: sorted array
]
```

The array MUST contain exactly twelve elements.

### 8.3 Profile discriminator

Index 0 MUST equal the exact text string:

```text
OLP-LIFECYCLE-STATUS
```

### 8.4 Version

Index 1 MUST equal integer `1`.

A processor receiving another syntactically valid version MUST report `UNSUPPORTED_LIFECYCLE_STATUS_VERSION` unless it implements that version.

### 8.5 Target

Index 2 MUST be a valid `LifecycleTargetV1`.

### 8.6 Event

Index 3 MUST be:

- one compact core event defined by Section 9; or
- an absolute-URI extension event identifier.

Unknown compact strings are non-conforming.

Unknown extension event identifiers are `UNSUPPORTED_LIFECYCLE_EVENT`, not malformed merely because the local implementation does not implement them.

### 8.7 Status authority

Index 4 MUST be either:

- `null`; or
- a Principal Identifier under Specification 0006.

If non-null, the statement claims that the named principal is the lifecycle authority on whose behalf the assertion is made.

A named authority is not self-authenticating.

### 8.8 Effective time

Index 5 MUST be either:

- `null`; or
- a valid RFC 3339 date-time accepted by the applicable OLP date-time profile.

It is an authenticated semantic assertion.

It is not independent trusted time.

### 8.9 Sequence

Index 6 MUST be either:

- `null`; or
- a non-negative integer.

If `sequence` is non-null, `statusAuthority` MUST also be non-null.

This prevents an ambiguous source-local sequence from being attached to an unnamed authority.

### 8.10 Scope

Index 7 MUST be either:

- `null`; or
- an absolute URI.

A null scope means the producer did not declare a narrower lifecycle context.

A non-null scope identifies the context in which the lifecycle assertion is intended to apply.

### 8.11 Next update

Index 8 MUST be either:

- `null`; or
- a valid RFC 3339 date-time.

`nextUpdate` means:

> The status producer asserts that consumers seeking a current-status conclusion should expect this status source or mechanism to be refreshed, reconsidered, or rechecked by this time.

It does not imply that the opposite lifecycle state begins after that time.

It does not establish that a later update actually exists.

### 8.12 Reason

Index 9 MUST be either:

- `null`; or
- an absolute URI identifying a reason vocabulary term.

OLP v1 defines no compact lifecycle-reason vocabulary.

Reason values are descriptive evidence.

A policy that assigns security behavior to a reason identifier MUST explicitly understand that identifier.

### 8.13 Qualifiers

Index 10 MUST be a map.

Compact qualifier names are reserved for future OLP specifications.

Third-party qualifier names MUST be absolute URIs.

Unknown non-critical qualifiers MUST be preserved when the record is re-serialized through a semantically preserving processor.

### 8.14 Critical qualifiers

Index 11 MUST be an array of qualifier identifiers.

Every entry MUST:

- identify a property present in `qualifiers`;
- be unique; and
- be sorted according to the deterministic ordering rules adopted by the enclosing record specification.

If a processor does not understand a critical qualifier, semantic lifecycle evaluation MUST report `UNSUPPORTED_CRITICAL_LIFECYCLE_QUALIFIER`.

### 8.15 Duplicate map keys

Duplicate qualifier keys are malformed.

Implementations MUST NOT resolve duplicate keys using first-wins, last-wins, or parser-specific behavior.

### 8.16 Proofs

A lifecycle-status record MAY have zero or more ordinary detached OLP proofs under Specification 0004.

A lifecycle status intended to be attributable to a producer SHOULD normally carry at least one valid proof with:

```text
proofPurpose = assertion
```

OLP v1 does not define a separate `revocation` or `status` proof purpose.

### 8.17 Record identity

Lifecycle-status records have ordinary Record Identity under Specification 0003.

No additional mutable status identifier is defined by this specification.

---

## 9. Core Lifecycle Event Vocabulary

OLP v1 defines seven compact lifecycle event identifiers:

```text
activate
suspend
resume
retire
revoke
compromise
deprecate
```

These values define producer-asserted lifecycle semantics.

They do not define universal policy consequences.

### 9.1 `activate`

Meaning:

> The status producer asserts that the target is intended to be active, enabled, usable, or applicable within the statement's declared scope according to the producer's lifecycle semantics.

`activate` does not prove that the target is trustworthy, authorized, uncompromised, or accepted by any application.

`activate` MUST NOT automatically erase accepted evidence of revocation, compromise, retirement, or deprecation.

### 9.2 `suspend`

Meaning:

> The status producer asserts that use or reliance on the target should be temporarily suspended within the statement's declared scope from the asserted effective time or according to the producer's lifecycle semantics.

Suspension is intended to be potentially reversible.

### 9.3 `resume`

Meaning:

> The status producer asserts that a previously applicable suspension should no longer prevent use or reliance within the statement's declared scope.

`resume` is narrowly about suspension.

It MUST NOT automatically undo `revoke`, `compromise`, `retire`, or `deprecate` evidence.

### 9.4 `retire`

Meaning:

> The status producer asserts that the target is no longer intended for creation of new actions, proofs, bindings, grants, or other new use according to the target's lifecycle semantics.

Retirement is compatible with continued historical verification or archival processing.

Retirement does not imply compromise.

### 9.5 `revoke`

Meaning:

> The status producer asserts that the target has been withdrawn from intended reliance or use within the declared scope according to the producer's authority and lifecycle semantics.

Revocation does not delete or mutate historical evidence.

OLP core does not define one universal rule about whether an accepted revocation may later be corrected or superseded; such treatment requires explicit evidence and policy.

### 9.6 `compromise`

Meaning:

> The status producer asserts that unauthorized control, disclosure, modification, forgery capability, integrity loss, or another security compromise affecting the target may have occurred.

For a verification method, this commonly means that proving material may no longer be exclusively controlled by the intended controller.

For other target types, the applicable extension or domain policy defines the precise compromise semantics.

Compromise evidence can be security-significant without changing historical cryptographic validity.

### 9.7 `deprecate`

Meaning:

> The status producer asserts that the target is no longer recommended for new use, while compatibility, historical processing, or limited continued use may remain appropriate.

Deprecation is particularly useful for:

- cryptographic suites;
- schemas;
- endpoints;
- verification methods;
- role definitions;
- authority mechanisms; and
- protocol features.

Deprecation is weaker than revocation unless a local policy explicitly treats it otherwise.

### 9.8 Extension events

An extension lifecycle event MUST use an absolute URI and MUST define:

- the exact producer-asserted meaning;
- compatible target types;
- interaction with core events;
- whether the event is intended to be temporary or terminal;
- any scope semantics;
- any ordering requirements;
- any required qualifiers; and
- security considerations.

An extension event MUST NOT redefine the semantics of a core event.

### 9.9 No implicit event hierarchy

OLP core defines no universal ordering such as:

```text
compromise > revoke > suspend > deprecate
```

Applications often will treat some events as more severe than others, but that is policy.

---

## 10. Status Attribution and Authority

### 10.1 Record existence is not authority

The existence of a lifecycle-status record does not establish that its producer had authority to issue status for the target.

### 10.2 Proof attribution

A valid assertion proof establishes that the proof's verification method cryptographically asserted the lifecycle-status record.

This does not, by itself, establish the identity of the status producer.

### 10.3 Named status authority

If `statusAuthority` is non-null, a consumer evaluating attribution SHOULD determine whether the proof-producing verification method is acceptably bound to that Principal Identifier.

Such binding MAY be established by:

- `controlsVerificationMethod` evidence under Specification 0006;
- DID/native resolution semantics;
- X.509/PKI semantics;
- an external credential;
- locally pinned key material;
- another accepted identity system; or
- other explicit evidence.

### 10.4 Authority to issue status

Even when the proof producer is acceptably bound to the named status authority, an application MUST separately determine whether that authority is accepted for:

- the target;
- the lifecycle event;
- the declared scope; and
- the relying application's purpose.

### 10.5 Authority grants

A deployment MAY use Authority Grant records under Specification 0006 to represent status-issuing authority.

For example, an organization could grant a security service authority to suspend or revoke a class of verification methods.

OLP v1 does not define one mandatory Action Identifier for status administration.

### 10.6 Unnamed status authority

If `statusAuthority` is null, an application MAY accept a status statement directly based on the proof verification method or another status-source rule.

The absence of a named principal MUST remain visible.

### 10.7 Multiple proofs

A lifecycle-status record may have multiple independent proofs.

Multiple proofs do not automatically mean multiple independent authorities.

They may represent:

- co-signature;
- witness evidence;
- redundant cryptographic suites;
- key rotation overlap; or
- unrelated proof producers.

Applications MUST interpret each proof independently under Specification 0004.

### 10.8 Status-source plurality

Different accepted sources may issue different lifecycle statements about the same target.

OLP does not designate one globally superior source.

Source precedence is contextual.

---

## 11. Sequence and Ordering

### 11.1 Purpose

`sequence` exists to permit a status authority to express local ordering without relying solely on wall-clock timestamps.

### 11.2 Comparison domain

Two sequence values MAY be directly compared by OLP lifecycle processing only when all of the following are exactly equal:

- `statusAuthority`;
- `target`;
- `scope`; and
- lifecycle statement version.

An external lifecycle profile MAY narrow the comparison domain further.

### 11.3 Higher sequence meaning

Within a valid comparison domain, a higher `sequence` means:

> The named status authority asserts that this status statement occurs later in its declared lifecycle ordering than a lower-sequence statement.

This is source-declared ordering.

It is not independent time.

### 11.4 Sequence gaps

A sequence gap such as:

```text
7 -> 11
```

MUST NOT automatically be interpreted as evidence that statements 8, 9, and 10 exist.

It MAY indicate missing evidence under a source profile that promises contiguous sequencing.

### 11.5 Equal sequence values

Two materially different lifecycle statements in the same comparison domain with the same non-null sequence value constitute a sequence conflict.

A processor SHOULD report:

```text
STATUS_SEQUENCE_CONFLICT
```

unless an applicable status profile explicitly permits the situation.

### 11.6 Sequence rollback

If an evaluator previously observed an accepted higher sequence and later receives only a lower sequence from the same comparison domain, it SHOULD surface potential rollback or stale evidence.

It MUST NOT silently present the lower sequence as a newer status view.

### 11.7 Sequence does not prove completeness

The largest known sequence value does not prove that no larger sequence exists.

A current-status conclusion still depends on freshness and source-coverage semantics.

### 11.8 Timestamp and sequence disagreement

If producer-declared `effectiveAt` ordering conflicts with source-local sequence ordering, both facts MUST remain visible.

OLP core defines no universal precedence between them.

A source-specific profile MAY define which field controls issuer-declared ordering.

---

## 12. Scope Semantics

### 12.1 Null scope

A null `scope` means the producer did not declare a narrower application scope.

It does not mean the statement is accepted globally.

### 12.2 URI scope

A non-null scope is an exact absolute URI.

Examples might identify:

- a production environment;
- a geographic or legal regime;
- an authentication use;
- a signing use;
- a payment context;
- a specific service; or
- another lifecycle domain.

### 12.3 Exact-match baseline

OLP core lifecycle processing uses exact scope matching.

A scope URI MUST NOT be treated as a wildcard, prefix, hierarchy, or namespace ancestor unless a domain specification explicitly defines such semantics.

### 12.4 Scoped events do not leak into other scopes

A suspension asserted for:

```text
https://example.org/scopes/production-signing
```

MUST NOT automatically be applied to:

```text
https://example.org/scopes/test-signing
```

or another scope.

### 12.5 Unknown scope semantics

If an application requires semantic interpretation of a scope URI it does not understand, the relevant lifecycle evaluation SHOULD be `UNSUPPORTED` or `INDETERMINATE` rather than silently broadening or ignoring the scope.

### 12.6 Scope and native mechanisms

A native status mechanism MAY define its own scope model.

Adapters MUST preserve that model sufficiently to avoid treating a scoped native revocation as globally equivalent or vice versa.

---

## 13. Effective Time and Temporal Evidence

### 13.1 Producer-declared semantic time

`effectiveAt` is part of the immutable status assertion.

It can express statements such as:

```text
"this key should be treated as compromised from 2026-08-01T12:00:00Z"
```

or:

```text
"this grant suspension is effective from 2026-09-01T00:00:00Z"
```

### 13.2 Backdating

A status producer can sign an `effectiveAt` value in the past.

Therefore the value alone cannot prove that the status record existed in the past.

### 13.3 Future effective time

A status statement MAY declare an effective time in the future.

A current evaluator SHOULD distinguish:

```text
STATUS_EVENT_NOT_YET_EFFECTIVE
```

from malformed or invalid evidence.

### 13.4 Null effective time

A null effective time means the producer did not assert a precise semantic effective time in the lifecycle statement.

It MUST NOT be replaced implicitly with:

- record arrival time;
- proof `created` time;
- local system time; or
- resolver retrieval time.

An application MAY use those values under explicit local policy while reporting the inference.

### 13.5 Independent temporal evidence

Independent time evidence MAY include:

- RFC 3161 timestamp tokens;
- transparency-log evidence;
- ledger or blockchain anchoring;
- countersigned archival evidence;
- evidence-record systems;
- independently witnessed publication; or
- future time-evidence mechanisms.

Such evidence can establish stronger propositions about when a lifecycle record existed.

### 13.6 Historical compromise reasoning

Suppose:

```text
Proof P.created = 2026-01-01
Compromise effectiveAt = 2026-02-01
```

Without independent evidence that P existed before the compromise, OLP MUST NOT conclude that P safely predates compromise.

A holder of compromised private key material can backdate new proofs.

### 13.7 Historical status reasoning

Likewise, a lifecycle record claiming:

```text
effectiveAt = 2026-01-01
```

does not prove that relying parties could have known or acted on that status on January 1.

Discovery/publication time and semantic effective time are distinct.

---

## 14. Next Update and Freshness Signaling

### 14.1 Meaning

`nextUpdate` is a source-declared freshness signal.

It is conceptually similar to status mechanisms that indicate when a status response or list is expected to be refreshed.

### 14.2 Not an inverse event

If:

```text
nextUpdate = T
```

and T passes, the lifecycle event does not reverse automatically.

Instead, evidence intended for a current-status decision may become stale.

### 14.3 Null next update

A null `nextUpdate` means that this OLP status statement does not itself declare a refresh deadline.

It does **not** mean:

- the statement is fresh forever;
- the statement is current forever; or
- no future status event exists.

### 14.4 Local freshness policy

An application MAY require evidence newer than a local maximum age even when `nextUpdate` is null or later.

### 14.5 Source-declared stale status

If a trusted local clock indicates that current time is later than an accepted statement's non-null `nextUpdate`, a current-status evaluator SHOULD report:

```text
STALE_BY_SOURCE
```

unless fresher accepted evidence supersedes the concern.

### 14.6 Observation time

A collector SHOULD retain the local observation or retrieval time of externally obtained status evidence.

Observation time is processing provenance.

It MUST NOT be silently inserted into the immutable lifecycle record as though the status producer signed it.

### 14.7 Freshness and offline bundles

An offline evidence bundle may contain perfectly valid historical lifecycle evidence that is not fresh enough for a current decision.

The correct result can therefore be:

```text
recordConformance = CONFORMING
proofValidity     = VALID
freshness         = STALE
currentStatus     = INDETERMINATE
```

---

## 15. Expiration and Intrinsic Validity

### 15.1 Intrinsic validity belongs to the target specification

If another OLP profile defines:

```text
validUntil
expires
notAfter
```

that value remains part of the target's own semantics.

### 15.2 No lifecycle event required for natural expiration

A target can cease to be temporally applicable because its intrinsic validity interval ended even when no lifecycle-status record exists.

### 15.3 Expiration is not revocation

Expiration generally means an intended validity interval ended naturally.

Revocation is an explicit lifecycle assertion withdrawing intended reliance.

Applications MUST NOT collapse those concepts when historical meaning matters.

### 15.4 Short-lived targets

Some ecosystems intentionally rely on short validity periods rather than revocation distribution.

OLP MUST be able to represent:

```text
statusMechanism = NONE_AVAILABLE_BY_DESIGN
```

or an equivalent external processing result without treating the target as malformed.

### 15.5 Expired proof metadata

Specification 0004 proof `expires` remains proof metadata.

A cryptographically valid but expired proof can still be represented as cryptographically valid with temporal applicability expired.

Lifecycle records do not overwrite that distinction.

---

## 16. Event Combination and Non-State-Machine Semantics

### 16.1 Why OLP does not define one universal state machine

Different target categories have incompatible lifecycle rules.

For example:

- a verification method can be retired but historically verifiable;
- an account can be suspended and resumed;
- a cryptosuite can be deprecated but still supported;
- an authority grant can expire naturally;
- a proof can be withdrawn from reliance without becoming mathematically invalid;
- a compromised key may later be recovered operationally but historical uncertainty remains.

A single global state machine would encode domain policy into the protocol core.

### 16.2 Resume only addresses suspension

Core `resume` MUST be interpreted only as a producer assertion that an applicable suspension no longer applies.

### 16.3 Activate is not resurrection

Core `activate` MUST NOT be interpreted as a universal reinstatement after revocation, compromise, retirement, or deprecation.

If a domain permits formal reinstatement after revocation, it SHOULD define an explicit extension event with precise semantics.

### 16.4 Revocation correction

If a revocation statement was erroneous, appropriate mechanisms include:

- a `corrects` relationship under Specification 0005;
- a `disputes` relationship;
- a `supersedes` relationship;
- a domain-defined reinstatement event; or
- external native status correction semantics.

The erroneous revocation record remains immutable evidence.

### 16.5 Multiple simultaneous dimensions

A target can legitimately have multiple lifecycle dimensions at once.

For example:

```text
proof cryptographic validity = VALID
proof reliance status        = REVOKED_BY_ISSUER
verification method status   = RETIRED
cryptosuite status            = DEPRECATED
```

A conforming implementation MUST be capable of preserving such distinctions.

---

## 17. Lifecycle Evidence Collection

### 17.1 Collection is separate from evaluation

Collectors obtain evidence.

Evaluators interpret supplied evidence.

The same evaluator may be used with:

- a local archive;
- a remote resolver;
- a status list cache;
- a certificate store;
- a transparency-log client;
- a bundle supplied by another participant; or
- no network at all.

### 17.2 No implicit graph crawling

A generic lifecycle evaluator MUST NOT automatically crawl arbitrary references, URLs, or graph edges merely because they appear in untrusted evidence.

### 17.3 Explicit resolver policy

Network-capable collectors MUST apply explicit security policy for:

- allowed URI schemes;
- allowed hosts;
- redirects;
- private-network access;
- authentication;
- TLS;
- response size;
- decompression limits;
- timeouts;
- caching;
- content types; and
- recursion depth.

### 17.4 Supplied evidence first

Applications SHOULD be able to provide lifecycle evidence directly to the evaluator.

This enables deterministic offline testing and archival verification.

### 17.5 Collection provenance

A collector SHOULD retain:

- source identifier;
- retrieval URI where applicable;
- observation time;
- cache metadata;
- native status-mechanism type;
- response identity or digest where practical; and
- any source authentication result.

Collection provenance does not automatically become part of the lifecycle record itself.

---

## 18. Current-Status Evaluation

### 18.1 Inputs

A current-status evaluator takes, conceptually:

```text
target
lifecycleEvidence[]
proofResults[]
sourceAuthorityEvidence[]
externalStatusEvidence[]
evaluationTime
requiredScope?
freshnessPolicy
sourcePolicy
localLifecyclePolicy
```

### 18.2 Baseline procedure

A conforming evaluator SHOULD perform the following logical stages:

1. validate the target;
2. validate each lifecycle-status record structurally;
3. verify or ingest the proof result for each lifecycle-status record;
4. confirm target equality;
5. process critical qualifiers;
6. evaluate proof purpose;
7. evaluate named status-authority binding where required;
8. evaluate whether each source is accepted for the target and event;
9. apply exact scope matching or explicit domain scope semantics;
10. classify effective-time applicability;
11. evaluate source-local sequence information;
12. evaluate source-supplied `nextUpdate` and local freshness rules;
13. integrate native external status evidence without flattening unsupported distinctions;
14. detect conflicts, equivocation, rollback, and missing prerequisites;
15. determine evidence completeness or coverage where possible;
16. produce a structured lifecycle evidence summary; and
17. optionally apply an explicitly named local policy to derive an operational state.

### 18.3 No mandatory collapsed state

Steps 1–16 are OLP lifecycle evidence processing.

Step 17 is policy-dependent.

An implementation MUST NOT imply that a policy-derived `ACTIVE` or `REVOKED` result is an OLP-universal truth.

### 18.4 Fail-closed integration

For security-sensitive authorization decisions, an application SHOULD fail closed when required lifecycle dimensions are:

```text
UNSUPPORTED
UNAVAILABLE
STALE
INCOMPLETE
CONFLICTING
INDETERMINATE
NOT_EVALUATED
```

unless explicit local policy says otherwise.

### 18.5 Positive status requires positive semantics

An evaluator MUST NOT report a protocol-derived positive status merely because no accepted negative lifecycle record was found in an incomplete evidence set.

### 18.6 Evaluation time

Current-status evaluation SHOULD use an explicit `evaluationTime` supplied by the application or trusted runtime environment.

The evaluator SHOULD report that time in result provenance.

---

## 19. Historical-Status Evaluation

### 19.1 Historical question

A historical evaluation asks a question such as:

> What accepted lifecycle evidence supports conclusions about target T at time H?

### 19.2 Stronger evidence requirements

Historical evaluation may require more than current evaluation because later-compromised signing material can create backdated statements.

### 19.3 Independent time

Where the conclusion depends on proving that evidence existed before or after another event, the evaluator SHOULD require independent temporal evidence rather than relying solely on producer-declared timestamps.

### 19.4 Historical source status

The evaluator SHOULD distinguish:

```text
source was accepted at H
source is accepted now
source key was valid at H
source key is revoked now
```

These can differ.

### 19.5 Later revocation does not erase earlier cryptography

A proof can remain mathematically valid even when its verification method is later revoked or compromised.

### 19.6 Historical completeness

A historical evaluator MUST NOT claim a complete status view unless the relevant status mechanism provides evidence supporting completeness for the historical interval.

An arbitrary subset of OLP lifecycle records cannot establish that no additional historical records existed.

### 19.7 Archival evidence

Applications performing long-term historical evaluation SHOULD preserve:

- original lifecycle records;
- original proofs;
- verification material;
- native status artifacts;
- relevant status-source certificates or credentials;
- independent timestamps;
- algorithm-policy evidence where needed; and
- archival renewal evidence.

---

## 20. Completeness and Coverage

### 20.1 Open-world default

An ordinary collection of OLP lifecycle-status records is open-world evidence.

It does not imply that the collection contains every status event ever issued.

### 20.2 Coverage states

A lifecycle evaluator SHOULD distinguish at least:

```text
COMPLETE
INCOMPLETE
UNKNOWN
NOT_EVALUATED
```

for source coverage where applicable.

### 20.3 Complete requires an explicit mechanism

`COMPLETE` MUST NOT be asserted merely because:

- a database query returned no more rows;
- a bundle contained no more records;
- a resolver returned HTTP success;
- sequence values appear contiguous; or
- no revocation was found.

Completeness requires semantics from an accepted source or mechanism that actually supports such a conclusion.

### 20.4 Native complete-status mechanisms

Examples of mechanisms that can provide stronger coverage semantics include:

- certificate revocation lists within their defined issuer/scope/time semantics;
- authenticated online certificate-status responses;
- authenticated bitstring status lists;
- signed registry snapshots;
- append-only transparency/log checkpoints; or
- domain-defined complete status snapshots.

Each mechanism retains its own semantics.

### 20.5 Partial bundles

An `EvidenceBundle` under Specification 0005 MAY contain only part of the relevant lifecycle graph.

The bundle MUST NOT be treated as complete merely because it is internally well-formed.

### 20.6 Negative evidence from complete mechanisms

A complete native mechanism MAY support a negative-status proposition such as “not listed as revoked within this issuer's current CRL scope.”

Adapters MUST preserve the exact strength and limits of that proposition.

They MUST NOT automatically convert it to universal `ACTIVE` or `TRUSTED`.

---

## 21. Freshness and Staleness

### 21.1 Freshness is contextual

Different applications need different freshness guarantees.

A software-package mirror may tolerate hours.

A payment authorization system may require seconds or minutes.

An archival historical evaluation may care about evidence age differently.

### 21.2 Source freshness and local freshness

An evaluator MAY consider:

- `nextUpdate`;
- native `thisUpdate` / `nextUpdate` values;
- HTTP/cache metadata;
- observation time;
- source sequence advancement;
- source-specific validity intervals; and
- local maximum-age policy.

### 21.3 Stale is not invalid

Stale status evidence can remain cryptographically authentic and historically useful.

Therefore:

```text
statusEvidenceCryptography = VALID
freshness                  = STALE
```

is a legitimate result.

### 21.4 Unknown freshness

If evidence has no trusted or policy-usable freshness signal, an evaluator SHOULD report:

```text
freshness = UNKNOWN
```

rather than silently treating it as fresh.

### 21.5 Cache replay

Caches MUST NOT present old lifecycle evidence as current without exposing freshness and observation metadata.

### 21.6 Offline use

Offline evaluation SHOULD report the last known observation or source refresh information where available.

It SHOULD avoid presenting stale snapshots as live status.

---

## 22. Conflict, Equivocation, and Rollback

### 22.1 Conflict classes

Lifecycle evidence can conflict because of:

- multiple authorities;
- multiple verification methods for one authority;
- equal source-local sequence values with different statements;
- disagreement between OLP and native status systems;
- scope ambiguity;
- correction/dispute evidence;
- resolver split views;
- status-source compromise; or
- stale versus newer evidence.

### 22.2 Preserve material conflicts

A conforming evaluator MUST expose material conflicts relevant to the requested conclusion.

### 22.3 No majority vote

OLP does not resolve conflicts by counting records, signatures, authorities, or graph edges.

### 22.4 Same-authority equivocation

If the same accepted status authority produces incompatible statements for the same target/scope/sequence domain, the evaluator SHOULD report potential equivocation.

### 22.5 Split-view detection

Where a status source supports transparency or checkpoint comparison, applications SHOULD retain evidence that can detect inconsistent views.

OLP core does not require one transparency mechanism.

### 22.6 Rollback detection

If a collector has durable evidence of a newer accepted sequence or snapshot and receives an older one, it SHOULD report potential rollback.

### 22.7 Conflict is not automatically target invalidity

A status conflict means the lifecycle conclusion is disputed or indeterminate.

It does not automatically imply that the target's content or proof is cryptographically invalid.

---

## 23. Corrections, Disputes, and Supersession

### 23.1 Use evidence relationships

Specification 0005 relationship records SHOULD be used when one lifecycle record:

- corrects another;
- disputes another;
- supersedes another;
- references supporting evidence; or
- anchors external status evidence.

### 23.2 Correction does not delete original status

A corrected lifecycle record remains independently addressable by Record Identity.

### 23.3 Accepted correction requires accepted authority

A `corrects` relationship does not automatically make the correction authoritative.

The correcting record and relationship proofs must be evaluated under applicable source policy.

### 23.4 Revocation correction

A domain that permits revocation correction SHOULD make that semantic explicit.

It MUST NOT rely on a bare later `activate` or `resume` event to erase the prior revocation universally.

### 23.5 Dispute is not reversal

A dispute is evidence that the status assertion is contested.

It is not automatically the opposite lifecycle event.

---

## 24. Interoperability with Native Status Mechanisms

### 24.1 General rule

OLP SHOULD interoperate with established status mechanisms before inventing replacements.

### 24.2 X.509 CRLs

X.509 PKI defines Certificate Revocation Lists with issuer, scope, timing, and revocation semantics.

An OLP adapter MUST preserve those semantics.

In particular, absence of a serial number from a CRL is meaningful only within the CRL's issuer, scope, validity/freshness, and processing rules.

### 24.3 OCSP

OCSP defines status responses such as:

```text
good
revoked
unknown
```

An adapter MUST preserve `unknown` as an inability to determine status from that responder.

It MUST NOT silently convert `unknown` to `good` or `revoked`.

Likewise, an OCSP `good` response MUST NOT be inflated into claims that the certificate was necessarily issued correctly, is within every validity interval, or is trusted for the relying application's purpose.

### 24.4 W3C Bitstring Status List

W3C Bitstring Status List defines privacy-conscious, space-efficient status-list mechanisms for credential status such as revocation and suspension.

An OLP implementation MAY evaluate such status natively and expose the result in lifecycle-processing provenance.

It SHOULD NOT expand a compact status list into one permanent globally published OLP record per credential unless the application has a clear reason and has considered privacy consequences.

### 24.5 DID and controlled-identifier mechanisms

If a DID or controlled-identifier method defines verification-method lifecycle or controller semantics, an implementation SHOULD evaluate those native semantics directly.

An OLP lifecycle record MAY carry an additional portable assertion but MUST NOT silently override native method semantics.

### 24.6 Short-lived credentials and no-revocation mechanisms

Some systems intentionally publish no revocation information for short-lived credentials or certificates.

An adapter SHOULD distinguish:

```text
NO_REVOCATION_MECHANISM_BY_DESIGN
```

from:

```text
STATUS_SOURCE_UNAVAILABLE
```

or:

```text
STATUS_UNKNOWN
```

### 24.7 Native signed artifacts

Where practical, applications SHOULD preserve the original signed native status artifact rather than only storing a translated OLP summary.

A translated OLP lifecycle record is an attestation by its producer unless the original native signature semantics are independently preserved and verified.

### 24.8 Lossless projection requirement

An adapter that projects native status into OLP structured results MUST preserve all distinctions material to security and policy.

If it cannot do so, it SHOULD expose the native result as opaque external evidence rather than manufacture a misleading OLP equivalent.

### 24.9 External status evidence as graph evidence

Applications MAY represent links to external status artifacts using Specification 0005 relationship records such as:

```text
references
anchors
derivesFrom
```

The relationship does not validate the external artifact automatically.

---

## 25. Interaction with Specification 0006 Status Profiles

### 25.1 Existing profiles remain valid

Specification 0006 defines:

- `AuthorityStatusStatementV1`; and
- `VerificationMethodStatusStatementV1`.

Those records remain valid immutable OLP records under their own profile definitions.

This specification does not retroactively change their Record Identities.

### 25.2 Generalization

`LifecycleStatusStatementV1` provides a generic cross-domain lifecycle profile.

New applications MAY choose the generic lifecycle profile where domain-specific status fields are unnecessary.

### 25.3 Authority grant mapping

An Authority Status record targeting an Authority Grant can be conceptually projected as:

```text
targetType = record
reference  = RecordRef(authorityGrant)
```

with events such as:

```text
suspend
resume
revoke
```

### 25.4 Verification-method mapping

A Verification Method Status record can be conceptually projected as:

```text
targetType = verificationMethod
reference  = exact verificationMethod URI
```

with events such as:

```text
retire
suspend
resume
revoke
compromise
```

### 25.5 Projection is not identity equivalence

A projected `LifecycleStatusStatementV1` and an existing Specification 0006 status record are **different records** unless they are literally the same underlying Specification 0003 record content, which they ordinarily are not.

An implementation MUST NOT claim that a newly generated generic lifecycle record has the Record Identity of an older specialized record.

### 25.6 No duplicate status required

Implementations do not need to duplicate every Specification 0006 status record into Specification 0007 form.

Evaluators SHOULD be able to ingest supported lifecycle evidence from both profiles.

### 25.7 Domain-specific profile wins on domain-specific semantics

Where Specification 0006 defines more specific semantics for authority or verification-method lifecycle, those profile semantics remain applicable.

The generic lifecycle layer MUST NOT weaken them.

---

## 26. Verification-Method Lifecycle

### 26.1 Cryptographic validity remains separate

For a proof P signed by verification method K:

```text
Verify(P, K) = VALID
```

may coexist with lifecycle evidence:

```text
K = RETIRED
K = REVOKED
K = COMPROMISE_REPORTED
```

### 26.2 Rotation

Key rotation commonly produces:

```text
old key: retire
new key: activate
```

but OLP does not mandate that exact sequence.

A new key does not erase evidence produced by the old key.

### 26.3 Compromise

If compromise timing affects historical reliance, independent temporal evidence SHOULD be considered.

### 26.4 Key-status source

Applications SHOULD prefer status semantics native to the verification-method ecosystem when available and sufficiently authoritative.

### 26.5 No key-type inference

Lifecycle processing MUST NOT infer key type, cryptosuite, controller identity, or authority merely from a status event.

---

## 27. Authority-Grant Lifecycle

### 27.1 Grant record immutability

Authority grants under Specification 0006 remain immutable.

### 27.2 Suspension

A lifecycle `suspend` targeting the grant record can express temporary withdrawal from reliance.

### 27.3 Resume

A lifecycle `resume` can express the end of suspension.

It does not automatically override an accepted revocation event.

### 27.4 Revocation

A lifecycle `revoke` can express withdrawal of the grant according to accepted status-authority semantics.

### 27.5 Intrinsic expiration

If the grant's `validUntil` has passed, the grant can be temporally inapplicable even without lifecycle revocation evidence.

### 27.6 Delegation

If a parent grant becomes suspended, revoked, expired, or otherwise inapplicable, descendant authority conclusions may be affected according to Specification 0006 and local policy.

The descendant records themselves remain immutable.

### 27.7 Historical authority

A later revocation of a grant does not automatically prove that earlier actions were unauthorized.

Historical authority evaluation requires the relevant time, status, delegation, and evidence context.

---

## 28. Lifecycle Evidence Graph Projection

### 28.1 Lifecycle records are nodes

A lifecycle-status record is an ordinary record node in the evidence graph.

### 28.2 Target edge

A graph view MAY project:

```text
LifecycleStatusRecord --statusOf--> LifecycleTarget
```

for queries and visualization.

This projected edge is derived from the immutable statement.

### 28.3 Relationship to corrections

A correction can be represented as:

```text
CorrectionRecord --corrects--> LifecycleStatusRecord
```

### 28.4 Relationship to disputes

A dispute can be represented as:

```text
DisputeRecord --disputes--> LifecycleStatusRecord
```

### 28.5 Relationship to temporal evidence

Independent time evidence can be linked using `anchors` or another defined relationship.

### 28.6 Cycles

Lifecycle and correction/dispute relationships can form cycles.

Processors MUST apply the cycle and resource-limit rules of Specification 0005.

### 28.7 No graph reachability status

The existence of any path to a `revoke` record MUST NOT automatically make a target revoked.

The lifecycle statement, proof, status authority, scope, and policy must be evaluated explicitly.

---

## 29. Resolution, Caching, and Offline Processing

### 29.1 Resolution boundary

Status resolution is an application dependency.

The generic lifecycle evaluator MUST accept pre-resolved evidence.

### 29.2 No implicit network access

Receiving a lifecycle target URI or qualifier MUST NOT automatically trigger network access.

### 29.3 Cache keys

A cache SHOULD avoid conflating status across different:

- targets;
- scopes;
- status authorities;
- native status mechanisms; and
- policy profiles.

### 29.4 Cache freshness

Caches SHOULD retain:

- observation time;
- source-provided next-update information;
- ETag/version/digest where applicable;
- native response validity metadata; and
- source sequence information.

### 29.5 Cache poisoning

Cached status artifacts MUST be authenticated and validated according to their source mechanism before being treated as accepted evidence.

### 29.6 Offline packages

Offline packages SHOULD include enough provenance for the consumer to distinguish:

```text
historically valid evidence
```

from:

```text
fresh current status
```

### 29.7 Resolution failure

Failure to obtain current lifecycle evidence is not equivalent to:

```text
ACTIVE
```

nor:

```text
REVOKED
```

The correct result is generally `UNAVAILABLE`, `UNKNOWN`, or `INDETERMINATE` depending on the stage.

---

## 30. Structured Lifecycle Processing Results

### 30.1 No overloaded `status`

An API returning only:

```text
status = "valid"
```

for lifecycle processing is NOT RECOMMENDED.

It hides whether “valid” refers to record syntax, proof cryptography, source authority, freshness, target applicability, or policy.

### 30.2 Recommended dimensions

A lifecycle evaluator SHOULD expose dimensions such as:

```text
recordConformance
targetConformance
eventSupport
proofResults
proofPurposeStatus
statusAuthorityBinding
statusSourceAcceptance
scopeStatus
effectiveTimeStatus
sequenceStatus
freshnessStatus
coverageStatus
nativeStatusResults
acceptedEvents
conflicts
temporalEvidenceStatus
warnings
errors
policyDecision
policyProfile
```

### 30.3 Common processing states

Where applicable, implementations SHOULD distinguish:

```text
CONFORMING
MALFORMED
SUPPORTED
UNSUPPORTED
VALID
INVALID
MATCH
MISMATCH
ACCEPTED
NOT_ACCEPTED
AVAILABLE
UNAVAILABLE
FRESH
STALE
UNKNOWN
COMPLETE
INCOMPLETE
CONSISTENT
CONFLICTING
SATISFIED
NOT_SATISFIED
INDETERMINATE
NOT_EVALUATED
```

### 30.4 Accepted event summary

An evaluator MAY expose a non-collapsed event summary such as:

```text
acceptedEvents = [
    {
        event: "retire",
        source: "did:example:alice",
        sequence: 8,
        effectiveAt: "2026-08-01T00:00:00Z"
    },
    {
        event: "compromise",
        source: "did:example:security-office",
        sequence: null,
        effectiveAt: "2026-08-03T10:00:00Z"
    }
]
```

### 30.5 Policy result

If a local policy collapses lifecycle evidence to an operational state, the result SHOULD identify the policy.

For example:

```text
policyDecision = BLOCK_NEW_SIGNATURES
policyProfile  = https://example.org/policies/key-lifecycle-v4
```

### 30.6 No hidden default policy

Implementations SHOULD NOT expose an unlabeled policy-derived state as though OLP core produced it universally.

---

## 31. Core Reason Codes

Implementations SHOULD use stable machine-readable reason codes.

This specification defines at least the following.

### 31.1 Structural errors

```text
MALFORMED_LIFECYCLE_TARGET
UNSUPPORTED_LIFECYCLE_TARGET_TYPE
MALFORMED_LIFECYCLE_STATUS
UNSUPPORTED_LIFECYCLE_STATUS_VERSION
UNSUPPORTED_LIFECYCLE_EVENT
UNSUPPORTED_CRITICAL_LIFECYCLE_QUALIFIER
DUPLICATE_LIFECYCLE_QUALIFIER
INVALID_LIFECYCLE_CRITICAL_DECLARATION
INVALID_LIFECYCLE_SEQUENCE
INVALID_LIFECYCLE_SCOPE
INVALID_LIFECYCLE_TIME
```

### 31.2 Target errors

```text
LIFECYCLE_TARGET_MISMATCH
LIFECYCLE_TARGET_UNAVAILABLE
LIFECYCLE_TARGET_IDENTITY_MISMATCH
```

### 31.3 Proof and attribution errors

```text
STATUS_PROOF_MISSING
STATUS_PROOF_INVALID
STATUS_PROOF_UNVERIFIABLE
STATUS_PURPOSE_MISMATCH
STATUS_AUTHORITY_BINDING_NOT_ESTABLISHED
STATUS_SOURCE_NOT_ACCEPTED
```

### 31.4 Ordering and conflict results

```text
STATUS_SEQUENCE_CONFLICT
STATUS_SEQUENCE_ROLLBACK
STATUS_ORDERING_INDETERMINATE
STATUS_EVIDENCE_CONFLICT
STATUS_SOURCE_EQUIVOCATION
```

### 31.5 Temporal and freshness results

```text
STATUS_EVENT_NOT_YET_EFFECTIVE
STATUS_EFFECTIVE_TIME_UNVERIFIED
STATUS_NEXT_UPDATE_EXCEEDED
STATUS_EVIDENCE_STALE
STATUS_FRESHNESS_UNKNOWN
INDEPENDENT_TIME_EVIDENCE_REQUIRED
HISTORICAL_STATUS_NOT_ESTABLISHED
```

### 31.6 Coverage and availability results

```text
STATUS_EVIDENCE_INCOMPLETE
STATUS_COVERAGE_UNKNOWN
STATUS_SOURCE_UNAVAILABLE
STATUS_SOURCE_UNSUPPORTED
NATIVE_STATUS_UNKNOWN
NO_REVOCATION_MECHANISM_BY_DESIGN
```

### 31.7 Scope results

```text
STATUS_SCOPE_MATCH
STATUS_SCOPE_MISMATCH
STATUS_SCOPE_UNSUPPORTED
```

Reason codes describe processing conditions.

They do not establish universal truth or policy outcome.

---

## 32. Lifecycle Status Production Algorithm

### 32.1 Inputs

A lifecycle-status producer conceptually takes:

```text
target
event
statusAuthority?
effectiveAt?
sequence?
scope?
nextUpdate?
reason?
qualifiers
critical
record-production inputs
proof-production inputs?
```

### 32.2 Procedure

A conforming producer MUST:

1. construct a valid `LifecycleTargetV1`;
2. select a core or globally unambiguous extension event;
3. validate `statusAuthority` when non-null;
4. validate `effectiveAt` when non-null;
5. validate `sequence` when non-null;
6. reject non-null `sequence` when `statusAuthority` is null;
7. validate `scope` when non-null;
8. validate `nextUpdate` when non-null;
9. validate `reason` when non-null;
10. validate qualifier keys;
11. validate critical declarations;
12. construct exactly one `LifecycleStatusStatementV1`;
13. place it into an ordinary Specification 0003 record;
14. compute ordinary Record Identity;
15. if attribution is intended, create one or more detached proofs under Specification 0004; and
16. normally use `proofPurpose = assertion` for direct status assertion.

### 32.3 Producer MUST NOT mutate target

Producing a lifecycle-status record MUST NOT modify the target object.

### 32.4 Producer SHOULD avoid unsupported semantics

A producer SHOULD NOT issue extension lifecycle events, scopes, or qualifiers without publishing stable semantics sufficient for independent implementation.

### 32.5 Source sequence discipline

A producer using non-null sequence values SHOULD define and maintain a durable monotonic sequence discipline for the applicable authority/target/scope domain.

A producer SHOULD NOT reuse a sequence number for materially different lifecycle statements.

---

## 33. Lifecycle Status Processing Algorithm

### 33.1 Inputs

A lifecycle-status processor conceptually takes:

```text
lifecycleStatusRecord
proofs?
resolvedTarget?
resolvedVerificationMethods?
statusAuthorityEvidence?
```

### 33.2 Procedure

A conforming processor MUST or SHOULD, as applicable:

1. validate the enclosing OLP record under Specification 0003;
2. confirm semantic content conforms to `LifecycleStatusStatementV1`;
3. validate target shape;
4. validate event identifier;
5. validate authority, time, sequence, scope, next-update, reason, qualifiers, and critical array;
6. identify unsupported critical semantics;
7. verify supplied proofs under Specification 0004 when requested;
8. report proof purpose independently;
9. if a concrete target object is supplied, recompute and compare target identity where applicable;
10. evaluate status-authority binding when requested and evidence is available;
11. preserve all provenance; and
12. return a structured processing result.

### 33.3 Structural validity is not lifecycle acceptance

A conforming lifecycle-status record can be structurally valid while its source is not accepted.

### 33.4 Cryptographic validity is not lifecycle acceptance

A valid assertion proof can coexist with:

```text
statusSourceAcceptance = NOT_ACCEPTED
```

### 33.5 Unsupported event is not false event

If an extension event is unknown, the processor SHOULD report unsupported semantics rather than claiming the asserted event is false.

---

## 34. Lifecycle Evaluation Algorithm

### 34.1 Evidence set

A lifecycle evaluator operates over a set of individually processed lifecycle evidence.

### 34.2 Evidence identity

Duplicate transmission of the same lifecycle-status record does not create additional protocol weight.

Processors SHOULD deduplicate by Record Identity where useful.

### 34.3 Source filtering

The evaluator MUST NOT treat unaccepted sources as authoritative merely because their proofs verify.

### 34.4 Scope filtering

Only lifecycle statements applicable to the requested scope SHOULD participate in a scoped operational conclusion.

Unscoped statements require local policy about whether they apply to the requested scope.

### 34.5 Temporal filtering

The evaluator SHOULD report whether each event is:

```text
EFFECTIVE
NOT_YET_EFFECTIVE
EFFECTIVE_TIME_UNKNOWN
```

relative to the supplied evaluation time and applicable temporal policy.

### 34.6 Sequence processing

Comparable sequence values MAY establish source-declared order.

The evaluator MUST preserve conflicts and gaps relevant to local completeness assumptions.

### 34.7 Freshness processing

The evaluator SHOULD combine source-provided and local freshness semantics without rewriting the cryptographic status of the evidence.

### 34.8 Native status processing

Native external status results SHOULD remain typed and provenance-preserving.

### 34.9 Conflict processing

The evaluator MUST surface material accepted conflicts.

### 34.10 Coverage processing

The evaluator MUST NOT claim complete negative status without a mechanism supporting completeness.

### 34.11 Local operational state

A local lifecycle policy MAY consume the structured evidence result and derive an operational state.

That state is outside universal OLP semantics.

---

## 35. Privacy Considerations

### 35.1 Status checking can reveal interest

Online status queries can reveal which credentials, keys, accounts, grants, or records a verifier is evaluating.

Applications SHOULD minimize unnecessary direct queries to status authorities.

### 35.2 Bulk and privacy-preserving status mechanisms

Where suitable, applications SHOULD consider privacy-preserving bulk status mechanisms, local caches, content distribution, or other techniques that reduce per-target query correlation.

### 35.3 Stable target identifiers enable correlation

Repeated use of stable Principal Identifiers, Verification Method Identifiers, Record Identities, and Proof Identities can enable cross-context correlation.

Lifecycle bundles SHOULD contain only evidence necessary for the relying purpose.

### 35.4 Reason values can reveal sensitive information

A reason URI might reveal:

- employment termination;
- suspected key compromise;
- fraud investigation;
- legal restriction;
- sanctions or compliance action;
- device theft; or
- other sensitive circumstances.

Producers SHOULD minimize reason disclosure.

### 35.5 Timing metadata can reveal activity

`effectiveAt`, `nextUpdate`, sequence advancement, and observation times can reveal operational timing.

Applications SHOULD consider whether exact timing is necessary.

### 35.6 Status archives can create permanent dossiers

Because OLP lifecycle evidence is immutable, indiscriminate publication can preserve sensitive historical status indefinitely.

Applications SHOULD consider data minimization, access control, selective sharing, and jurisdictional obligations.

### 35.7 Do not publish one record per credential without need

At large scale, one public lifecycle record per credential or account can create privacy and indexing harms.

Native privacy-preserving list mechanisms may be more appropriate.

### 35.8 Resolver privacy

Resolvers and collectors SHOULD avoid exposing unnecessary target identifiers to unrelated third parties.

### 35.9 Cache privacy

Shared caches should avoid leaking sensitive status query histories across tenants or users.

---

## 36. Security Considerations

### 36.1 Forged status evidence

Attackers may create false lifecycle records.

Applications MUST evaluate proofs and accepted status authority rather than trusting syntax.

### 36.2 Status-authority impersonation

Naming:

```text
statusAuthority = did:example:acme
```

does not prove the producer acts for ACME.

Identity binding must be evaluated separately.

### 36.3 Status poisoning

An attacker may flood an evidence graph with false revocation or compromise claims.

OLP MUST NOT resolve status by raw record count.

### 36.4 Stale-status replay

An attacker may replay old “active” or “good” evidence after a later revocation.

Freshness, sequence, observation provenance, and native status semantics should be evaluated.

### 36.5 Rollback attack

A malicious intermediary may hide newer sequence values or snapshots and present older lifecycle views.

Clients SHOULD retain durable high-water marks where appropriate.

### 36.6 Freeze attack

A malicious intermediary may indefinitely withhold updates while continuing to serve an old valid snapshot.

Applications SHOULD enforce freshness requirements for current security-sensitive decisions.

### 36.7 Equivocation

A status authority may present different lifecycle views to different relying parties.

Transparency, signed snapshots, shared checkpoints, or other domain mechanisms MAY mitigate this.

### 36.8 Backdated status

A compromised status-authority key can sign lifecycle records with old `effectiveAt` values.

Independent temporal evidence is required for strong historical claims.

### 36.9 Compromised status authority

A valid signature from a compromised status authority may require contextual re-evaluation.

The signature's cryptographic validity remains distinct from source trust.

### 36.10 Sequence misuse

Sequence values are not global clocks.

Comparing sequences across unrelated domains can cause incorrect status ordering.

### 36.11 Sequence collision

Reusing one sequence for incompatible statements can indicate misconfiguration or equivocation.

Processors SHOULD surface the condition.

### 36.12 Scope confusion

Ignoring a lifecycle scope can incorrectly globalize a narrow suspension or revocation.

Applications MUST preserve scope semantics relevant to reliance.

### 36.13 Event confusion

`resume` MUST NOT be treated as a universal inverse of every negative event.

`retire` MUST NOT be treated as `compromise`.

`deprecate` MUST NOT be silently treated as `revoke` unless local policy explicitly says so.

### 36.14 Target substitution

When a concrete record or proof is supplied for a lifecycle target, its identity MUST be recomputed under the applicable OLP specification and compared with the target reference.

### 36.15 URI rewriting

Verification Method and Principal URI references MUST NOT be silently rewritten before exact target comparison.

### 36.16 Resolver SSRF

Untrusted lifecycle evidence MUST NOT cause unrestricted network dereferencing.

### 36.17 Decompression attacks

Native status mechanisms that use compression can expose decompression-bomb or resource-exhaustion risks.

Collectors MUST enforce size and resource limits.

### 36.18 Status-list index abuse

List-based status mechanisms may contain invalid or attacker-controlled indexes.

Adapters MUST validate bounds and native mechanism rules.

### 36.19 Cache poisoning

Unauthenticated cached status data can produce false lifecycle decisions.

Caches must preserve source authentication.

### 36.20 Current-status false positive

The most dangerous failure mode is often incorrectly treating an incomplete or stale evidence set as positively active.

Security-sensitive applications SHOULD fail closed when status is required but not sufficiently fresh, complete, or authoritative.

### 36.21 Native-status semantic loss

Flattening OCSP `unknown`, CRL scope, or credential status-list purpose into a generic boolean can create security bugs.

Adapters MUST preserve material distinctions.

### 36.22 Status record self-reference and cycles

Lifecycle records can target other lifecycle records.

Graph processors MUST apply cycle and resource limits.

### 36.23 Malicious reason vocabularies

A reason URI can point to malicious or unavailable content.

Processors MUST NOT need to dereference reason URIs merely to preserve the status record.

### 36.24 Time source compromise

A compromised local clock can affect current/future status classification.

High-assurance systems may require independent time sources.

### 36.25 Long-term algorithm changes

Historical lifecycle proofs may use algorithms that later become deprecated.

Algorithm lifecycle and cryptographic validity must remain distinct, as required by Specification 0004.

### 36.26 No truth oracle

Lifecycle processing improves provenance and explicitness.

It does not create a universal truth oracle for whether an object “really is revoked.”

---

## 37. Conformance Classes

An implementation MAY claim conformance to one or more of the following classes.

### 37.1 Lifecycle Target Processor

A conforming Lifecycle Target Processor MUST:

- support all four core `LifecycleTargetV1` target types;
- validate exact target shapes;
- preserve exact URI strings;
- validate EvidenceRef kinds for record and proof targets;
- avoid implicit aliasing; and
- report unsupported extension target types distinctly.

### 37.2 Lifecycle Status Producer

A conforming Lifecycle Status Producer MUST:

- produce an ordinary Specification 0003 record;
- place exactly one valid `LifecycleStatusStatementV1` in semantic content;
- support all seven core lifecycle events;
- validate authority, time, sequence, scope, next-update, reason, qualifiers, and critical semantics;
- reject sequence without named `statusAuthority`;
- avoid mutating the target; and
- use ordinary detached proofs under Specification 0004 when cryptographic attribution is required.

### 37.3 Lifecycle Status Processor

A conforming Lifecycle Status Processor MUST:

- validate `LifecycleStatusStatementV1`;
- support all seven core events;
- support all four core target types;
- preserve unknown non-critical qualifiers;
- reject complete semantic processing when a critical qualifier is unsupported;
- keep proof validity separate from status-source authority;
- keep lifecycle status separate from target cryptographic validity; and
- return structured results.

### 37.4 Lifecycle Evaluator

A conforming Lifecycle Evaluator MUST:

- accept pre-resolved lifecycle evidence;
- preserve source provenance;
- preserve scope distinctions;
- preserve effective-time uncertainty;
- support source-local sequence processing;
- detect equal-sequence conflict;
- distinguish freshness from cryptographic validity;
- distinguish completeness from absence of negative evidence;
- surface material conflicts;
- avoid majority-vote status; and
- distinguish local policy results from OLP lifecycle evidence results.

### 37.5 Lifecycle Collector

A conforming Lifecycle Collector MUST:

- use explicit resolver/network policy;
- preserve observation provenance;
- preserve native status semantics;
- apply resource limits;
- avoid silent status flattening; and
- permit cached/offline evidence to be labeled with freshness state.

### 37.6 Native Status Adapter

A conforming Native Status Adapter MUST:

- identify the native mechanism;
- validate native artifacts according to that mechanism;
- preserve status distinctions material to security;
- preserve source, freshness, and scope semantics;
- avoid mapping unknown/unavailable to active; and
- expose lossy mappings as such.

### 37.7 Historical Lifecycle Evaluator

A conforming Historical Lifecycle Evaluator MUST:

- distinguish producer-declared time from independent temporal evidence;
- preserve later revocation/compromise separately from historical signature validity;
- report historical completeness limitations;
- preserve archival provenance; and
- avoid claiming historical existence based solely on backdatable signer-controlled timestamps.

---

## 38. Interoperability Test Cases

These cases test semantic interoperability.

Full Record Identity is computed by Specification 0003 and proofs are computed by Specification 0004.

### 38.1 Test Case A — Verification method retirement

Statement:

```text
[
  "OLP-LIFECYCLE-STATUS",
  1,
  ["verificationMethod", "did:example:alice#key-1"],
  "retire",
  "did:example:alice",
  "2026-08-20T00:00:00Z",
  7,
  null,
  null,
  null,
  {},
  []
]
```

Expected structural result:

```text
recordConformance   = CONFORMING
targetConformance   = CONFORMING
eventSupport        = SUPPORTED
```

A valid assertion proof from `did:example:alice#key-1` does not by itself establish that the method is authorized to speak for the principal `did:example:alice`; binding evidence is still required when the application requires that attribution.

### 38.2 Test Case B — Valid historical signature with retired key

Historical proof:

```text
cryptographicValidity = VALID
```

Accepted lifecycle event:

```text
retire
```

Expected:

```text
cryptographicValidity = VALID
lifecycleEvent        = retire
```

The processor MUST NOT rewrite the historical signature as `INVALID` solely because of retirement.

### 38.3 Test Case C — Resume does not undo revocation

Accepted events:

```text
sequence 10: revoke
sequence 11: resume
```

Expected OLP core result:

```text
acceptedEvents = [revoke, resume]
```

The evaluator MUST NOT universally conclude:

```text
ACTIVE
```

because `resume` only addresses suspension semantics.

### 38.4 Test Case D — Suspension and resume

Accepted events in one authority/target/scope sequence domain:

```text
20: suspend
21: resume
```

A local lifecycle policy MAY conclude that the suspension no longer applies.

OLP core reports the ordered accepted events and does not need to invent a mutable target state.

### 38.5 Test Case E — Sequence conflict

Two valid accepted records have identical:

```text
statusAuthority
target
scope
sequence = 42
```

but one asserts:

```text
suspend
```

and the other:

```text
activate
```

Expected:

```text
sequenceStatus = CONFLICTING
reason         = STATUS_SEQUENCE_CONFLICT
```

### 38.6 Test Case F — Different authorities, same sequence

Authority A:

```text
sequence = 9
revoke
```

Authority B:

```text
sequence = 9
activate
```

The two sequence values MUST NOT be directly compared merely because the integers are equal.

### 38.7 Test Case G — No status evidence

Input:

```text
no lifecycle records
no complete native status mechanism
```

Expected:

```text
coverage      = UNKNOWN
currentStatus = INDETERMINATE
```

The processor MUST NOT output `ACTIVE` solely from absence.

### 38.8 Test Case H — Stale status evidence

Accepted statement:

```text
nextUpdate = 2026-08-20T01:00:00Z
```

Evaluation time:

```text
2026-08-20T02:00:00Z
```

No fresher evidence is available.

Expected:

```text
freshness = STALE
reason    = STATUS_NEXT_UPDATE_EXCEEDED
```

The record and proof may remain valid.

### 38.9 Test Case I — Future effective event

Status event:

```text
effectiveAt = 2027-01-01T00:00:00Z
```

Evaluation time:

```text
2026-12-01T00:00:00Z
```

Expected:

```text
effectiveTimeStatus = NOT_YET_EFFECTIVE
reason              = STATUS_EVENT_NOT_YET_EFFECTIVE
```

### 38.10 Test Case J — Compromise and backdated proof

Proof says:

```text
created = 2026-01-01T00:00:00Z
```

Accepted lifecycle evidence says:

```text
compromise effectiveAt = 2026-02-01T00:00:00Z
```

No independent timestamp evidence exists for the proof.

Expected:

```text
proofCreatedClaimPredatesCompromise      = true
historicalExistencePredatesCompromise    = NOT_ESTABLISHED
reason                                   = INDEPENDENT_TIME_EVIDENCE_REQUIRED
```

### 38.11 Test Case K — Scope mismatch

Status event scope:

```text
https://example.org/scopes/production-signing
```

Requested scope:

```text
https://example.org/scopes/test-signing
```

Expected:

```text
scopeStatus = MISMATCH
reason      = STATUS_SCOPE_MISMATCH
```

The evaluator MUST NOT apply the event to the requested scope under core exact-match semantics.

### 38.12 Test Case L — Unknown critical qualifier

Statement includes:

```text
qualifiers = {
  "https://vendor.example/status/conditional-reinstatement": true
}

critical = [
  "https://vendor.example/status/conditional-reinstatement"
]
```

A processor that does not understand the qualifier must report:

```text
UNSUPPORTED_CRITICAL_LIFECYCLE_QUALIFIER
```

It MUST NOT silently ignore the qualifier and claim complete lifecycle interpretation.

### 38.13 Test Case M — OCSP unknown

Native OCSP result:

```text
unknown
```

Expected adapter result:

```text
nativeStatus = UNKNOWN
```

The adapter MUST NOT output:

```text
ACTIVE
```

or:

```text
REVOKED
```

solely from OCSP `unknown`.

### 38.14 Test Case N — Complete native list negative result

An accepted, fresh, authenticated native status list is complete for the relevant issuer/scope and does not mark the target as revoked.

Expected result MAY include a native-mechanism-specific conclusion such as:

```text
nativeRevocationStatus = NOT_REVOKED_WITHIN_LIST_SCOPE
coverage               = COMPLETE
```

The adapter MUST NOT inflate this to universal `TRUSTED`.

### 38.15 Test Case O — Specialized Specification 0006 record

Input is a valid `VerificationMethodStatusStatementV1` from Specification 0006.

A Lifecycle Evaluator supporting Specification 0006 SHOULD ingest it as lifecycle evidence without rewriting the record into a new `LifecycleStatusStatementV1` or changing Record Identity.

### 38.16 Test Case P — Mistaken revocation correction

Evidence graph contains:

```text
R1: lifecycle revoke(target)
R2: correction statement
R3: R2 corrects R1
```

Expected:

```text
R1 remains addressable
R2 remains addressable
R3 remains addressable
```

Whether the correction restores operational reliance depends on accepted source authority and local policy.

---

## 39. Design Summary

OLP v1 lifecycle architecture is:

```text
                        Immutable Target
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
      Status S1           Status S2           Status S3
      suspend              retire             compromise
          |                   |                   |
          v                   v                   v
       Proof P1            Proof P2            Proof P3
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                    Authority / source evidence
                              |
                              v
                   Structured lifecycle result
                              |
                  +-----------+-----------+
                  |           |           |
                  v           v           v
              freshness    conflicts    coverage
                  |           |           |
                  +-----------+-----------+
                              |
                              v
                       Local policy
```

The core design decisions are:

1. **Lifecycle is additive evidence, not mutation.**
2. **A lifecycle event is an ordinary immutable OLP record.**
3. **Records, proofs, verification methods, and principals can be lifecycle targets.**
4. **The core event vocabulary is small and semantically explicit.**
5. **Core events are not a universal state machine.**
6. **`resume` does not undo revocation or compromise.**
7. **`activate` is not universal resurrection.**
8. **Status authority is separate from proof validity.**
9. **Named status authority requires identity/authority evidence when relied upon.**
10. **Producer-declared time is not independent chronology.**
11. **Source-local sequence can express ordering without becoming a global clock.**
12. **Scope is explicit and exact-match by default.**
13. **`nextUpdate` expresses freshness expectation, not state reversal.**
14. **Expiration, retirement, revocation, compromise, and deprecation remain distinct.**
15. **No status evidence does not mean active.**
16. **Current status requires freshness and coverage semantics.**
17. **Conflicting lifecycle evidence remains visible.**
18. **Corrections and disputes preserve prior history.**
19. **Native external status systems retain their own semantics.**
20. **Offline lifecycle evaluation is first-class.**
21. **Network collection is explicit and policy-controlled.**
22. **A policy-derived operational state is not universal OLP truth.**
23. **Historical status requires stronger temporal reasoning when compromise or revocation timing matters.**
24. **Specification 0006 status profiles remain valid and are not rewritten.**
25. **OLP does not create a global revocation service or status authority.**

The essential invariant is:

> **OLP preserves what was said, by whom it was cryptographically asserted, what lifecycle evidence later appeared, and how that evidence was evaluated. It does not rewrite old evidence to manufacture a single timeless status bit.**

---

## 40. References

### 40.1 Normative OLP references

- OLP Specification 0003 — Record Representation.
- OLP Specification 0004 — Proofs and Verification.
- OLP Specification 0005 — Evidence Relationships and Graphs.
- OLP Specification 0006 — Identity and Authority Evidence.

### 40.2 Normative Internet references

- RFC 2119, *Key words for use in RFCs to Indicate Requirement Levels*.
- RFC 8174, *Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words*.
- RFC 3339, *Date and Time on the Internet: Timestamps*.
- RFC 3986, *Uniform Resource Identifier (URI): Generic Syntax*.

### 40.3 Informative interoperability references

- RFC 5280, *Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile*.
- RFC 6960, *X.509 Internet Public Key Infrastructure Online Certificate Status Protocol — OCSP*.
- RFC 9654, *Online Certificate Status Protocol (OCSP) Nonce Extension*.
- RFC 9608, *No Revocation Available for X.509 Public Key Certificates*.
- RFC 3161, *Internet X.509 Public Key Infrastructure Time-Stamp Protocol (TSP)*.
- RFC 4998, *Evidence Record Syntax (ERS)*.
- RFC 9921, *COSE Header Parameter for Timestamp Tokens as Defined in RFC 3161*.
- W3C Recommendation, *Bitstring Status List v1.0*, 15 May 2025.
- W3C Recommendation, *Verifiable Credentials Data Model v2.0*, 15 May 2025.

These external standards are referenced for interoperability and architectural precedent.

They do not become mandatory OLP infrastructure unless another OLP profile explicitly requires them.

---

## 41. Deferred Work

The following topics are deliberately deferred to later specifications or profiles:

- a standardized OLP bulk lifecycle-status list format;
- an OLP Merkleized status snapshot format;
- an OLP transparency-log profile;
- an OLP complete-status checkpoint mechanism;
- a standardized status-discovery protocol;
- a standardized status subscription protocol;
- a standardized status-push protocol;
- domain-specific reinstatement events;
- domain-specific terminal-event precedence rules;
- status authority delegation profiles;
- standardized lifecycle reason vocabularies;
- standardized lifecycle scope vocabularies;
- privacy-preserving anonymous status checking;
- selective disclosure of lifecycle evidence;
- zero-knowledge status proofs;
- multi-party threshold status authorities;
- status-source transparency and gossip protocols;
- long-term archival renewal profiles;
- normalized projections for specific external status mechanisms; and
- normative wire serialization for evidence exchange.

Those mechanisms can be layered on the lifecycle primitives defined here without changing the identity or semantics of existing lifecycle-status records.

---

**End of OLP Specification 0007 — Draft v0.1**
