# OLP Specification 0012 — Transport and API Profiles

**Status:** Draft  
**Version:** v0.1  
**Milestone:** 12 — Transport & API Profiles  
**Filename:** `specification/0012-transport-and-api-profiles.md`

---

## 1. Abstract

This specification defines the Open Layer Protocol (OLP) v1 transport and API profiles.

It defines:

- transport-independent evidence semantics over standard JSON, CBOR, JSON Text Sequences, and CBOR Sequences;
- a reversible OLP JSON Value Encoding (`OJVE-1`) for byte strings, maps, and large integers;
- textual presentation forms for Record Identity, Proof Identity, and bundle-manifest identity;
- a versioned OLP transport envelope;
- streaming bundle frames;
- an HTTP API profile for capabilities, immutable record retrieval, proof retrieval, bundle retrieval, bundle queries, resolution, disclosure planning, and optional bundle submission;
- HTTP content negotiation using standard media types;
- error handling and structured OLP error codes;
- HTTP digest integration;
- optional HTTP Message Signatures for request/response authentication without replacing OLP object proofs;
- caching, redirects, authentication, authorization, rate limits, and privacy boundaries;
- requirements for immutable-object serving;
- transport neutrality and no dependence of OLP identities on HTTP/JSON serialization;
- conformance requirements; and
- interoperability test cases.

This specification intentionally uses existing standard media types where possible rather than inventing unregistered OLP media types.

OLP evidence identity remains independent of transport.

---

## 2. Scope

This specification answers:

> How can OLP records, proofs, bundles, resolution requests, disclosure requests, and processing results be exchanged over practical network APIs without making HTTP, JSON, or any one server architecture part of the underlying evidence model?

This specification builds on OLP Specifications 0003 through 0011.

It does **not** define:

- a global OLP server;
- a mandatory hosted service;
- a mandatory `.well-known` endpoint;
- a global OLP domain name;
- a mandatory account system;
- a mandatory authentication protocol;
- a mandatory authorization framework;
- a mandatory payment model;
- a global storage service;
- a universal federation protocol;
- a universal replication protocol; or
- a requirement that OLP use HTTP in all deployments.

Non-HTTP transports MAY carry the same abstract OLP objects.

---

## 3. Requirements Language

BCP 14 requirement keywords have the meanings defined by RFC 2119 and RFC 8174 when written in all capitals.

---

## 4. Core Invariants

### 4.1 Transport does not define evidence identity

Record Identity, Proof Identity, and bundle ID MUST NOT depend on whether an object was transported as JSON, CBOR, JSON Sequence, CBOR Sequence, a database row, or another encoding.

### 4.2 Transport security is not OLP proof validity

TLS, HTTP Message Signatures, API authentication, and HTTP digests protect transport or message properties.

They do not replace OLP object-level proof verification.

### 4.3 Object proof validity is not transport authorization

A valid OLP proof does not automatically authorize an HTTP request.

### 4.4 Standard media types are preferred

The v1 HTTP profile uses:

```text
application/json
application/cbor
application/json-seq
application/cbor-seq
application/problem+json
```

where appropriate.

No unregistered `application/olp+...` media type is required.

### 4.5 Content negotiation is explicit

A server MUST NOT send a representation the client explicitly declared unacceptable.

### 4.6 Immutable retrieval verifies identity

A server returning an object under an identity-bearing path MUST ensure the object's recomputed OLP identity matches the requested identity.

### 4.7 HTTP 404 is local

A `404 Not Found` response means the addressed server did not provide the resource under that request context.

It does not establish global nonexistence.

### 4.8 Network APIs preserve structured protocol states

HTTP status codes MUST NOT replace the detailed OLP result status.

### 4.9 JSON mapping is reversible

A conforming JSON transport MUST preserve every abstract OLP v1 value it claims to support without byte-string or map-key ambiguity.

### 4.10 Streaming order is not semantic

Transport frames MAY arrive in any profile-permitted order without implying evidence chronology or trust.

### 4.11 Resource limits are explicit

Servers and clients MUST impose finite limits.

### 4.12 Sensitive exchange requires confidentiality

Public-network deployments exchanging non-public evidence MUST use a secure transport such as HTTPS.

---

## 5. Transport Profiles

OLP v1 defines:

```text
cbor-single-v1
json-single-v1
cbor-sequence-v1
json-sequence-v1
http-read-v1
http-resolution-v1
http-bundle-query-v1
http-disclosure-v1
http-bundle-submission-v1
```

An implementation MAY support only a subset and MUST advertise applicable capabilities according to Specification 0011.

---

## 6. Textual Identity Forms

Binary identities remain authoritative.

Textual forms exist only for transport, logs, paths, and user interfaces.

### 6.1 Record Identity text

A 32-octet Record Identity digest is encoded:

```text
r1_<base64url-no-padding>
```

### 6.2 Proof Identity text

A 32-octet Proof Identity digest is encoded:

```text
p1_<base64url-no-padding>
```

### 6.3 Bundle ID text

Because bundle ID is the Record Identity of the manifest record, the same digest MAY be presented in bundle context as:

```text
b1_<base64url-no-padding>
```

`b1_` does not create a separate identity.

It is a typed transport presentation of the manifest Record Identity.

### 6.4 Encoding

Base64url is as defined by RFC 4648.

Padding `=` MUST be omitted.

For a 32-octet digest, the encoded body MUST contain exactly 43 characters.

Decoders MUST reject:

- standard Base64 `+` or `/`;
- padding;
- whitespace;
- wrong decoded length; and
- non-canonical pad bits.

### 6.5 Equality

Textual prefixes do not change binary equality.

For example, a manifest digest presented as `r1_...` and the same digest presented as `b1_...` refer to the same underlying manifest Record Identity in their respective contexts.

---

## 7. OLP JSON Value Encoding v1 (`OJVE-1`)

### 7.1 Purpose

JSON cannot natively distinguish arbitrary byte strings, non-string map keys, and all large integers in a consistently safe cross-language manner.

`OJVE-1` provides a reversible mapping for abstract OLP values.

### 7.2 Supported abstract values

`OJVE-1` supports:

```text
null
boolean
integer
byte string
text string
array
map
```

Profiles requiring another abstract type MUST use another explicitly defined encoding.

### 7.3 Null, Boolean, and Text

They map directly to JSON `null`, booleans, and strings.

### 7.4 Safe integers

Integers in the inclusive range:

```text
-(2^53 - 1) .. (2^53 - 1)
```

MAY be encoded as JSON numbers without a fractional or exponent part.

### 7.5 Large integers

Other integers MUST be encoded:

```json
{
  "$olp": "int",
  "v": "18446744073709551615"
}
```

`v` is the shortest canonical base-10 representation with optional leading `-` and no leading zeros except `0`.

### 7.6 Byte strings

A byte string is encoded:

```json
{
  "$olp": "bytes",
  "v": "SGVsbG8"
}
```

using base64url without padding.

### 7.7 Arrays

Arrays map recursively to JSON arrays.

### 7.8 Maps

Every abstract OLP map is encoded as:

```json
{
  "$olp": "map",
  "v": [
    [<key>, <value>],
    [<key>, <value>]
  ]
}
```

where keys and values are recursively encoded with `OJVE-1`.

This avoids ambiguity between:

```text
integer key 1
text key "1"
byte-string key h'31'
```

### 7.9 Map order

Map entry order has no semantic meaning.

Senders SHOULD sort entries by the deterministic CBOR encoding of the abstract key when deterministic textual output is useful.

Receivers MUST NOT use JSON order as semantic evidence.

### 7.10 Wrapper validation

An object containing `$olp` is valid only if it exactly matches a defined OJVE wrapper shape.

Unknown `$olp` values MUST yield `UNSUPPORTED_OJVE_TAG`.

Because all abstract OLP maps use the explicit `"map"` wrapper, application data cannot collide with these wrappers.

### 7.11 No floating-point coercion

A JSON parser MUST NOT silently coerce OLP integers into imprecise floating-point values.

### 7.12 Duplicate JSON object names

Every JSON object processed as an OLP transport envelope, OJVE-1 value, conformance-adapter message, or nested OLP JSON structure MUST contain unique member names.

A receiver MUST reject a JSON text containing duplicate object member names before interpreting that object as OLP data. A receiver MUST NOT apply first-wins, last-wins, merge, or parser-specific duplicate-name behavior.

This rule applies recursively at every JSON object nesting level, including wrapper objects and transport metadata.

### 7.13 Parser resource bounds

JSON receivers MUST impose finite input-size and structural-nesting limits before recursively materializing or processing arbitrary attacker-controlled depth. Resource exhaustion MUST NOT be reclassified as valid evidence, successful verification, or proof invalidity.

---

## 8. Single-Object Transport Envelope

### 8.1 Abstract envelope

```text
OLPTransportEnvelopeV1 = [
    "OLP-TRANSPORT",
    1,
    messageType,
    payload
]
```

Exactly four elements.

### 8.2 Core message types

```text
record
proof
bundle
bundleQuery
resolutionRequest
resolutionResult
disclosureRequest
disclosureResult
capabilities
submissionResult
error
```

Third-party message types MUST use absolute URI identifiers.

### 8.3 CBOR single-object encoding

For `application/cbor`, the envelope is encoded directly as CBOR.

Senders SHOULD use deterministic CBOR.

Receivers MUST NOT treat non-deterministic-but-valid transport encoding as changing contained OLP identities.

### 8.4 JSON single-object encoding

For `application/json`, the wire object is:

```json
{
  "olp": 1,
  "type": "record",
  "payload": <OJVE-1 value>
}
```

Unknown top-level members MAY be ignored only if they are explicitly non-critical transport metadata.

Security-relevant extensions require a future transport-envelope version or named critical mechanism.

---

## 9. Streaming Transport

### 9.1 Frame

A streaming item is:

```text
OLPTransportFrameV1 = [
    "OLP-FRAME",
    1,
    frameType,
    payload
]
```

### 9.2 Core frame types

```text
manifest
record
proof
resource
result
end
```

### 9.3 CBOR Sequence

`cbor-sequence-v1` uses RFC 8742 `application/cbor-seq`.

Each sequence item is one CBOR-encoded `OLPTransportFrameV1`.

### 9.4 JSON Text Sequence

`json-sequence-v1` uses RFC 7464 `application/json-seq`.

Each JSON text is the JSON form:

```json
{
  "olpFrame": 1,
  "type": "record",
  "payload": <OJVE-1 value>
}
```

### 9.5 Manifest-first bundle stream

For a manifested bundle stream, the first semantic bundle frame MUST be `manifest`.

Transport-level informational frames before the manifest are not defined in v1.

### 9.6 End frame

An `end` frame MAY provide counts and processing metadata.

Absence of an `end` frame does not change bundle identity.

End-of-transport plus manifest inventory determines whether expected items were missing.

### 9.7 Truncation

A truncated stream MUST produce incomplete transport/bundle processing.

Already verified independent objects MAY remain individually valid.

---

## 10. HTTP API Base URI

An OLP HTTP service is configured or discovered with an absolute **base URI**.

This specification does not derive the base URI from a Principal Identifier.

Discovery MAY use Specification 0009.

All endpoint paths below are relative to:

```text
{base}/v1/
```

A deployment MAY mount the base under any path.

---

## 11. HTTPS Requirement

A public-network OLP HTTP endpoint handling non-public evidence, credentials, authorization data, or authenticated requests MUST use HTTPS.

Plain HTTP MAY be used for:

- loopback development;
- isolated test fixtures; or
- deployments whose security profile explicitly provides equivalent lower-layer protection.

Implementations MUST NOT silently downgrade `https` URLs to `http`.

---

## 12. Capabilities Endpoint

### 12.1 Request

```http
GET {base}/v1/capabilities
```

### 12.2 Response

`200 OK` with `OLPTransportEnvelopeV1` message type `capabilities`.

Conceptual payload:

```text
CapabilitiesV1 = [
    "OLP-CAPABILITIES",
    1,
    protocolDraft,
    capabilities,
    mediaTypes,
    limits,
    extensions
]
```

### 12.3 Semantics

Capabilities describe this endpoint's implementation/configuration.

They are not a guarantee of availability.

A server SHOULD avoid advertising disabled capabilities.

---

## 13. Record Retrieval

### 13.1 Request

```http
GET {base}/v1/records/{recordIdText}
```

### 13.2 Server validation

Before returning `200`, the server MUST:

1. decode the requested textual Record Identity;
2. obtain the candidate record;
3. recompute Record Identity under Specification 0003;
4. compare it byte-for-byte.

Mismatch MUST NOT return a successful record representation.

### 13.3 Success

`200 OK`, message type `record`.

### 13.4 Not found

`404 Not Found` means only that this server did not provide the requested record in this request context.

---

## 14. Proof Retrieval

### 14.1 Request

```http
GET {base}/v1/proofs/{proofIdText}
```

### 14.2 Server validation

The server MUST recompute Proof Identity under Specification 0005 before successful response.

### 14.3 Success

`200 OK`, message type `proof`.

---

## 15. Bundle Retrieval

### 15.1 Request

```http
GET {base}/v1/bundles/{bundleIdText}
```

### 15.2 Identity

`bundleIdText` decodes to the manifest Record Identity.

### 15.3 Success

A server MAY return:

- a single bundle envelope using `application/cbor` or `application/json`; or
- a stream using `application/cbor-seq` or `application/json-seq`.

The manifest record MUST match the requested bundle ID.

---

## 16. Bundle Query

### 16.1 Request

```http
POST {base}/v1/bundles/query
```

with message type `bundleQuery`.

### 16.2 Exact request

```text
BundleQueryRequestV1 = [
    "OLP-BUNDLE-QUERY",
    1,
    roots,
    profile,
    requiredCapabilities,
    options
]
```

### 16.3 Semantics

This operation asks the server to construct or return an evidence bundle for known roots.

It is not a universal search API.

### 16.4 Success

`200 OK` with a bundle or bundle stream.

If the server cannot satisfy a mandatory self-contained requirement, it MUST return a structured failure rather than silently downgrade to `portable`.

---

## 17. Resolution API

### 17.1 Request

```http
POST {base}/v1/resolve
```

message type `resolutionRequest`.

Payload is `ResolutionRequestV1` from Specification 0009.

### 17.2 Success

`200 OK` message type `resolutionResult`.

A resolution result can semantically be `NOT_FOUND`, `UNAVAILABLE`, or `AMBIGUOUS` while HTTP transport itself succeeded.

Therefore these semantic statuses SHOULD normally be carried in a successful `200` response when the server successfully executed the resolution operation.

HTTP `404` is reserved for the API resource itself being absent or for direct immutable-object retrieval.

---

## 18. Disclosure API

### 18.1 Request

```http
POST {base}/v1/disclose
```

with message type `disclosureRequest`.

### 18.2 Success

`200 OK` with:

- `disclosureResult`; or
- a bundle if the request explicitly asks the server to return the constructed disclosure bundle.

### 18.3 Authorization

A server MUST apply its own access-control policy before disclosing evidence.

A successful OLP evidence proof does not authorize disclosure by itself.

---

## 19. Optional Bundle Submission

### 19.1 Request

An endpoint advertising `http-bundle-submission-v1` accepts:

```http
POST {base}/v1/bundles
```

with a manifested bundle.

### 19.2 Semantics

Transport acceptance MUST NOT be described as trust acceptance.

A server MAY:

- validate structure;
- verify selected proofs;
- store content;
- queue processing;
- reject according to local policy.

### 19.3 Response statuses

Conceptual `SubmissionResultV1`:

```text
[
    "OLP-SUBMISSION-RESULT",
    1,
    status,
    bundleId,
    receiptUri,
    warnings,
    errors
]
```

Core statuses:

```text
ACCEPTED_FOR_PROCESSING
STORED
REJECTED
PARTIALLY_ACCEPTED
```

### 19.4 HTTP status

Typical mappings:

```text
200 OK       -> processed synchronously
201 Created  -> stored as a new server resource
202 Accepted -> queued/accepted for later processing
4xx          -> request/client/profile failure
5xx          -> server processing failure
```

A `201` or `202` does not mean contained claims are true or trusted.

---

## 20. Content Negotiation

Clients SHOULD send `Accept`.

Servers MUST respect standard HTTP negotiation semantics.

At minimum, an HTTP Exchange Node SHOULD support:

```text
application/cbor
application/json
```

for single messages.

A streaming-capable node SHOULD support at least one of:

```text
application/cbor-seq
application/json-seq
```

If no acceptable representation exists, the server SHOULD return `406 Not Acceptable`.

---

## 21. Request Content Types

Servers MUST validate `Content-Type` on requests with content.

Unsupported content type SHOULD return:

```text
415 Unsupported Media Type
```

A body declared as JSON but not valid according to the required OLP envelope and OJVE mapping is malformed application input.

---

## 22. HTTP Digest Fields

Implementations MAY use RFC 9530 `Content-Digest` or `Repr-Digest`.

For state-changing or large bundle submissions, clients and servers SHOULD support `Content-Digest` when operationally practical.

Digest validation protects HTTP content integrity.

It does not replace:

- Record Identity;
- Proof Identity;
- resource commitments;
- bundle manifest identity; or
- OLP proof verification.

For streamed content, an implementation MAY use trailers when supported by the HTTP stack and profile.

---

## 23. HTTP Message Signatures

RFC 9421 HTTP Message Signatures MAY be used for:

- request authentication;
- response authentication;
- authorization protocols;
- gateway-to-origin integrity; or
- audit requirements.

An HTTP Message Signature and an OLP proof have different scopes.

```text
HTTP signature -> HTTP message components
OLP proof      -> exact OLP record Proof Input
```

A valid HTTP Message Signature MUST NOT be treated as an OLP proof unless an explicit profile creates separate corresponding OLP evidence.

---

## 24. Authentication and Authorization

This specification does not mandate OAuth, GNAP, mutual TLS, API keys, HTTP Message Signatures, or another authentication system.

Servers MUST document or advertise required authentication separately.

Authorization to:

- retrieve a record;
- retrieve a bundle;
- resolve a principal;
- disclose sensitive evidence; or
- submit a bundle

is an HTTP service policy decision.

---

## 25. Errors

### 25.1 Transport versus OLP errors

The HTTP status code describes the HTTP/API operation.

The OLP error code describes protocol processing.

### 25.2 JSON problem details

When returning a conventional JSON HTTP error outside an OLP envelope, a server SHOULD use RFC 9457 `application/problem+json`.

An OLP problem detail SHOULD include an extension member:

```json
"olpCode": "RESOURCE_DIGEST_MISMATCH"
```

when a stable OLP reason code exists.

### 25.3 OLP error envelope

For negotiated OLP content, an error MAY be returned as message type `error`:

```text
OLPErrorV1 = [
    "OLP-ERROR",
    1,
    code,
    title,
    detail,
    instance,
    diagnostics
]
```

`detail` and `diagnostics` MUST avoid leaking sensitive internal state.

---

## 26. Recommended HTTP Status Mapping

Typical mappings:

```text
400 Bad Request
    malformed envelope, invalid textual ID, malformed request

401 Unauthorized
    authentication required or failed

403 Forbidden
    authenticated caller lacks service permission

404 Not Found
    direct addressed API resource unavailable at this server

406 Not Acceptable
    no acceptable representation

409 Conflict
    submission conflicts with local immutable-object/storage policy

413 Content Too Large
    configured request-size limit exceeded

415 Unsupported Media Type
    request media type unsupported

422 Unprocessable Content
    syntactically transport-valid request with semantic profile failure

429 Too Many Requests
    service rate limit

500 Internal Server Error
    unexpected server failure

503 Service Unavailable
    temporary endpoint/service dependency unavailable
```

Semantic OLP result codes remain required where applicable.

---

## 27. Redirects

Clients SHOULD NOT automatically follow redirects for security-sensitive POST operations unless policy permits them.

For immutable GET retrieval, redirects MAY be followed under the resolver/network policy from Specification 0009.

A redirect MUST NOT change the requested Record Identity or Proof Identity.

Credentials MUST NOT be forwarded to unrelated redirect targets without explicit authorization.

---

## 28. Caching

OLP records and proofs are immutable by identity.

HTTP representations, however, can differ by media type or content coding.

Servers MAY use HTTP caching.

They MUST ensure validators and cache metadata are correct for the selected HTTP representation.

An object identity digest MUST NOT automatically be used as a strong HTTP ETag across byte-different JSON and CBOR representations.

Sensitive evidence SHOULD NOT be marked publicly cacheable unless application policy explicitly allows it.

---

## 29. Conditional Requests

Servers MAY support HTTP conditional requests.

Conditional transport semantics do not alter OLP identity semantics.

A `304 Not Modified` response refers to the HTTP representation validator, not a new OLP proof of historical persistence.

---

## 30. Pagination

Immutable object retrieval is not paginated.

Large graph queries or server-specific search APIs MAY paginate, but pagination is outside core resolution-by-identity semantics.

Bundle query SHOULD prefer streaming over pagination when the result is one manifested bundle, because arbitrary page boundaries are not bundle semantics.

---

## 31. Range Requests

Servers MAY support HTTP byte ranges for stored representations.

A partial byte range is not a complete OLP object unless the object format/profile explicitly permits independent partial verification.

Clients MUST NOT attempt Record Identity or Proof Identity verification over incomplete transport bytes as if they were the full abstract object.

---

## 32. Rate Limits and Quotas

Servers MAY apply rate limits and quotas.

A rate-limit response MUST NOT be represented as evidence `INVALID`.

Where practical, `429 Too Many Requests` SHOULD include standard retry guidance.

Rate-limit identifiers and diagnostics SHOULD avoid leaking sensitive account or policy information.

---

## 33. Request Size and Processing Limits

Servers MUST configure finite limits for:

- request body size;
- bundle object count;
- bundle resource bytes;
- decompressed size;
- graph traversal;
- resolution recursion;
- cryptographic operations;
- concurrent requests;
- processing time.

A server MAY reject a conforming but excessive request.

---

## 34. Compression

Standard HTTP content codings MAY be used.

OLP identities are computed from abstract/canonical OLP rules, never from compressed transport bytes.

Clients and servers MUST protect against decompression bombs.

---

## 35. Privacy

HTTP endpoints can expose evidence through:

- access logs;
- URLs;
- query strings;
- referrer behavior;
- proxy logs;
- DNS;
- TLS metadata;
- response sizes;
- timing.

Therefore:

- sensitive identifiers SHOULD NOT be placed in URL query strings when a POST request body can express the operation;
- bundle and disclosure queries use POST in this profile;
- servers SHOULD minimize sensitive error details;
- clients SHOULD follow Specification 0010 resolver/disclosure minimization guidance;
- operators SHOULD treat logs as sensitive data where appropriate.

Direct record/proof GET paths necessarily contain content identifiers; those identifiers can still be correlating information.

---

## 36. CORS and Browser Clients

Cross-Origin Resource Sharing policy is deployment-specific.

Servers MUST NOT enable permissive cross-origin access to sensitive evidence merely for convenience.

Browser-exposed endpoints SHOULD account for credential mode, preflight behavior, response caching, and referrer leakage.

---

## 37. Capability Negotiation

Before using optional operations, a client SHOULD obtain capabilities or rely on trusted configuration/discovery.

Capability negotiation MUST NOT override explicit caller security requirements.

If the client requires:

```text
selfContainedVerification
```

and the server advertises only portable bundles, the client MUST NOT silently downgrade.

---

## 38. API Versioning

The path segment:

```text
/v1/
```

identifies the HTTP API major version.

It does not replace the versions inside OLP evidence structures.

A future `/v2/` API might transport unchanged OLP v1 records.

Similarly, `/v1/` may transport future evidence versions only when its capability contract explicitly supports them.

---

## 39. Unknown Fields and Forwarding

Transport envelopes SHOULD be versioned rather than relying on arbitrary unknown security-relevant top-level members.

Proxies that do not understand payload semantics MAY forward byte content but MUST NOT claim semantic conformance.

Criticality inside OLP evidence structures remains governed by the relevant core specification.

---

## 40. Streaming Bundle Verification Algorithm

For a manifested CBOR/JSON sequence:

1. parse the manifest frame;
2. validate and index the manifest record;
3. compute bundle ID;
4. initialize expected inventory;
5. for each record frame:
   - parse;
   - recompute Record Identity;
   - match against inventory;
   - index;
6. for each proof frame:
   - parse;
   - recompute Proof Identity;
   - match;
   - optionally verify when target and verification material are available;
7. for each resource frame:
   - validate `ResourceRefV1`;
   - hash bytes;
   - match digest;
   - index;
8. preserve unexpected frames/items separately;
9. on end-of-stream, report missing inventory;
10. never treat frame order as evidence order.

---

## 41. HTTP Read Profile Conformance

A `transport-http-reader-v1` client MUST:

- support HTTPS;
- support `application/cbor` or `application/json`;
- validate transport envelope version/type;
- validate textual identity forms;
- recompute object identities after retrieval;
- distinguish HTTP failure from OLP semantic failure;
- enforce response-size limits.

A stronger Exchange Node SHOULD support both JSON and CBOR.

---

## 42. HTTP Server Conformance

A `transport-http-server-v1` server MUST implement:

```text
GET /v1/capabilities
GET /v1/records/{id}
GET /v1/proofs/{id}
```

and at least one bundle exchange operation:

```text
GET  /v1/bundles/{id}
POST /v1/bundles/query
```

It MUST:

- validate successful object identity;
- support content negotiation;
- return structured errors;
- enforce finite limits;
- not claim network-global nonexistence from local misses.

Optional resolution/disclosure/submission operations require their corresponding capabilities.

---

## 43. Interoperability Test Cases

### 43.1 Record JSON/CBOR equivalence

Same record transported via JSON OJVE and CBOR.

Expected:

```text
same abstract record
same Record Identity
```

### 43.2 Proof JSON/CBOR equivalence

Same proof transported in both encodings.

Expected:

```text
same ProofInputV1
same proofValue bytes
same Proof Identity
```

### 43.3 Byte-string preservation

JSON byte wrapper contains 32-byte digest.

Expected exact round trip.

### 43.4 Large integer preservation

Integer greater than `2^53 - 1` uses tagged decimal wrapper.

Expected exact integer round trip.

### 43.5 Map key distinction

Map contains integer key `1` and text key `"1"`.

Expected both remain distinct.

### 43.6 Wrong record path

Server candidate record does not match requested `r1_...`.

Expected no `200` record response.

### 43.7 Resolution not found

`POST /resolve` executes correctly but finds no object.

Expected:

```text
HTTP 200
resolution status = NOT_FOUND
```

unless the request itself was malformed.

### 43.8 Self-contained downgrade prevention

Client requests self-contained bundle; server cannot supply verification material.

Expected structured failure; no silent portable bundle.

### 43.9 Streaming order

Proof/resource frames swapped.

Expected same bundle semantic result.

### 43.10 Truncated stream

Stream ends before required inventory item.

Expected:

```text
bundle processing = INCOMPLETE
present independent objects retain individual validity
```

### 43.11 Digest mismatch

HTTP `Content-Digest` is wrong but inner OLP objects would otherwise verify.

Expected transport integrity failure.

The client MUST NOT silently ignore a required validated digest.

### 43.12 HTTP signature versus OLP proof

HTTP request signature valid; contained OLP proof invalid.

Expected:

```text
HTTP authentication may succeed
OLP cryptographicValidity = INVALID
```

No conflation.

---

## 44. Security Considerations

### 44.1 Parser differentials

JSON and CBOR parsers can disagree on numbers, duplicate keys, Unicode handling, and invalid encodings.

OJVE-1 and strict OLP structural validation are intended to reduce ambiguity. JSON inputs with duplicate object names MUST be rejected as required by Section 7.12 rather than resolved according to parser-specific first-wins or last-wins behavior.

Implementations SHOULD apply input-size, nesting, and collection limits before expensive decoding, canonicalization, graph expansion, or cryptographic work.

### 44.2 HTTP intermediaries

Proxies can transform HTTP messages.

Object-level OLP proofs protect evidence semantics independent of normal transport transformations.

### 44.3 SSRF

Resolution/disclosure endpoints MUST apply Specification 0009 network policy and MUST NOT become generic attacker-controlled URL fetchers.

### 44.4 Authorization bypass

Possessing a Record ID or Bundle ID is not authorization to retrieve it.

### 44.5 Identifier enumeration

Content identifiers can sometimes be guessed from known public content and used to test whether a server stores it.

Access control must not rely solely on identifier secrecy.

### 44.6 Error leakage

Diagnostics can expose existence, access-control decisions, filesystem paths, resolver configuration, or internal network information.

### 44.7 Submission abuse

Bundle-submission endpoints need quotas, authentication where appropriate, malware/resource scanning policies for opaque external resources, and storage controls.

### 44.8 Replay

HTTP request replay and portable evidence replay are separate concerns.

Application protocols requiring freshness SHOULD use suitable request-authentication mechanisms and OLP proof challenge/domain semantics.

---

## 45. Design Summary

```text
                    OLP semantic objects
                            |
             +--------------+--------------+
             |                             |
             v                             v
       CBOR transport                 JSON OJVE-1
             |                             |
             +--------------+--------------+
                            |
                     OLP envelope
                            |
             +--------------+--------------+
             |                             |
             v                             v
           HTTP                       other transport
             |
      +------+------+------+------+------+
      |      |      |      |      |      |
      v      v      v      v      v      v
 capabilities records proofs bundles resolve disclose
```

The architecture preserves:

```text
Record Identity  != JSON bytes
Proof Identity   != HTTP message
bundle ID        != stream order
TLS security     != OLP proof validity
HTTP auth        != OLP authority evidence
HTTP 404         != global nonexistence
transport digest != evidence trust
```

The essential invariant is:

> **OLP can move over ordinary Internet protocols without allowing transport representation or server behavior to redefine the evidence itself.**

---

## 46. References

### 46.1 Normative OLP references

- OLP Specifications 0003 through 0011.

### 46.2 Normative Internet references

- RFC 2119 — Requirements Language.
- RFC 8174 — BCP 14 clarification.
- RFC 3986 — URI Generic Syntax.
- RFC 4648 — Base-N Encodings.
- RFC 7464 — JSON Text Sequences.
- RFC 8259 — JSON.
- RFC 8742 — CBOR Sequences.
- RFC 8949 — CBOR.
- RFC 9110 — HTTP Semantics.
- RFC 9457 — Problem Details for HTTP APIs.
- RFC 9530 — Digest Fields.

### 46.3 Informative references

- RFC 8288 — Web Linking.
- RFC 9421 — HTTP Message Signatures.
- RFC 9651 — Structured Field Values for HTTP.
- RFC 9290 — Concise Problem Details for constrained environments.

---

## 47. Deferred Work

Deferred topics include:

- IANA registration of OLP-specific media types if later justified;
- standardized `.well-known` discovery;
- WebSocket transport;
- QUIC-native transport;
- message-queue profiles;
- peer-to-peer replication;
- synchronization/change feeds;
- subscriptions;
- GraphQL profiles;
- gRPC/protobuf profiles;
- CoAP profiles;
- resumable chunk upload;
- standardized authorization scopes;
- federation;
- privacy relays; and
- server-to-server push.

---

**End of OLP Specification 0012 — Draft v0.1**
