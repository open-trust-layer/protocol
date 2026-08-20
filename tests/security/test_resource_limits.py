import pytest

from olp.errors import ResourceLimitError
from olp.model.record import RecordV1


def test_record_freeze_rejects_excessive_depth_before_python_recursion_overflow():
    value = "leaf"
    for _ in range(1000):
        value = [value]
    with pytest.raises(ResourceLimitError, match="nesting depth"):
        RecordV1(1, "claim", value)
