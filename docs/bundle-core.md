# Milestone 19 — Evidence Bundle Core

Milestone 19 makes the deterministic reader/validation subset of Specification 0008 executable without inventing an archive format or hidden resolver behavior.

The core validates `BundleManifestStatementV1`, `ResourceRefV1`, manifest Record Identity as bundle ID, root/inventory canonical sets, supplied Record/Proof identities, packaged-resource SHA-256 digests, missing/unexpected evidence, critical extensions, and self-contained no-network semantics.

Important separations remain explicit:

- bundle membership != endorsement;
- bundle integrity != evidence truth;
- missing evidence != invalid evidence;
- unexpected evidence != extra weight;
- resource digest validity != resource authority;
- self-contained verification != permission to fall back to the network.

The public conformance profile `bundle-v1` adds eight implementation-neutral cases while the Draft v0.2 `core-v1` profile remains frozen at 62 cases. Python/Rust parity is additionally required by the interoperability suite.
