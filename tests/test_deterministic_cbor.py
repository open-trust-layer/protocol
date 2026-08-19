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
