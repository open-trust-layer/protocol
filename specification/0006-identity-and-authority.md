# OLP Specification 0006 — Identity and Authority Evidence

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 6 — Identity & Authority Evidence  
**Filename:** `specification/0006-identity-and-authority.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) v1 identity-binding and authority-evidence layer.

It defines:

- opaque, globally unambiguous Principal Identifiers;
- explicit evidence relating principals to verification methods;
- explicit evidence relating principals to other principals and roles;
- the `PrincipalRelationStatementV1` semantic record profile;
- the core principal relations `controlsVerificationMethod`, `sameSubjectAs`, `memberOf`, and `holdsRole`;
- the `AuthorityGrantStatementV1` semantic record profile;
- action, resource, context, validity-interval, constraint, and delegation semantics for authority grants;
- explicit immutable authority-status events;
- explicit verification-method-status evidence;
- interaction with OLP proof purposes, especially `assertion` and `authorization`;
- structured processing semantics that keep identity, cryptographic control, authority, status, and policy acceptance distinct;
- interoperability boundaries for DID, Controlled Identifier, Verifiable Credential, X.509, GNAP, and other external identity or authorization systems;
- conformance requirements; and
- security and privacy considerations.

OLP does not create a global identity provider, global account namespace, global role registry, global authorization server, or universal trust root.

Identity evidence is evidence.

Authority evidence is evidence.

Neither becomes universally true merely because it is represented by OLP or protected by a valid cryptographic proof.

---

## 2. Scope

This specification answers the question:

> How can OLP represent portable, cryptographically attributable evidence about who or what a participant identifier refers to, which verification methods are associated with that participant, which roles or memberships are claimed, and which permissions or delegations are claimed, without turning OLP into a universal identity or authorization authority?

This specification builds directly on:

- OLP Specification 0003 — Record Representation;
- OLP Specification 0004 — Proofs and Verification; and
- OLP Specification 0005 — Evidence Relationships and Graphs.

Specification 0004 establishes that cryptographic control is not identity and that a proof purpose does not establish authority by itself.

Specification 0005 establishes immutable evidence relationships and graph composition.

This specification adds reusable identity and authority statement profiles while preserving those invariants.

This specification does **not** define:

- a universal human identity scheme;
- a universal organization identifier;
- a universal software-agent identifier;
- a mandatory DID method;
- a mandatory PKI;
- a mandatory credential format;
- a global KYC or AML regime;
- a global legal-identity registry;
- a universal role ontology;
- a universal business-action ontology;
- a universal resource namespace;
- a universal access-control decision procedure;
- a universal delegation policy;
- a global certificate authority;
- a global revocation authority;
- a global trust score;
- a global identity-confidence score;
- automatic authorization from graph reachability;
- automatic trust from role, membership, or identity evidence;
- automatic identity merging; or
- a mandatory network resolver.

Applications MAY use OLP evidence alongside such systems.

Where an external identity or authorization standard already expresses a claim adequately, implementations SHOULD prefer interoperating with that standard over creating a semantically lossy OLP duplicate.

---

## 3. Requirements Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described by BCP 14 when, and only when, they appear in all capitals.

---

## 4. Core Invariants

The following invariants are normative.

### 4.1 Identity is not trust

A statement relating an identifier to a principal, verification method, organization, or role MUST NOT be interpreted by OLP as establishing that the principal is trustworthy.

Identity evidence answers identity-related questions.

Trust remains contextual and application-specific.

### 4.2 Cryptographic control is not identity

A valid OLP proof demonstrates control of the proving material required by the selected cryptosuite under the authenticated proof context.

It does not, by itself, establish the real-world identity of the controller.

A proof using verification method `K` MUST NOT be silently reinterpreted as a proof by principal `P` merely because an application expects `P` to control `K`.

A binding between `P` and `K` requires separate evidence or external resolution semantics.

### 4.3 Identity is not authority

Evidence that principal `P` is associated with verification method `K` does not establish that `P` is authorized to perform action `A`.

Evidence that `P` holds role `R` does not establish that `R` grants action `A`.

Evidence that `P` is a member of organization `O` does not establish that `P` can act for `O`.

Authority requires explicit authority evidence and application policy.

### 4.4 Authority intent is not authority sufficiency

A cryptographically valid `authorization` proof over an authority-grant record establishes authorization intent attributable to the proof's verification method.

It does not, by itself, establish that the proof producer possessed sufficient authority to issue the grant.

Applications MUST evaluate any required grantor identity, scope, delegation, status, and policy evidence separately.

### 4.5 No OLP-global principal object

OLP v1 does not define a universal mutable `Actor`, `User`, `Account`, or `Principal` object whose state is globally authoritative.

A participant is referred to by one or more `PrincipalIdentifier` values originating in external or self-certifying identifier systems.

This preserves identity-system neutrality.

### 4.6 Principal identifiers are opaque

Except for requiring absolute-URI syntax where specified, OLP core treats Principal Identifiers as opaque exact strings.

OLP MUST NOT infer:

- entity type;
- legal status;
- geographic location;
- ownership;
- trust level;
- hierarchy;
- organization membership; or
- authority

from URI spelling alone.

### 4.7 No canonical identity merge

Two identifiers that are asserted to refer to the same subject remain two distinct identifiers.

OLP MUST NOT replace them with a protocol-defined canonical identifier.

`sameSubjectAs` evidence does not cause destructive node merging.

### 4.8 No implicit identity transitivity

OLP v1 MUST NOT automatically infer:

```text
A sameSubjectAs B
B sameSubjectAs C
therefore A sameSubjectAs C
```

as a new protocol-level fact.

Applications MAY perform such inference under local rules while retaining provenance of every source statement.

### 4.9 No implicit membership or role transitivity

OLP MUST NOT infer that:

```text
A memberOf B
B memberOf C
```

implies:

```text
A memberOf C
```

Similarly, role and organizational hierarchies require explicit evidence or domain-specific policy.

### 4.10 No implicit authority propagation

An authority grant to principal `P` MUST NOT automatically propagate to:

- members of an organization associated with `P`;
- principals sharing a role with `P`;
- principals connected through `sameSubjectAs` evidence;
- keys associated with `P` except as allowed by explicit identity-binding and local policy; or
- downstream delegates

without explicit evidence and applicable policy.

### 4.11 Status does not rewrite history

A later verification-method revocation, retirement, compromise claim, authority suspension, or authority revocation MUST NOT change the identity or mathematical cryptographic validity of historical OLP records or proofs.

Status is additional evidence.

### 4.12 Signer-declared time is not trusted chronology

`validFrom`, `validUntil`, `effectiveAt`, and similar fields defined here are authenticated semantic time assertions.

They do not independently prove that a statement existed at the claimed time.

Historical chronology requiring stronger evidence SHOULD use independent time evidence as described by Specifications 0004 and 0005.

### 4.13 Actor neutrality

OLP core MUST NOT assign different protocol-level evidentiary status merely because a principal is believed to be:

- a human;
- an organization;
- a government entity;
- a software agent;
- a service;
- a device;
- an account; or
- another economic participant.

Applications MAY apply domain-specific policy where such distinctions legitimately matter.

### 4.14 Evidence provenance remains visible

Identity and authority statements are ordinary immutable OLP records.

Their proofs, supporting evidence, disputes, corrections, supersessions, and status statements remain independently addressable.

An application MUST NOT replace this evidence history with a silent mutable boolean such as:

```text
isVerified = true
```

or:

```text
isAuthorized = true
```

without preserving the underlying evidence and policy context required for that conclusion.

---

## 5. Terminology

### 5.1 Principal

An entity, role-bearing participant, account-like subject, organization, software agent, service, device, or other entity that an application needs to identify or reason about for identity or authority purposes.

`Principal` is a conceptual term.

OLP v1 does not define a universal principal object.

### 5.2 Principal Identifier

An absolute URI used to refer to a principal within this specification.

A Principal Identifier is an identifier, not proof of identity.

### 5.3 Verification Method Identifier

The absolute URI identifying verification material as defined by Specification 0004.

### 5.4 Role Identifier

An absolute URI identifying a role within an external or application-defined role vocabulary.

OLP does not define a universal role registry.

### 5.5 Principal relation record

An ordinary OLP record whose semantic content conforms to `PrincipalRelationStatementV1`.

### 5.6 Authority grant record

An ordinary OLP record whose semantic content conforms to `AuthorityGrantStatementV1`.

### 5.7 Authority status record

An ordinary OLP record whose semantic content conforms to `AuthorityStatusStatementV1`.

### 5.8 Verification-method status record

An ordinary OLP record whose semantic content conforms to `VerificationMethodStatusStatementV1`.

### 5.9 Grantor

The Principal Identifier named by an authority-grant statement as the principal purportedly issuing the grant.

Naming a grantor does not establish that the record's proof producer is that principal.

### 5.10 Grantee

The Principal Identifier named as the recipient of an authority grant.

### 5.11 Action Identifier

An absolute URI identifying the action or capability class to which an authority grant refers.

### 5.12 Authority Resource Reference

A typed reference identifying the resource or evidence object to which an authority grant applies.

### 5.13 Authority constraint

An application- or domain-defined restriction that narrows the applicability of an authority grant.

Every authority constraint is security-relevant by default.

### 5.14 Parent grant

An optional Record Reference to another authority-grant record from which a later grant claims delegated provenance.

### 5.15 Identity-binding evidence

Evidence used to support a proposition connecting a Principal Identifier to another Principal Identifier, Verification Method Identifier, organization, or role.

### 5.16 Authority evidence

Evidence used to support a proposition that a principal intended, possessed, delegated, restricted, suspended, or withdrew authority for some action or context.

### 5.17 Reliance decision

An application-specific decision to rely on some identity or authority evidence for a concrete purpose.

Reliance decisions are outside OLP core.

---

## 6. Architectural Model

This specification deliberately separates five layers:

```text
Principal identifier
        |
        | identity/control evidence
        v
Verification method
        |
        | cryptographic proof
        v
Authenticated statement
        |
        | authority/status evidence
        v
Evidence graph
        |
        | local policy
        v
Application decision
```

These layers MUST NOT be collapsed.

### 6.1 Example

Suppose an authority grant says:

```text
Grantor: did:example:acme
Grantee: did:example:agent-7
Action:  https://acme.example/actions/release-payment
```

The record is proved using:

```text
verificationMethod = did:example:acme#finance-key-2
proofPurpose       = authorization
```

A verifier can establish cryptographically that the key authenticated the exact grant record.

To conclude that ACME issued the grant, an application may also require evidence that:

```text
did:example:acme
    controlsVerificationMethod
        did:example:acme#finance-key-2
```

To conclude that the grant was permitted under ACME policy, the application may additionally require:

- role evidence;
- delegation evidence;
- grant status evidence;
- independent time evidence;
- domain-specific constraints; and
- local authorization policy.

OLP carries and verifies the evidence.

OLP does not issue the final business decision.

### 6.2 No mandatory identity stack

An application MAY source identity-binding evidence from:

- DID or Controlled Identifier documents;
- Verifiable Credentials;
- X.509 certificates and certification paths;
- organization registries;
- local key registries;
- account systems;
- hardware attestation systems;
- contractual records;
- OLP principal relation records; or
- other systems.

No one source is universally privileged by OLP.

### 6.3 Existing evidence may remain external

OLP SHOULD NOT require a semantically complete external credential to be translated into an OLP-native identity statement merely to participate in an evidence graph.

An OLP record MAY instead reference, encapsulate, or derive from the external evidence according to appropriate profiles.

The application remains responsible for validating the external evidence under its native specification.

---

## 7. Principal Identifiers

### 7.1 Syntax

A `PrincipalIdentifier` MUST be a non-empty absolute URI under RFC 3986.

Examples of syntactically possible Principal Identifiers include:

```text
did:example:123
https://accounts.example/principals/7
urn:example:organization:42
acct:alice@example.org
```

These examples do not imply that every scheme is suitable for every application.

### 7.2 Exact cryptographic value

Where a Principal Identifier participates in identity-bearing OLP record content, its exact Unicode string value participates in record identity according to Specification 0003.

Implementations MUST NOT silently normalize it before identity construction.

In particular, implementations MUST NOT automatically:

- lowercase the identifier;
- uppercase percent encodings;
- decode percent encodings;
- remove path segments;
- follow redirects and substitute a resulting URI;
- remove fragments;
- append fragments;
- convert one DID form into another; or
- substitute a resolver-selected canonical identifier.

### 7.3 Scheme-specific resolution

A resolver MAY apply scheme-specific rules when resolving or comparing external identifier metadata.

Such processing MUST NOT alter the exact identifier authenticated by the OLP record.

### 7.4 Dereferenceability is not required

A Principal Identifier does not need to be dereferenceable over a network.

Receiving a Principal Identifier MUST NOT be treated as permission for automatic network access.

### 7.5 No type inference

The identifier scheme or URI spelling MUST NOT cause OLP core to infer whether the principal is a human, organization, software agent, device, role, or other category.

Entity-type claims MAY be represented by external credentials or domain-specific OLP statements.

### 7.6 Multiple identifiers

One real-world or digital principal MAY legitimately have multiple Principal Identifiers.

OLP does not choose a canonical identifier.

### 7.7 Reuse and reassignment

Identifier systems differ in whether identifiers are persistent, recyclable, versioned, self-certifying, or mutable.

Applications SHOULD understand the lifecycle semantics of any identifier scheme on which they rely.

OLP MUST NOT assume non-reassignment unless the identifier system actually guarantees it.

---

## 8. Principal Object References

### 8.1 Representation

`PrincipalObjectRefV1` is a two-element array:

```text
PrincipalObjectRefV1 = [
    kind,
    identifier
]
```

The array MUST contain exactly two elements.

### 8.2 Principal object

Kind `0` identifies another principal:

```text
[0, principalIdentifier]
```

The second element MUST be a valid Principal Identifier.

### 8.3 Verification-method object

Kind `1` identifies a verification method:

```text
[1, verificationMethodIdentifier]
```

The second element MUST be a valid absolute URI compatible with Specification 0004's verification-method identifier rules.

### 8.4 Role object

Kind `2` identifies a role:

```text
[2, roleIdentifier]
```

The second element MUST be a valid absolute URI.

### 8.5 Unsupported kinds

No other kinds are defined by `PrincipalObjectRefV1`.

A processor receiving another kind MUST report `UNSUPPORTED_PRINCIPAL_OBJECT_KIND` unless it implements a later specification defining that kind.

### 8.6 Equality

Two Principal Object References are equal if and only if both:

- `kind` is equal; and
- the exact identifier string is equal.

Resolver aliases and external equivalence claims do not change core equality.

---

## 9. Principal Relation Records

### 9.1 Semantic profile

A principal relation record is an ordinary OLP record conforming to Specification 0003 whose semantic record content is one `PrincipalRelationStatementV1`.

No new identity-bearing record envelope is introduced.

`PrincipalRelationStatementV1` is deliberately distinct from Specification 0005's `RelationshipStatementV1`. Specification 0005 relates immutable OLP evidence objects to other immutable OLP evidence objects through `EvidenceRefV1`. This profile relates externally named principals, verification methods, and roles. Keeping the profiles distinct prevents external actor identifiers from being misrepresented as content-addressed OLP evidence references.

### 9.2 Exact statement

`PrincipalRelationStatementV1` is the following eight-element array:

```text
PrincipalRelationStatementV1 = [
    "OLP-PRINCIPAL-RELATION",  ; index 0: profile discriminator
    1,                         ; index 1: version
    relationType,              ; index 2
    subject,                   ; index 3: PrincipalIdentifier
    object,                    ; index 4: PrincipalObjectRefV1
    context,                   ; index 5: PrincipalIdentifier or null
    qualifiers,                ; index 6: map
    critical                   ; index 7: sorted array
]
```

The array MUST contain exactly eight elements.

### 9.3 Profile discriminator

Index 0 MUST equal:

```text
OLP-PRINCIPAL-RELATION
```

### 9.4 Version

Index 1 MUST equal integer `1`.

Unsupported versions MUST be reported as `UNSUPPORTED_PRINCIPAL_RELATION_VERSION` rather than being treated as false claims.

### 9.5 Relation type

Index 2 MUST be a non-empty text string.

Core relation types defined by this specification use compact identifiers.

Extension relation types MUST use absolute URI identifiers.

### 9.6 Subject

Index 3 MUST be a valid Principal Identifier.

### 9.7 Object

Index 4 MUST be one valid `PrincipalObjectRefV1`.

The selected relation type constrains the permitted object kind.

### 9.8 Context

Index 5 is either:

- a Principal Identifier; or
- `null`.

Core relation rules specify when a context is required or forbidden.

Context identifies a principal or organizational domain in which the relation is asserted to hold.

It does not create authority by itself.

### 9.9 Qualifiers

Index 6 MUST be a map.

If no qualifiers are present, it MUST be the empty map.

Every qualifier key MUST be an absolute URI.

Qualifier values MUST use data types permitted by Specification 0003.

### 9.10 Critical qualifiers

Index 7 MUST be an array of qualifier identifiers whose semantics must be understood to safely interpret the relation.

Every member:

- MUST be an absolute URI;
- MUST be unique;
- MUST name a qualifier present in index 6; and
- MUST NOT name a core field.

Before record identity construction, members MUST be sorted in ascending bytewise lexicographic order of their UTF-8 encodings.

### 9.11 Unknown qualifiers

Unknown non-critical qualifiers MAY be preserved without semantic interpretation.

An unknown critical qualifier MUST yield:

```text
UNSUPPORTED_CRITICAL_PRINCIPAL_QUALIFIER
```

for semantic relation processing.

It MUST NOT make a cryptographically valid proof over the record mathematically invalid.

### 9.12 Duplicate keys

Duplicate qualifier keys are non-conforming.

Implementations MUST NOT use parser-specific first-wins, last-wins, or merge behavior.

### 9.13 Proofs over principal relations

A cryptographically attributable principal relation SHOULD normally carry one or more valid OLP proofs with:

```text
proofPurpose = assertion
```

A valid proof means the proof producer's verification method asserted the exact relation record.

It does not establish that the relation is objectively correct.

---

## 10. Core Principal Relation Vocabulary

OLP v1 defines exactly four compact principal relation types:

```text
controlsVerificationMethod
sameSubjectAs
memberOf
holdsRole
```

They are semantically distinct and MUST NOT be substituted for one another.

### 10.1 `controlsVerificationMethod`

Required form:

```text
relationType = controlsVerificationMethod
subject      = PrincipalIdentifier
object.kind  = 1
context      = null
```

Meaning:

> The statement asserts that the principal identified by `subject` controls, or is represented for the stated purpose by, the verification method identified by `object`.

This is an identity/control claim.

It does not establish:

- exclusive control;
- current control;
- uncompromised control;
- legal identity;
- authority for every action;
- authority for every proof purpose; or
- application trust.

### 10.2 Self-asserted control evidence

A `controlsVerificationMethod` relation may be proved by the same verification method named in the object.

For example:

```text
subject: did:example:alice
object:  did:example:alice#key-1
proof verificationMethod: did:example:alice#key-1
```

If the proof verifies, this demonstrates that the key controller cryptographically asserted the association.

It does **not**, by itself, prove that the external identifier system recognizes the controller as the legitimate subject of `did:example:alice`.

That stronger conclusion may require resolver semantics, external credentials, registry evidence, or other policy.

### 10.3 Third-party control attestation

A different verification method MAY prove the same relation.

That proves that the third-party method asserted the relation.

The verifier still needs separate evidence or policy to determine who controls the attesting method and how much weight its assertion deserves.

### 10.4 Multiple control relations

A principal MAY have multiple verification methods.

A verification method MAY appear in multiple relation records.

OLP core does not assume one-to-one mapping.

Applications requiring exclusivity MUST establish it through external semantics or additional evidence.

### 10.5 `sameSubjectAs`

Required form:

```text
relationType = sameSubjectAs
subject      = PrincipalIdentifier
object.kind  = 0
context      = null
```

Meaning:

> The statement asserts that the subject Principal Identifier and object Principal Identifier refer to the same underlying principal for the statement producer's intended interpretation.

This relation is an identity-equivalence **claim**, not a protocol merge operation.

### 10.6 No automatic equivalence closure

A processor MUST NOT automatically merge storage, histories, keys, roles, authority, or policy state merely because a `sameSubjectAs` statement exists.

A processor MAY project a reverse convenience relation because the stated semantic is symmetric, but MUST preserve provenance to the exact relation record.

A processor MUST NOT automatically compute transitive closure as a protocol fact.

### 10.7 Conflicting same-subject claims

The following may coexist:

```text
R1: A sameSubjectAs B
R2: A sameSubjectAs C
R3: D disputes R1
```

OLP preserves the evidence.

It does not collapse A, B, and C into one authoritative node.

### 10.8 `memberOf`

Required form:

```text
relationType = memberOf
subject      = PrincipalIdentifier
object.kind  = 0
context      = null
```

Meaning:

> The statement asserts that the subject principal is a member of the object principal, where the object is interpreted by the relevant ecosystem as an organization, group, collective, or analogous principal.

Membership does not imply:

- employment;
- officer status;
- ownership;
- authority to sign for the organization;
- authority to access resources;
- authority to delegate; or
- trustworthiness.

### 10.9 `holdsRole`

Required form:

```text
relationType = holdsRole
subject      = PrincipalIdentifier
object.kind  = 2
context      = PrincipalIdentifier
```

Meaning:

> The statement asserts that the subject principal holds the identified role within the context principal.

For example:

```text
subject = did:example:alice
object  = [2, https://acme.example/roles/finance-approver]
context = did:example:acme
```

The role identifier's semantics are defined externally.

### 10.10 Role evidence is not authority evidence

A `holdsRole` statement MUST NOT, by itself, satisfy an authority requirement.

An application may separately have policy such as:

```text
finance-approver may authorize payments below EUR 5000
```

That policy is outside OLP core unless represented as explicit authority evidence under this or another specification.

### 10.11 Extension principal relations

A non-core principal relation type MUST use an absolute URI.

An extension specification SHOULD define:

- allowed object kind;
- context requirements;
- expected proof purpose;
- qualifier semantics;
- whether any symmetry is intended;
- whether any domain-specific inference is safe; and
- security considerations.

Unknown extension relation types MUST be reported as `UNSUPPORTED_PRINCIPAL_RELATION_TYPE` for semantic processing while preserving record and proof validity dimensions.

---

## 11. Authority Grant Records

### 11.1 Semantic profile

An authority grant record is an ordinary OLP record conforming to Specification 0003 whose semantic record content is one `AuthorityGrantStatementV1`.

The grant record is immutable.

Revocation, suspension, correction, supersession, or delegation MUST be represented through additional evidence rather than mutation.

### 11.2 Exact statement

`AuthorityGrantStatementV1` is the following thirteen-element array:

```text
AuthorityGrantStatementV1 = [
    "OLP-AUTHORITY-GRANT",  ; index 0: profile discriminator
    1,                      ; index 1: version
    grantor,                ; index 2: PrincipalIdentifier
    grantee,                ; index 3: PrincipalIdentifier
    action,                 ; index 4: ActionIdentifier
    resource,               ; index 5: AuthorityResourceRefV1 or null
    context,                ; index 6: absolute URI or null
    validFrom,              ; index 7: RFC 3339 date-time or null
    validUntil,             ; index 8: RFC 3339 date-time or null
    delegable,              ; index 9: boolean
    parentGrant,            ; index 10: RecordRef or null
    constraints,            ; index 11: map
    extensions              ; index 12: map
]
```

The array MUST contain exactly thirteen elements.

### 11.3 Profile discriminator

Index 0 MUST equal:

```text
OLP-AUTHORITY-GRANT
```

### 11.4 Version

Index 1 MUST equal integer `1`.

Unsupported versions MUST be reported as:

```text
UNSUPPORTED_AUTHORITY_GRANT_VERSION
```

### 11.5 Grantor

Index 2 MUST be a valid Principal Identifier.

The grantor field is a semantic assertion contained in the grant record.

It does not automatically bind the proof producer to the grantor.

### 11.6 Grantee

Index 3 MUST be a valid Principal Identifier.

### 11.7 Action

Index 4 MUST be a non-empty absolute URI.

The action URI identifies the capability, operation, or permission class to which the grant refers.

OLP v1 defines no compact business-action vocabulary.

Examples of application-defined action identifiers might conceptually include:

```text
https://example.org/actions/read
https://example.org/actions/release-payment
https://example.org/actions/sign-contract
https://example.org/actions/publish-artifact
```

The semantics of an action URI MUST be defined by the ecosystem using it.

### 11.8 Resource

Index 5 is either:

- one valid `AuthorityResourceRefV1`; or
- `null`.

`null` means the statement does not identify one specific resource using this field.

It MUST NOT be interpreted as universally unlimited authority unless the action/context semantics and application policy explicitly define that result.

### 11.9 Context

Index 6 is either:

- a non-empty absolute URI; or
- `null`.

Context identifies an authority domain, tenant, jurisdictional context, protocol context, service context, or analogous scope defined by the surrounding application.

A context URI is opaque to OLP core.

### 11.10 Validity interval

Indices 7 and 8 are each either:

- a valid RFC 3339 date-time string; or
- `null`.

If both are present:

```text
validFrom < validUntil
```

MUST hold according to RFC 3339 instant comparison.

The interval is half-open for application evaluation:

```text
validFrom <= evaluationTime < validUntil
```

where a missing boundary is open-ended.

These fields are grant semantic assertions, not independent timestamp evidence.

### 11.11 Delegable

Index 9 MUST be a boolean.

If `false`, the grant states that the grantee is not permitted by this grant to issue a downstream grant derived from it.

If `true`, the grant states that delegation is permitted subject to:

- action semantics;
- resource scope;
- context;
- validity interval;
- constraints;
- parent-chain evidence; and
- application policy.

`delegable = true` does not make every downstream grant valid automatically.

### 11.12 Parent grant

Index 10 is either:

- one `RecordRef` as defined by Specification 0005; or
- `null`.

If present, it asserts that this grant derives authority from the referenced parent grant.

The referenced record SHOULD resolve to a valid `AuthorityGrantStatementV1` record.

A mismatched record profile MUST be reported as:

```text
PARENT_GRANT_TYPE_MISMATCH
```

### 11.13 Root-like grants

`parentGrant = null` means the grant does not claim delegated provenance through another OLP authority grant.

It does **not** mean that the grantor is a universal root of authority.

The grantor's authority may arise from:

- law;
- contract;
- ownership;
- an external authorization system;
- a platform policy;
- a credential;
- a corporate governance process;
- another evidence system; or
- local application configuration.

OLP does not determine which source is sufficient.

### 11.14 Constraints

Index 11 MUST be a map.

Each constraint key MUST be an absolute URI.

Constraint values MUST use data types permitted by Specification 0003.

If no constraints are present, the map MUST be empty.

### 11.15 All authority constraints are critical

Every entry in `constraints` is security-relevant by definition.

An application MUST NOT treat a grant as semantically applicable if it encounters a constraint it does not understand.

Unknown constraints MUST produce:

```text
UNSUPPORTED_AUTHORITY_CONSTRAINT
```

for authority-applicability processing.

This specification intentionally does not use a separate `critical` list for authority constraints.

The safe default is that **all constraints are critical**.

### 11.16 Extensions

Index 12 MUST be a map of non-constraint extension data.

Every extension key MUST be an absolute URI.

Extensions MUST NOT silently change:

- grantor;
- grantee;
- action;
- resource;
- context;
- validity interval;
- delegation semantics;
- parent grant; or
- constraint interpretation.

An extension carrying security-relevant applicability semantics belongs in `constraints`, not `extensions`.

Unknown extension values MAY be preserved and ignored if they do not affect safe authority interpretation.

### 11.17 Duplicate map keys

Duplicate keys in `constraints` or `extensions` are non-conforming.

### 11.18 Grant record identity

An authority grant record receives its ordinary Record Identity under Specification 0003.

No separate Authority Grant Identity is defined.

---

## 12. Authority Resource References

### 12.1 Representation

`AuthorityResourceRefV1` is a two-element array:

```text
AuthorityResourceRefV1 = [
    kind,
    value
]
```

### 12.2 URI resource

Kind `0` identifies an externally named resource:

```text
[0, absoluteURI]
```

The second element MUST be a non-empty absolute URI.

Examples may include:

```text
https://api.example/accounts/123
urn:example:asset:987
https://repo.example/projects/olp
```

OLP does not define ownership or dereference semantics for the URI.

### 12.3 Evidence resource

Kind `1` identifies an exact OLP evidence object:

```text
[1, evidenceRef]
```

The second element MUST be a valid `EvidenceRefV1` from Specification 0005.

This permits a grant to target an immutable record or proof exactly.

### 12.4 Unsupported kinds

No other resource-reference kinds are defined by v1.

Unknown kinds MUST yield:

```text
UNSUPPORTED_AUTHORITY_RESOURCE_KIND
```

### 12.5 Resource reference is not ownership evidence

A grant naming resource R does not establish that the grantor owns, controls, administers, or is otherwise entitled to grant authority over R.

That is a separate authority question.

### 12.6 Resource equality

Two v1 resource references are equal only under their exact kind-specific rules:

- URI resource: exact URI string equality;
- evidence resource: exact Evidence Reference equality under Specification 0005.

No resolver aliasing is applied by OLP core.

---

## 13. Authority Grant Attribution

### 13.1 Record existence is not grant attribution

Anyone can construct an OLP record naming:

```text
grantor = did:example:acme
```

Therefore the existence of an authority grant record does not establish that ACME issued it.

### 13.2 Required proof purpose for grant intent

To use an OLP proof as evidence that its proof producer intentionally issued the authority grant, the proof MUST have:

```text
proofPurpose = authorization
```

A valid `assertion` proof over the same record means only that the proof producer asserted the existence/content of the grant statement.

It MUST NOT be silently upgraded to authorization intent.

### 13.3 Grantor binding remains separate

Even with:

```text
cryptographicValidity = VALID
proofPurpose           = authorization
```

the application has established intent by the proof's verification method, not yet by the named grantor Principal Identifier.

To attribute the grant to the named grantor, the application SHOULD establish an acceptable binding between:

```text
grantor PrincipalIdentifier
        and
proof.verificationMethod
```

using:

- `controlsVerificationMethod` evidence;
- identifier-system resolution;
- external credentials;
- PKI path validation;
- configured local bindings; or
- another accepted mechanism.

### 13.4 No circular bootstrap by default

An application MUST NOT assume a `controlsVerificationMethod` statement is authoritative merely because it is proved by the method whose control it asserts.

Such a proof demonstrates a self-asserted association.

Whether that is sufficient depends on the identifier system and application policy.

### 13.5 Multiple authorization proofs

An authority grant record MAY carry multiple independent `authorization` proofs.

This can represent multi-party approval without changing the grant record.

Proof count has no protocol-defined weight.

An application may require:

- one specific grantor method;
- N-of-M organizational methods;
- an executive plus auditor;
- a hardware-backed method; or
- another local policy.

OLP core does not choose that rule.

### 13.6 Authorization proof over another record

A valid `authorization` proof over a record that is not an `AuthorityGrantStatementV1` retains its normal Specification 0004 meaning.

This specification does not redefine the proof purpose globally.

---

## 14. Authority Scope and Applicability

### 14.1 Applicability dimensions

An authority grant can be semantically relevant only when all locally required dimensions are satisfied.

Typical dimensions include:

```text
grant attribution
requested grantee
requested action
requested resource
requested context
evaluation time
constraints
delegation provenance
grant status
local policy
```

### 14.2 Exact action matching baseline

Absent an action-specific extension specification, OLP core defines only exact Action Identifier matching.

A request for action:

```text
A
```

is not satisfied by a grant for:

```text
B
```

unless the application has external semantics establishing that B covers A.

OLP defines no global action hierarchy.

### 14.3 Exact context matching baseline

If an application requires context C, a grant with a different non-null context MUST NOT satisfy that requirement through OLP-core inference.

A null context MUST NOT be treated as a wildcard automatically.

### 14.4 Resource matching baseline

OLP core defines exact resource-reference matching only.

A grant over:

```text
https://example.org/accounts/1
```

MUST NOT automatically apply to:

```text
https://example.org/accounts/1/subresource
```

based on URI hierarchy.

URI path structure does not create authority semantics.

### 14.5 Wildcards require explicit semantics

An ecosystem that requires wildcard actions or resources MUST define them explicitly through:

- a dedicated action vocabulary;
- a constraint vocabulary;
- a domain-specific resource model; or
- another interoperable specification.

Hidden string-prefix wildcard rules are forbidden.

### 14.6 Temporal applicability

If an evaluation time is supplied, a processor MAY evaluate the grant's stated validity interval.

Results SHOULD distinguish:

```text
WITHIN_DECLARED_INTERVAL
BEFORE_DECLARED_INTERVAL
AFTER_DECLARED_INTERVAL
NO_DECLARED_BOUND
NOT_EVALUATED
```

This is semantic interval evaluation, not trusted-time validation.

### 14.7 Independent time

Where historical authority depends on proving that a grant existed before compromise, revocation, transaction execution, or another event, applications SHOULD evaluate independent temporal evidence.

The signed `validFrom`, `validUntil`, or record timestamps alone do not establish historical existence.

### 14.8 Constraint processing

For each authority constraint:

1. identify the constraint URI;
2. determine whether the implementation understands its semantics;
3. obtain required evaluation context;
4. evaluate the constraint;
5. report the result independently.

If any required constraint is unsupported or not evaluable, the authority grant MUST NOT be reported as fully applicable.

### 14.9 Constraint result model

A processor SHOULD support at least:

```text
SATISFIED
NOT_SATISFIED
UNSUPPORTED
NOT_EVALUATED
ERROR
```

for each constraint.

### 14.10 No universal final `authorized` bit

An OLP core processor MUST NOT claim a universal final result:

```text
authorized = true
```

merely from structural and cryptographic processing.

An application MAY compute a local authorization decision after applying its own policy.

The result SHOULD identify the policy profile or application context used for that decision.

---

## 15. Delegation Evidence

### 15.1 Delegation is explicit

A downstream authority grant that claims delegated provenance SHOULD set `parentGrant` to the exact Record Reference of the grant from which it claims authority.

A downstream grant MUST NOT infer its parent from:

- timestamps;
- storage order;
- graph proximity;
- matching grantor/grantee names; or
- application database insertion order.

### 15.2 Parent grantee and child grantor

For a direct delegated-grant interpretation, the parent grant's `grantee` SHOULD equal the child grant's `grantor` under exact Principal Identifier comparison.

If they differ, an OLP core processor SHOULD report:

```text
DELEGATION_PRINCIPAL_MISMATCH
```

It MUST NOT silently apply `sameSubjectAs` closure to make them equal.

An application MAY use additional accepted identity evidence to reconcile identifiers, but that becomes an explicit policy/evidence step.

### 15.3 Parent delegable flag

If a parent grant has:

```text
delegable = false
```

and a child cites it as `parentGrant`, a processor SHOULD report:

```text
PARENT_GRANT_NOT_DELEGABLE
```

This does not make the child record malformed or its proof cryptographically invalid.

It means the claimed delegated provenance is not supported by the parent grant's own semantics.

### 15.4 Delegable true is not enough

`delegable = true` does not establish that the child grant stays within parent scope.

A complete delegation policy may need to compare:

- actions;
- resources;
- contexts;
- time intervals;
- constraints;
- role requirements;
- downstream delegation limits; and
- external policy.

OLP v1 does not define universal subset semantics for arbitrary action and constraint vocabularies.

### 15.5 Scope narrowing

Ecosystems SHOULD design authority vocabularies so that delegated grants can be proven or evaluated as no broader than their parents.

Where such semantics exist, processors SHOULD expose the result as a separate delegation-scope dimension.

### 15.6 Delegation chains

A parent grant MAY itself have a parent grant.

Processors MAY traverse the resulting chain or graph.

They MUST:

- detect cycles;
- enforce resource limits;
- preserve each exact Record Reference;
- avoid hidden network access; and
- report unresolved parents separately from invalid delegation.

### 15.7 Delegation cycles

An authority delegation cycle is not automatically a malformed evidence graph because immutable records may contain conflicting or erroneous claims.

However, a cycle MUST NOT be accepted as proof of self-originating authority.

A delegation evaluator MUST terminate and SHOULD report:

```text
DELEGATION_CYCLE_DETECTED
```

### 15.8 No authority from graph reachability

The existence of a path:

```text
A -> B -> C -> D
```

in a graph of grants does not, by itself, authorize D.

Every relevant grant, identity binding, status, scope condition, and policy requirement remains separately evaluable.

---

## 16. Authority Status Records

### 16.1 Additive status evidence

An authority status record is an ordinary OLP record conforming to Specification 0003 whose semantic record content is one `AuthorityStatusStatementV1`.

Authority grants are immutable.

Changes in intended reliance are represented through separate authority-status records.

### 16.2 Exact statement

`AuthorityStatusStatementV1` is the following eight-element array:

```text
AuthorityStatusStatementV1 = [
    "OLP-AUTHORITY-STATUS",  ; index 0
    1,                       ; index 1: version
    targetGrant,             ; index 2: RecordRef
    event,                   ; index 3
    effectiveAt,             ; index 4: RFC 3339 date-time or null
    reason,                  ; index 5: absolute URI or null
    qualifiers,              ; index 6: map
    critical                 ; index 7: sorted array
]
```

The array MUST contain exactly eight elements.

### 16.3 Target grant

Index 2 MUST be a Record Reference as defined by Specification 0005.

When resolved for semantic processing, the referenced record SHOULD conform to `AuthorityGrantStatementV1`.

### 16.4 Core authority-status events

Index 3 MUST be one of the following compact v1 values or an absolute-URI extension event identifier:

```text
suspend
resume
revoke
```

### 16.5 `suspend`

Meaning:

> The status producer asserts that reliance on the referenced authority grant should be temporarily suspended from the asserted effective time or according to the status producer's intended semantics.

### 16.6 `resume`

Meaning:

> The status producer asserts that a previously suspended grant may resume according to the status producer's intended semantics.

`resume` MUST NOT be interpreted as undoing a `revoke` event automatically.

### 16.7 `revoke`

Meaning:

> The status producer asserts that the referenced grant is withdrawn for future or otherwise applicable reliance according to the status producer's authority and policy context.

Revocation does not mutate or delete the original grant.

### 16.8 Effective time

Index 4 is either a valid RFC 3339 date-time or `null`.

It is an authenticated status assertion, not independent proof of when the event actually occurred.

### 16.9 Reason

Index 5 is either:

- an absolute URI identifying a reason vocabulary term; or
- `null`.

OLP v1 defines no compact reason vocabulary.

### 16.10 Qualifiers and critical qualifiers

Indices 6 and 7 follow the same extension and criticality rules as `PrincipalRelationStatementV1`.

### 16.11 Status attribution

A structurally valid status record does not establish that its producer had authority to suspend, resume, or revoke the grant.

Applications MUST evaluate the status record's proofs and any required producer-authority evidence.

### 16.12 Proof purpose

A status statement SHOULD normally be accompanied by a valid proof with:

```text
proofPurpose = assertion
```

because the proof producer is asserting the status event represented by the record.

OLP v1 does not define a separate `revocation` proof purpose.

### 16.13 No universal latest status

Multiple status records may conflict.

OLP does not define a global `latest status` algorithm based solely on producer-declared timestamps.

Applications MAY determine an effective state using:

- trusted time evidence;
- recognized status authorities;
- local policy;
- sequence numbers from an external system; or
- another defined mechanism.

### 16.14 Grant expiration

Reaching `validUntil` does not require a revocation record.

Expiration and revocation remain semantically distinct.

---

## 17. Verification-Method Status Evidence

### 17.1 Purpose

A verification-method status record is an ordinary OLP record conforming to Specification 0003 whose semantic record content is one `VerificationMethodStatusStatementV1`.

Specification 0004 separates cryptographic validity from verification-method status.

This section defines an OLP-native record profile for carrying status claims about a verification method.

It does not replace status mechanisms native to DID, PKI, hardware, account, or other key-management systems.

### 17.2 Exact statement

`VerificationMethodStatusStatementV1` is the following eight-element array:

```text
VerificationMethodStatusStatementV1 = [
    "OLP-VERIFICATION-METHOD-STATUS",  ; index 0
    1,                                 ; index 1
    verificationMethod,                ; index 2: absolute URI
    event,                             ; index 3
    effectiveAt,                       ; index 4: RFC 3339 date-time or null
    reason,                            ; index 5: absolute URI or null
    qualifiers,                        ; index 6: map
    critical                           ; index 7: sorted array
]
```

### 17.3 Verification method

Index 2 MUST be a valid Verification Method Identifier under Specification 0004.

### 17.4 Core method-status events

Index 3 MUST be one of:

```text
retire
suspend
resume
revoke
compromise
```

or an absolute-URI extension event identifier.

### 17.5 `retire`

Meaning:

> The status producer asserts that the verification method is no longer intended for creation of new proofs.

Retirement does not imply compromise.

Historical proofs MAY remain cryptographically valid.

### 17.6 `suspend`

Meaning:

> The status producer asserts that use or reliance should be temporarily suspended according to the applicable context.

### 17.7 `resume`

Meaning:

> The status producer asserts that a previous suspension no longer applies according to the applicable context.

`resume` does not automatically undo revocation or compromise evidence.

### 17.8 `revoke`

Meaning:

> The status producer asserts that the verification method has been withdrawn from intended reliance.

### 17.9 `compromise`

Meaning:

> The status producer asserts that unauthorized control or disclosure of the proving material may have occurred.

A compromise claim can be more security-significant than ordinary retirement.

OLP core nevertheless treats it as evidence requiring provenance and policy evaluation.

### 17.10 Current status versus historical validity

A historical proof may legitimately produce:

```text
cryptographicValidity      = VALID
verificationMethodStatus   = REVOKED
```

or:

```text
cryptographicValidity      = VALID
verificationMethodStatus   = COMPROMISED
```

These are not contradictions.

### 17.11 Backdating resistance

A proof whose authenticated `created` field predates a compromise or revocation claim MUST NOT, by that fact alone, be treated as proven to predate the event.

Independent temporal evidence is required for stronger historical conclusions.

### 17.12 Status-source authority

Anyone can create a status statement naming a verification method.

Applications MUST determine whether the proof producer is an acceptable source of status for that method.

Possible sources may include:

- the controller;
- an issuer;
- a certificate authority;
- an organizational security authority;
- a hardware attestation authority;
- a court or regulator;
- a local administrator; or
- another domain-specific authority.

OLP does not define one universal status authority.

### 17.13 Native status mechanisms

If the verification-method ecosystem already provides authoritative status semantics, applications SHOULD normally evaluate those native semantics directly.

An OLP status record can:

- preserve a portable copy of a status assertion;
- reference native status evidence;
- link it into the OLP graph; or
- carry an additional independent claim.

It MUST NOT silently override the native system's semantics.

---

## 18. Role and Membership Evidence

### 18.1 Role identifiers are external

OLP v1 does not reserve compact role names such as:

```text
admin
manager
owner
employee
agent
```

because their meaning varies radically across organizations and jurisdictions.

Role Identifiers MUST be absolute URIs.

### 18.2 Role context is required

Core `holdsRole` statements require a context Principal Identifier.

This prevents a role such as:

```text
https://example.org/roles/approver
```

from being interpreted as a universal global property detached from an organization or other principal context.

### 18.3 Role does not imply permissions

An application MAY map role evidence to authority under local policy.

For example:

```text
role: finance-approver
policy: may approve invoices under 5000 EUR
```

That mapping is not defined by OLP core.

### 18.4 Membership does not imply role

A `memberOf` statement MUST NOT imply `holdsRole`.

### 18.5 Role does not imply membership

A `holdsRole` statement MUST NOT imply `memberOf` unless an external role specification explicitly defines that inference.

### 18.6 Conflicting role evidence

Different records may assert incompatible role status.

Applications SHOULD preserve the evidence and evaluate:

- producer provenance;
- effective time;
- corrections;
- disputes;
- supersessions;
- status evidence; and
- local organizational policy.

### 18.7 Sensitive roles

Role and membership records can expose employment, affiliation, operational, political, security, or other sensitive relationships.

Applications SHOULD apply data minimization and access control.

---

## 19. Identity Evidence Processing

### 19.1 Structural processing

A Principal Relation Processor MUST separate:

```text
record conformance
relation-profile conformance
proof verification
principal-binding interpretation
policy acceptance
```

### 19.2 Processing procedure

For a candidate principal relation record:

1. Validate the enclosing OLP record under Specification 0003.
2. Confirm the exact eight-element `PrincipalRelationStatementV1` structure.
3. Validate the profile discriminator and version.
4. Validate the relation type.
5. Validate the subject Principal Identifier.
6. Validate the object kind and identifier.
7. Validate context requirements.
8. Validate qualifiers and critical qualifiers.
9. Apply core or supported extension relation structural rules.
10. Optionally verify one or more OLP proofs under Specification 0004.
11. Preserve each proof result independently.
12. Return structured relation-processing results.

### 19.3 Unknown relation semantics

A processor that cannot interpret the relation type or critical qualifiers MUST NOT claim a successful identity-binding interpretation.

It MAY still validate:

- the record;
- Record Identity;
- proof cryptographic validity; and
- evidence graph references.

### 19.4 Binding confidence is not standardized

OLP core does not define:

```text
identityConfidence = 0.97
```

or any other universal confidence measure.

Applications may compute such scores locally.

### 19.5 Multiple evidence sources

An application MAY combine:

- OLP principal relations;
- external credentials;
- resolver results;
- local configuration;
- organizational directories; and
- independent attestations.

The application SHOULD retain provenance for each source used.

---

## 20. Authority Evidence Processing

### 20.1 Structured processing

An Authority Processor SHOULD expose independent dimensions rather than one boolean.

Conceptually:

```text
recordConformance
profileConformance
grantProof
proofPurpose
grantorBinding
actionMatch
resourceMatch
contextMatch
temporalStatus
constraints
delegationStatus
grantStatus
methodStatus
policyDecision
```

### 20.2 Core processing procedure

For a candidate authority grant:

1. Validate the enclosing record under Specification 0003.
2. Validate `AuthorityGrantStatementV1` structure.
3. Validate Principal Identifiers, Action Identifier, resource, context, interval, parent reference, constraints, and extensions.
4. Verify available proofs according to Specification 0004.
5. Identify valid proofs with `proofPurpose = authorization`.
6. Preserve the exact `verificationMethod` for each proof.
7. Obtain or evaluate evidence relating an accepted proof method to the named grantor when policy requires grantor attribution.
8. Compare requested grantee if applicable.
9. Compare requested action.
10. Compare requested resource.
11. Compare requested context.
12. Evaluate declared temporal interval when an evaluation time is supplied.
13. Evaluate every authority constraint.
14. Resolve and inspect parent grant when delegation provenance is required.
15. Evaluate available authority-status records.
16. Evaluate relevant verification-method-status evidence.
17. Return a structured result.
18. Apply local authorization policy outside the core semantic verifier.

### 20.3 Example result

An implementation might represent:

```text
recordConformance       = CONFORMING
grantProof              = VALID
grantProofPurpose       = AUTHORIZATION
grantorBinding          = ACCEPTED_BY_LOCAL_POLICY
actionMatch             = MATCH
resourceMatch           = MATCH
contextMatch            = MATCH
temporalStatus          = WITHIN_DECLARED_INTERVAL
constraints             = SATISFIED
delegationStatus        = NOT_APPLICABLE
grantStatus             = NO_ACCEPTED_REVOCATION_FOUND
methodStatus            = ACTIVE_OR_NO_ADVERSE_STATUS
```

The final application decision remains separate.

### 20.4 Unsupported does not mean denied by fact

If an application cannot evaluate a constraint or identity system, it SHOULD report an unsupported or indeterminate condition.

It MUST NOT rewrite that condition as:

```text
cryptographically invalid
```

or:

```text
false identity
```

### 20.5 Fail-closed authorization policy

Although OLP core preserves `UNSUPPORTED` and `NOT_EVALUATED` as distinct evidence-processing states, security-sensitive applications SHOULD normally fail closed when required authorization dimensions cannot be evaluated.

That is an application security recommendation, not a change to the underlying evidence result.

---

## 21. Interaction with OLP Proof Purposes

### 21.1 `assertion`

`assertion` is the normal proof purpose for:

- principal relation statements;
- verification-method status statements;
- authority status statements; and
- other statements that describe identity or status evidence.

It means the proof producer intentionally asserted the exact record.

### 21.2 `authorization`

`authorization` is the required proof purpose when a proof is used as direct evidence that its producer intended to grant the authority represented by an `AuthorityGrantStatementV1`.

### 21.3 `acknowledgement`

An `acknowledgement` proof over an authority grant means the proof producer acknowledges receipt or awareness of that exact grant record.

It MUST NOT be treated as issuing, accepting, or exercising the grant automatically.

### 21.4 `witness`

A `witness` proof over a principal relation, authority grant, or status record means the producer represents that it observed the relevant subject matter according to Specification 0004's witness semantics.

It does not replace the expected `assertion` or `authorization` purpose where those are required for application semantics.

### 21.5 No proof-purpose escalation

A processor MUST NOT infer:

```text
acknowledgement -> authorization
witness         -> assertion
authorization   -> identity binding
assertion       -> authority
```

unless an application explicitly applies a local inference rule outside OLP core.

### 21.6 Multiple purposes require multiple proofs

If one verification method intends to establish two distinct proof-purpose relationships to the same record, it SHOULD create two independent OLP proofs.

For example:

```text
Proof A: acknowledgement
Proof B: authorization
```

The purposes are cryptographically distinct because `proofPurpose` is authenticated by Specification 0004.

---

## 22. Identity and Authority Graph Projection

### 22.1 Reified evidence remains normative

Principal relations, authority grants, and status statements are ordinary immutable OLP records.

Graph processors MAY project convenient edges or nodes from them.

The underlying records and proofs remain normative evidence.

### 22.2 Principal relation projection

For a valid principal relation record, a graph processor MAY project:

```text
Principal A --relationType--> Object B
```

Every projected relation MUST retain provenance identifying the exact relation Record Identity.

### 22.3 Control projection

A `controlsVerificationMethod` record MAY be projected as:

```text
Principal P --controlsVerificationMethod--> Method K
```

The projected edge MUST NOT be treated as universally accepted simply because it exists.

### 22.4 Same-subject projection

A `sameSubjectAs` statement MAY be visualized bidirectionally for convenience:

```text
A <----sameSubjectAs----> B
```

The implementation MUST retain the one exact relationship record that produced the claim.

It MUST NOT merge A and B destructively.

### 22.5 Authority grant projection

An authority grant MAY be projected conceptually as:

```text
Grantor G --grants(action, resource, constraints)--> Grantee H
```

The projected edge does not replace:

- the immutable grant record;
- its proofs;
- grantor binding evidence;
- parent-grant evidence;
- status evidence; or
- local policy.

### 22.6 Status projection

Status records MAY be attached to the targeted grant or method for graph queries.

The graph MUST preserve each distinct status record rather than collapsing conflicting evidence into one silent mutable field.

### 22.7 Graph cycles

Identity and authority graphs MAY contain cycles.

Examples include:

- reciprocal same-subject claims;
- circular membership claims;
- erroneous delegation cycles; and
- status records that reference disputed evidence.

Processors MUST detect cycles during recursive evaluation and enforce resource limits.

### 22.8 Graph count is not identity confidence

The number of identity edges pointing to a principal MUST NOT create protocol-defined identity confidence.

### 22.9 Graph count is not authority

The number of grants, roles, memberships, or apparent delegation paths MUST NOT create protocol-defined authority strength.

---

## 23. Interoperability with External Identity Systems

### 23.1 General rule

OLP is an evidence interoperability layer, not a replacement for existing identity systems.

Applications SHOULD validate external identity evidence under the native specification that defines it.

### 23.2 Decentralized Identifiers

A DID is suitable syntactically as a Principal Identifier because it is an absolute URI.

A DID URL identifying a verification method is suitable syntactically as a Verification Method Identifier when used consistently with the applicable DID method and resolver.

OLP does not require DIDs.

### 23.3 DID verification relationships

DID and Controlled Identifier ecosystems can explicitly associate identifiers with verification methods for purposes such as assertion, authentication, capability invocation, or capability delegation.

Where those native relationships are available and accepted, an application MAY use them directly as binding evidence instead of requiring an OLP `controlsVerificationMethod` record.

### 23.4 No DID semantic rewriting

OLP MUST NOT reinterpret a DID verification relationship as broader authority than the DID or Controlled Identifier specification and local application permit.

For example, a method authorized for authentication MUST NOT automatically be treated as authorized for arbitrary OLP authority grants.

### 23.5 Verifiable Credentials

A Verifiable Credential can express claims about a subject and identify an issuer.

An application MAY use a valid credential as external evidence for:

- identity attributes;
- membership;
- role;
- license;
- certification;
- account status; or
- other domain claims.

OLP does not require credentials to be transformed into `PrincipalRelationStatementV1`.

### 23.6 Credential status

Credential suspension or revocation remains governed by the credential/status mechanism being used.

An OLP record MAY reference credential-status evidence but MUST NOT silently override its native semantics.

### 23.7 X.509

An X.509 certificate and validated certification path MAY supply identity and key-purpose evidence to an application.

Key Usage and Extended Key Usage restrictions MUST be respected according to the applicable PKI profile.

A certificate that validates cryptographically MUST NOT automatically be treated as suitable for every OLP proof or authority purpose.

### 23.8 Certificate names and Principal Identifiers

Mapping an X.509 subject, SAN value, or other certificate name to an OLP Principal Identifier is application- or profile-specific.

OLP core defines no universal transformation from Distinguished Names to URIs.

### 23.9 GNAP and authorization protocols

Authorization protocols such as GNAP can establish or convey authorization state for software and resources.

OLP SHOULD NOT duplicate their interactive grant negotiation or token semantics.

Applications MAY preserve resulting grants, decisions, receipts, or references as OLP evidence when portability or auditability is useful.

### 23.10 Account and platform identities

Platform accounts MAY be represented by Principal Identifiers using an appropriate URI scheme or URI under the platform's namespace.

OLP does not guarantee account persistence, transferability, or non-reassignment.

### 23.11 Local identities

An application MAY use local or enterprise Principal Identifiers if they are absolute URIs with stable semantics within the relevant ecosystem.

Portability depends on other participants understanding or resolving those identifiers.

### 23.12 Self-certifying identifiers

Self-certifying identifiers can reduce dependence on external resolution for some control-binding questions.

They still do not establish legal identity, organizational role, or general authority by themselves.

---

## 24. Resolution Boundaries

### 24.1 Explicit dependency

Principal resolution, verification-method resolution, credential retrieval, certificate-path discovery, status retrieval, and organizational-directory lookup are explicit dependencies.

The core semantic processor MUST NOT silently perform arbitrary network access because an untrusted record contains a URI.

### 24.2 Offline operation

A conforming processor SHOULD support operation with already supplied:

- records;
- proofs;
- resolved verification methods;
- external credential evidence;
- status evidence; and
- local policy.

### 24.3 Resolver provenance

Where resolution occurs, applications SHOULD preserve:

- the requested identifier;
- resolver type;
- retrieval time;
- resolved version or content identity where available;
- status metadata;
- errors; and
- cache provenance.

### 24.4 Resolver result is not OLP truth

A resolver result is an input to evidence processing.

OLP does not certify every resolver as correct.

### 24.5 Mutable resolver state

Current resolver state can differ from historical state.

Applications performing historical identity or authority evaluation SHOULD obtain versioned, archived, or otherwise appropriate historical evidence where required.

### 24.6 Network security

Network-enabled resolvers SHOULD enforce:

- allowed URI schemes;
- host allow/deny policy;
- private-network restrictions;
- redirect limits;
- response-size limits;
- timeouts;
- TLS requirements where applicable;
- content-type checks; and
- cache controls.

These controls mitigate SSRF, resource exhaustion, and privacy leakage.

---

## 25. Structured Result Semantics

### 25.1 Principal relation result

A Principal Relation Processor SHOULD expose dimensions such as:

```text
recordConformance
relationConformance
relationSupport
proofResults
criticalQualifierStatus
resolutionStatus
localAcceptance
```

### 25.2 Authority grant result

An Authority Processor SHOULD expose dimensions such as:

```text
recordConformance
profileConformance
authorizationProofStatus
grantorBindingStatus
actionStatus
resourceStatus
contextStatus
temporalStatus
constraintResults
delegationStatus
authorityStatusEvidence
verificationMethodStatusEvidence
warnings
errors
```

### 25.3 No overloaded `verified`

An API returning only:

```text
verified = true
```

for authority processing is NOT RECOMMENDED because it fails to distinguish what was actually verified.

### 25.4 Suggested common states

Where applicable, processors SHOULD distinguish:

```text
VALID
INVALID
SUPPORTED
UNSUPPORTED
MATCH
MISMATCH
AVAILABLE
UNAVAILABLE
SATISFIED
NOT_SATISFIED
NOT_EVALUATED
INDETERMINATE
```

### 25.5 Local acceptance

If an implementation exposes a local acceptance or authorization result, it SHOULD clearly label it as policy-dependent.

For example:

```text
policyDecision = ALLOW
policyProfile  = https://example.org/policies/payment-approval-v3
```

rather than presenting it as an OLP-universal result.

### 25.6 Reason codes

Implementations SHOULD use stable machine-readable reason codes.

This specification defines at least:

```text
MALFORMED_PRINCIPAL_RELATION
UNSUPPORTED_PRINCIPAL_RELATION_VERSION
UNSUPPORTED_PRINCIPAL_RELATION_TYPE
UNSUPPORTED_PRINCIPAL_OBJECT_KIND
UNSUPPORTED_CRITICAL_PRINCIPAL_QUALIFIER

MALFORMED_AUTHORITY_GRANT
UNSUPPORTED_AUTHORITY_GRANT_VERSION
UNSUPPORTED_AUTHORITY_RESOURCE_KIND
UNSUPPORTED_AUTHORITY_CONSTRAINT
AUTHORIZATION_PROOF_MISSING
AUTHORIZATION_PROOF_INVALID
AUTHORIZATION_PURPOSE_MISMATCH
GRANTOR_BINDING_NOT_ESTABLISHED
ACTION_MISMATCH
RESOURCE_MISMATCH
CONTEXT_MISMATCH
GRANT_NOT_YET_APPLICABLE
GRANT_DECLARED_INTERVAL_EXPIRED
PARENT_GRANT_UNAVAILABLE
PARENT_GRANT_TYPE_MISMATCH
PARENT_GRANT_NOT_DELEGABLE
DELEGATION_PRINCIPAL_MISMATCH
DELEGATION_CYCLE_DETECTED
DELEGATION_SCOPE_NOT_EVALUATED

MALFORMED_AUTHORITY_STATUS
UNSUPPORTED_AUTHORITY_STATUS_EVENT
AUTHORITY_STATUS_SOURCE_NOT_ACCEPTED

MALFORMED_VERIFICATION_METHOD_STATUS
UNSUPPORTED_VERIFICATION_METHOD_STATUS_EVENT
VERIFICATION_METHOD_STATUS_SOURCE_NOT_ACCEPTED
```

Reason codes describe processing conditions.

They do not establish universal truth.

---

## 26. Privacy Considerations

### 26.1 Identity correlation

Principal Identifiers and stable Record Identities can make cross-context correlation easy.

Applications SHOULD avoid publishing identity-binding evidence more broadly than necessary.

### 26.2 `sameSubjectAs` is highly correlating

A `sameSubjectAs` statement can link previously separate identifier domains.

Publishing such evidence can defeat intentional pseudonymity or contextual separation.

Producers SHOULD treat it as privacy-sensitive evidence.

### 26.3 Verification-method correlation

A `controlsVerificationMethod` statement can link cryptographic activity across applications.

Applications SHOULD support key separation and context-specific verification methods where privacy requirements justify it.

### 26.4 Role and membership leakage

`memberOf` and `holdsRole` statements can reveal sensitive affiliations and organizational structure.

Data minimization is strongly recommended.

### 26.5 Authority graph leakage

Authority grants can expose:

- internal organizational hierarchy;
- spending limits;
- operational responsibilities;
- sensitive resources;
- delegation structures;
- security roles; and
- planned actions.

Evidence packages SHOULD contain only the authority evidence necessary for the intended verifier.

### 26.6 Public graph indexing

Public indexing of Principal Identifiers, control bindings, roles, or authority grants can create large-scale profiling risks.

OLP does not require public indexing.

### 26.7 Resolver privacy

Remote resolution can reveal which principals, keys, roles, or grants a verifier is investigating.

Offline, cached, privacy-preserving, or proxied resolution MAY be appropriate.

### 26.8 Selective disclosure

This specification does not define selective disclosure.

Future OLP work SHOULD support disclosure of the minimum identity/authority subgraph required for a decision.

---

## 27. Security Considerations

### 27.1 Identity-binding spoofing

Anyone can create a relation record claiming:

```text
Victim controls AttackerKey
```

Applications MUST evaluate proof provenance and identifier-system semantics before relying on the claim.

### 27.2 Self-assertion confusion

A key can always assert that it belongs to a prestigious or high-authority Principal Identifier.

A valid self-signed binding proves key control and claim intent, not external legitimacy of the named identifier.

### 27.3 Same-subject hijacking

Attackers may publish `sameSubjectAs` statements linking themselves to trusted principals.

Applications MUST NOT merge identity nodes automatically.

### 27.4 Role inflation

Attackers may claim powerful roles.

Role claims require provenance and policy evaluation.

### 27.5 Membership inflation

Membership evidence MUST NOT be accepted merely because a record exists or a self-controlled key asserted it.

### 27.6 Grantor spoofing

An attacker can construct an authority grant naming another principal as grantor.

Applications requiring grantor attribution MUST evaluate the `authorization` proof and binding between the proof verification method and grantor.

### 27.7 Proof-purpose confusion

Treating an `assertion` or `acknowledgement` proof as an `authorization` proof can escalate privileges.

Processors MUST preserve exact authenticated proof purpose.

### 27.8 Key-purpose confusion

A verification method accepted for one purpose MUST NOT automatically be accepted for all purposes.

Applications integrating DID/Controlled Identifier or X.509 evidence MUST respect native verification relationships, Key Usage, Extended Key Usage, and other purpose restrictions.

### 27.9 Authority wildcard ambiguity

Applications MUST NOT invent wildcard semantics from URI prefixes, empty strings, null resources, or path structures.

Wildcard or hierarchical authority requires explicit domain semantics.

### 27.10 Unknown constraints

Ignoring an unknown authority constraint can broaden authority beyond what the grant intended.

Therefore every constraint is critical by default.

### 27.11 Delegation amplification

A delegate may attempt to issue broader grants than the parent grant permits.

Applications MUST evaluate action, resource, context, time, constraints, and local delegation policy where relevant.

### 27.12 Delegation loops

Recursive delegation evaluation MUST detect cycles and enforce limits.

### 27.13 Revocation spoofing

Anyone can issue an authority or verification-method status statement.

Status provenance MUST be evaluated before reliance.

### 27.14 Revocation suppression

An adversary may withhold adverse status evidence.

Applications requiring current status SHOULD define explicit freshness and completeness requirements.

### 27.15 Backdated grants

A compromised key can create a new grant containing an old `validFrom` value.

Signer-controlled timestamps do not establish historical existence.

### 27.16 Backdated identity bindings

The same issue applies to identity/control relation records.

Historical identity conclusions may require independent temporal evidence.

### 27.17 Historical key rotation

Current absence of a verification method from a resolver MUST NOT automatically prove that every historical proof using it was invalid when created.

Historical evaluation requires appropriate status semantics.

### 27.18 Identifier reassignment

If an external identifier system permits identifier reassignment, later control of the same textual Principal Identifier may not imply continuity with earlier evidence.

Applications MUST understand identifier-lifecycle semantics.

### 27.19 Homograph and display attacks

Unicode and URI display can create visually deceptive identifiers.

User interfaces SHOULD display identifier scheme, provenance, and exact values appropriately and SHOULD NOT rely solely on visually confusable labels.

### 27.20 URI parser disagreement

Processors MUST preserve exact identifier strings and use standards-conforming URI parsing.

They MUST NOT allow different parser normalization behavior to change record identity.

### 27.21 SSRF

Untrusted Principal Identifiers, action URIs, resource URIs, reason URIs, constraint URIs, or role URIs MUST NOT trigger arbitrary network requests.

### 27.22 Graph amplification

Attackers may create large identity or delegation graphs to exhaust processing resources.

Processors MUST enforce depth, node, edge, resolution, and time limits.

### 27.23 Policy confusion

An application SHOULD identify which policy produced an authorization decision.

A decision under one policy MUST NOT be silently reused under another context.

### 27.24 Conflicting evidence

OLP can preserve conflicting identity, role, grant, and status evidence.

It cannot guarantee that conflicts are resolvable cryptographically.

Applications SHOULD surface material conflicts rather than hide them.

### 27.25 No trust by namespace prestige

An identifier under a prestigious-looking domain, DID method, certificate namespace, or organization name MUST NOT receive protocol-defined trust merely because of its namespace.

### 27.26 Compromised authority source

If an authority source or identity attester is compromised, valid historical signatures from that source may require contextual re-evaluation.

The cryptographic validity of those signatures remains a separate dimension.

### 27.27 No truth oracle

This layer improves provenance for identity and authority claims.

It does not turn those claims into universal truth.

---

## 28. Conformance Classes

An implementation MAY claim conformance to one or more of the following classes.

### 28.1 Principal Identifier Processor

A conforming Principal Identifier Processor MUST:

- validate absolute-URI syntax;
- preserve exact identifier strings;
- avoid unauthorized normalization;
- distinguish Principal, Verification Method, and Role object kinds; and
- avoid implicit network resolution.

### 28.2 Principal Relation Producer

A conforming Principal Relation Producer MUST:

- produce an ordinary OLP record under Specification 0003;
- place one valid `PrincipalRelationStatementV1` in semantic content;
- obey core relation structural constraints;
- validate qualifiers and critical qualifiers;
- preserve exact identifier strings; and
- compute ordinary Record Identity under Specification 0003.

### 28.3 Principal Relation Processor

A conforming Principal Relation Processor MUST:

- validate the enclosing record;
- validate `PrincipalRelationStatementV1`;
- support all four core relation types;
- reject malformed core relation shapes;
- preserve unknown non-critical qualifiers;
- reject semantic completion when a critical qualifier is unsupported; and
- preserve proof and policy distinctions.

### 28.4 Authority Grant Producer

A conforming Authority Grant Producer MUST:

- produce a valid `AuthorityGrantStatementV1` record;
- validate grantor and grantee identifiers;
- validate action, resource, context, interval, delegation, parent, constraints, and extensions;
- treat every constraint as critical; and
- use `proofPurpose = authorization` when producing a proof intended to express grant issuance.

### 28.5 Authority Grant Processor

A conforming Authority Grant Processor MUST:

- validate `AuthorityGrantStatementV1`;
- distinguish proof cryptographic validity from proof purpose;
- distinguish proof verification method from named grantor;
- support exact action/resource/context baseline matching;
- evaluate or report every constraint;
- preserve delegation-status distinctions;
- preserve authority-status distinctions; and
- not expose structural processing as universal authorization truth.

### 28.6 Authority Status Processor

A conforming Authority Status Processor MUST:

- support `suspend`, `resume`, and `revoke`;
- validate target Record References;
- preserve proof provenance;
- not silently select a universal latest status from untrusted timestamps; and
- not mutate the target grant.

### 28.7 Verification-Method Status Processor

A conforming Verification-Method Status Processor MUST:

- support `retire`, `suspend`, `resume`, `revoke`, and `compromise`;
- preserve exact verification-method identifiers;
- keep method status separate from proof cryptographic validity;
- preserve status provenance; and
- not infer historical timing from proof `created` alone.

### 28.8 Authority Evidence Evaluator

An implementation claiming `Authority Evidence Evaluator` conformance MUST:

- expose structured evaluation dimensions;
- identify unsupported or unevaluated constraints;
- detect delegation cycles;
- avoid hidden identity merges;
- preserve status evidence provenance;
- distinguish local policy results from OLP semantic results; and
- support fail-closed application integration for required unevaluated dimensions.

---

## 29. Interoperability Test Cases

These cases test semantic interoperability rather than a new cryptographic primitive.

Full Record Identity is computed by Specification 0003, and proofs are computed by Specification 0004.

### 29.1 Test Case A — Self-asserted control binding

Statement:

```text
[
  "OLP-PRINCIPAL-RELATION",
  1,
  "controlsVerificationMethod",
  "did:example:alice",
  [1, "did:example:alice#key-1"],
  null,
  {},
  []
]
```

A valid assertion proof over the enclosing record uses:

```text
verificationMethod = did:example:alice#key-1
```

Expected processing:

```text
relationConformance = CONFORMING
proofValidity       = VALID
proofPurpose        = assertion
bindingNature       = SELF_ASSERTED_CONTROL_ASSOCIATION
```

A conforming processor MUST NOT report:

```text
realWorldIdentityVerified = true
```

solely from this evidence.

### 29.2 Test Case B — Same-subject evidence without merge

Statement:

```text
[
  "OLP-PRINCIPAL-RELATION",
  1,
  "sameSubjectAs",
  "did:example:alice",
  [0, "https://accounts.example/users/42"],
  null,
  {},
  []
]
```

Expected:

```text
relationConformance = CONFORMING
```

The processor MAY project a symmetric relation for queries.

It MUST NOT replace both identifiers with one canonical OLP identifier.

### 29.3 Test Case C — Role does not authorize automatically

Statement:

```text
[
  "OLP-PRINCIPAL-RELATION",
  1,
  "holdsRole",
  "did:example:alice",
  [2, "https://acme.example/roles/finance-approver"],
  "did:example:acme",
  {},
  []
]
```

Expected:

```text
relationConformance = CONFORMING
roleEvidence        = PRESENT
```

A conforming OLP core processor MUST NOT derive:

```text
mayReleasePayment = true
```

without separate authority evidence or policy.

### 29.4 Test Case D — Direct authority grant

Statement:

```text
[
  "OLP-AUTHORITY-GRANT",
  1,
  "did:example:acme",
  "did:example:agent-7",
  "https://acme.example/actions/release-payment",
  [0, "https://acme.example/accounts/escrow-9"],
  "https://acme.example/contexts/production",
  "2026-08-01T00:00:00Z",
  "2026-09-01T00:00:00Z",
  false,
  null,
  {},
  {}
]
```

Suppose a proof over this record is cryptographically valid with:

```text
proofPurpose       = authorization
verificationMethod = did:example:acme#finance-key-2
```

Expected:

```text
grantRecord            = CONFORMING
authorizationProof      = VALID
grantIntentByMethod     = ESTABLISHED
grantorIdentityBinding  = NOT_EVALUATED
finalAuthorization      = OUTSIDE_OLP_CORE
```

### 29.5 Test Case E — Assertion proof is not grant intent

Use the same grant record as Test Case D, but:

```text
proofPurpose = assertion
```

Expected:

```text
cryptographicValidity  = VALID
authorizationProof     = PURPOSE_MISMATCH
```

The processor MUST NOT treat the proof as direct grant issuance evidence.

### 29.6 Test Case F — Unknown constraint

Grant contains:

```text
constraints = {
  "https://example.org/constraints/maxAmount": 5000
}
```

A processor that does not implement that constraint must report:

```text
UNSUPPORTED_AUTHORITY_CONSTRAINT
```

It MUST NOT ignore the constraint and report the grant as fully applicable.

### 29.7 Test Case G — Non-delegable parent

Parent grant:

```text
delegable = false
```

Child grant:

```text
parentGrant = RecordRef(parent)
```

Expected:

```text
childRecordValidity  = CONFORMING
childProofValidity   = evaluated independently
delegationStatus     = PARENT_GRANT_NOT_DELEGABLE
```

The child record itself is not malformed merely because the claimed delegation is unsupported.

### 29.8 Test Case H — Revoked method and valid historical signature

Historical proof:

```text
cryptographicValidity = VALID
```

Later accepted method-status evidence:

```text
event = revoke
```

Expected representation permits:

```text
cryptographicValidity    = VALID
verificationMethodStatus = REVOKED
```

A conforming processor MUST NOT rewrite cryptographic validity to `INVALID` solely because of current status.

### 29.9 Test Case I — Backdated proof after compromise

A proof says:

```text
created = 2026-01-01T00:00:00Z
```

Accepted status evidence says:

```text
compromise effectiveAt = 2026-02-01T00:00:00Z
```

No independent timestamp evidence exists.

Expected:

```text
proofCreatedClaimPredatesCompromise = true
historicalExistencePredatesCompromise = NOT_ESTABLISHED
```

### 29.10 Test Case J — Identity mismatch across delegation

Parent:

```text
grantee = did:example:alice
```

Child:

```text
grantor = https://accounts.example/users/42
parentGrant = RecordRef(parent)
```

Even if separate evidence asserts:

```text
did:example:alice sameSubjectAs https://accounts.example/users/42
```

OLP core exact delegation matching yields:

```text
DELEGATION_PRINCIPAL_MISMATCH
```

An application MAY explicitly evaluate and accept the identity-equivalence evidence under local policy, but the core processor MUST NOT silently merge the identifiers.

---

## 30. Design Summary

OLP v1 identity and authority architecture is:

```text
                Principal Identifier
                        |
                        | immutable relation evidence
                        v
            Verification Method / Role /
              Other Principal Identifier
                        |
                        v
                  OLP Proof(s)
                        |
              cryptographic provenance
                        |
                        v
              Identity Evidence Graph


Grantor Principal ----------------------------+
        |                                      |
        | binding evidence                     |
        v                                      |
Verification Method                           |
        |                                      |
        | authorization proof                  |
        v                                      |
Authority Grant Record -----------------------+
        |
        +--> Grantee
        +--> Action
        +--> Resource
        +--> Context
        +--> Validity interval
        +--> Constraints
        +--> Parent grant
        |
        +<-- Status records
        |
        v
Local application policy
        |
        v
Application authorization decision
```

The architecture deliberately preserves:

```text
identifier       != identity proof
key control      != identity
identity         != authority
role             != authority
grant intent     != grantor authority
grant            != final authorization
status evidence  != historical mutation
policy decision  != protocol truth
```

This permits OLP to interoperate with many identity and authorization ecosystems while remaining neutral about which ones an application trusts.

---

## 31. References

### 31.1 Normative

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels.
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
- RFC 3339 — Date and Time on the Internet: Timestamps.
- RFC 3986 — Uniform Resource Identifier (URI): Generic Syntax.
- OLP Specification 0003 — Record Representation.
- OLP Specification 0004 — Proofs and Verification.
- OLP Specification 0005 — Evidence Relationships and Graphs.

### 31.2 Informative

- RFC 5280 — Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List Profile.
- RFC 8820 — URI Design and Ownership.
- RFC 9635 — Grant Negotiation and Authorization Protocol (GNAP).
- W3C Decentralized Identifiers (DIDs) v1.x.
- W3C Controlled Identifiers v1.0.
- W3C Verifiable Credentials Data Model v2.0.
- W3C Bitstring Status List v1.0.

---

## 32. Deferred Work

The following are intentionally deferred to later OLP specifications:

- a standardized textual presentation form for Principal Identifiers beyond native URI form;
- a universal principal-type vocabulary;
- legal-identity profiles;
- organization-registration profiles;
- government-identity profiles;
- KYC/AML credential profiles;
- domain-specific role vocabularies;
- domain-specific business-action vocabularies;
- domain-specific authority-constraint vocabularies;
- formal scope-subset semantics for arbitrary delegation trees;
- threshold or quorum authorization policy languages;
- capability-token transport profiles;
- OAuth, GNAP, or macaroons translation profiles;
- X.509-to-OLP identity mapping profiles;
- DID/Controlled Identifier evidence packaging profiles;
- Verifiable Credential evidence packaging profiles;
- hardware-attestation identity profiles;
- device identity profiles;
- account reassignment evidence profiles;
- cryptographically private identity bindings;
- zero-knowledge identity or role proofs;
- selective disclosure of identity and authority graphs;
- unlinkable or pairwise Principal Identifier profiles;
- privacy-preserving status queries;
- standardized policy-decision artifacts;
- application trust-policy languages;
- universal reputation algorithms; and
- universal identity confidence scores.

Deferral is intentional.

These concerns depend on the clean separation established here between identifiers, cryptographic control, identity evidence, authority evidence, and application policy.

---

**End of OLP Specification 0006 — Draft v0.1**
