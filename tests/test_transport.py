from __future__ import annotations

import pytest

from olp.errors import ConformanceError, UnsupportedFeatureError
from olp.transport import (
    OJVEMap,
    TransportEnvelopeV1,
    decode_identity_text,
    decode_ojve,
    encode_identity_text,
    encode_ojve,
    materialize_map,
    project_abstract,
    unproject_abstract,
)


def test_textual_identity_roundtrip_for_record_proof_and_bundle():
    digest = bytes(range(32))
    for kind, prefix in (("record", "r1_"), ("proof", "p1_"), ("bundle", "b1_")):
        text = encode_identity_text(kind, digest)
        assert text.startswith(prefix)
        assert len(text) == 46
        decoded_kind, decoded = decode_identity_text(text, expected_kind=kind)
        assert decoded_kind == kind
        assert decoded == digest


def test_bundle_and_record_text_forms_share_underlying_digest():
    digest = bytes.fromhex("11" * 32)
    _, record_digest = decode_identity_text(encode_identity_text("record", digest))
    _, bundle_digest = decode_identity_text(encode_identity_text("bundle", digest))
    assert record_digest == bundle_digest == digest


def test_textual_identity_rejects_padding_standard_base64_and_noncanonical_pad_bits():
    digest = bytes(32)
    canonical = encode_identity_text("record", digest)
    with pytest.raises(ConformanceError):
        decode_identity_text(canonical + "=")
    with pytest.raises(ConformanceError):
        decode_identity_text(canonical[:-1] + "/")
    # 32 octets encode to 43 base64url characters; the final sextet has two
    # zero pad bits. B has the same high data bits as A but non-zero pad bits.
    assert canonical.endswith("A")
    with pytest.raises(ConformanceError):
        decode_identity_text(canonical[:-1] + "B")


def test_textual_identity_context_mismatch_is_explicit():
    text = encode_identity_text("proof", bytes.fromhex("22" * 32))
    with pytest.raises(ConformanceError) as exc:
        decode_identity_text(text, expected_kind="record")
    assert exc.value.code == "IDENTITY_TEXT_KIND_MISMATCH"


def test_ojve_byte_string_roundtrip_uses_base64url_without_padding():
    value = b"hello\x00world"
    encoded = encode_ojve(value)
    assert encoded == {"$olp": "bytes", "v": "aGVsbG8Ad29ybGQ"}
    assert decode_ojve(encoded) == value


def test_ojve_large_integers_roundtrip_without_json_number_coercion():
    for value in ((1 << 53), (1 << 64) - 1, -(1 << 64)):
        encoded = encode_ojve(value)
        assert encoded["$olp"] == "int"
        assert encoded["v"] == str(value)
        assert decode_ojve(encoded) == value


def test_ojve_rejects_unsafe_raw_json_integer():
    with pytest.raises(ConformanceError) as exc:
        decode_ojve(1 << 53)
    assert exc.value.code == "MALFORMED_OJVE"


def test_ojve_map_preserves_integer_text_and_byte_keys():
    abstract = OJVEMap(((1, "integer"), ("1", "text"), (b"1", "bytes")))
    encoded = encode_ojve(abstract)
    assert encoded["$olp"] == "map"
    decoded = decode_ojve(encoded)
    assert isinstance(decoded, OJVEMap)
    assert decoded == abstract
    assert project_abstract(decoded) == {
        "$map": [[1, "integer"], ["1", "text"], [{"$bytes": "31"}, "bytes"]]
    }


def test_ojve_map_rejects_duplicate_abstract_keys():
    raw = {"$olp": "map", "v": [[1, "a"], [1, "b"]]}
    with pytest.raises(ConformanceError) as exc:
        decode_ojve(raw)
    assert exc.value.code == "DUPLICATE_OJVE_MAP_KEY"


def test_ojve_wrapper_shape_and_unknown_tag_fail_closed():
    with pytest.raises(ConformanceError):
        decode_ojve({"$olp": "bytes", "v": "AA", "extra": True})
    with pytest.raises(UnsupportedFeatureError) as exc:
        decode_ojve({"$olp": "future", "v": None})
    assert exc.value.code == "UNSUPPORTED_OJVE_TAG"


def test_ojve_canonical_decimal_rejects_leading_zero_and_negative_zero():
    for text in ("01", "-0", "+1"):
        with pytest.raises(ConformanceError):
            decode_ojve({"$olp": "int", "v": text})


def test_conformance_projection_roundtrip_preserves_generic_maps():
    projected = {
        "$map": [
            [{"$bytes": "01"}, [1, 2]],
            ["x", {"$map": [[1, {"$bytes": "ff"}]]}],
        ]
    }
    value = unproject_abstract(projected)
    assert project_abstract(value) == projected


def test_materialization_rejects_transport_key_types_not_allowed_by_object_schema():
    value = OJVEMap(((b"key", "value"),))
    with pytest.raises(ConformanceError) as exc:
        materialize_map(value)
    assert exc.value.code == "TRANSPORT_OBJECT_KEY_TYPE_MISMATCH"


def test_json_transport_envelope_roundtrip_preserves_payload():
    payload = OJVEMap((("subject", "urn:example:alice"), (1, b"digest")))
    envelope = TransportEnvelopeV1("record", payload)
    wire = envelope.to_json()
    assert wire["olp"] == 1
    assert wire["type"] == "record"
    decoded = TransportEnvelopeV1.from_json(wire)
    assert decoded.message_type == envelope.message_type
    assert decoded.payload == payload


def test_transport_envelope_accepts_absolute_uri_extension_type():
    envelope = TransportEnvelopeV1("https://example.test/messages/custom", "payload")
    assert TransportEnvelopeV1.from_json(envelope.to_json()) == envelope


def test_transport_envelope_rejects_wrong_version_and_unqualified_extension_type():
    with pytest.raises(UnsupportedFeatureError) as exc:
        TransportEnvelopeV1.from_json({"olp": 2, "type": "record", "payload": None})
    assert exc.value.code == "UNSUPPORTED_TRANSPORT_ENVELOPE_VERSION"
    with pytest.raises(ConformanceError):
        TransportEnvelopeV1("customMessage", None)


def test_transport_envelope_cbor_is_transport_only_and_deterministic_for_core_keys():
    payload = OJVEMap((("envelope_version", 1), ("type", "claim"), ("content", "hello")))
    envelope = TransportEnvelopeV1("record", payload)
    first = envelope.to_cbor()
    second = envelope.to_cbor()
    assert first == second
    assert first.startswith(b"\x84")
