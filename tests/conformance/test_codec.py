from olp_conformance.codec import decode_value, encode_value


def test_generic_byte_projection_round_trips_nested_values():
    original = {'a': b'\x00\x11', 'nested': (1, {'b': b'\xff'})}
    encoded = encode_value(original)
    assert encoded == {'a': {'$bytes': '0011'}, 'nested': [1, {'b': {'$bytes': 'ff'}}]}
    decoded = decode_value(encoded)
    assert decoded['a'] == b'\x00\x11'
    assert decoded['nested'][1]['b'] == b'\xff'


def test_partial_policy_projection_preserves_unspecified_defaults():
    from olp_conformance.codec import policy_from_json
    from olp.model.verification import VerificationPolicy

    default = VerificationPolicy()
    projected = policy_from_json({'understood_extensions': ['https://example.org/ext/a']})
    assert projected.understood_extensions == frozenset({'https://example.org/ext/a'})
    assert projected.allowed_commitment_algorithms == default.allowed_commitment_algorithms
    assert projected.allowed_cryptosuites == default.allowed_cryptosuites
