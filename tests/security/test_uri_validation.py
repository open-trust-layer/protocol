from olp.values import is_absolute_uri


def test_absolute_uri_rejects_injection_whitespace_and_bad_percent_escapes():
    assert not is_absolute_uri("urn:example:ok\nINJECT")
    assert not is_absolute_uri("urn:hello world")
    assert not is_absolute_uri("urn:x%GG")
    assert not is_absolute_uri("urn:x%")


def test_absolute_uri_accepts_exact_ascii_uri_without_normalizing():
    assert is_absolute_uri("urn:example:A%2fb?x=1#Frag")
    assert is_absolute_uri("https://example.org/a%20b?x=1&y=2#z")


# --- SSRF host classification -------------------------------------------------
#
# ipaddress.ip_address accepts only dotted-quad IPv4, but the C resolver used by
# real HTTP stacks also accepts decimal, hexadecimal, octal and short spellings.
# Treating an unparseable host as a public DNS name let a loopback, private-range
# or metadata-service target pass the Specification 0009 section 25 policy check
# with no DNS involvement at all.

import pytest

from olp.model.resolution import ResolutionRequestV1
from olp.resolution import _blocked_network_target, resolve_request

_NETWORK_SOURCE = [
    {
        "source_class": "network",
        "source_identifier": "urn:resolver:https",
        "status": "resolved",
    }
]


@pytest.mark.parametrize(
    "host",
    [
        "127.0.0.1",        # canonical dotted quad
        "2130706433",       # decimal
        "0x7f000001",       # hexadecimal
        "017700000001",     # octal
        "127.1",            # short form, final label absorbs 24 bits
        "127.0.1",          # short form, final label absorbs 16 bits
        "0",                # the unspecified address, decimal
        "0.0.0.0",
        "[::1]",
    ],
)
def test_loopback_and_unspecified_blocked_in_every_spelling(host):
    assert _blocked_network_target(f"http://{host}/admin")


@pytest.mark.parametrize(
    "host",
    ["169.254.169.254", "2852039166", "0xa9fea9fe"],
)
def test_metadata_service_blocked_in_every_spelling(host):
    assert _blocked_network_target(f"http://{host}/latest/meta-data/")


@pytest.mark.parametrize(
    "host",
    ["10.0.0.1", "192.168.1.1", "172.16.0.1", "[fe80::1]", "224.0.0.1", "localhost"],
)
def test_private_ranges_remain_blocked(host):
    assert _blocked_network_target(f"http://{host}/x")


@pytest.mark.parametrize(
    "host",
    [
        "example.org",
        "sub.example.org",
        "host-1.example.net",
        "registry.example.co.uk",
        "xn--bcher-kva.example",
        "93.184.216.34",
        "8.8.8.8",
        "[2606:4700:4700::1111]",
    ],
)
def test_public_targets_are_not_over_blocked(host):
    assert not _blocked_network_target(f"http://{host}/x")


@pytest.mark.parametrize("host", ["999.999.999.999", "1.2.3.4.5", "0x", "0xzz"])
def test_unparseable_address_literal_fails_closed(host):
    # A host whose labels are all numeric cannot be a DNS name, so a literal
    # that does not parse must never be treated as a public target.
    assert _blocked_network_target(f"http://{host}/x")


def test_non_http_schemes_are_not_network_targets():
    for uri in ("urn:example:x", "did:example:123", "file:///etc/passwd"):
        assert not _blocked_network_target(uri)


@pytest.mark.parametrize(
    "target",
    [
        "http://127.0.0.1/admin",
        "http://2130706433/admin",
        "http://0x7f000001/admin",
        "http://017700000001/admin",
        "http://127.1/admin",
        "http://2852039166/latest/meta-data/",
    ],
)
def test_resolver_blocks_non_canonical_private_targets_end_to_end(target):
    request = ResolutionRequestV1(
        target_class="externalResource", target=target, options={0: False}
    )
    result = resolve_request(request, sources=_NETWORK_SOURCE)
    payload = result if isinstance(result, dict) else result.as_dict()
    assert payload["status"] == "POLICY_BLOCKED"
    assert "RESOLUTION_POLICY_BLOCKED" in payload["errors"]
    assert payload["network_requests"] == 0
