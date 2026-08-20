# Milestone 24 Streaming & HTTP Vector Index

Profile: `streaming-http-v1`

Capabilities:

```text
olp.streaming-transport.v1
olp.http-api.v1
```

Total cases: **36**

## Streaming transport — 13 cases

| Case | Category | Operation |
|---|---|---|
| `m24.stream.frame-wire.001` | positive | `encode_stream_frame` |
| `m24.stream.sequence-wire.001` | positive | `encode_stream_sequence` |
| `m24.stream.bundle-complete.001` | positive | `process_bundle_stream` |
| `m24.stream.order-record-resource.001` | positive | `process_bundle_stream` |
| `m24.stream.order-resource-record.001` | positive | `process_bundle_stream` |
| `m24.stream.truncated.001` | negative | `process_bundle_stream` |
| `m24.stream.end-optional.001` | positive | `process_bundle_stream` |
| `m24.stream.invalid-resource-complete.001` | negative | `process_bundle_stream` |
| `m24.stream.manifest-not-first.001` | malformed | `process_bundle_stream` |
| `m24.stream.duplicate-manifest.001` | malformed | `process_bundle_stream` |
| `m24.stream.frame-after-end.001` | malformed | `process_bundle_stream` |
| `m24.stream.version.001` | unsupported | `process_bundle_stream` |
| `m24.stream.type.001` | unsupported | `process_bundle_stream` |

## HTTP API semantics — 23 cases

| Case | Category | Operation |
|---|---|---|
| `m24.http.read-record.001` | positive | `evaluate_http_read` |
| `m24.http.read-identity-mismatch.001` | negative | `evaluate_http_read` |
| `m24.http.read-local-not-found.001` | negative | `evaluate_http_read` |
| `m24.http.read-auth-missing.001` | negative | `evaluate_http_read` |
| `m24.http.read-auth-denied.001` | negative | `evaluate_http_read` |
| `m24.http.read-not-acceptable.001` | negative | `evaluate_http_read` |
| `m24.http.operation-unsupported-media.001` | negative | `evaluate_http_operation` |
| `m24.http.resolution-not-found.001` | positive | `evaluate_http_operation` |
| `m24.http.bundle-self-contained.001` | negative | `evaluate_http_operation` |
| `m24.http.content-digest-valid.001` | positive | `validate_content_digest` |
| `m24.http.content-digest-mismatch.001` | negative | `validate_content_digest` |
| `m24.http.content-digest-length.001` | malformed | `validate_content_digest` |
| `m24.http.content-digest-missing.001` | negative | `validate_content_digest` |
| `m24.http.redirect-https-downgrade.001` | negative | `evaluate_http_redirect` |
| `m24.http.redirect-identity-change.001` | negative | `evaluate_http_redirect` |
| `m24.http.redirect-cross-origin-no-creds.001` | positive | `evaluate_http_redirect` |
| `m24.http.redirect-post-blocked.001` | negative | `evaluate_http_redirect` |
| `m24.http.auth-proof-separated.001` | positive | `separate_http_auth_from_olp` |
| `m24.http.cache-representation-specific.001` | positive | `evaluate_http_cache` |
| `m24.http.cache-sensitive-public.001` | negative | `evaluate_http_cache` |
| `m24.http.range-partial.001` | negative | `evaluate_http_range` |
| `m24.http.limit-413.001` | negative | `evaluate_http_limit` |
| `m24.http.rate-limit-429.001` | negative | `evaluate_http_rate_limit` |

## Important fixture boundaries

The exact frame/sequence cases pin producer wire bytes for RFC 7464 JSON Text Sequences and self-delimiting CBOR Sequences.

The stream semantic cases operate on **already-parsed frame objects**. They do not certify a complete hostile-input JSON-sequence parser or general CBOR decoder.

HTTP `Accept` fixtures contain **already-parsed media ranges** relevant to OLP negotiation. They do not represent a second complete raw HTTP-field parser.

`Content-Digest` fixtures contain **already-parsed RFC 9530 dictionary members** as algorithm identifiers plus digest bytes. RFC 8941 Structured Fields parsing remains the HTTP stack's responsibility.

The profile is additive and does not modify `core-v1` or any previously accepted higher-layer profile.
