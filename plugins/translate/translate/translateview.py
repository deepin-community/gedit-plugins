# -*- coding: utf-8 -*-
#
#  Copyrignt (C) 2017 Jordi Mas <jmas@softcatala.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor,
#  Boston, MA 02110-1301, USA.


from gi.repository import GLib, Gtk

class TranslateView(Gtk.ScrolledWindow):

    def __init__(self, namespace = {}):
        Gtk.ScrolledWindow.__init__(self)

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_shadow_type(Gtk.ShadowType.NONE)
        self.view = Gtk.TextView()
        self.view.set_editable(False)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.add(self.view)
        self.view.show()

    def do_grab_focus(self):
        self.view.grab_focus()

    def stop(self):
        self.namespace = None

    def scroll_to_end(self):
        i = self.view.get_buffer().get_end_iter()
        self.view.scroll_to_iter(i, 0.0, False, 0.5, 0.5)
        return False

    def write(self, text):
        text = text + "\n"
        buf = self.view.get_buffer()
        buf.insert(buf.get_end_iter(), text)
        GLib.idle_add(self.scroll_to_end)

    def destroy(self):
        pass

