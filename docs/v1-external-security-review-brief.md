# OLP v1 Independent External Security Review Brief

**Status:** reviewer brief; independent review not yet commissioned/completed  
**Candidate:** `olp-v1.0`  
**Review-target source commit:** not yet frozen

## Purpose

This document describes the intended scope for an independent external security review of the OLP v1.0 candidate. It does not claim that such a review has occurred.

The project deliberately keeps this gate separate from maintainer review, automated conformance, and the internal Milestone 17/Milestone 26 adversarial work.

## Minimum review scope

The external review should challenge the exact frozen source snapshot, including at minimum:

- Record canonicalization and Record Identity;
- commitment construction and algorithm binding;
- ProofInputV1 domain separation;
- Ed25519 proof creation/verification and substitution resistance;
- Proof Identity;
- EvidenceRefV1 and relationship semantics;
- malformed/duplicate/Unicode/numeric/resource-bound parsing behavior;
- graph traversal, cycle/convergence, and amplification behavior;
- bundle inventory/resource commitment semantics where the optional bundle profile is assessed;
- resolver SSRF/private-address/redirect/freshness/resource policy where resolution is assessed;
- identity/authority/delegation/lifecycle separation where those optional profiles are assessed;
- privacy/disclosure minimization and correlation behavior where assessed;
- OJVE/transport type preservation, canonical textual identities, and sequence/framing behavior where assessed;
- modeled HTTP integrity/status/auth separation where assessed;
- versioning, extensions, downgrade resistance, and registry governance;
- cross-specification contradictions or ambiguity;
- conformance corpus adequacy and meaningful negative coverage; and
- release/promotion rules that could permit stale review evidence or premature stable claims.

## High-value attacker models

Review should assume hostile participants can provide adversarial JSON/CBOR/OJVE values, records, proofs, relationships, bundles, resolver inputs, URLs, headers, streams, extensions, and misleading but syntactically valid metadata.

Review should consider attempts to:

- create two conforming interpretations with different authenticated identity bytes;
- substitute keys, algorithms, proof purposes, records, verification methods, or referenced evidence;
- exploit unsupported/noncritical extension handling;
- turn policy rejection into cryptographic invalidity or vice versa;
- turn missing evidence into proof of absence;
- turn transport/resolution success into proof validity or truth;
- bypass delegation scope or lifecycle/status constraints;
- cause graph/bundle/parser resource exhaustion;
- induce SSRF, redirect-policy, cache, or content-integrity confusion;
- exploit disclosure/correlation surfaces; and
- reuse review/conformance artifacts against changed source.

## Deliberate non-claims

The candidate does not claim that protocol conformance certifies:

- production DNS/TLS stacks;
- a production HTTP client/server implementation;
- proxy/cache deployment security;
- operational key custody;
- application authorization frameworks;
- host/cloud hardening;
- monitoring or incident response; or
- production-scale denial-of-service resistance.

Findings in those areas are still useful when they expose a protocol/specification assumption that is unsafe or underspecified.

## Expected reviewer output

A useful review deliverable should identify:

- the exact frozen source commit reviewed;
- review methodology and scope;
- findings with severity and affected components;
- whether each finding changes deterministic bytes, capability semantics, implementation-only behavior, or documentation;
- any excluded areas;
- residual risks; and
- a durable public or project-verifiable reference suitable for the promotion manifest once disclosure permits.

A review of a different source commit cannot satisfy the external-security promotion gate for the frozen target.

## Finding disposition

High/critical findings affecting the promoted boundary keep stable promotion blocked until resolved. If a material source change is required, the project must freeze a new review-target identifier and obtain review evidence for that new target rather than reusing the old completion state.

Sensitive vulnerability details should use the coordinated process in `SECURITY.md`.
