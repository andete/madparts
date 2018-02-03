// (c) 2016-2018 Joost Yervante Damad <joost@damad.be>

extern crate gtk;
extern crate gdk_pixbuf;
extern crate cairo;
extern crate clap;
extern crate inotify;
extern crate glib;
extern crate range;
extern crate cpython;
extern crate env_logger;
#[macro_use] extern crate log;

use std::path::Path;
use std::io;
use std::io::Read;
use std::sync::{Mutex,Arc};

use clap::{Arg, App};

use inotify::{WatchMask, Inotify};


use gtk::prelude::*;
use gtk::{AboutDialog, Menu, MenuBar, MenuItem, DrawingArea, Statusbar};
use gtk::{Notebook, Label, TextView, TextBuffer, ScrolledWindow};
use gdk_pixbuf::Pixbuf;

use cpython::Python;

const VERSION: &'static str = env!("CARGO_PKG_VERSION");

fn read_file(name: &str) -> Result<String, io::Error> {
    let mut f = std::fs::File::open(name)?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}

fn main() {
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

    if gtk::init().is_err() {
        error!("Failed to initialize GTK.");
        return;
    }

    let mut ino = match Inotify::init() {
        Ok(ino) => ino,
        _ => {
            error!("Failed to initialize INotify");
            return;
        },
    };
    
    let file_watch = match ino.add_watch(Path::new(&filename), WatchMask::MODIFY) {
        Ok(watch) => watch,
        Err(err) => {
            error!("IO Error for {}: {}", filename, err);
            return;
        },
    };
    
    let window = gtk::Window::new(gtk::WindowType::Toplevel);

    window.set_title(&format!("madparts (rustic edition) {}", VERSION));
    window.set_border_width(10);
    window.set_position(gtk::WindowPosition::Center);
    window.set_default_size(350, 70);

    let exit = Arc::new(Mutex::new(false));
    
    {
        let exit = exit.clone();
        window.connect_delete_event(move |_, _| {
            let mut e = exit.lock().unwrap();
            *e = true;
            Inhibit(false)
        });
    }
    

    let v_box = gtk::Box::new(gtk::Orientation::Vertical, 10);

    let menu_bar = MenuBar::new();
    
    let menu = Menu::new();
    let quit = MenuItem::new_with_label("Quit");
    menu.append(&quit);
    let file = MenuItem::new_with_label("File");
    file.set_submenu(Some(&menu));
    
    let menu = Menu::new();
    let about = MenuItem::new_with_label("About");
    menu.append(&about);
    let help = MenuItem::new_with_label("Help");
    help.set_submenu(Some(&menu));
    
    menu_bar.append(&file);
    menu_bar.append(&help);

    {
        let exit = exit.clone();
        quit.connect_activate(move |_| {
            let mut e = exit.lock().unwrap();
            *e = true;
        });
    }

    about.connect_activate(|_| {
        let about = AboutDialog::new();
        about.add_credit_section("Credits", &["Joost Yervante Damad <joost@damad.be>"]);
        about.set_copyright(Some("MIT/Apache-2.0"));
        about.set_program_name("madparts");
        about.set_version(Some(VERSION));
        about.set_website(Some("http://madparts.org/"));
        about.set_website_label(Some("madparts"));
        let logo = Pixbuf::new_from_file_at_size("../media/icon.svg", 64, 64).unwrap();
        about.set_logo(Some(&logo));
        about.show();
        about.run();
        about.hide();
    });



    v_box.pack_start(&menu_bar, false, false, 0);

    let notebook = Notebook::new();

    v_box.pack_start(&notebook, true, true, 0);

    let input_buffer = TextBuffer::new(None);
    let data = read_file(&filename).unwrap();
    input_buffer.set_text(&data);
    let input = TextView::new_with_buffer(&input_buffer);
    input.set_editable(false);
    let scrolled_input = ScrolledWindow::new(None,None);
    scrolled_input.add(&input);
    notebook.append_page(&scrolled_input,Some(&Label::new(Some("input"))));
    
    let view = DrawingArea::new();
    notebook.append_page(&view,Some(&Label::new(Some("view"))));

    let statusbar = Statusbar::new();
    statusbar.push(0, "Ready.");
    v_box.pack_start(&statusbar, false, false, 0);

    window.add(&v_box);

    let update_input = Arc::new(Mutex::new(true));
    let update_input_timeout_loop = update_input.clone();
    gtk::timeout_add(250, move || {
        let mut buffer = [0; 1024];
        for event in ino.read_events(&mut buffer).unwrap() {
            if event.wd == file_watch {
                trace!("modified!");
                let mut update = update_input_timeout_loop.lock().unwrap();
                *update = true;
            }
        }
        glib::Continue(true)
    });
    
    window.show_all();

    let gil = Python::acquire_gil();
    let py = gil.python();

    let sys = py.import("sys").unwrap();
    let version: String = sys.get(py, "version").unwrap().extract(py).unwrap();
    
    info!("using python: {}", version);
    
    loop {
        {
            if *exit.lock().unwrap() {
                break;
            }
        }
        gtk::main_iteration();
        let mut update = update_input.lock().unwrap();
        if *update {
            statusbar.push(1, "Updating...");
            *update = false;
            let data = read_file(&filename).unwrap();
            input_buffer.set_text(&data);
            statusbar.pop(1);
            trace!("updated");
            py.run(&data,None,None).unwrap(); // TODO
            let res = py.eval("footprint()", None,None).unwrap();
            info!("res: {:?}", res);
        }
    }
}
