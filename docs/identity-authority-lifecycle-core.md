# Milestone 21 — Identity, Authority & Lifecycle Core

Milestone 21 makes the deterministic, security-sensitive subset of Specifications 0006 and 0007 executable while preserving the protocol boundary between evidence and application policy.

## Executable capability

`olp.identity-authority-lifecycle.v1` is exposed through the separate `identity-authority-lifecycle-v1` conformance profile. Draft v0.2 `core-v1` remains frozen at eight capabilities / 62 cases; `bundle-v1` remains 8 cases and `resolution-v1` remains 16 cases.

The executable slice covers:

- opaque absolute-URI Principal Identifiers;
- principal relations for verification-method control, subject equivalence claims, membership, and roles;
- authority grants with exact action, resource, context, interval, delegation, parent, and constraint fields;
- explicit delegation-chain evaluation against an exact parent grant;
- immutable authority-status evidence;
- immutable lifecycle/status evidence for records, proofs, verification methods, and principals;
- effective-time, source-freshness, scope, provenance/completeness, and conflict signals.

## Deliberate separation of dimensions

The core does not collapse principal identity, verification-method control, role, authority, authentication, cryptographic validity, lifecycle evidence, or local trust policy into one protocol state.

In particular:

- `holdsRole` never implies authority;
- `controlsVerificationMethod` never implies universal authority or trust;
- a syntactically valid grant does not prove grantor attribution;
- a supported delegation chain does not produce an application authorization decision;
- lifecycle evidence does not create a mutable canonical current-state object; and
- absence of revocation or lifecycle evidence never means `active`.

Outputs therefore expose dimensions such as `NOT_EVALUATED`, `UNKNOWN`, and `INDETERMINATE` rather than manufacturing certainty from incomplete evidence.

## Delegation integrity

A child grant that names `parentGrant` is not evaluated against an arbitrary caller-supplied parent object.

The implementation:

1. parses the child grant and its exact record reference;
2. recomputes the ordinary OLP Record Identity of the supplied parent record;
3. compares that identity byte-for-byte with `parentGrant`;
4. confirms that the referenced record is an Authority Grant statement; and only then
5. evaluates the exact OLP-core delegation baseline.

The baseline keeps distinct failure reasons for principal mismatch, `delegable = false`, action mismatch, resource mismatch, context mismatch, validity-interval widening, and constraint-scope uncertainty. URI hierarchy and string-prefix matching never create implicit authority scope.

## Status and lifecycle evidence

Authority revocation and lifecycle events are immutable evidence statements. They do not rewrite the target object.

Lifecycle projection preserves:

- the original event;
- named status authority where present;
- declared sequence;
- effective-time evaluation;
- source `nextUpdate` freshness signals;
- same-sequence conflicts; and
- unknown evidence completeness.

A stale status source is reported as stale; it does not erase or invert the signed event. Conflicting same-sequence evidence is preserved as `STATUS_SEQUENCE_CONFLICT` rather than silently choosing a winner.

## Fail-closed extension handling

Authority constraints are security-relevant by definition. Unknown constraints are `UNSUPPORTED_AUTHORITY_CONSTRAINT` rather than ignored.

Unknown critical principal, authority-status, or lifecycle qualifiers are likewise unsupported. Unknown absolute-URI extension relation/event types remain distinguishable from malformed compact identifiers.

## Independent implementations

The Python reference implementation and the dependency-free Rust 1.85 implementation independently execute the same implementation-neutral corpus. The Rust implementation recomputes parent Record Identity using its own deterministic encoding/identity code and does not import or spawn the Python reference implementation.

## Acceptance gate

Milestone 21 requires:

- all repository tests on Python 3.11–3.14;
- frozen `core-v1` 62/62 on Python and Rust;
- `bundle-v1` 8/8 on Python and Rust;
- `resolution-v1` 16/16 on Python and Rust;
- `identity-authority-lifecycle-v1` 18/18 on Python and Rust;
- direct Python↔Rust M21 interoperability over identity/role separation, verified and rejected delegation, conflicts, and freshness behavior; and
- source-contract checks preserving Rust implementation independence and the no-synthesized-authorization boundary.
