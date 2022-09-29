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

import os

class History:
    def __init__(self, filename):
        self._filename = filename
        self._history = ['']
        self._ptr = 0

        self.load()

    def find(self, direction, prefix):
        ptr = self._ptr + direction

        while ptr >= 0 and ptr < len(self._history):
            if self._history[ptr].startswith(prefix):
                return ptr

            ptr += direction

        return -1

    def move(self, direction, prefix):
        next = self.find(direction, prefix)

        if next != -1:
            self._ptr = next
            return self._history[self._ptr]
        else:
            return None

    def up(self, prefix=''):
        return self.move(-1, prefix)

    def down(self, prefix=''):
        return self.move(1, prefix)

    def add(self, line):
        if line.strip() != '':
            if self._history[-1] != '':
                self._history.append(line)
            else:
                self._history[-1] = line

        if self._history[-1] != '':
            self._history.append('')

        self._ptr = len(self._history) - 1

    def update(self, line):
        self._history[self._ptr] = line

    def load(self):
        try:
            #FIXME: we should rewrite this
            self._history = list(map(lambda x: x.strip("\n"), open(self._filename, 'r').readlines()))
            self._history.append('')
            self._ptr = len(self._history) - 1
        except IOError:
            pass

    def save(self):
        try:
            os.makedirs(os.path.dirname(self._filename))
        except OSError:
            pass

        try:
            f = open(self._filename, 'w')

            if self._history[-1] == '':
                hist = self._history[:-1]
            else:
                hist = self._history

            f.writelines(map(lambda x: x + "\n", hist))
            f.close()
        except IOError:
            pass

# ex:ts=4:et
