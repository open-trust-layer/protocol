//! Ed25519 via the system OpenSSL EVP API.
//!
//! This keeps the independent Rust core free of crates.io dependencies while
//! delegating the cryptographic primitive to OpenSSL.  The OLP construction,
//! canonicalization, and verification state machine are implemented here in Rust.
use std::ffi::c_void;
#[repr(C)]struct EVP_PKEY{_p:[u8;0]}#[repr(C)]struct EVP_MD_CTX{_p:[u8;0]}#[repr(C)]struct EVP_PKEY_CTX{_p:[u8;0]}
#[link(name="crypto")]
extern "C"{
 fn OBJ_sn2nid(s:*const std::ffi::c_char)->i32;
 fn EVP_PKEY_new_raw_private_key(t:i32,e:*mut c_void,key:*const u8,keylen:usize)->*mut EVP_PKEY;
 fn EVP_PKEY_new_raw_public_key(t:i32,e:*mut c_void,key:*const u8,keylen:usize)->*mut EVP_PKEY;
 fn EVP_PKEY_free(p:*mut EVP_PKEY);
 fn EVP_MD_CTX_new()->*mut EVP_MD_CTX;fn EVP_MD_CTX_free(c:*mut EVP_MD_CTX);
 fn EVP_DigestSignInit(c:*mut EVP_MD_CTX,pctx:*mut *mut EVP_PKEY_CTX,md:*const c_void,e:*mut c_void,pkey:*mut EVP_PKEY)->i32;
 fn EVP_DigestSign(c:*mut EVP_MD_CTX,sig:*mut u8,siglen:*mut usize,msg:*const u8,msglen:usize)->i32;
 fn EVP_DigestVerifyInit(c:*mut EVP_MD_CTX,pctx:*mut *mut EVP_PKEY_CTX,md:*const c_void,e:*mut c_void,pkey:*mut EVP_PKEY)->i32;
 fn EVP_DigestVerify(c:*mut EVP_MD_CTX,sig:*const u8,siglen:usize,msg:*const u8,msglen:usize)->i32;
 fn EVP_PKEY_get_raw_public_key(p:*const EVP_PKEY,pubkey:*mut u8,len:*mut usize)->i32;
}
struct Pkey(*mut EVP_PKEY);impl Drop for Pkey{fn drop(&mut self){unsafe{EVP_PKEY_free(self.0)}}}
struct Md(*mut EVP_MD_CTX);impl Drop for Md{fn drop(&mut self){unsafe{EVP_MD_CTX_free(self.0)}}}
fn ed25519_nid()->Result<i32,String>{let nid=unsafe{OBJ_sn2nid(b"ED25519\0".as_ptr().cast())};if nid==0{Err("OpenSSL does not expose the ED25519 key type".into())}else{Ok(nid)}}
pub fn sign(seed:&[u8],msg:&[u8])->Result<[u8;64],String>{if seed.len()!=32{return Err("Ed25519 private seed must contain exactly 32 octets".into());}unsafe{let p=Pkey(EVP_PKEY_new_raw_private_key(ed25519_nid()?,std::ptr::null_mut(),seed.as_ptr(),seed.len()));if p.0.is_null(){return Err("OpenSSL rejected Ed25519 private key".into());}let c=Md(EVP_MD_CTX_new());if c.0.is_null(){return Err("OpenSSL EVP_MD_CTX_new failed".into());}let mut pc=std::ptr::null_mut();if EVP_DigestSignInit(c.0,&mut pc,std::ptr::null(),std::ptr::null_mut(),p.0)!=1{return Err("OpenSSL Ed25519 DigestSignInit failed".into());}let mut out=[0u8;64];let mut n=out.len();if EVP_DigestSign(c.0,out.as_mut_ptr(),&mut n,msg.as_ptr(),msg.len())!=1||n!=64{return Err("OpenSSL Ed25519 signing failed".into());}Ok(out)}}
pub fn verify(public_key:&[u8],sig:&[u8],msg:&[u8])->Result<bool,String>{if public_key.len()!=32{return Err("Ed25519 public key must contain exactly 32 octets".into());}if sig.len()!=64{return Err("Ed25519 signature must contain exactly 64 octets".into());}unsafe{let p=Pkey(EVP_PKEY_new_raw_public_key(ed25519_nid()?,std::ptr::null_mut(),public_key.as_ptr(),public_key.len()));if p.0.is_null(){return Err("OpenSSL rejected Ed25519 public key".into());}let c=Md(EVP_MD_CTX_new());if c.0.is_null(){return Err("OpenSSL EVP_MD_CTX_new failed".into());}let mut pc=std::ptr::null_mut();if EVP_DigestVerifyInit(c.0,&mut pc,std::ptr::null(),std::ptr::null_mut(),p.0)!=1{return Err("OpenSSL Ed25519 DigestVerifyInit failed".into());}Ok(EVP_DigestVerify(c.0,sig.as_ptr(),sig.len(),msg.as_ptr(),msg.len())==1)}}
pub fn public_from_seed(seed:&[u8])->Result<[u8;32],String>{if seed.len()!=32{return Err("Ed25519 private seed must contain exactly 32 octets".into());}unsafe{let p=Pkey(EVP_PKEY_new_raw_private_key(ed25519_nid()?,std::ptr::null_mut(),seed.as_ptr(),seed.len()));if p.0.is_null(){return Err("OpenSSL rejected Ed25519 private key".into());}let mut out=[0u8;32];let mut n=32usize;if EVP_PKEY_get_raw_public_key(p.0,out.as_mut_ptr(),&mut n)!=1||n!=32{return Err("OpenSSL public-key extraction failed".into());}Ok(out)}}
