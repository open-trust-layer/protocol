# Milestone 22 — Privacy & Disclosure Core

Milestone 22 makes the deterministic, security-sensitive planning subset of Specification 0010 executable without inventing field-level selective-disclosure semantics that OLP v1 does not define.

## Executable capability

`olp.privacy-disclosure.v1` is exposed through the separate `privacy-disclosure-v1` conformance profile.

The executable operation is:

```text
plan_disclosure
```

It consumes the exact eight-element `DisclosureRequestV1` plus explicit caller-supplied planner context describing available immutable evidence, committed resources, and task dependencies.

Planner context is processing input. It is not a new OLP evidence record type and does not create a universal policy language.

## Native OLP v1 disclosure boundary

The executable core supports:

- whole-object disclosure of exact immutable records and proofs;
- graph-subset disclosure through explicit task dependencies;
- task-scoped dependency closure;
- omission of unrelated sibling evidence;
- explicit unresolved dependencies;
- offline/self-contained supporting-resource selection when requested;
- exact Record Identity and Proof Identity verification for supplied bodies;
- exact `ResourceRefV1` digest verification for supplied resource content;
- structured privacy and policy warnings;
- explicit external-native-presentation permission; and
- deterministic output without ambient network I/O.

The core does **not** support:

- deleting fields from an identified OLP record while retaining its identity;
- native OLP zero-knowledge disclosure;
- redactable signatures;
- a mandatory SD-JWT or BBS profile;
- audience encryption;
- a universal consent or lawful-basis model;
- a universal privacy score;
- a universal completeness proof; or
- a claim that one selected set is globally minimum among all possible satisfying sets.

## Identity preservation and redaction substitution

A supplied record body is recomputed through the normal Record Identity algorithm before the planner can select it under a `RecordRef`.

A field-deleted or otherwise altered record therefore receives a different identity and cannot masquerade as the original object. The planner always reports:

```text
field_redaction_performed = false
```

If field-level selective disclosure is required, the evidence must use a cryptographic mechanism that explicitly defines those semantics.

## Task-scoped closure

Closure is relative to the declared task.

The planner follows only explicit dependencies classified by the processing context. It does not automatically traverse all evidence sharing a principal, verification method, relationship endpoint, lifecycle target, or bundle of origin.

This preserves the Specification 0010 distinction:

```text
withheld evidence != nonexistent evidence
subset bundle     != globally complete graph
```

The planner therefore reports:

```text
disclosure_claim = TASK_SCOPED_MINIMIZED_DISCLOSURE
global_completeness_established = false
```

## Offline and resolver privacy

Offline/self-contained verification can reduce resolver-query leakage while increasing disclosed payload.

When offline verification is requested, explicit offline support dependencies may be selected and `SELF_CONTAINED_OVERDISCLOSURE` may be reported. Planned network resolution may produce `NETWORK_RESOLUTION_LEAKAGE`, but the planner itself performs no DNS, HTTP, filesystem, DID, status-service, or other ambient resolution.

## External native selective-disclosure presentations

External native presentations are carried only when the request explicitly permits them. Their native cryptographic system remains authoritative for its own selective-disclosure semantics.

OLP does not reconstruct undisclosed claims and does not claim unlinkability merely because the external proof system can provide it. Surrounding stable identifiers can still trigger correlation warnings such as `STABLE_PRINCIPAL_CORRELATION` or `EXTERNAL_PRESENTATION_UNLINKABILITY_UNKNOWN`.

## Bundle-size boundary

`maxBundleBytes` belongs to `DisclosureRequestV1`, but the abstract planner cannot know the exact encoded size of the eventual Specification 0008 package or manifest.

The planner therefore does not falsely certify that limit. It emits `MAX_BUNDLE_BYTES_REQUIRES_PACKAGING_CHECK`, leaving exact byte-limit enforcement to the packaging stage where the final bytes are available.

## Conformance

Milestone 22 uses a separate 18-case `privacy-disclosure-v1` corpus covering:

- whole-object minimization;
- graph-subset closure;
- offline support resources;
- exact proof selection;
- same-subject/stable-identifier correlation;
- network leakage warnings;
- external native-presentation allow/block policy;
- unresolved and missing dependencies;
- redaction substitution;
- resource digest mismatch;
- required-capability failure;
- malformed purpose/capability/dependency inputs; and
- unsupported request versions.

The profile is additive. Earlier `core-v1`, `bundle-v1`, `resolution-v1`, and `identity-authority-lifecycle-v1` case sets remain unchanged.

The acceptance gate requires deterministic Python and independent Rust execution against the same corpus plus direct Python↔Rust interoperability checks.
