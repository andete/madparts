// (c) 2017-2018 Joost Yervante Damad <joost@damad.be>

use error::MpError;

pub fn main_run<X>(run: X)
    where X: Fn() -> Result<(), MpError>
{
    if let Err(ref e) = run() {
        error!("{:?}", e);
        ::std::process::exit(1);
    }
}
