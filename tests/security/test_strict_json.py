import pytest

from olp_conformance.strict_json import StrictJSONError, loads


def test_duplicate_json_names_are_rejected():
    with pytest.raises(StrictJSONError, match="duplicate JSON property"):
        loads('{"operation":"safe","operation":"evil"}')


def test_float_nonstandard_constant_and_excessive_depth_are_rejected():
    with pytest.raises(StrictJSONError):
        loads('{"x":1.5}')
    with pytest.raises(StrictJSONError):
        loads('{"x":NaN}')
    with pytest.raises(StrictJSONError, match="nesting depth"):
        loads("[" * 129 + "0" + "]" * 129)


def test_lone_surrogate_is_rejected_as_strict_json_error():
    with pytest.raises(StrictJSONError, match="non-scalar Unicode"):
        loads('"\ud800"')
