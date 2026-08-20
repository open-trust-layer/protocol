// Specification 0009 deterministic, offline-first resolution core.
// Contract discriminator: OLP-RESOLUTION-REQUEST.
// Offline-first policy explicitly reports NETWORK_ACCESS_DISABLED when no permitted
// deterministic network snapshot may be consulted.
// The implementation is split into mechanically sized fragments for reviewability.
include!("resolution_part1.rs");
