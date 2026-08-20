#[derive(Debug,Clone)]
pub struct OlpError{pub classification:&'static str,pub reason:String,pub message:String}
impl OlpError{pub fn malformed(reason:&str,msg:impl Into<String>)->Self{Self{classification:"MALFORMED",reason:reason.into(),message:msg.into()}}pub fn unsupported(reason:&str,msg:impl Into<String>)->Self{Self{classification:"UNSUPPORTED",reason:reason.into(),message:msg.into()}}}
impl std::fmt::Display for OlpError{fn fmt(&self,f:&mut std::fmt::Formatter<'_>)->std::fmt::Result{write!(f,"{}: {}",self.reason,self.message)}}
impl std::error::Error for OlpError{}
