from dataclasses import replace

from olp.encoding.proof_identity import proof_identity, proof_identity_bytes, proof_identity_preimage


def test_proof_identity_is_stable_and_32_bytes(sample_proof):
    preimage = proof_identity_preimage(sample_proof)
    encoded = proof_identity_bytes(sample_proof)
    digest = proof_identity(sample_proof)
    assert preimage[0:2] == ("OLP-PROOF-ID", 1)
    assert preimage[2]
    assert preimage[3] == sample_proof.proofValue
    assert encoded
    assert len(digest) == 32
    assert digest == proof_identity(sample_proof)


def test_proof_identity_changes_when_proof_value_changes(sample_proof):
    mutated = replace(sample_proof, proofValue=bytes([sample_proof.proofValue[0] ^ 1]) + sample_proof.proofValue[1:])
    assert proof_identity(mutated) != proof_identity(sample_proof)


def test_proof_identity_changes_when_authenticated_input_changes(sample_proof):
    mutated = replace(sample_proof, domain="example.test")
    assert proof_identity(mutated) != proof_identity(sample_proof)
