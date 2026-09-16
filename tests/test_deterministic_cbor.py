from __future__ import annotations

import pytest

from olp.encoding.deterministic_cbor import CborLimits, encode
from olp.errors import EncodingError, ResourceLimitError


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "f6"),
        (False, "f4"),
        (True, "f5"),
        (0, "00"),
        (23, "17"),
        (24, "1818"),
        (255, "18ff"),
        (256, "190100"),
        (-1, "20"),
        (-24, "37"),
        (-25, "3818"),
        (b"", "40"),
        (b"a", "4161"),
        ("", "60"),
        ("a", "6161"),
        ((), "80"),
        ({}, "a0"),
    ],
)
def test_known_encodings(value, expected):
    assert encode(value).hex() == expected


def test_map_keys_sorted_by_complete_encoded_key_bytes():
    # Encoded "b" begins 0x61; encoded "aa" begins 0x62, so bytewise
    # lexicographic ordering puts "b" before "aa" regardless of source order.
    assert encode({"aa": 1, "b": 2}).hex() == "a261620262616101"


def test_integer_map_labels_are_deterministic():
    assert encode({4: b"n", 0: "t"}).hex() == "a200617404416e"


def test_map_ordering_is_bytewise_not_length_first():
    # Regression barrier for the RFC 8949 vs RFC 7049 canonical-ordering split.
    #
    # OLP-CIE-1 (Specification 0003 6.4) and ProofInputV1 (Specification 0004
    # 17.2) both require ascending bytewise lexicographic order of the complete
    # deterministic CBOR encoding of each key. RFC 7049 3.9 "canonical CBOR"
    # instead ordered shorter encodings first, and several CBOR libraries still
    # implement that rule in their canonical mode.
    #
    # Text-only keys cannot tell the two rules apart: within one major type the
    # head byte grows monotonically with length, so bytewise and length-first
    # agree. They diverge only when a map mixes a multi-octet integer key with
    # a single-octet key, which is what this case pins.
    #
    # Key 24 encodes as 0x1818 (two octets); key -1 encodes as 0x20 (one
    # octet). Bytewise puts 24 first; length-first would put -1 first.
    assert encode({24: "a", -1: "b"}).hex() == "a218186161206162"
    assert encode({-1: "b", 24: "a"}).hex() == "a218186161206162"


def test_map_ordering_is_bytewise_across_major_types():
    # Key 24 encodes as 0x1818; the empty text key encodes as 0x60. Bytewise
    # puts the integer first; length-first would put the shorter text key first.
    assert encode({24: "a", "": "b"}).hex() == "a218186161606162"
    # Three keys whose length order and bytewise order disagree.
    assert encode({1: "x", 24: "y", -1: "z"}).hex() == "a30161781818617920617a"


def test_float_is_forbidden():
    with pytest.raises(EncodingError):
        encode(1.5)


def test_unsupported_map_key_is_forbidden():
    with pytest.raises(EncodingError):
        encode({b"bytes-key": 1})


def test_uint64_boundary_supported():
    assert encode((1 << 64) - 1).hex() == "1bffffffffffffffff"


def test_beyond_uint64_argument_rejected():
    with pytest.raises(EncodingError):
        encode(1 << 64)


def test_depth_limit_is_enforced():
    value = [[[[0]]]]
    with pytest.raises(ResourceLimitError):
        encode(value, limits=CborLimits(max_depth=2))


def test_text_limit_is_enforced():
    with pytest.raises(ResourceLimitError):
        encode("abcd", limits=CborLimits(max_text_bytes=3))


def test_output_limit_is_enforced():
    with pytest.raises(ResourceLimitError):
        encode("abcd", limits=CborLimits(max_output_bytes=2))


def test_map_output_limit_is_enforced_while_collecting_sort_rows():
    with pytest.raises(ResourceLimitError):
        encode({'a': '1234', 'b': '5678'}, limits=CborLimits(max_output_bytes=8))
