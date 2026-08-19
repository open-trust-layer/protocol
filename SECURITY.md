# Security Policy

Open Layer Protocol is currently **experimental / pre-0.1**.

The Draft v0.1 specifications are implementation-test material and must not be treated as a production security standard merely because they define cryptographic mechanisms.

## Supported versions

There is currently no stable production-supported release.

| Version / branch | Security support |
|---|---|
| Draft v0.1 specifications | Experimental review only |
| Future tagged pre-releases | As documented with the release |
| Stable v1.0 | Not released |

## Reporting a vulnerability

Please do **not** publish exploitable vulnerability details in a public GitHub issue.

Use GitHub's private vulnerability reporting / Security Advisory workflow for this repository when available.

If private vulnerability reporting is not available, contact the repository owners privately through the project's GitHub organization before disclosing exploit details publicly.

A useful report should include, where possible:

- the affected specification section or implementation component;
- a minimal reproducible example or test vector;
- expected versus observed behavior;
- security impact;
- whether the issue affects interoperability or canonicalization;
- whether network access or untrusted input is required;
- known mitigations; and
- any proposed specification wording change.

## High-priority security areas

Reports are especially valuable for:

- canonicalization or Record Identity collisions caused by parser differences;
- malformed CBOR accepted inconsistently across implementations;
- signature or hash algorithm confusion;
- Ed25519 key-type confusion;
- proof-purpose, record, or verification-method substitution;
- critical-extension downgrade;
- backdating or lifecycle-status misinterpretation;
- resolver SSRF, redirect, DNS, or resource-exhaustion attacks;
- proof/evidence graph cycles or amplification attacks;
- bundle bombs, decompression bombs, or unbounded allocation;
- privacy or selective-disclosure failures;
- differences between cryptographic validity and policy/status reporting that could be exploited; and
- conformance vectors that permit two conforming implementations to disagree on security-relevant behavior.

## Specification defects are security defects too

If an ambiguity in the specification causes implementations to make different security decisions, the preferred fix is not merely an implementation workaround.

The issue should also be reflected in the relevant specification and, where appropriate, in a negative or conformance test vector.

## Disclosure expectations

The project aims to coordinate fixes and specification clarification before public disclosure where practical.

Because the project has no stable release yet, compatibility may be intentionally broken to correct a security design defect.

## Cryptographic disclaimer

The presence of standardized primitives such as SHA-256 and Ed25519 does not mean the overall OLP construction has completed independent cryptographic or security review.

Do not deploy Draft v0.1 as high-assurance production security infrastructure without an appropriate independent review and threat assessment.
