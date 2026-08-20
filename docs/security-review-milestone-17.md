# Milestone 17 — Adversarial & Security Review

**Status:** implementation fixes complete; cross-language CI verification required before acceptance  
**Scope:** executable OLP core through Specification 0005 plus the conformance transport boundary

Milestone 17 attacks executable behavior rather than treating specification prose as sufficient evidence of safety. The review focused on parser differentials, canonicalization ambiguity, policy/cryptography separation, denial of service, graph processing, relationship semantics, and cross-language drift.

This is not a claim that OLP is generally secure or production-ready. Specifications 0006–0012 are not yet fully executable, so resolver SSRF, bundle ingestion, disclosure planning, and higher-layer privacy behavior remain future executable-review targets.

## Method

The review used four rules:

1. reproduce a suspected defect before changing code;
2. prefer implementation-neutral regression vectors when behavior crosses language boundaries;
3. amend specifications when the defect is normative rather than merely local; and
4. preserve OLP's semantic separations instead of making security policy silently redefine cryptographic facts.

## Findings

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| M17-01 | Medium | Absolute-URI validation accepted raw whitespace/control characters and malformed percent escapes. | Hardened Python and Rust exact-string URI syntax guards; added malformed conformance coverage. |
| M17-02 | High | Python JSON accepted duplicate object names with last-wins behavior while Rust rejected duplicates. | Added strict duplicate-name rejection at every JSON nesting level; amended Specification 0012. |
| M17-03 | High | Record immutability freezing could recurse through hostile depth before normative resource validation. | Added pre-freeze depth, collection, text, and byte-string bounds; deep inputs now raise `ResourceLimitError`. |
| M17-04 | High | `VerificationPolicy.allowed_cryptosuites` existed but was not enforced by Python verification. | Enforced cryptosuite policy with `CRYPTOSUITE_REJECTED_BY_POLICY`; added shared conformance case. |
| M17-05 | Medium | Commitment-algorithm policy rejection incorrectly prevented mathematical signature verification. | Technical support and policy acceptance are now independent; Specification 0004 amended and conformance locked. |
| M17-06 | Medium | Graph traversal reported DAG convergence as a cycle. | Replaced repeated-visit heuristic with bounded directed-cycle detection over the explored graph. |
| M17-07 | Medium | `EvidenceGraph.add_record()` could leave projected edges stale until an explicit rebuild. | Projection now refreshes immediately for incremental relationship additions while bulk construction remains single-pass. |
| M17-08 | High | Conformance JSON projection stringified map keys, collapsing integer `1` and text `"1"`; wrapper-shaped maps could collide with byte wrappers. | Added reversible `$map` projection and wrapper escaping; added shared record/proof-input vectors. |
| M17-09 | High | Rust adapter read stdin without a finite bound and could panic on invalid UTF-8. | Added bounded input reads, explicit UTF-8 failure handling, JSON size limits, and depth limits. |
| M17-10 | High | Rust deterministic-CBOR map encoding reset nesting depth while recursively encoding map entries. | Preserved enclosing depth across map keys/values and added finite collection/scalar/output limits plus Rust regression tests. |
| M17-11 | Medium | Relationship processing preserved unknown noncritical qualifiers but did not expose that they were uninterpreted. | Python and Rust adapter outputs now expose deterministic `uninterpreted_qualifiers`; existing conformance vector asserts it. |

## Normative amendments

### Specification 0004

The verification model now explicitly defines `CRYPTOSUITE_REJECTED_BY_POLICY` and clarifies that policy rejection of a technically supported cryptosuite or commitment algorithm does not erase independently computable record binding or signature mathematics.

For example, the following state is valid and intentionally non-contradictory:

```text
cryptosuiteSupport = REJECTED_BY_POLICY
recordBinding = VALID
cryptographicValidity = VALID
```

The proof can still be unacceptable to the relying application. The result simply does not rewrite a mathematical fact into a policy fact.

### Specification 0012

JSON OLP transports now normatively reject duplicate object member names recursively and require finite parser input/nesting bounds before arbitrary recursive materialization. First-wins, last-wins, merge, and parser-specific duplicate-name behavior are forbidden for OLP JSON input.

## Executable regressions

Milestone 17 expands `core-v1` from 57 to **62** implementation-neutral cases. New shared cases cover:

- policy-rejected-but-mathematically-valid cryptosuite verification;
- policy-rejected-but-mathematically-valid commitment verification;
- malformed whitespace in a verification-method URI;
- mixed integer/text Proof Input map keys; and
- literal adapter-wrapper-shaped record maps.

The Python security-regression suite additionally covers duplicate JSON names, excessive JSON depth, lone Unicode surrogates, pre-freeze record depth, DAG convergence, live graph projection refresh, and traversal edge limits.

## Residual risks and deferred attack surfaces

The following remain deliberately open rather than being declared safe without executable evidence:

- **Resolver SSRF / network policy:** Specification 0009 boundaries are defined, but the current executable reference slice performs no implicit resolver network access and therefore cannot yet exercise a real resolver stack.
- **Bundle ingestion amplification:** Specification 0008 defines limits and manifested bundles, but full bundle parsing/storage is not yet implemented in the executable core.
- **Selective-disclosure privacy:** Specification 0010 defines minimization and correlation boundaries; privacy leakage requires executable disclosure profiles before meaningful adversarial testing.
- **Verification-method ecosystem parsing:** the current core accepts explicitly supplied Ed25519 method material; DID/X.509/other resolver-specific parser surfaces remain outside this milestone.
- **System OpenSSL boundary in Rust:** the Rust implementation deliberately uses a narrow system `libcrypto` FFI for Ed25519. Platform-specific provider/configuration behavior remains a deployment concern.
- **Resource limits are implementation profiles:** finite limits are now enforced, but production deployments must select operational limits appropriate to their threat model rather than treating the reference values as universal constants.

## Acceptance gate

Milestone 17 is accepted only when GitHub CI demonstrates all of the following from a clean checkout:

```text
Python repository tests                         PASS
Python core-v1 conformance                      62 / 62 PASS
Rust crate tests                                PASS
Rust release conformance adapter                BUILD PASS
Rust core-v1 conformance                        62 / 62 PASS
Python ↔ Rust interoperability                  PASS
```

Any cross-language disagreement is a protocol/conformance investigation, not a reason to special-case one implementation.
