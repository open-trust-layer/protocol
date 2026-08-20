# OLP Specification 0014 — Release Profiles and Conformance Suite Commitments

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 25 — Draft v0.3 Integration & Conformance Freeze  
**Filename:** `specification/0014-release-profiles-and-conformance-suite-commitments.md`

---

## 1. Abstract

This specification defines release-level interoperability profiles and deterministic commitments to exact Open Layer Protocol conformance corpora.

It extends the versioning, registry, capability, and vector-governance rules in Specification 0013 without changing any existing identity-bearing OLP object, canonical encoding, cryptosuite, or accepted capability semantics.

Draft v0.3 is an integration and conformance-freeze release. It groups the independently reproduced executable capabilities accepted through Milestone 24 into one aggregate profile and gives that exact corpus a reproducible SHA-256 identity.

A corpus commitment identifies test material. It is not an OLP evidence identity, proof, certification, trust score, or security rating.

---

## 2. Scope

This specification defines:

- the Draft v0.3 aggregate interoperability profile;
- the relationship between release labels and already-versioned capabilities;
- standalone conformance-profile metadata normalization;
- deterministic selection of cases for a release profile;
- deterministic selection of only the manifest fragments that contribute to that profile/case set;
- SHA-256 file commitments;
- the exact binary preimage for `OLP-CONFORMANCE-SUITE-COMMITMENT-V1`;
- release-manifest requirements for pinning an accepted corpus; and
- migration from Draft v0.2 to Draft v0.3.

It does not define a certification authority, package-manager release, deployment architecture, network service, trust policy, or new evidence semantics.

---

## 3. Requirements language

BCP 14 requirement keywords have the meanings defined by RFC 2119 and RFC 8174 when written in all capitals.

---

## 4. Release labels do not rewrite protocol versions

Draft v0.3 is a specification-set release label.

The transition from Draft v0.2 to Draft v0.3 MUST NOT by itself change:

- Record envelope version `1`;
- `OLP-CIE-1` Record Identity bytes;
- the SHA-256 Record Commitment baseline;
- `OLPProof` version `1`;
- `ProofInputV1`;
- `eddsa-ed25519-v1`;
- Proof Identity v1;
- `EvidenceRefV1`;
- accepted relationship statement semantics;
- accepted bundle, resolution, authority/lifecycle, privacy/disclosure, or transport capability semantics; or
- the meaning of an already-published capability identifier.

A change that would alter previously conforming deterministic output or materially change an accepted capability MUST follow the breaking-change/versioning rules in Specification 0013 instead of being hidden inside a set-release transition.

---

## 5. Draft v0.3 aggregate interoperability profile

The aggregate profile identifier is:

```text
draft-v0.3-interoperable-v1
```

It contains exactly these capability identifiers, in this order:

```text
olp.record-identity.v1
olp.record-commitment.sha256.v1
olp.proof-input.v1
olp.proof.eddsa-ed25519.v1
olp.proof-verification.v1
olp.proof-identity.v1
olp.evidence-ref.v1
olp.evidence-relationship.v1
olp.bundle.v1
olp.resolution.v1
olp.identity-authority-lifecycle.v1
olp.privacy-disclosure.v1
olp.transport-encoding.v1
olp.streaming-transport.v1
olp.http-api.v1
```

The aggregate profile does not replace the narrower profiles. Implementations MAY claim only the narrower capabilities they actually implement.

Claiming `draft-v0.3-interoperable-v1` requires every capability listed above.

---

## 6. Draft v0.3 accepted case set

At the Milestone 25 freeze, the aggregate profile selects exactly 180 existing implementation-neutral cases.

Selection is deterministic:

1. load `conformance/manifest.json`;
2. load additive manifest fragments from `conformance/manifests/*.json` in filename UTF-8 byte order;
3. obtain the ordered capability list for `draft-v0.3-interoperable-v1`;
4. preserve manifest loading order; and
5. select every case whose `capability` is in the aggregate profile.

Case IDs MUST remain globally unique.

Adding a selected-capability case, removing a selected case, changing a selected case's capability, changing a referenced vector, or changing aggregate profile membership changes the release corpus and therefore MUST change its suite commitment.

Adding a future manifest fragment that contributes only unrelated profiles/capabilities MUST NOT change an already-frozen profile commitment.

---

## 7. Standalone profile metadata

A standalone `olp-conformance-profile-v1` document contains exactly:

```text
schema
id
version
status
capabilities
```

For the current profile schema:

- `schema` MUST equal `olp-conformance-profile-v1`;
- `version` MUST equal integer `1`;
- `id` MUST equal the profile filename stem;
- `status` identifies the specification-set release metadata snapshot; and
- `capabilities` MUST be unique and MUST exactly match the same profile definition loaded by the executable manifest.

Standalone profile metadata does not redefine capability semantics. A profile-registry mismatch is a release/conformance defect.

---

## 8. Corpus file set

For a profile corpus commitment, the committed file set consists of:

1. the base conformance manifest supplied to the commitment operation;
2. each additive manifest fragment that **contributes to the selected corpus**;
3. the standalone profile declaration `profiles/<profile>.json`; and
4. every vector file referenced by a selected case.

An additive manifest fragment contributes when either:

- it defines the selected profile identifier; or
- it contains at least one case whose capability is in the selected profile.

Fragments that only introduce unrelated future profiles/capabilities are intentionally excluded. This permits append-only repository growth without changing a previously frozen release commitment.

The complete manifest loader MUST still validate all visible fragments before corpus selection; excluding an unrelated fragment from a particular commitment does not make malformed global manifest composition acceptable.

Each logical relative path is included at most once.

Paths are relative to the conformance root and use `/` separators.

A path that escapes the conformance root MUST be rejected.

A referenced file that does not exist MUST be rejected.

The final file inventory is sorted by raw UTF-8 bytes of the relative path.

---

## 9. Per-file digest

Each committed corpus file is hashed over its exact file bytes using SHA-256.

For each file the commitment model records:

```text
relativePath
sha256Digest32
```

Text newline conversion, JSON reserialization, Unicode normalization, whitespace normalization, or semantic parsing MUST NOT be applied before the file hash.

The exact repository bytes are committed.

---

## 10. Integer and text framing

`U32BE(n)` is the unsigned 32-bit big-endian encoding of `n`.

A value that cannot be represented as unsigned 32-bit MUST be rejected by this commitment version.

`LP-UTF8(s)` is:

```text
U32BE(len(UTF8(s))) || UTF8(s)
```

where `len` is the octet length.

No Unicode normalization is applied.

---

## 11. `OLP-CONFORMANCE-SUITE-COMMITMENT-V1`

The exact commitment preimage is:

```text
ASCII("OLP-CONFORMANCE-SUITE-COMMITMENT-V1") || 0x00
|| LP-UTF8(profileId)
|| LP-UTF8(harnessVersion)
|| U32BE(capabilityCount)
|| LP-UTF8(capability[0]) ... LP-UTF8(capability[n])
|| U32BE(caseCount)
|| LP-UTF8(caseId[0]) ... LP-UTF8(caseId[n])
|| U32BE(fileCount)
|| fileEntry[0] ... fileEntry[n]
```

Each `fileEntry` is:

```text
LP-UTF8(relativePath) || sha256Digest32
```

Capabilities are encoded in profile order.

Case IDs are encoded in deterministic manifest loading/selection order defined in Section 6.

File entries are encoded in the UTF-8 path order defined in Section 8.

The suite commitment is:

```text
SHA-256(preimage)
```

The digest is 32 octets. Hexadecimal display is lowercase and is presentation only.

---

## 12. Commitment diagnostic document

Tools MAY expose a JSON diagnostic document using schema identifier:

```text
olp-conformance-suite-commitment-v1
```

The diagnostic form SHOULD expose the profile, harness version, ordered capabilities, ordered case IDs, per-file SHA-256 values, commitment algorithm, preimage identifier, and final digest.

The JSON diagnostic serialization itself is not the commitment preimage.

---

## 13. Release manifest pinning

A specification-set release that claims an accepted aggregate conformance corpus MUST record at minimum:

- release identifier;
- release status;
- integration milestone;
- baseline/release repository snapshot information;
- previous specification-set release;
- wire-compatibility statement;
- aggregate profile identifier;
- capability list;
- accepted case count;
- suite commitment algorithm and digest; and
- independent implementation acceptance evidence.

The release manifest MUST NOT imply that passing conformance proves operational security or trustworthiness.

---

## 14. Corpus identity is separate from test results

The suite commitment identifies the exact test corpus.

It does not state that any implementation passed it.

A conformance report identifies observed execution results against a corpus.

A signed `ConformanceClaimStatementV1`, when used, states that its producer made a claim about a test result.

These are distinct facts:

```text
corpus identity != execution result != signed claim != certification != trust
```

---

## 15. Independent implementation evidence

Promotion of an aggregate release profile SHOULD require at least two independent implementations to pass the exact committed corpus.

Where canonical bytes are normative, direct cross-implementation byte comparisons SHOULD remain part of release acceptance.

An aggregate pass MUST NOT hide a required case as skipped.

---

## 16. Draft v0.3 compatibility with Draft v0.2

Draft v0.3 does not create a new wire-format generation.

Existing conforming Draft v0.2 v1 objects do not require regeneration, re-signing, or re-identification solely because the repository set-release label changes.

Draft v0.3 primarily changes the demonstrated release surface: capabilities accepted through Milestones 19–24 are now grouped into one reproducibly committed interoperability profile.

Historical narrower profile results remain valid evidence about the exact corpus revisions they identify.

---

## 17. Relationship to Specification 0013

Specification 0013 continues to govern general version domains, identifier governance, extension governance, reason-code governance, capability stability, vector governance, and breaking-change classification.

This specification supersedes only repository-status statements in Specification 0013 that described higher layers as not yet independently executed. Those statements remain historically accurate for Draft v0.2 but are not the Draft v0.3 capability status.

The eight-capability `core-v1` remains the smallest frozen deterministic core. The 15-capability Draft v0.3 aggregate profile is an additional release-level interoperability claim, not a redefinition of `core-v1`.

---

## 18. Security considerations

A corpus commitment can be misleading if the wrong corpus is selected, if case IDs are omitted, if file bytes are normalized before hashing, if a profile advertises capabilities it does not contain in the executable manifest, or if a passing report is represented as a general security certification.

A release commitment can also be operationally unusable if unrelated future profile growth changes the frozen digest. Therefore unrelated manifest fragments are excluded using the deterministic contribution rule in Section 8.

Implementations MUST fail on path escape, missing committed files, unknown profile identifiers, empty profile capability sets, or profiles that select no cases.

Release documentation MUST preserve the distinction between deterministic conformance and deployment security.

Live sockets, DNS, TLS, external service operation, proxy/cache behavior, production authentication, production authorization policy, and independent external security audit remain outside the Draft v0.3 conformance claim unless separately documented and tested.

---

## 19. Conformance requirements

A tool claiming support for `OLP-CONFORMANCE-SUITE-COMMITMENT-V1` MUST:

1. use the exact file selection rules in Section 8;
2. hash exact file bytes with SHA-256;
3. preserve profile capability order;
4. preserve deterministic selected-case order;
5. sort file paths by UTF-8 bytes;
6. use the exact framing in Sections 10–11;
7. reject path escape and missing files;
8. ignore unrelated future profile fragments for an already selected profile; and
9. produce the same 32-octet digest for the same selected corpus snapshot.

An implementation claiming `draft-v0.3-interoperable-v1` MUST implement all 15 capabilities and pass every required case in the committed release corpus.

---

## 20. Summary

Draft v0.3 freezes a release-level lesson:

> A conformance claim is only precise when the profile, exact test corpus, implementation, and result can all be named independently.

OLP therefore keeps release labels, capability semantics, corpus identity, execution results, cryptographic evidence, and trust decisions as separate layers.
