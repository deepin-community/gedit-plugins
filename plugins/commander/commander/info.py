# -*- coding: utf-8 -*-
#
#  info.py - commander
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

from gi.repository import Pango, Gdk, Gtk
import math

class ScrolledWindow(Gtk.ScrolledWindow):
    __gtype_name__ = "CommanderScrolledWindow"

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self._max_height = 0
        self._max_lines = 10

        self.view = Gtk.TextView()
        self.view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.view.set_editable(False)
        self.view.set_can_focus(False)

        self.view.connect('style-updated', self._on_style_updated)

        self._update_max_height()

        self.view.show()

        self.add(self.view)

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

    def _update_max_height(self):
        layout = self.view.create_pango_layout('Some text to measure')
        extents = layout.get_pixel_extents()

        maxh = extents[1].height * self._max_lines

        if maxh != self._max_height:
            self._max_height = maxh
            self.queue_resize()

    def _on_style_updated(self, widget):
        self._update_max_height()

    def do_get_preferred_height(self):
        hp, vp = self.get_policy()

        ret = self.view.get_preferred_height()

        if vp == Gtk.PolicyType.NEVER and ret[0] > self._max_height:
            self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
            self.set_min_content_height(self._max_height)
        elif vp == Gtk.PolicyType.ALWAYS and ret[0] < self._max_height:
            self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
            self.set_min_content_height(0)

        return Gtk.ScrolledWindow.do_get_preferred_height(self)

class Info(Gtk.Box):
    __gtype_name__ = "CommanderInfo"

    def __init__(self):
        super(Info, self).__init__()

        self._button_bar = None
        self._status_label = None

        self._build_ui()

    def _build_ui(self):
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(3)
        self.set_can_focus(False)

        self._sw = ScrolledWindow()
        self._sw.set_border_width(6)

        css = Gtk.CssProvider()
        css.load_from_data(bytes("""
.trough {
    background: transparent;
}
""", 'utf-8'))

        self._sw.get_vscrollbar().get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._sw.show()
        self.add(self._sw)

        self._attr_map = {
            Pango.AttrType.STYLE: ('style', Pango.AttrInt),
            Pango.AttrType.WEIGHT: ('weight', Pango.AttrInt),
            Pango.AttrType.VARIANT: ('variant', Pango.AttrInt),
            Pango.AttrType.STRETCH: ('stretch', Pango.AttrInt),
            Pango.AttrType.SIZE: ('size', Pango.AttrInt),
            Pango.AttrType.FOREGROUND: ('foreground', Pango.AttrColor),
            Pango.AttrType.BACKGROUND: ('background', Pango.AttrColor),
            Pango.AttrType.UNDERLINE: ('underline', Pango.AttrInt),
            Pango.AttrType.STRIKETHROUGH: ('strikethrough', Pango.AttrInt),
            Pango.AttrType.RISE: ('rise', Pango.AttrInt),
            Pango.AttrType.SCALE: ('scale', Pango.AttrFloat)
        }

    @property
    def text_view(self):
        return self._sw.view

    @property
    def is_empty(self):
        buf = self.text_view.get_buffer()
        return buf.get_start_iter().equal(buf.get_end_iter())

    def status(self, text=None):
        if self._status_label == None and text != None:
            self._status_label = Gtk.Label()

            context = self.text_view.get_style_context()
            state = context.get_state()
            font_desc = context.get_font(state)

            self._status_label.override_font(font_desc)

            self._status_label.override_color(Gtk.StateFlags.NORMAL, context.get_color(Gtk.StateFlags.NORMAL))
            self._status_label.show()
            self._status_label.set_alignment(0, 0.5)
            self._status_label.set_padding(10, 0)
            self._status_label.set_use_markup(True)
            self._status_label.set_halign(Gtk.Align.FILL)

            self._ensure_button_bar()
            self._button_bar.pack_start(self._status_label, True, True, 0)

        if text != None:
            self._status_label.set_markup(text)
        elif self._status_label:
            self._status_label.destroy()

            if not self._button_bar and self.is_empty:
                self.destroy()

    def _attr_to_tag(self, attr):
        buf = self.text_view.get_buffer()
        table = buf.get_tag_table()
        ret = []

        tp = attr.klass.type

        if not tp in self._attr_map:
            return None

        propname, klass = self._attr_map[tp]

        # The hack! Set __class__ so we can access .value/.color,
        # then set __class__ back. This is expected to break at any time
        cls = attr.__class__
        attr.__class__ = klass

        if tp == Pango.AttrType.FOREGROUND or tp == Pango.AttrType.BACKGROUND:
            value = attr.color
        else:
            value = attr.value

        attr.__class__ = cls

        tagname = str(tp) + ':' + str(value)

        tag = table.lookup(tagname)

        if not tag:
            tag = buf.create_tag(tagname)
            tag.set_property(propname, value)

        return tag

    def add_lines(self, line, use_markup=False):
        buf = self.text_view.get_buffer()

        if not buf.get_start_iter().equal(buf.get_end_iter()):
            line = "\n" + line

        if not use_markup:
            buf.insert(buf.get_end_iter(), line)
            return

        try:
            ret = Pango.parse_markup(line, -1, '\x00')
        except Exception as e:
            print('Could not parse markup:', e)
            buf.insert(buf.get_end_iter(), line)
            return

        text = ret[2]

        mark = buf.create_mark(None, buf.get_end_iter(), True)
        buf.insert(buf.get_end_iter(), text)

        attrs = []
        ret[1].filter(lambda x: attrs.append(x))

        for attr in attrs:
            # Try/catch everything since the _attr_to_tag stuff is a big
            # hack
            try:
                tag = self._attr_to_tag(attr)
            except:
                continue

            if not tag is None:
                start = buf.get_iter_at_mark(mark)
                end = start.copy()

                start.forward_chars(attr.start_index)
                end.forward_chars(attr.end_index)

                buf.apply_tag(tag, start, end)

    def add_action(self, name, callback, data=None):
        image = Gtk.Image.new_from_icon_name(name, Gtk.IconSize.MENU)
        image.show()

        self._ensure_button_bar()

        ev = Gtk.EventBox()
        ev.set_visible_window(True)
        ev.add(image)
        ev.show()

        ev.set_halign(Gtk.Align.END)

        self._button_bar.pack_end(ev, False, False, 0)
        ev.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.HAND2))

        ev.connect('button-press-event', self._on_action_activate, callback, data)
        ev.connect('enter-notify-event', self._on_action_enter_notify)
        ev.connect('leave-notify-event', self._on_action_leave_notify)

        ev.connect_after('destroy', self._on_action_destroy)
        return ev

    def clear(self):
        self.text_view.get_buffer().set_text('')

    def _ensure_button_bar(self):
        if not self._button_bar:
            self._button_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
            self._button_bar.show()
            self.pack_start(self._button_bar, False, False, 0)

    def _on_action_destroy(self, widget):
        if self._button_bar and len(self._button_bar.get_children()) == 0:
            self._button_bar.destroy()
            self._button_bar = None

    def _on_action_enter_notify(self, widget, evnt):
        img = widget.get_child()
        img.set_state(Gtk.StateType.PRELIGHT)

    def _on_action_leave_notify(self, widget, evnt):
        img = widget.get_child()
        img.set_state(Gtk.StateType.NORMAL)

    def _on_action_activate(self, widget, evnt, callback, data):
        if data:
            callback(data)
        else:
            callback()

# ex:ts=4:et
