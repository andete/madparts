// (c) 2017-2018 Joost Yervante Damad <joost@damad.be>

use std::{fs, io};
use std::io::Read;

use error::MpError;

pub fn main_run<X>(run: X)
    where X: Fn() -> Result<(), MpError>
{
    if let Err(ref e) = run() {
        error!("{:?}", e);
        ::std::process::exit(1);
    }
}

pub fn read_file(name: &str) -> Result<String, io::Error> {
    let mut f = fs::File::open(name)?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}
