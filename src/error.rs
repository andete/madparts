// (c) 2018 Joost Yervante Damad <joost@damad.be>

use std::io;

use glib;
use cpython;

// TODO: use failure crate

#[derive(Debug)]
pub enum MpError {
    GuiError(String),
    IOError(String),
    Python(String),
}

impl From<glib::BoolError> for MpError {
    fn from(e: glib::BoolError) -> MpError {
        MpError::GuiError(format!("{:?}", e))
    }
}

impl From<io::Error> for MpError {
    fn from(e: io::Error) -> MpError {
        MpError::IOError(format!("{:?}", e))
    }
}

impl From<cpython::PyErr> for MpError {
    fn from(e: cpython::PyErr) -> MpError {
        MpError::Python(format!("{:?}", e))
    }
}
