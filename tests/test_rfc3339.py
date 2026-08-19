from __future__ import annotations

import pytest

from olp.model.proof import is_rfc3339, parse_rfc3339


@pytest.mark.parametrize(
    "value",
    [
        "2026-08-20T00:00:00Z",
        "2026-08-20t00:00:00z",
        "2026-08-20T00:00:00+03:00",
        "2024-02-29T23:59:60Z",
        "2026-08-20T00:00:00.123456-05:30",
    ],
)
def test_valid_rfc3339(value):
    assert is_rfc3339(value)
    assert parse_rfc3339(value).tzinfo is not None


@pytest.mark.parametrize(
    "value",
    [
        "2026-08-20",
        "2026-08-20T00:00:00",
        "2026-02-30T00:00:00Z",
        "2026-08-20T24:00:00Z",
        "2026-08-20T00:60:00Z",
        "2026-08-20T00:00:61Z",
    ],
)
def test_invalid_rfc3339(value):
    assert not is_rfc3339(value)
