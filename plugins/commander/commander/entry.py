# -*- coding: utf-8 -*-
#
#  entry.py - commander
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

from gi.repository import GObject, GLib, Gdk, Gtk
import cairo
import os
import re
import inspect
import sys
import colorsys

import commander.commands as commands
import commands.completion
import commands.module
import commands.method
import commands.exceptions
import commands.accel_group

import commander.utils as utils

from history import History
from info import Info
from xml.sax import saxutils
import traceback

class Entry(Gtk.Box):
    __gtype_name__ = "CommanderEntry"

    def _show(self):
        self._reveal.set_reveal_child(True)

    def _hide(self):
        self._reveal.set_reveal_child(False)

    def __init__(self, view):
        super(Entry, self).__init__()

        self._view = view
        view.connect("destroy", self._on_view_destroyed)

        self._history = History(os.path.join(GLib.get_user_config_dir(), 'gedit/commander/history'))
        self._history_prefix = None

        self._prompt_text = None
        self._accel_group = None

        self._wait_timeout = 0
        self._cancel_button = None
        self._info = None
        self._info_revealer = None

        self._suspended = None

        self._handlers = [
            [0, Gdk.KEY_Up, self._on_history_move, -1],
            [0, Gdk.KEY_Down, self._on_history_move, 1],
            [None, Gdk.KEY_Return, self._on_execute, None],
            [None, Gdk.KEY_KP_Enter, self._on_execute, None],
            [0, Gdk.KEY_Tab, self._on_complete, None],
            [0, Gdk.KEY_ISO_Left_Tab, self._on_complete, None]
        ]

        self._re_complete = re.compile('("((?:\\\\"|[^"])*)"?|\'((?:\\\\\'|[^\'])*)\'?|[^\s]+)')
        self._command_state = commands.Commands.State()

        self.connect('destroy', self._on_destroy)

        self._build_ui()
        self._setup_keybindings()

        self._attach()

    def view(self):
        return self._view

    def _setup_keybindings(self):
        css = Gtk.CssProvider()
        css.load_from_data(bytes("""
@binding-set terminal-like-bindings {
    unbind "<Control>A";

    bind "<Control>W" { "delete-from-cursor" (word-ends, -1) };
    bind "<Control>A" { "move-cursor" (buffer-ends, -1, 0) };
    bind "<Control>U" { "delete-from-cursor" (display-line-ends, -1) };
    bind "<Control>K" { "delete-from-cursor" (display-line-ends, 1) };
    bind "<Control>E" { "move-cursor" (buffer-ends, 1, 0) };
    bind "Escape" { "delete-from-cursor" (display-lines, 1) };
}

GtkEntry#gedit-commander-entry {
    gtk-key-bindings: terminal-like-bindings;

    background-image: none;
    box-shadow: 0 0;
    transition: none;
    border: 0;
}

""", 'utf-8'))

        self._entry.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _find_overlay(self, view):
        parent = view.get_parent()

        while not isinstance(parent, Gtk.Overlay):
            parent = parent.get_parent()

        return parent

    def _build_ui(self):
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self._overlay = self._find_overlay(self._view)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.show()

        self.pack_end(hbox, False, False, 0)

        self._info_revealer = Gtk.Revealer()

        self._info_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self._info_revealer.set_transition_duration(150)

        self.pack_start(self._info_revealer, False, False, 0)
        self._info_revealer.connect('notify::child-revealed', self._on_info_revealer_child_revealed)

        self._prompt_label = Gtk.Label(label='<b>&gt;&gt;&gt;</b>', use_markup=True)
        self._prompt_label.set_margin_top(3)
        self._prompt_label.set_margin_bottom(3)
        self._prompt_label.set_margin_start(3)

        self._prompt_label.show()
        hbox.add(self._prompt_label)

        self._entry = Gtk.Entry()
        self._entry.set_has_frame(False)
        self._entry.set_name('gedit-commander-entry')
        self._entry.set_hexpand(True)
        self._entry.set_margin_top(3)
        self._entry.set_margin_bottom(3)
        self._entry.set_margin_end(3)

        self._entry.connect('key-press-event', self._on_entry_key_press)

        self._entry.show()
        hbox.add(self._entry)

        self._copy_style_from_view()
        self._view_style_updated_id = self._view.connect('style-updated', self._on_view_style_updated)

    def _on_view_destroyed (self, widget, user_data=None):
        self._view.disconnect(self._view_style_updated_id)
        self._view_style_updated_id = None

    def _on_view_style_updated(self, widget):
        self._copy_style_from_view()

    @property
    def _border_color(self):
        style = self._view.get_buffer().get_style_scheme().get_style('right-margin')

        if not style is None and style.props.foreground_set:
            color = Gdk.RGBA()
            color.parse(style.props.foreground)
        else:
            color = self._get_background_color(Gtk.StateFlags.NORMAL, 'bottom').copy()
            color.red = 1 - color.red
            color.green = 1 - color.green
            color.blue = 1 - color.blue

        color.alpha = 0.3
        return color

    def _get_background_color(self, state, cls=None):
        context = self._view.get_style_context()

        context.save()

        if not cls is None:
            context.add_class(cls)

        ret = context.get_background_color(state)

        context.restore()

        return ret

    def _get_foreground_color(self, state, cls=None):
        context = self._view.get_style_context()

        context.save()

        if not cls is None:
            context.add_class(cls)

        ret = context.get_color(state)

        context.restore()

        return ret

    def _get_font(self):
        context = self._view.get_style_context()
        return context.get_font(Gtk.StateFlags.NORMAL)

    def _styled_widgets(self):
        widgets = [self, self._entry, self._prompt_label]

        if not self._info is None:
            widgets.append(self._info)
            widgets.append(self._info.text_view)

        return widgets

    def _modify_bg(self, col, widget):
        if self._info is None or (self._info.text_view != widget and self._info != widget):
            return col

        d = 0.1

        h, l, s = colorsys.rgb_to_hls(col.red, col.green, col.blue)

        if l < 0.5:
            factor = 1 + d
        else:
            factor = 1 - d

        l = max(0, min(1, l * factor))
        s = max(0, min(1, s * factor))

        r, g, b = colorsys.hls_to_rgb(h, l, s)

        return Gdk.RGBA(r, g, b, col.alpha)

    def _copy_style_from_view(self, widgets=None):
        font = self._get_font()
        fg = self._get_foreground_color(Gtk.StateFlags.NORMAL, 'bottom')
        bg = self._get_background_color(Gtk.StateFlags.NORMAL, 'bottom')

        fgsel = self._get_foreground_color(Gtk.StateFlags.SELECTED)
        bgsel = self._get_background_color(Gtk.StateFlags.SELECTED)

        cursor = self._view.style_get_property('cursor-color')

        if not cursor is None:
            cursor = Gdk.RGBA.from_color(cursor)

        secondary_cursor = self._view.style_get_property('secondary-cursor-color')

        if not secondary_cursor is None:
            secondary_cursor = Gdk.RGBA.from_color(secondary_cursor)

        if widgets is None:
            widgets = self._styled_widgets()

        for widget in widgets:
            widget.override_color(Gtk.StateFlags.NORMAL, fg)
            widget.override_background_color(Gtk.StateFlags.NORMAL, self._modify_bg(bg, widget))

            widget.override_color(Gtk.StateFlags.SELECTED, fgsel)
            widget.override_background_color(Gtk.StateFlags.SELECTED, self._modify_bg(bgsel, widget))

            widget.override_font(font)
            widget.override_cursor(cursor, secondary_cursor)

    def _attach(self):
        reveal = Gtk.Revealer()
        reveal.add(self)
        self.show()

        reveal.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        reveal.set_transition_duration(200)

        reveal.set_valign(Gtk.Align.END)
        reveal.set_halign(Gtk.Align.FILL)

        self._overlay.add_overlay(reveal)
        reveal.show()

        reveal.set_reveal_child(True)
        self._reveal = reveal

        self._entry.grab_focus()

    def grab_focus(self):
        self._entry.grab_focus()

    def _on_entry_key_press(self, widget, evnt):
        state = evnt.state & Gtk.accelerator_get_default_mod_mask()
        text = self._entry.get_text()

        if evnt.keyval == Gdk.KEY_Escape:
            if not self._info is None:
                if not self._suspended is None:
                    self._suspended.resume()

                if not self._info is None:
                    self._info_revealer.set_reveal_child(False)

                self._entry.set_sensitive(True)
            elif self._accel_group:
                self._accel_group = self._accel_group.parent

                if not self._accel_group or not self._accel_group.parent:
                    self._entry.set_editable(True)
                    self._accel_group = None

                self._prompt()
            elif text:
                self._entry.set_text('')
            elif self._command_state:
                self._command_state.clear()
                self._prompt()
            else:
                self._view.grab_focus()
                self._reveal.set_reveal_child(False)

            return True

        if state or self._accel_group:
            # Check if it should be handled by the accel group
            group = self._accel_group

            if not self._accel_group:
                group = commands.Commands().accelerator_group()

            accel = group.activate(evnt.keyval, state)

            if isinstance(accel, commands.accel_group.AccelGroup):
                self._accel_group = accel
                self._entry.set_text('')
                self._entry.set_editable(False)
                self._prompt()

                return True
            elif isinstance(accel, commands.accel_group.AccelCallback):
                self._entry.set_editable(True)
                self._run_command(lambda: accel.activate(self._command_state, self))
                return True

        if not self._entry.get_editable():
            return True

        for handler in self._handlers:
            if (handler[0] == None or handler[0] == state) and evnt.keyval == handler[1] and handler[2](handler[3], state):
                return True

        if not self._info is None and self._info.is_empty:
            self._info_revealer.set_reveal_child(False)

        self._history_prefix = None
        return False

    def _on_history_move(self, direction, modifier):
        pos = self._entry.get_position()

        self._history.update(self._entry.get_text())

        if self._history_prefix == None:
            if len(self._entry.get_text()) == pos:
                self._history_prefix = self._entry.get_chars(0, pos)
            else:
                self._history_prefix = ''

        if self._history_prefix == None:
            hist = ''
        else:
            hist = self._history_prefix

        next = self._history.move(direction, hist)

        if next != None:
            self._entry.set_text(next)
            self._entry.set_position(-1)

        return True

    def _prompt(self, pr=''):
        self._prompt_text = pr

        if self._accel_group != None:
            pr = '<i>%s</i>' % (saxutils.escape(self._accel_group.full_name()),)

        if not pr:
            pr = ''
        else:
            pr = ' ' + pr

        self._prompt_label.set_markup('<b>&gt;&gt;&gt;</b>%s' % pr)

    def _make_info(self):
        if self._info is None:
            self._info = Info()

            self._copy_style_from_view([self._info, self._info.text_view])

            self._info_revealer.add(self._info)
            self._info.show()

            self._info_revealer.show()
            self._info_revealer.set_reveal_child(True)

            self._info.connect('destroy', self._on_info_destroy)

    def _on_info_revealer_child_revealed(self, widget, pspec):
        if not self._info_revealer.get_child_revealed():
            self._info.destroy()
            self._info_revealer.hide()

    def _on_info_destroy(self, widget):
        self._info = None

    def info_show(self, text='', use_markup=False):
        self._make_info()
        self._info.add_lines(text, use_markup)

    def info_status(self, text):
        self._make_info()
        self._info.status(text)

    def _info_add_action(self, stock, callback, data=None):
        self._make_info()
        return self._info.add_action(stock, callback, data)

    def _command_history_done(self):
        self._history.add(self._entry.get_text())
        self._history_prefix = None
        self._entry.set_text('')

    def _on_wait_cancel(self):
        self._on_execute(None, 0)

    def _show_wait_cancel(self):
        self._cancel_button = self._info_add_action('process-stop-symbolic', self._on_wait_cancel)
        self.info_status('<i>Waiting to finish\u2026</i>')

        self._wait_timeout = 0
        return False

    def _complete_word_match(self, match):
        for i in (3, 2, 0):
            if match.group(i) != None:
                return [match.group(i), match.start(i), match.end(i)]

    def _on_suspend_resume(self):
        if self._wait_timeout:
            GLib.source_remove(self._wait_timeout)
            self._wait_timeout = 0
        else:
            if not self._cancel_button is None:
                self._cancel_button.destroy()
                self._cancel_button = None

            self.info_status(None)

        self._entry.set_sensitive(True)
        self._command_history_done()

        if self._entry.props.has_focus or (not self._info is None and not self._info.is_empty):
            self._entry.grab_focus()

    def _run_command(self, cb):
        self._suspended = None

        try:
            ret = cb()
        except Exception as e:
            sys.stderr.write(self._format_trace() + '\n')

            self._command_history_done()
            self._command_state.clear()

            self._prompt()

            # Show error in info
            self.info_show('<b><span color="#f66">Error:</span></b> ' + saxutils.escape(str(e)), True)

            if not isinstance(e, commands.exceptions.Execute):
                self.info_show(self._format_trace(), False)

            return None

        mod = sys.modules['commander.commands.result']

        if ret == mod.Result.SUSPEND:
            # Wait for it...
            self._suspended = ret
            ret.register(self._on_suspend_resume)

            self._wait_timeout = GLib.timeout_add(500, self._show_wait_cancel)
            self._entry.set_sensitive(False)
        else:
            self._command_history_done()
            self._prompt('')

            if ret == mod.Result.PROMPT:
                self._prompt(ret.prompt)
            elif (ret == None or ret == mod.HIDE) and not self._prompt_text and (self._info is None or self._info.is_empty):
                self._command_state.clear()
                self._view.grab_focus()
                self._reveal.set_reveal_child(False)
            else:
                self._entry.grab_focus()

        return ret

    def _format_trace(self):
        tp, val, tb = sys.exc_info()

        origtb = tb

        thisdir = os.path.dirname(__file__)

        # Skip frames up until after the last entry.py...
        while not tb is None:
            filename = tb.tb_frame.f_code.co_filename

            dname = os.path.dirname(filename)

            if not dname.startswith(thisdir):
                break

            tb = tb.tb_next

        msg = traceback.format_exception(tp, val, tb)
        r = ''.join(msg[0:-1])

        # This is done to prevent cyclic references, see python
        # documentation on sys.exc_info
        del origtb

        return r

    def _on_execute(self, dummy, modifier):
        if not self._info is None and not self._suspended:
            self._info_revealer.set_reveal_child(False)

        text = self._entry.get_text().strip()
        words = list(self._re_complete.finditer(text))
        wordsstr = []

        for word in words:
            spec = self._complete_word_match(word)
            wordsstr.append(spec[0])

        if not wordsstr and not self._command_state:
            self._entry.set_text('')
            return

        self._run_command(lambda: commands.Commands().execute(self._command_state, text, words, wordsstr, self, modifier))

        return True

    def _on_complete(self, dummy, modifier):
        # First split all the text in words
        text = self._entry.get_text()
        pos = self._entry.get_position()

        words = list(self._re_complete.finditer(text))
        wordsstr = []

        for word in words:
            spec = self._complete_word_match(word)
            wordsstr.append(spec[0])

        # Find out at which word the cursor actually is
        # Examples:
        #  * hello world|
        #  * hello| world
        #  * |hello world
        #  * hello wor|ld
        #  * hello  |  world
        #  * "hello world|"
        posidx = None

        for idx in range(0, len(words)):
            spec = self._complete_word_match(words[idx])

            if words[idx].start(0) > pos:
                # Empty space, new completion
                wordsstr.insert(idx, '')
                words.insert(idx, None)
                posidx = idx
                break
            elif spec[2] == pos:
                # At end of word, resume completion
                posidx = idx
                break
            elif spec[1] <= pos and spec[2] > pos:
                # In middle of word, do not complete
                return True

        if posidx == None:
            wordsstr.append('')
            words.append(None)
            posidx = len(wordsstr) - 1

        # First word completes a command, if not in any special 'mode'
        # otherwise, relay completion to the command, or complete by advice
        # from the 'mode' (prompt)
        cmds = commands.Commands()

        if not self._command_state and posidx == 0:
            # Complete the first command
            ret = commands.completion.command(words=wordsstr, idx=posidx)
        else:
            complete = None
            realidx = posidx

            if not self._command_state:
                # Get the command first
                cmd = commands.completion.single_command(wordsstr, 0)
                realidx -= 1

                ww = wordsstr[1:]
            else:
                cmd = self._command_state.top()
                ww = wordsstr

            if cmd:
                complete = cmd.autocomplete_func()

            if not complete:
                return True

            # 'complete' contains a dict with arg -> func to do the completion
            # of the named argument the command (or stack item) expects
            args, varargs = cmd.args()

            # Remove system arguments
            s = ['argstr', 'args', 'entry', 'view']
            args = list(filter(lambda x: not x in s, args))

            if realidx < len(args):
                arg = args[realidx]
            elif varargs:
                arg = '*'
            else:
                return True

            if not arg in complete:
                return True

            func = complete[arg]

            try:
                spec = utils.getargspec(func)

                if not ww:
                    ww = ['']

                kwargs = {
                    'words': ww,
                    'idx': realidx,
                    'view': self._view
                }

                if not spec.keywords:
                    for k in list(kwargs.keys()):
                        if not k in spec.args:
                            del kwargs[k]

                ret = func(**kwargs)
            except Exception as e:
                # Can be number of arguments, or return values or simply buggy
                # modules
                print(e)
                traceback.print_exc()
                return True

        if not ret or not ret[0]:
            return True

        res = ret[0]
        completed = ret[1]

        if len(ret) > 2:
            after = ret[2]
        else:
            after = ' '

        # Replace the word
        if words[posidx] == None:
            # At end of everything, just append
            spec = None

            self._entry.insert_text(completed, self._entry.get_text_length())
            self._entry.set_position(-1)
        else:
            spec = self._complete_word_match(words[posidx])

            self._entry.delete_text(spec[1], spec[2])
            self._entry.insert_text(completed, spec[1])
            self._entry.set_position(spec[1] + len(completed))

        if len(res) == 1:
            # Full completion
            lastpos = self._entry.get_position()

            if not isinstance(res[0], commands.module.Module) or not res[0].commands():
                if words[posidx] and after == ' ' and (words[posidx].group(2) != None or words[posidx].group(3) != None):
                    lastpos = lastpos + 1

                self._entry.insert_text(after, lastpos)
                self._entry.set_position(lastpos + 1)
            elif completed == wordsstr[posidx] or not res[0].method:
                self._entry.insert_text('.', lastpos)
                self._entry.set_position(lastpos + 1)

            if not self._info is None:
                self._info_revealer.set_reveal_child(False)
        else:
            # Show popup with completed items
            if not self._info is None:
                self._info.clear()

            ret = []

            for x in res:
                if isinstance(x, commands.method.Method):
                    ret.append('<b>' + saxutils.escape(x.name) + '</b> (<i>' + x.oneline_doc() + '</i>)')
                else:
                    ret.append(str(x))

            self.info_show("\n".join(ret), True)

        return True

    def do_draw(self, ctx):
        ret = Gtk.Box.do_draw(self, ctx)

        col = self._border_color

        ctx.set_line_width(1)
        ctx.set_source_rgba(col.red, col.green, col.blue, col.alpha)

        w = self.get_allocated_width()

        ctx.move_to(0, 0.5)
        ctx.line_to(w, 0.5)
        ctx.stroke()

        if not self._info is None:
            alloc = self._info_revealer.get_allocation()
            y = alloc.y + alloc.height + 0.5

            if y >= 3:
                ctx.move_to(0, y)
                ctx.line_to(w, y)
                ctx.stroke()

        return ret

    def _on_destroy(self, widget):
        # Note we do this not as an override because somehow something
        # goes wrong when finalizing in that case, maybe self is NULL
        # or something like that, and then gets some new empty instance?
        if self._view_style_updated_id:
            self._view.disconnect(self._view_style_updated_id)

        self._history.save()

        self._view = None
        self._view_style_updated_id = None

# ex:ts=4:et
