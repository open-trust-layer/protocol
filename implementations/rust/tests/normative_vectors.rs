use olp_rust::{json,record,proof,proof_identity,openssl_ed25519,util::hex_encode};

#[test]
fn specification_0003_record_identity_vector() {
    let record_json=json::parse(r#"{"envelope_version":1,"type":"claim","content":{"statement":"example","subject":"urn:example:subject:1"}}"#).unwrap();
    let bytes=record::identity_bytes(&record_json).unwrap();
    assert_eq!(hex_encode(&bytes),"886a4f4c502d5245434f52440165636c61696da2677375626a6563747575726e3a6578616d706c653a7375626a6563743a316973746174656d656e74676578616d706c65a08080a0");
    let out=record::identity_output(&record_json).unwrap();
    assert_eq!(out.get("record_identity_text").unwrap().as_str().unwrap(),"r1_xp7Q9MIvwCQtqTnUVEjsH6t0ZPoFSvM0kn3A-RdBy7Q");
}

#[test]
fn specification_0004_proof_input_vector() {
    let input=json::parse(r#"{"cryptosuite":"eddsa-ed25519-v1","proof_purpose":"assertion","verification_method":"urn:example:olp:test-key-1","record_commitment":{"algorithm":-16,"digest_hex":"bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7"},"extensions":{},"critical":[]}"#).unwrap();
    let out=proof::encode_input_operation(&input).unwrap();
    assert_eq!(out.get("proof_input_hex").unwrap().as_str().unwrap(),"89694f4c502d50524f4f46017065646473612d656432353531392d763169617373657274696f6e781a75726e3a6578616d706c653a6f6c703a746573742d6b65792d31822f5820bf37c3cd8285b777daba2aa38b2cb996a66ff4ee89e14dd9dff7895509e24ee7a0a080");
}

#[test]
fn specification_0004_ed25519_vector() {
    let seed=olp_rust::util::hex_decode("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60").unwrap();
    let msg=olp_rust::util::hex_decode("89694f4c502d50524f4f46017065646473612d656432353531392d763169617373657274696f6e781a75726e3a6578616d706c653a6f6c703a746573742d6b65792d31822f5820c69ed0f4c22fc0242da939d45448ec1fab7464fa054af334927dc0f91741cbb4a0a080").unwrap();
    let sig=openssl_ed25519::sign(&seed,&msg).unwrap();
    assert_eq!(hex_encode(&sig),"a53978e0f7ff28583dd1d08d4f69da6684675765d299371e034f7db2f056d768c4be9bcee26e5be6b53d534f61034f3a16ea97fac421c03d96ccc7742e5ef805");
    let public=openssl_ed25519::public_from_seed(&seed).unwrap();
    assert_eq!(hex_encode(&public),"d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a");
    assert!(openssl_ed25519::verify(&public,&sig,&msg).unwrap());
}

#[test]
fn specification_0005_proof_identity_vector() {
    let input=json::parse(r#"{"proof":{"type":"OLPProof","version":1,"cryptosuite":"eddsa-ed25519-v1","proofPurpose":"assertion","verificationMethod":"urn:example:olp:test-key-1","recordCommitment":{"algorithm":-16,"digest_hex":"c69ed0f4c22fc0242da939d45448ec1fab7464fa054af334927dc0f91741cbb4"},"proofValue_hex":"a53978e0f7ff28583dd1d08d4f69da6684675765d299371e034f7db2f056d768c4be9bcee26e5be6b53d534f61034f3a16ea97fac421c03d96ccc7742e5ef805","critical":[],"extensions":{}}}"#).unwrap();
    let out=proof_identity::proof_identity_operation(&input).unwrap();
    assert_eq!(out.get("proof_identity_digest_hex").unwrap().as_str().unwrap(),"02f4942b2bb0e5e4e3ae448015a17368237f7452801d0a6eaffa4efaadc853ba");
    assert_eq!(out.get("proof_identity_bytes_length").unwrap().as_i64().unwrap(),189);
}

#[test]
fn specification_0005_record_evidence_ref_vector() {
    let input=json::parse(r#"{"kind":0,"identity_digest_hex":"c69ed0f4c22fc0242da939d45448ec1fab7464fa054af334927dc0f91741cbb4"}"#).unwrap();
    let out=olp_rust::evidence::encode_ref_operation(&input).unwrap();
    assert_eq!(out.get("evidence_ref_hex").unwrap().as_str().unwrap(),"82005820c69ed0f4c22fc0242da939d45448ec1fab7464fa054af334927dc0f91741cbb4");
}
