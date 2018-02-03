// (c) 2018 Joost Yervante Damad <joost@damad.be>

use gtk;
use gtk::prelude::*;
use gtk::{AboutDialog, Menu, MenuBar, MenuItem, DrawingArea, Statusbar};
use gtk::{Notebook, Label, TextView, TextBuffer, ScrolledWindow, Window};
use gdk_pixbuf::Pixbuf;

use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

use util;
use ::VERSION;

pub fn make_gui(filename: &str) -> (Window, Statusbar, TextBuffer, Arc<AtomicBool>) {

 let window = gtk::Window::new(gtk::WindowType::Toplevel);

    window.set_title(&format!("madparts (rustic edition) {}", VERSION));
    window.set_border_width(10);
    window.set_position(gtk::WindowPosition::Center);
    window.set_default_size(350, 70);

    let exit = Arc::new(AtomicBool::new(false));
    
    {
        let exit = exit.clone();
        window.connect_delete_event(move |_, _| {
            exit.store(true, Ordering::SeqCst);
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
    let about_me = MenuItem::new_with_label("About");
    menu.append(&about_me);
    let help = MenuItem::new_with_label("Help");
    help.set_submenu(Some(&menu));
    
    menu_bar.append(&file);
    menu_bar.append(&help);

    {
        let exit = exit.clone();
        quit.connect_activate(move |_| {
            exit.store(true, Ordering::SeqCst);
        });
    }

    let about = {
        let about = AboutDialog::new();
        about.set_transient_for(Some(&window));
        about.add_credit_section("Credits", &["Joost Yervante Damad <joost@damad.be>"]);
        about.set_copyright(Some("MIT/Apache-2.0"));
        about.set_program_name("madparts");
        about.set_version(Some(VERSION));
        about.set_website(Some("http://madparts.org/"));
        about.set_website_label(Some("madparts"));
        let logo = Pixbuf::new_from_file_at_size("../media/icon.svg", 64, 64).unwrap();
        about.set_logo(Some(&logo));
        about
    };

    about_me.connect_activate(move |_| {
        about.show();
        about.run();
        about.hide();
    });

    v_box.pack_start(&menu_bar, false, false, 0);

    let notebook = Notebook::new();

    v_box.pack_start(&notebook, true, true, 0);

    let input_buffer = TextBuffer::new(None);
    let data = util::read_file(&filename).unwrap();
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
    (window, statusbar, input_buffer, exit)
}
