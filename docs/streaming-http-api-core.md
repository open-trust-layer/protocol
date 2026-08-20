# Milestone 24 — Streaming & HTTP API Core

Milestone 24 makes a deterministic, no-ambient-network subset of Specification 0012 executable after the independently verified Milestone 23 transport-encoding layer.

It does **not** create a universal OLP server or make HTTP part of OLP evidence identity.

## Executable capabilities

M24 adds two independently advertised capabilities:

```text
olp.streaming-transport.v1
olp.http-api.v1
```

The combined acceptance profile is:

```text
streaming-http-v1
```

The two capability identifiers remain separate because a non-HTTP deployment may support sequence transport without exposing the HTTP profile, while M24 project acceptance requires both implementations to reproduce both dimensions.

## Deterministic conformance boundary

The M24 implementations perform **zero ambient network I/O**.

Network-sensitive facts are explicit caller inputs. No M24 conformance operation performs DNS resolution, opens sockets, follows redirects, sends credentials, or contacts an external service.

This preserves reproducibility while making the security decisions executable.

The central separations are:

```text
stream completeness        != evidence validity
bundle validity            != transport completeness
HTTP status                != OLP semantic status
Content-Digest validity    != OLP evidence identity
HTTP authentication        != OLP proof validity
HTTP authorization         != OLP authority evidence
local HTTP 404             != global nonexistence
partial representation     != full OLP object
HTTP 413 / 429             != invalid evidence
cache validator            != OLP object identity
redirect permission        != trust in redirected content
frame order                != evidence chronology or trust
```

## Streaming transport

M24 models Specification 0012 `OLPTransportFrameV1`:

```text
[
  "OLP-FRAME",
  1,
  frameType,
  payload
]
```

Accepted frame types are:

```text
manifest
record
proof
resource
result
end
```

### Wire production

The executable profile produces exact bytes for:

- RFC 7464 JSON Text Sequence items: `RS + JSON text + LF`;
- concatenated JSON Text Sequences; and
- RFC 8742-style CBOR Sequences formed by concatenating self-delimiting CBOR frame items.

The profile uses the independently verified OJVE-1 and deterministic-CBOR machinery established by Milestone 23.

### Parsed-frame semantic boundary

M24 does **not** implement or certify a general-purpose hostile-input JSON Text Sequence parser or arbitrary CBOR decoder.

The semantic stream processor receives already-parsed frame objects from the transport stack. It then enforces OLP frame and bundle semantics:

- the first manifested-bundle frame is `manifest`;
- exactly one manifest is present;
- `end`, if present, is final;
- record/proof/resource frame order after the manifest has no evidence semantics;
- expected inventory omissions remain explicit;
- transport truncation remains explicit;
- present independently addressable objects are not invalidated merely because the stream is incomplete; and
- a fully delivered but semantically invalid object does not make the transport incomplete.

That last distinction is security-critical. For example, a resource whose bytes fail its committed digest may produce:

```text
transport_status = COMPLETE
bundle.status     = INVALID
```

because all expected transport bytes arrived even though the supplied evidence is invalid.

## Immutable HTTP reads

The deterministic HTTP read model covers identity-bearing Record, Proof, and Bundle retrieval.

Before a successful response is modeled, the implementation:

1. decodes the typed textual identity;
2. recomputes the candidate Record Identity or Proof Identity using the existing verified implementation;
3. compares the digest byte-for-byte; and
4. refuses a successful object response on mismatch.

A modeled `404 Not Found` always carries:

```text
global_nonexistence_established = false
```

The local endpoint's failure to provide an object never becomes a protocol claim that the object does not exist elsewhere.

Authentication/authorization gates run before candidate-existence reporting when required, preventing the fixture model from treating protected storage existence as public information.

## HTTP semantic status separation

For modeled operations such as resolution, disclosure, and bundle query, HTTP execution success does not replace the detailed OLP result.

For example:

```text
HTTP status                 = 200
resolution semantic status  = NOT_FOUND
```

is valid when the operation executed successfully but found no object.

Similarly:

- unsupported request content type remains HTTP `415`;
- unacceptable response media remains HTTP `406`;
- unsatisfied mandatory self-contained bundle behavior returns structured failure instead of silently downgrading the requested profile.

## Content negotiation boundary

M24 does not embed a second complete HTTP field parser.

The conformance model receives **already-parsed media ranges** for `Accept` and deterministic offered-media lists. It tests exact ranges, `type/*`, and `*/*` selection semantics relevant to the OLP profile.

Full raw HTTP grammar parsing, qvalue processing, header coalescing, and framework-specific field normalization remain responsibilities of a conforming HTTP stack.

## `Content-Digest` boundary

Specification 0012 uses RFC 9530 `Content-Digest` for HTTP content integrity.

RFC 9530 defines `Content-Digest` using RFC 8941 Structured Fields dictionary semantics. M24 deliberately does **not** implement a partial competing Structured Fields parser.

The HTTP stack is responsible for parsing the raw field according to RFC 8941. The OLP conformance operation receives the parsed semantic result:

```text
[(algorithm, digestBytes), ...]
```

The M24 semantic layer then:

- preserves field absence separately from algorithm absence;
- rejects duplicate parsed algorithm members;
- requires a parsed `sha-256` value to contain exactly 32 octets;
- computes SHA-256 over the actual HTTP content bytes;
- reports `VALID` or `MISMATCH`; and
- keeps transport-integrity status separate from Record Identity, Proof Identity, or proof verification.

Unknown parsed algorithms can coexist with SHA-256. If required digest validation is requested and no supported SHA-256 member is present, the semantic result is explicit rather than silently successful.

## Redirect policy

M24 models redirect decisions without following redirects.

The deterministic policy blocks or constrains:

- `https` -> `http` downgrade;
- redirect of sensitive non-GET/HEAD requests unless explicitly permitted;
- identity-bearing immutable retrieval when the terminal path changes the requested typed identity; and
- automatic credential forwarding to a different origin unless explicitly authorized.

The model computes origin from scheme, host, and effective port and fails closed on malformed ports.

A redirect decision does not establish trust in the redirected content. The eventual OLP object still requires its normal identity/proof checks.

## HTTP authentication and authorization

M24 keeps four dimensions independent:

```text
HTTP authentication
service authorization
OLP cryptographic validity
OLP authority evidence
```

A successful HTTP authentication cannot change an invalid OLP proof into a valid one.

A valid OLP proof does not grant HTTP authorization.

The executable profile does not prescribe a universal authentication scheme, account system, authorization language, OAuth deployment, mTLS deployment, or HTTP Message Signature policy.

RFC 9421 HTTP Message Signatures remain an optional transport/authentication mechanism from Specification 0012. M24 does not implement their cryptography; an HTTP stack may supply the resulting authentication state to the deterministic semantic model.

## Cache, range, and resource-limit semantics

### Representation-specific validators

M24 creates representation-specific validators from actual response bytes and explicitly records:

```text
object_identity_automatically_reused_as_strong_etag = false
```

The same OLP object can have different JSON and CBOR bytes, so OLP identity cannot automatically be a strong validator for both representations.

Sensitive content is not allowed to become publicly cacheable unless application policy explicitly permits it.

### Ranges

A partial HTTP byte range is not automatically a complete OLP object.

If full-object verification is requested for a partial representation, the deterministic model blocks the verification claim rather than validating missing bytes by assumption.

### Limits and rate limiting

Modeled HTTP `413` and `429` states preserve:

```text
evidence_invalid = false
```

Resource exhaustion or service throttling is not evidence invalidity.

## What M24 does not certify

M24 acceptance does **not** claim:

- a production HTTP server or client;
- live socket/DNS behavior;
- SSRF-safe arbitrary URL fetching beyond the separately verified resolution model;
- complete raw RFC 8941 Structured Fields parsing;
- complete raw RFC 7464 sequence parsing;
- a general-purpose CBOR decoder for hostile streams;
- HTTP Message Signature cryptography;
- a universal authentication/authorization framework;
- TLS implementation correctness;
- production proxy/load-balancer behavior;
- global cache correctness; or
- global federation/replication semantics.

Those remain deployment/transport-stack responsibilities or separate future review surfaces.

## Conformance corpus

`streaming-http-v1` contains **36 fixed cases** across the two M24 capabilities.

The corpus covers exact frame/sequence bytes and adversarial semantic boundaries including:

- manifest-first enforcement;
- frame-order independence;
- truncation;
- optional end frame;
- complete-but-invalid resource delivery;
- duplicate/late/unsupported frames;
- immutable Record Identity path validation;
- local-only 404;
- 401/403 ordering;
- 406/415;
- resolution `NOT_FOUND` over HTTP 200;
- self-contained downgrade prevention;
- parsed `Content-Digest` valid/mismatch/missing/malformed-length states;
- redirect downgrade, identity, method, and credential policy;
- HTTP authentication versus OLP proof validity;
- representation-specific caching;
- sensitive public-cache policy;
- partial ranges;
- 413; and
- 429.

Acceptance requires Python 3.11–3.14 and the independent dependency-free Rust 1.85 implementation to pass the same corpus, plus direct Python↔Rust interoperability and source-contract guards preserving the no-network and semantic-separation boundaries.
