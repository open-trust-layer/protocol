fn resource_ref_json_from_projection(v: &Json) -> Result<ResourceRef, OlpError> {
    parse_resource_ref(v)
}

fn resource_eq(a: &ResourceRef, b: &ResourceRef) -> bool {
    a == b
}

fn resolve_resource(req: &Request, sources: &[Json]) -> Result<Json, OlpError> {
    let (target_uri, target_ref) = match &req.target {
        Json::String(s) => (Some(s.clone()), None),
        Json::Object(m) if m.len() == 1 && m.contains_key("resource_ref") => {
            let rr = resource_ref_json_from_projection(m.get("resource_ref").expect("checked key"))?;
            (rr.resource_id.clone(), Some(rr))
        }
        _ => {
            return Err(malformed(
                "MALFORMED_RESOLUTION_REQUEST",
                "external resource target malformed",
            ))
        }
    };

    let mut freshness_blocked = false;

    // Package/local hits are attempted before any network-policy decision.
    for (source_index, sv) in sources.iter().enumerate() {
        let s = sv
            .as_object()
            .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?;
        let class = match s.get("source_class") {
            Some(Json::String(value)) => value.as_str(),
            _ => continue,
        };
        if class != "bundle" && class != "localStore" {
            continue;
        }

        let resources = match s.get("resources") {
            None => &[][..],
            Some(value) => value
                .as_array()
                .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?,
        };

        for rv in resources {
            let ro = rv
                .as_object()
                .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?;
            let rr = resource_ref_json_from_projection(
                ro.get("resource_ref")
                    .ok_or_else(|| malformed("RESOLVER_RESPONSE_MALFORMED", "missing resource_ref"))?,
            )?;

            if let Some(target) = &target_ref {
                if !resource_eq(target, &rr) {
                    continue;
                }
            } else if rr.resource_id != target_uri {
                continue;
            }
            if !req.accept.is_empty() && !req.accept.contains(&rr.media_type) {
                continue;
            }

            let content_hex = ro
                .get("content_hex")
                .ok_or_else(|| malformed("RESOLVER_RESPONSE_MALFORMED", "missing content_hex"))?
                .as_str()
                .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?;
            let content = hex_decode(content_hex)
                .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?;
            if size_exceeds(req, content.len() as u64) {
                return Ok(Json::Object(base(
                    "LIMIT_EXCEEDED",
                    vec!["RESOLUTION_LIMIT_EXCEEDED"],
                    vec![],
                    0,
                    "NOT_APPLICABLE",
                )));
            }

            if rr.algorithm == -16 && sha256::digest(&content) != rr.digest {
                let mut out = base(
                    "IDENTITY_MISMATCH",
                    vec!["RESOURCE_DIGEST_MISMATCH"],
                    vec![],
                    0,
                    "NOT_APPLICABLE",
                );
                let mut conflict = Json::object();
                conflict.insert(
                    "resource_id".into(),
                    rr.resource_id.clone().map(Json::String).unwrap_or(Json::Null),
                );
                conflict.insert("source_index".into(), Json::Int(source_index as i128));
                out.insert("conflicts".into(), Json::Array(vec![Json::Object(conflict)]));
                return Ok(Json::Object(out));
            }

            let freshness = source_freshness(s)?;
            if req.require_fresh && freshness != "FRESH" {
                freshness_blocked = true;
                continue;
            }

            let source_identifier = match s.get("source_identifier") {
                Some(Json::String(value)) => Some(value.clone()),
                None | Some(Json::Null) => None,
                Some(_) => {
                    return Err(malformed(
                        "RESOLVER_RESPONSE_MALFORMED",
                        "source identifier malformed",
                    ))
                }
            };

            let mut out = base("RESOLVED", vec![], vec![], 0, &freshness);
            let mut matched = Json::object();
            matched.insert(
                "resource_id".into(),
                rr.resource_id.clone().map(Json::String).unwrap_or(Json::Null),
            );
            matched.insert("digest_hex".into(), Json::String(hex_encode(&rr.digest)));
            matched.insert("source_class".into(), Json::String(class.into()));
            matched.insert(
                "source_identifier".into(),
                source_identifier.clone().map(Json::String).unwrap_or(Json::Null),
            );
            out.insert("matches".into(), Json::Array(vec![Json::Object(matched)]));

            let mut provenance = Json::object();
            provenance.insert("source_class".into(), Json::String(class.into()));
            provenance.insert(
                "source_identifier".into(),
                source_identifier.map(Json::String).unwrap_or(Json::Null),
            );
            provenance.insert("source_index".into(), Json::Int(source_index as i128));
            out.insert(
                "provenance".into(),
                Json::Array(vec![Json::Object(provenance)]),
            );
            return Ok(Json::Object(out));
        }
    }

    if freshness_blocked {
        return Ok(Json::Object(base(
            "POLICY_BLOCKED",
            vec!["FRESHNESS_REQUIREMENT_NOT_MET"],
            vec![],
            0,
            "NOT_APPLICABLE",
        )));
    }

    let network: Vec<(usize, &BTreeMap<String, Json>)> = sources
        .iter()
        .enumerate()
        .filter_map(|(index, value)| {
            value.as_object().ok().and_then(|object| match object.get("source_class") {
                Some(Json::String(class)) if class == "network" => Some((index, object)),
                _ => None,
            })
        })
        .collect();

    if req.offline_only || network.is_empty() {
        return Ok(Json::Object(base(
            "POLICY_BLOCKED",
            vec!["NETWORK_ACCESS_DISABLED"],
            vec![],
            0,
            "NOT_APPLICABLE",
        )));
    }

    let Some(uri) = target_uri else {
        return Ok(Json::Object(base(
            "UNSUPPORTED",
            vec!["UNSUPPORTED_IDENTIFIER_SCHEME"],
            vec![],
            0,
            "NOT_APPLICABLE",
        )));
    };
    if !is_absolute_uri(&uri) || !matches!(uri_scheme(&uri), "http" | "https") {
        return Ok(Json::Object(base(
            "UNSUPPORTED",
            vec!["UNSUPPORTED_IDENTIFIER_SCHEME"],
            vec![],
            0,
            "NOT_APPLICABLE",
        )));
    }
    if blocked_network_target(&uri) {
        return Ok(Json::Object(base(
            "POLICY_BLOCKED",
            vec!["RESOLUTION_POLICY_BLOCKED"],
            vec![],
            0,
            "NOT_APPLICABLE",
        )));
    }

    // Network sources are deterministic snapshots. No network I/O occurs here.
    for (source_index, s) in network {
        let chain = match s.get("chain") {
            None => &[][..],
            Some(value) => value
                .as_array()
                .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?,
        };
        if chain.len() > 32 {
            return Ok(Json::Object(base(
                "LIMIT_EXCEEDED",
                vec!["RESOLUTION_LIMIT_EXCEEDED"],
                vec![],
                0,
                "NOT_APPLICABLE",
            )));
        }

        let mut seen = BTreeSet::new();
        let mut chain_strings = Vec::with_capacity(chain.len());
        for value in chain {
            let item = value
                .as_str()
                .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?;
            if !is_absolute_uri(item) {
                return Err(malformed(
                    "RESOLVER_RESPONSE_MALFORMED",
                    "network chain identifier malformed",
                ));
            }
            chain_strings.push(item.to_string());
            if !seen.insert(item.to_string()) {
                return Ok(Json::Object(base(
                    "LIMIT_EXCEEDED",
                    vec!["RESOLUTION_LOOP"],
                    chain_strings,
                    0,
                    "NOT_APPLICABLE",
                )));
            }
            if blocked_network_target(item) {
                return Ok(Json::Object(base(
                    "POLICY_BLOCKED",
                    vec!["RESOLUTION_POLICY_BLOCKED"],
                    chain_strings,
                    0,
                    "NOT_APPLICABLE",
                )));
            }
        }

        let redirects = match s.get("redirects") {
            None => Vec::new(),
            Some(value) => value
                .as_array()
                .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?
                .iter()
                .map(|item| {
                    item.as_str()
                        .map(str::to_string)
                        .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))
                })
                .collect::<Result<Vec<_>, _>>()?,
        };
        for item in &redirects {
            if !is_absolute_uri(item) {
                return Err(malformed(
                    "RESOLVER_RESPONSE_MALFORMED",
                    "redirect identifier malformed",
                ));
            }
        }
        if !redirects.is_empty() && !req.allow_redirects {
            return Ok(Json::Object(base(
                "POLICY_BLOCKED",
                vec!["REDIRECT_BLOCKED"],
                redirects,
                0,
                "NOT_APPLICABLE",
            )));
        }
        if redirects.iter().any(|item| blocked_network_target(item)) {
            return Ok(Json::Object(base(
                "POLICY_BLOCKED",
                vec!["RESOLUTION_POLICY_BLOCKED"],
                redirects,
                0,
                "NOT_APPLICABLE",
            )));
        }

        if let Some(value) = s.get("response_bytes") {
            let bytes = value
                .as_u64()
                .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?;
            if size_exceeds(req, bytes) {
                return Ok(Json::Object(base(
                    "LIMIT_EXCEEDED",
                    vec!["RESOLUTION_LIMIT_EXCEEDED"],
                    redirects,
                    0,
                    "NOT_APPLICABLE",
                )));
            }
        }

        let freshness = source_freshness(s)?;
        if req.require_fresh && freshness != "FRESH" {
            return Ok(Json::Object(base(
                "POLICY_BLOCKED",
                vec!["FRESHNESS_REQUIREMENT_NOT_MET"],
                redirects,
                1,
                &freshness,
            )));
        }

        let status = s
            .get("status")
            .ok_or_else(|| malformed("RESOLVER_RESPONSE_MALFORMED", "missing network snapshot status"))?
            .as_str()
            .map_err(|e| malformed("RESOLVER_RESPONSE_MALFORMED", e))?;
        if status == "notFound" {
            return Ok(Json::Object(base(
                "NOT_FOUND",
                vec!["RESOLUTION_NOT_FOUND"],
                redirects,
                1,
                &freshness,
            )));
        }
        if status == "unavailable" {
            return Ok(Json::Object(base(
                "UNAVAILABLE",
                vec!["RESOLUTION_UNAVAILABLE"],
                redirects,
                1,
                &freshness,
            )));
        }
        if status == "resolved" {
            let source_identifier = match s.get("source_identifier") {
                Some(Json::String(value)) => Some(value.clone()),
                None | Some(Json::Null) => None,
                Some(_) => {
                    return Err(malformed(
                        "RESOLVER_RESPONSE_MALFORMED",
                        "source identifier malformed",
                    ))
                }
            };
            let resolved_id = match s.get("resolved_id") {
                Some(Json::String(value)) => value.clone(),
                None => uri.clone(),
                Some(_) => {
                    return Err(malformed(
                        "RESOLVER_RESPONSE_MALFORMED",
                        "resolved id malformed",
                    ))
                }
            };

            let mut out = base("RESOLVED", vec![], redirects, 1, &freshness);
            let mut matched = Json::object();
            matched.insert("resource_id".into(), Json::String(resolved_id));
            matched.insert("source_class".into(), Json::String("network".into()));
            matched.insert(
                "source_identifier".into(),
                source_identifier.clone().map(Json::String).unwrap_or(Json::Null),
            );
            out.insert("matches".into(), Json::Array(vec![Json::Object(matched)]));

            let mut provenance = Json::object();
            provenance.insert("source_class".into(), Json::String("network".into()));
            provenance.insert(
                "source_identifier".into(),
                source_identifier.map(Json::String).unwrap_or(Json::Null),
            );
            provenance.insert("source_index".into(), Json::Int(source_index as i128));
            out.insert(
                "provenance".into(),
                Json::Array(vec![Json::Object(provenance)]),
            );
            return Ok(Json::Object(out));
        }

        return Err(malformed(
            "RESOLVER_RESPONSE_MALFORMED",
            "unknown network snapshot status",
        ));
    }

    Ok(Json::Object(base(
        "NOT_FOUND",
        vec!["RESOLUTION_NOT_FOUND"],
        vec![],
        0,
        "NOT_APPLICABLE",
    )))
}

pub fn resolve_operation(input: &Json) -> Result<Json, OlpError> {
    let request = input
        .get("request")
        .map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let req = parse_request(request)?;
    let sources = match input
        .get_opt("sources")
        .map_err(|e| malformed("MALFORMED_INPUT", e))?
    {
        None => &[][..],
        Some(value) => value
            .as_array()
            .map_err(|e| malformed("MALFORMED_INPUT", e))?,
    };
    if sources.len() > 64 {
        return Err(malformed(
            "RESOURCE_LIMIT_EXCEEDED",
            "resolution source count exceeds implementation limit",
        ));
    }

    // Reserved by this first deterministic executable slice. Parsing and type validation
    // are still normative, even though only one result is returned today.
    let _ = req.max_results;

    if req.target_class == "evidence" {
        resolve_evidence(&req, sources)
    } else {
        resolve_resource(&req, sources)
    }
}
