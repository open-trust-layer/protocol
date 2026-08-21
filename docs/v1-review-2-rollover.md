# OLP v1 Review-2 Rollover

**Status:** review-governance record  
**Previous target:** `olp-v1.0-review-1`  
**Previous source:** `877493826d673ccf9bb94e7b6b113b35141ad220`  
**New target:** `olp-v1.0-review-2`  
**New source:** not yet frozen

## Why review-1 was superseded

Issue #21 identified a release-integrity and reproducibility defect in the frozen review-1 source.

Specification 0014 commits exact repository file bytes and explicitly forbids newline conversion before per-file hashing. The Python conformance commitment and promotion tooling therefore hash file bytes directly.

The review-1 source had no `.gitattributes`. A Git for Windows checkout using the common `core.autocrlf=true` policy could materialize LF repository text as CRLF in the working tree. A reviewer following the reproduction instructions could therefore observe different bytes from the committed repository blobs and obtain:

- different `core-v1` and Draft v0.3 corpus commitment values; and
- failed required-artifact SHA-256 checks causing `promotion-check` to report `INVALID`.

The cryptographic commitment construction itself was not changed, and the published LF-repository-byte commitment values were not found to be incorrect. The defect was the repository's failure to guarantee those bytes across ordinary checkout environments.

## Correction

The corrected source adds:

1. root `.gitattributes` with `* text=auto eol=lf`;
2. explicit `-text` handling for common binary artifact extensions;
3. `tests/conformance/test_repository_byte_reproducibility.py`, which enumerates the current hash-critical corpus and required-artifact text paths and rejects CRLF working-tree materialization; and
4. a `windows-latest` v1 candidate readiness job that sets `core.autocrlf=true` before checkout, inspects effective Git line-ending policy, runs the exact-byte regressions, and executes the reviewer-facing commitment and promotion commands.

The Windows job proves that the common Git for Windows newline policy no longer changes the observed hash-critical bytes.

## Invariants preserved

The rollover does not alter:

- any OLP evidence or wire semantics;
- Specifications 0001–0015;
- Python or Rust protocol implementation behavior;
- conformance manifest/profile/vector corpus bytes;
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

## Review evidence handling

`olp-v1.0-review-1` remains permanently bound to its original source commit. It is historical evidence and is never rebound to the corrected source.

`olp-v1.0-review-2` begins in `preparing` state with no source commit. After the corrected preparation snapshot is merged and the full repository matrix passes, a metadata-only follow-up freezes review-2 to that exact immutable source SHA.

Both external review gates remain pending for review-2. Any review-1 discussion may be useful background, but it cannot automatically satisfy a review-2 completion gate.

## Stable-promotion consequence

Stable promotion remains intentionally `BLOCKED`. The rollover does not waive, complete, or weaken either required external gate.
