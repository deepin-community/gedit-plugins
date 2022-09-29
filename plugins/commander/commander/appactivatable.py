# -*- coding: utf-8 -*-
#
#  __init__.py - commander
#
#  Copyright (C) 2010 - Jesse van den Kieboom
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

from gi.repository import GLib, GObject, Gio, Gedit
import sys, os
import commander.commands as commands

try:
    import gettext
    gettext.bindtextdomain('gedit-plugins')
    gettext.textdomain('gedit-plugins')
    _ = gettext.gettext
except:
    _ = lambda s: s


class CommanderAppActivatable(GObject.Object, Gedit.AppActivatable):

    app = GObject.Property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self._path = os.path.dirname(__file__)

        if not self._path in sys.path:
            sys.path.insert(0, self._path)

        commands.Commands().set_dirs([
            os.path.join(GLib.get_user_config_dir(), 'gedit/commander/modules'),
            os.path.join(self.plugin_info.get_data_dir(), 'modules')
        ])

        self.app.add_accelerator("<Primary>comma", "win.commander", None)

        self.menu_ext = self.extend_menu("view-section-1")
        item = Gio.MenuItem.new(_('Commander Mode'), "win.commander")
        self.menu_ext.append_menu_item(item)

    def deactivate(self):
        commands.Commands().stop()

        if self._path in sys.path:
            sys.path.remove(self._path)

        self.app.remove_accelerator("win.commander", None)
        self.menu_ext = None

# ex:ts=4:et
