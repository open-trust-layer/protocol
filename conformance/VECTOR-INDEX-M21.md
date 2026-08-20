# Milestone 21 Identity, Authority & Lifecycle Vector Index

Profile: `identity-authority-lifecycle-v1`

Capability: `olp.identity-authority-lifecycle.v1`

Total cases: **18**

| Case | Category | Operation |
|---|---|---|
| `m21.principal.role-separated.001` | positive | `evaluate_authority_lifecycle` |
| `m21.principal.control-separated.001` | positive | `evaluate_authority_lifecycle` |
| `m21.principal.object-kind.001` | malformed | `evaluate_authority_lifecycle` |
| `m21.principal.unsupported-object-kind.001` | unsupported | `evaluate_authority_lifecycle` |
| `m21.grant.interval.001` | positive | `evaluate_authority_lifecycle` |
| `m21.grant.invalid-interval.001` | malformed | `evaluate_authority_lifecycle` |
| `m21.grant.unknown-constraint.001` | unsupported | `evaluate_authority_lifecycle` |
| `m21.delegation.verified.001` | positive | `evaluate_authority_lifecycle` |
| `m21.delegation.identity-mismatch.001` | negative | `evaluate_authority_lifecycle` |
| `m21.delegation.non-delegable.001` | negative | `evaluate_authority_lifecycle` |
| `m21.delegation.scope-mismatch.001` | negative | `evaluate_authority_lifecycle` |
| `m21.authority-status.revoke.001` | positive | `evaluate_authority_lifecycle` |
| `m21.lifecycle.absence.001` | negative | `evaluate_authority_lifecycle` |
| `m21.lifecycle.sequence-conflict.001` | negative | `evaluate_authority_lifecycle` |
| `m21.lifecycle.stale.001` | negative | `evaluate_authority_lifecycle` |
| `m21.lifecycle.future-event.001` | negative | `evaluate_authority_lifecycle` |
| `m21.lifecycle.sequence-without-authority.001` | malformed | `evaluate_authority_lifecycle` |
| `m21.lifecycle.unsupported-event.001` | unsupported | `evaluate_authority_lifecycle` |

The profile is additive. It does not modify the frozen `core-v1`, `bundle-v1`, or `resolution-v1` case sets.
