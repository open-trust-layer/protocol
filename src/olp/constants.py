"""Normative constants for the Draft v0.1 OLP reference core."""

RECORD_DOMAIN = "OLP-RECORD"
RECORD_IDENTITY_VERSION = 1
RECORD_TEXT_PREFIX = "r1_"

PROOF_TYPE = "OLPProof"
PROOF_DOMAIN = "OLP-PROOF"
PROOF_VERSION = 1
PROOF_INPUT_VERSION = 1
MANDATORY_CRYPTOSUITE = "eddsa-ed25519-v1"
SHA256_COSE_ALGORITHM_ID = -16

CORE_PROOF_PURPOSES = frozenset(
    {"assertion", "acknowledgement", "witness", "authorization"}
)

CORE_PROOF_PROPERTIES = frozenset(
    {
        "type",
        "version",
        "cryptosuite",
        "proofPurpose",
        "verificationMethod",
        "recordCommitment",
        "proofValue",
        "created",
        "expires",
        "domain",
        "challenge",
        "nonce",
        "critical",
    }
)

METADATA_LABELS = {
    "created": 0,
    "expires": 1,
    "domain": 2,
    "challenge": 3,
    "nonce": 4,
}
