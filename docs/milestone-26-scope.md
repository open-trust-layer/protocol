# Milestone 26 — v1.0 Candidate Boundary & Promotion Gates

**Status:** active  
**Baseline:** `5acc4b8934305a5215379c480db32bd0fd22f3ae`  
**Specification-set baseline:** Draft v0.3

## Purpose

Milestone 26 is a stabilization milestone. It adds no new OLP evidence semantics, identity-bearing object format, cryptosuite, transport encoding, resolver behavior, or authorization policy.

Its purpose is to make the path from Draft v0.3 to a future stable OLP v1.0 explicit, conservative, and machine-checkable.

## Architectural boundary

The existing eight-capability `core-v1` profile is the **mandatory v1.0 core candidate**. This does not make it stable yet and does not rename or redefine it.

The already accepted higher-layer profiles remain **optional v1.0 candidates**:

- `bundle-v1`;
- `resolution-v1`;
- `identity-authority-lifecycle-v1`;
- `privacy-disclosure-v1`;
- `transport-encoding-v1`; and
- `streaming-http-v1` (covering `olp.streaming-transport.v1` and `olp.http-api.v1`).

A future stable release may promote optional profiles independently. Passing Draft v0.3 does not make every optional profile mandatory.

## Required outputs

1. normative stable-promotion governance and candidate-boundary rules;
2. a machine-readable v1.0 candidate manifest;
3. a machine-readable promotion/readiness evaluator and CLI;
4. a deployment-independent OLP v1 threat model;
5. an explicit contradiction/errata and promotion-blocker register;
6. stable migration/deprecation and release-publication requirements;
7. CI gates that prove all internally satisfiable requirements and prove stable promotion remains blocked while required external review is absent;
8. repository status/roadmap/security documentation aligned with the accepted result.

## Promotion invariants

Stable promotion MUST NOT occur merely because:

- two implementations pass the same corpus;
- a release corpus is committed;
- a draft profile has existed for a long time;
- no public issue happens to be open; or
- a deployment uses standard primitives such as SHA-256 or Ed25519.

A stable promotion decision must preserve at least these distinctions:

```text
interoperability != correctness proof
conformance      != security certification
protocol safety  != deployment safety
candidate        != stable
optional profile != mandatory core
absence of known issue != proof of absence
```

## Acceptance target

Milestone 26 is complete only when:

- the mandatory candidate core is exactly `core-v1` and remains byte/semantic compatible with the Draft v0.3 accepted corpus;
- all optional candidate profiles are explicit and remain non-mandatory;
- the Draft v0.3 180-case commitment still verifies unchanged;
- Python 3.11–3.14 repository/conformance tests are green;
- independent Rust 1.85 conformance and full Python↔Rust interoperability are green;
- the promotion evaluator reports all internally satisfiable gates as passed;
- the promotion evaluator reports stable v1.0 promotion as **BLOCKED** while independent external security review is incomplete;
- unresolved normative contradictions inside the candidate boundary are either fixed/versioned or explicitly block promotion; and
- no existing accepted vector or expected result is silently changed.

## Non-goals

Milestone 26 does not:

- publish OLP v1.0;
- claim external security review;
- certify production DNS/TLS/HTTP implementations;
- certify operational key management or incident response;
- create a central registry or certification authority;
- make optional higher-layer profiles part of the mandatory core; or
- add protocol features merely to advance the milestone number.
