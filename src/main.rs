// (c) 2016 Joost Yervante Damad <joost@damad.be>

extern crate gtk;
extern crate gdk_pixbuf;

use gtk::prelude::*;
use gtk::{AboutDialog, CheckMenuItem, IconSize, Image, Label, Menu, MenuBar, MenuItem, Window,
          WindowPosition, WindowType};
use gdk_pixbuf::Pixbuf;

const VERSION: &'static str = env!("CARGO_PKG_VERSION");

fn main() {
    if gtk::init().is_err() {
        println!("Failed to initialize GTK.");
        return;
    }

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
        about.add_credit_section("Credits",&["Joost Yervante Damad <joost@damad.be>"]);
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
                           
    
    let label = Label::new(Some("-madparts-"));

    v_box.pack_start(&menu_bar, false, false, 0);
    v_box.pack_start(&label, true, true, 0);

    window.add(&v_box);

    window.show_all();
    gtk::main();
}
