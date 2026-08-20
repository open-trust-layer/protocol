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


def test_mixed_integer_and_text_map_keys_round_trip_without_collision():
    original = {1: 'int-key', '1': 'text-key'}
    encoded = encode_value(original)
    assert encoded == {'$map': [[1, 'int-key'], ['1', 'text-key']]}
    assert decode_value(encoded) == original


def test_literal_wrapper_shaped_maps_round_trip_as_maps():
    for original in ({'$bytes': 'deadbeef'}, {'$map': 'literal'}):
        encoded = encode_value(original)
        assert '$map' in encoded
        assert decode_value(encoded) == original
