// (c) 2016 Joost Yervante Damad <joost@damad.be>

extern crate gtk;
extern crate gdk_pixbuf;
extern crate cairo;
extern crate inotify;
extern crate glib;

use inotify::INotify;
use inotify::ffi::*;
use std::path::Path;

use gtk::prelude::*;
use gtk::{AboutDialog, Menu, MenuBar, MenuItem, DrawingArea, Statusbar};
use gdk_pixbuf::Pixbuf;

const VERSION: &'static str = env!("CARGO_PKG_VERSION");

fn usage(program_name:&str) {
    println!("Usage: {} <coffee file>", program_name);
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
    println!("Using file: {}", filename);

    if gtk::init().is_err() {
        println!("Failed to initialize GTK.");
        return;
    }

    let mut ino = INotify::init().unwrap();
    ino.add_watch(Path::new(&filename), IN_MODIFY).unwrap();

    glib::timeout_add(250, move || {
        for event in ino.available_events().unwrap() {
            println!("{:?}", event);
        }
        glib::Continue(true)
    });
    
    let window = gtk::Window::new(gtk::WindowType::Toplevel);

    window.set_title(&format!("madparts (rustic edition) {}", VERSION));
    window.set_border_width(10);
    window.set_position(gtk::WindowPosition::Center);
    window.set_default_size(350, 70);

    window.connect_delete_event(|_, _| {
        gtk::main_quit();
        Inhibit(false)
    });

    let v_box = gtk::Box::new(gtk::Orientation::Vertical, 10);

    let menu = Menu::new();
    let menu_bar = MenuBar::new();
    let file = MenuItem::new_with_label("File");
    let about = MenuItem::new_with_label("About");
    let quit = MenuItem::new_with_label("Quit");
    menu.append(&about);
    menu.append(&quit);
    file.set_submenu(Some(&menu));
    menu_bar.append(&file);

    quit.connect_activate(|_| {
        gtk::main_quit();
    });

    about.connect_activate(|_| {
        let about = AboutDialog::new();
        about.add_credit_section("Credits", &["Joost Yervante Damad <joost@damad.be>"]);
        about.set_copyright(Some("MIT OR Apache-2.0"));
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

    let drawingarea = DrawingArea::new();

    v_box.pack_start(&drawingarea, true, true, 0);

    let statusbar = Statusbar::new();
    statusbar.push(0, "hello.");
    v_box.pack_start(&statusbar, false, false, 0);

    window.add(&v_box);

    window.show_all();
    gtk::main();
}
