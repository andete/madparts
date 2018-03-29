// (c) 2016-2018 Joost Yervante Damad <joost@damad.be>

extern crate cairo;
extern crate clap;
extern crate cpython;
extern crate env_logger;

extern crate gdk_pixbuf;
extern crate glib;
extern crate gtk;

extern crate inotify;
#[macro_use]
extern crate log;
extern crate range;


use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

use clap::{Arg, App};

use inotify::{WatchMask, Inotify};

use cpython::Python;

use gtk::{WidgetExt, StatusbarExt, TextBufferExt};

use error::MpError;

pub const VERSION: &'static str = env!("CARGO_PKG_VERSION");

fn run() -> Result<(), MpError> {
    std::env::set_var("RUST_LOG","debug");
    env_logger::init();
    let matches = App::new("madparts")
        .version(VERSION)
        .author("Joost Yervante Damad <joost@damad.be>")
        .about("a functional footprint editor")
        .arg(Arg::with_name("INPUT")
             .help("Sets the python file to use")
             .required(true)
             .index(1))
        .get_matches();

    let filename = matches.value_of("INPUT").unwrap();
    let filepath:PathBuf = Path::new(&filename).into();
    let filedir:PathBuf = filepath.parent().unwrap().into();

    info!("Filename: {}, Dir: {}", filepath.display(), filedir.display());

    if let Err(err) = gtk::init() {
        error!("Failed to initialize GTK.");
        return Err(err.into())
    }

    let mut ino = match Inotify::init() {
        Ok(ino) => ino,
        Err(err) => {
            error!("Failed to initialize INotify");
            return Err(err.into())
        },
    };

    // close_write,moved_to,create
    let create_watch = |i:&mut Inotify,f:&Path| {
        i.add_watch(&f, WatchMask::CREATE | WatchMask::MOVED_TO | WatchMask::CLOSE_WRITE).unwrap()
    };
    
    let mut file_watch = Some(create_watch(&mut ino, &filedir));

    let (window, statusbar, input_buffer, exit) = gui::make_gui(&filename);
    
    let update_input = Arc::new(AtomicBool::new(true));
    let update_input_timeout_loop = update_input.clone();
    gtk::timeout_add(250, move || {
        let mut buffer = [0; 1024];
        for event in ino.read_events(&mut buffer).unwrap() {
            let mut modified = false;
            if let Some(ref _fw) = file_watch {
                if event.name == filepath.file_name() {
                    debug!("modified!");
                    modified = true;
                }
            }
            if modified {
                update_input_timeout_loop.store(true, Ordering::SeqCst);
                let fw = file_watch.take().unwrap();
                ino.rm_watch(fw).unwrap();
                file_watch = Some(create_watch(&mut ino, &filedir));
                break;
            }
        }
        glib::Continue(true)
    });
    
    window.show_all();

    let gil = Python::acquire_gil();
    let py = gil.python();

    let sys = py.import("sys")?;
    let version: String = sys.get(py, "version")?.extract(py)?;
    
    info!("using python: {}", version);
    
    loop {
        {
            if exit.load(Ordering::SeqCst) {
                break;
            }
        }
        gtk::main_iteration();
        if update_input.compare_and_swap(true, false, Ordering::SeqCst) {
            statusbar.push(1, "Updating...");
            let data = util::read_file(&filename).unwrap();
            input_buffer.set_text(&data);
            statusbar.pop(1);
            trace!("updated");
            py.run(&data,None,None).unwrap(); // TODO
            let res = py.eval("footprint()", None,None).unwrap();
            info!("res: {:?}", res);
        }
    }
    Ok(())
}

fn main() {
    util::main_run(run);
}

mod error;
mod gui;
mod util;
