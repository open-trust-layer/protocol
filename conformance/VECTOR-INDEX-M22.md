# Milestone 22 Privacy & Disclosure Vector Index

Profile: `privacy-disclosure-v1`

Capability: `olp.privacy-disclosure.v1`

Operation: `plan_disclosure`

Total cases: **18**

| Case | Category |
|---|---|
| `m22.whole-object.minimal.001` | positive |
| `m22.graph-subset.required-branch.001` | positive |
| `m22.offline.support-resource.001` | positive |
| `m22.external-native.allowed.001` | positive |
| `m22.same-subject.correlation.001` | positive |
| `m22.network.leakage.001` | positive |
| `m22.max-bundle.deferred.001` | positive |
| `m22.proof.whole-object.001` | positive |
| `m22.dependency.unresolved.001` | negative |
| `m22.root.missing.001` | negative |
| `m22.redaction.identity-mismatch.001` | negative |
| `m22.resource.digest-mismatch.001` | negative |
| `m22.external-native.blocked.001` | negative |
| `m22.capability.unavailable.001` | negative |
| `m22.request.malformed-purpose.001` | malformed |
| `m22.request.unsorted-capabilities.001` | malformed |
| `m22.dependency.malformed-class.001` | malformed |
| `m22.request.unsupported-version.001` | unsupported |

The profile is additive. It does not modify the frozen `core-v1`, `bundle-v1`, `resolution-v1`, or `identity-authority-lifecycle-v1` case sets.

The corpus intentionally tests whole-object and graph-subset disclosure only. It does not define native OLP field-level selective disclosure, zero-knowledge proofs, redactable signatures, audience encryption, or a global completeness/minimality proof.
