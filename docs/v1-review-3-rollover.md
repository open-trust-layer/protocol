# OLP v1 Review-3 Rollover

**Status:** review-governance record  
**Previous target:** `olp-v1.0-review-2`  
**Previous source:** `d470970180bfa128ca14fd01ac920c95dd8ec288`  
**New target:** `olp-v1.0-review-3`  
**New source:** `f0dd778f09f904e334477bb1d6294f78d3d466f0`

## Why review-2 was superseded

Review-2 was superseded by a security defect and by a release-governance defect that surfaced while fixing it. Both required source changes inside the v1.0 candidate boundary.

### GHSA-x768-cq7q-w9mq — SSRF policy bypass

The Specification 0009 resolver classified a host using its platform address parser, which accepts only dotted-quad IPv4. Every other `inet_aton` spelling raised a parse error and was consequently treated as a public DNS name, so a loopback, private-range or metadata-service target written in decimal, hexadecimal, octal or short form was reported `RESOLVED` rather than `POLICY_BLOCKED`. No DNS resolution was involved; this was a host-parsing gap.

The Python reference implementation and the independent Rust implementation were each written from Specification 0009 and both reached the identical bypass. That is why Specification 0009 was corrected and not only the two implementations: section 25 required denying sensitive address ranges but never said which textual spellings of a host must be decoded before that membership test is applied.

The defect was not exploitable in either reference implementation, which perform no network I/O. The exposure was to adopters taking the policy shape and then performing real I/O.

### F-1 — corpus selection rewrote accepted release identity

Adding regression coverage for the defect exposed a second problem. A conformance case was selected purely by capability, so any new case carrying an already-selected capability was absorbed into every profile holding that capability. Adding the five negative resolution vectors moved `draft-v0.3-interoperable-v1` from 180 to 185 cases and changed its published commitment.

Correcting that by editing the published values would have required rewriting `CHANGELOG.md`, `specification/0000-overview.md` and `docs/milestone-25-scope.md`, which record what Milestone 25 accepted. The selection model was fixed instead.

## Correction

The review-3 source adds:

1. host-form canonicalization before private-address classification, in both implementations;
2. five negative conformance vectors covering the decimal, hexadecimal, octal, short and metadata-service spellings, as `resolution.network.private-address.002` through `.006`;
3. Specification 0009 v0.2, requiring range classification on a canonicalized host, unparseable address literals to fail closed, and explicit character-class validation;
4. `specification/releases/frozen-profile-corpora.json`, pinning frozen profiles to explicit ordered case-ID lists;
5. Specification 0014 v0.2, defining pinned selection alongside capability selection; and
6. the same pinned selection in the conformance runner, so the executed corpus cannot drift from the committed one.

Against the unfixed Rust adapter the new vectors produced `resolution-v1 21 cases, PASS 16, FAIL 5`, confirming the defect existed in both implementations and that the vectors detect it across languages.

## Invariants preserved

The rollover does not alter:

- any OLP evidence or wire semantics;
- Record Identity, Proof Identity, `ProofInputV1`, or any v1 identity-bearing construction;
- the accepted case set, expected results, or vector bytes of any previously accepted profile;
- mandatory or optional candidate profile membership;
- the three pinned required stabilization artifacts; or
- either published corpus commitment.

The commitments remain exactly:

```text
core-v1
8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e

draft-v0.3-interoperable-v1
62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc
```

`core-v1` is unchanged at 62 cases. `draft-v0.3-interoperable-v1` is unchanged at 180. The living `resolution-v1` profile grows to 21 and carries the new coverage. Preserving both commitments across a change that touched two normative specifications, both implementations, the corpus and CI is the point of the pinned-corpus fix.

## Changed semantics

`olp.resolution.v1` behavior changes. Non-canonical private-address spellings move from `RESOLVED` to `POLICY_BLOCKED`. Public hosts, ordinary dotted-quad addresses, IPv6 literals and non-`http` schemes are unaffected.

Corpus selection semantics change from capability sweep to pinned case-ID list for frozen profiles.

## Review evidence handling

`olp-v1.0-review-2` remains permanently bound to `d470970180bfa128ca14fd01ac920c95dd8ec288`. It is historical evidence and is never rebound to the corrected source.

`olp-v1.0-review-3` is frozen to:

```text
f0dd778f09f904e334477bb1d6294f78d3d466f0
```

Both external review gates remain pending for review-3. Any review-2 discussion may be useful background, but it cannot satisfy a review-3 completion gate.

## Provenance of the findings

Both defects were found by maintainer-side internal adversarial testing performed by an AI agent acting for the repository owner. Under Specification 0015 that is explicitly **not** the independent external security review required for stable promotion, and it must not be recorded as satisfying it. Finding a defect internally does not reduce the need for independent review; it is evidence the candidate had not yet been examined adversarially from outside.

## Stable-promotion consequence

Stable promotion remains intentionally `BLOCKED`. The rollover does not waive, complete, or weaken either required external gate.
