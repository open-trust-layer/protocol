from olp.values import is_absolute_uri


def test_absolute_uri_rejects_injection_whitespace_and_bad_percent_escapes():
    assert not is_absolute_uri("urn:example:ok\nINJECT")
    assert not is_absolute_uri("urn:hello world")
    assert not is_absolute_uri("urn:x%GG")
    assert not is_absolute_uri("urn:x%")


def test_absolute_uri_accepts_exact_ascii_uri_without_normalizing():
    assert is_absolute_uri("urn:example:A%2fb?x=1#Frag")
    assert is_absolute_uri("https://example.org/a%20b?x=1&y=2#z")
