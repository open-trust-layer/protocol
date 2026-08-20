from __future__ import annotations
import hashlib
from olp.encoding.record_identity import record_identity
from olp.model.bundle import ResourceRefV1
from olp.model.evidence import EvidenceKind, EvidenceRefV1
from olp.model.record import RecordV1
from olp.model.resolution import ResolutionRequestV1
from olp.resolution import resolve_request

def claim(text="example"): return RecordV1(1,"claim",{"subject":"urn:example:subject:1","statement":text})
def evidence_request(ref,**options): return ResolutionRequestV1("evidence",ref.to_value(),options={0:options.get("offline",True)})

def test_bundle_evidence_hit_recomputes_identity():
    rec=claim(); ref=EvidenceRefV1(EvidenceKind.RECORD,record_identity(rec)); out=resolve_request(evidence_request(ref),sources=[{"source_class":"bundle","source_identifier":"urn:bundle:test","candidates":[{"lookup_ref":ref.to_value(),"record":rec}]}]); assert out["status"]=="RESOLVED" and out["network_requests"]==0

def test_wrong_object_under_lookup_key_is_identity_mismatch():
    rec=claim(); wrong=claim("wrong"); ref=EvidenceRefV1(0,record_identity(rec)); out=resolve_request(evidence_request(ref),sources=[{"source_class":"localStore","source_identifier":"urn:store:test","candidates":[{"lookup_ref":ref.to_value(),"record":wrong}]}]); assert out["status"]=="IDENTITY_MISMATCH" and out["errors"]==["RESOLVED_IDENTITY_MISMATCH"]

def test_offline_miss_never_networks():
    rec=claim(); ref=EvidenceRefV1(0,record_identity(rec)); out=resolve_request(evidence_request(ref),sources=[]); assert out["status"]=="NOT_FOUND" and out["network_requests"]==0

def test_network_disabled_is_explicit():
    req=ResolutionRequestV1("externalResource","https://example.org/a",options={0:True}); out=resolve_request(req,sources=[{"source_class":"network","source_identifier":"urn:net:test","status":"resolved"}]); assert out["status"]=="POLICY_BLOCKED" and out["errors"]==["NETWORK_ACCESS_DISABLED"]

def test_private_address_blocked_before_network_request():
    req=ResolutionRequestV1("externalResource","http://127.0.0.1/admin",options={0:False}); out=resolve_request(req,sources=[{"source_class":"network","source_identifier":"urn:net:test","status":"resolved"}]); assert out["status"]=="POLICY_BLOCKED" and out["network_requests"]==0

def test_redirect_disabled_is_explicit():
    req=ResolutionRequestV1("externalResource","https://example.org/a",options={0:False,3:False}); out=resolve_request(req,sources=[{"source_class":"network","source_identifier":"urn:net:test","redirects":["https://example.org/b"],"status":"resolved"}]); assert out["errors"]==["REDIRECT_BLOCKED"] and out["network_requests"]==0

def test_resource_ref_bundle_hit_checks_digest():
    content=b"resource"; rr=ResourceRefV1("https://example.org/r","application/octet-stream",-16,hashlib.sha256(content).digest()); req=ResolutionRequestV1("externalResource",rr.to_value(),options={0:True}); out=resolve_request(req,sources=[{"source_class":"bundle","source_identifier":"urn:bundle:r","resources":[{"ref":rr,"content":content}]}]); assert out["status"]=="RESOLVED"

def test_resolution_loop_is_not_evidence_invalidity():
    req=ResolutionRequestV1("externalResource","https://example.org/a",options={0:False,3:True}); out=resolve_request(req,sources=[{"source_class":"network","source_identifier":"urn:net:test","chain":["https://example.org/a","https://example.org/b","https://example.org/a"],"status":"resolved"}]); assert out["status"]=="LIMIT_EXCEEDED" and out["errors"]==["RESOLUTION_LOOP"]

def test_network_non_http_scheme_is_unsupported_not_dereferenced():
    req=ResolutionRequestV1("externalResource","urn:example:resource",options={0:False}); out=resolve_request(req,sources=[{"source_class":"network","source_identifier":"urn:net:test","status":"resolved"}]); assert out["status"]=="UNSUPPORTED" and out["errors"]==["UNSUPPORTED_IDENTIFIER_SCHEME"] and out["network_requests"]==0

def test_redirect_to_private_address_is_blocked_before_network_request():
    req=ResolutionRequestV1("externalResource","https://example.org/a",options={0:False,3:True}); out=resolve_request(req,sources=[{"source_class":"network","source_identifier":"urn:net:test","redirects":["http://127.0.0.1/admin"],"status":"resolved"}]); assert out["status"]=="POLICY_BLOCKED" and out["errors"]==["RESOLUTION_POLICY_BLOCKED"] and out["network_requests"]==0

def test_max_bytes_blocks_packaged_resource():
    content=b"resource"; rr=ResourceRefV1("https://example.org/r","application/octet-stream",-16,hashlib.sha256(content).digest()); req=ResolutionRequestV1("externalResource",rr.to_value(),options={0:True,1:3}); out=resolve_request(req,sources=[{"source_class":"bundle","source_identifier":"urn:bundle:r","resources":[{"ref":rr,"content":content}]}]); assert out["status"]=="LIMIT_EXCEEDED" and out["errors"]==["RESOLUTION_LIMIT_EXCEEDED"]

def test_require_fresh_rejects_stale_local_match():
    rec=claim(); ref=EvidenceRefV1(0,record_identity(rec)); req=ResolutionRequestV1("evidence",ref.to_value(),options={0:True,4:True}); out=resolve_request(req,sources=[{"source_class":"bundle","source_identifier":"urn:bundle:test","freshness":"STALE","candidates":[{"lookup_ref":ref.to_value(),"record":rec}]}]); assert out["status"]=="POLICY_BLOCKED" and out["errors"]==["FRESHNESS_REQUIREMENT_NOT_MET"]

def test_require_fresh_network_snapshot_counts_request_after_preflight():
    req=ResolutionRequestV1("externalResource","https://example.org/a",options={0:False,4:True}); out=resolve_request(req,sources=[{"source_class":"network","source_identifier":"urn:net:test","freshness":"STALE","status":"resolved"}]); assert out["status"]=="POLICY_BLOCKED" and out["errors"]==["FRESHNESS_REQUIREMENT_NOT_MET"] and out["network_requests"]==1
