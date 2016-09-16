// (c) 2016 Joost Yervante Damad <joost@damad.be>

extern crate gtk;
extern crate gdk_pixbuf;
extern crate cairo;
extern crate inotify;
extern crate glib;
extern crate dyon;
extern crate range;

use inotify::INotify;
use inotify::ffi::*;
use std::path::Path;
use std::io::Read;
use std::sync::{Mutex,Arc};
use std::cell::Cell;

use gtk::prelude::*;
use gtk::{AboutDialog, Menu, MenuBar, MenuItem, DrawingArea, Statusbar};
use gtk::{Notebook, Label, TextView, TextBuffer, ScrolledWindow};
use gdk_pixbuf::Pixbuf;

const VERSION: &'static str = env!("CARGO_PKG_VERSION");

fn usage(program_name:&str) {
    println!("Usage: {} <dyon file>", program_name);
}

fn read_file(name: &str) -> std::result::Result<String, std::io::Error> {
    let mut f = try!(std::fs::File::open(name));
    let mut s = String::new();
    try!(f.read_to_string(&mut s));
    Ok(s)
}

fn main() {

    let mut args = std::env::args();
    let filename = if let Some(program_name) = args.next() {
        if let Some(filename) = args.next() {
            filename
        } else {
            usage(&program_name);
            return
        }
    } else {
        usage("unknown");
        return
    };

    if gtk::init().is_err() {
        println!("Failed to initialize GTK.");
        return;
    }

    let mut ino = match INotify::init() {
        Ok(ino) => ino,
        _ => {
            println!("Failed to initialize INotify");
            return;
        },
    };
    
    let file_watch = match ino.add_watch(Path::new(&filename), IN_MODIFY) {
        Ok(watch) => watch,
        Err(err) => {
            println!("IO Error for {}: {}", filename, err);
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
        for event in ino.available_events().unwrap() {
            if event.wd == file_watch {
                println!("modified!");
                let mut update = update_input_timeout_loop.lock().unwrap();
                *update = true;
            }
        }
        glib::Continue(true)
    });
    
    window.show_all();

    let mut dyon_runtime = dyon::Runtime::new();
    
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
            println!("updated");

            let mut module = dyon::Module::new_intrinsics(Arc::new(dyon::prelude::Prelude::new_intrinsics().functions));
            println!("X1");
            // TODO error handling for parse
            dyon::load_str(&filename, Arc::new(data), &mut module).unwrap();
            let name: Arc<String> = Arc::new("footprint".into());
            let call = dyon::ast::Call {
                name: name.clone(),
                f_index: Cell::new(module.find_function(&name, 0)),
                args: vec![],
                custom_source: None,
                source_range: range::Range::empty(0),
            };
            // TODO error handling for run
            let (v,_) = dyon_runtime.call(&call,&module).unwrap();
            println!("{:?}", v);
            println!("X2");
        }
    }
}
