/*
* Copyright (C) 2015 The Lemon Man
*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2, or (at your option)
* any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
*/

namespace Gedit {
namespace FindInFilesPlugin {

[GtkTemplate (ui = "/org/gnome/gedit/plugins/findinfiles/ui/dialog.ui")]
class FindDialog : Gtk.Dialog {
    [GtkChild]
    public Gtk.Entry search_entry;
    [GtkChild]
    public Gtk.FileChooserButton sel_folder;
    [GtkChild]
    public Gtk.CheckButton match_case_checkbutton;
    [GtkChild]
    public Gtk.CheckButton entire_word_checkbutton;
    [GtkChild]
    public Gtk.CheckButton regex_checkbutton;
    [GtkChild]
    public Gtk.Widget find_button;

    public FindDialog (File? root) {
        if (root != null) {
            try {
                    sel_folder.set_current_folder_file (root);
            }
            catch (Error err) {
                warning (err.message);
            }
        }

        set_default_response (Gtk.ResponseType.OK);
        set_response_sensitive (Gtk.ResponseType.OK, false);

        if (Gtk.Settings.get_default ().gtk_dialogs_use_header) {
            var header_bar = new Gtk.HeaderBar ();

            header_bar.set_title (_("Find in Files"));
            header_bar.set_show_close_button (true);

            this.set_titlebar (header_bar);
        } else {
            add_button (_("_Close"), Gtk.ResponseType.CLOSE);
        }

        search_entry.changed.connect (() => {
            find_button.sensitive = (search_entry.text != "");
        });
    }
}

} // namespace FindInFilesPlugin
} // namespace Gedit
