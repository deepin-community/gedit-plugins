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

public class Window : Gedit.WindowActivatable, Peas.ExtensionBase {
    public Window () {
        GLib.Object ();
    }

    public Gedit.Window window {
        owned get; construct;
    }

    File? get_file_browser_root () {
        var bus = window.get_message_bus ();

        if (bus.is_registered ("/plugins/filebrowser", "get_root")) {
            var msg = Object.new (bus.lookup ("/plugins/filebrowser", "get_root"),
                                  "method", "get_root",
                                  "object_path", "/plugins/filebrowser");

            bus.send_message_sync (msg as Gedit.Message);

            Value val = Value (typeof (Object));
            msg.get_property ("location", ref val);

            return val.dup_object () as File;
        }

        return null;
    }

    void dialog_run () {
        var active_doc = window.get_active_document ();

        // Use the filebrowser root as starting folder, if possible.
        var root = get_file_browser_root ();

        // If that's not possible try to use the current document folder.
        if (root == null) {
            var location = active_doc.get_file ().get_location ();
            if (location != null)
                root = location.get_parent ();
        }

        // Fall back to the user's root if none of the methods were successfully
        if (root == null)
            root = File.new_for_path (Environment.get_home_dir ());

        var dialog = new FindDialog (root);

        dialog.set_transient_for (window);
        dialog.set_destroy_with_parent (true);

        // Grab the selection and use it as search query
        Gtk.TextIter start, end;
        if (active_doc.get_selection_bounds (out start, out end)) {
            var selection = active_doc.get_text (start, end, true);

            dialog.search_entry.text = Gtk.SourceUtils.escape_search_text (selection);
        }

        dialog.response.connect ((response_id) => {
            if (response_id == Gtk.ResponseType.OK) {
                var search_text = dialog.search_entry.text;
                var search_path = dialog.sel_folder.get_filename ();

                // Make sure there's no other search with the same parameters
                var panel = (Gtk.Stack)window.get_bottom_panel ();
                var child = panel.get_child_by_name ("find-in-files");
                if (child != null) {
                    child.destroy ();
                }

                // Setup the job parameters
                var cancellable = new Cancellable ();
                var job = new FindJob (cancellable);

                job.ignore_case = !dialog.match_case_checkbutton.active;
                job.match_whole_word = dialog.entire_word_checkbutton.active;

                try {
                    job.prepare (dialog.search_entry.text, dialog.regex_checkbutton.active);
                    job.execute.begin (search_path);
                }
                catch (Error err) {
                    warning (err.message);
                    dialog.destroy ();
                    return;
                }

                // Prepare the panel to hold the results
                var result_panel = new ResultPanel.for_job (job, search_path, window);

                panel.add_titled (result_panel, "find-in-files", "\"%s\"".printf(search_text));

                result_panel.show_all ();

                // Make the panel visible
                panel.set_visible (true);

                // Focus the new search tab
                panel.set_visible_child_name ("find-in-files");

                result_panel.toggle_stop_button (true);
                result_panel.grab_focus ();
            }

            dialog.destroy ();
        });

        dialog.show_all ();
    }

    public void activate () {
        var act = new SimpleAction ("find-in-files", null);
        window.add_action (act);
        act.activate.connect (dialog_run);
   }

    public void deactivate () {
    }

    public void update_state () {
    }
}

public class App : GLib.Object, Gedit.AppActivatable {
    private Gedit.MenuExtension? menu_ext = null;

    public App () {
        GLib.Object ();
    }

    public Gedit.App app {
        owned get; construct;
    }

    public void activate () {
        menu_ext = extend_menu ("search-section");

        var item = new GLib.MenuItem (_("Find in Files…"), "win.find-in-files");
        menu_ext.append_menu_item (item);

        const string accels[] = { "<Shift><Ctrl>f", null };
        app.set_accels_for_action ("win.find-in-files", accels);
    }

    public void deactivate () {
        menu_ext.remove_items ();

        const string accels[] = { null };
        app.set_accels_for_action ("win.find-in-files", accels);
    }
}

} // namespace FindInFilesPlugin
} // namespace Gedit

[ModuleInit]
public void peas_register_types (TypeModule module)
{
    var objmodule = module as Peas.ObjectModule;

    Intl.bindtextdomain (Config.GETTEXT_PACKAGE, Config.GP_LOCALEDIR);

    objmodule.register_extension_type (typeof (Gedit.WindowActivatable),
                                       typeof (Gedit.FindInFilesPlugin.Window));
    objmodule.register_extension_type (typeof (Gedit.AppActivatable),
                                       typeof (Gedit.FindInFilesPlugin.App));
}
