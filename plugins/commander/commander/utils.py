# -*- coding: utf-8 -*-
#
#  utils.py - commander
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
import types
import inspect
import sys

class Struct(dict):
    def __getattr__(self, name):
        if not name in self:
            val = super(Struct, self).__getattr__(self, name)
        else:
            val = self[name]

        return val

    def __setattr__(self, name, value):
        if not name in self:
            super(Struct, self).__setattr__(self, name, value)
        else:
            self[name] = value

    def __delattr__(self, name):
        del self[name]

def is_commander_module(mod):
    if type(mod) == types.ModuleType:
        return mod and ('__commander_module__' in mod.__dict__)
    else:
        mod = str(mod)
        return mod.endswith('.py') or (os.path.isdir(mod) and os.path.isfile(os.path.join(mod, '__init__.py')))

def getargspec(func):
    ret = inspect.getargspec(func)

    # Before 2.6 this was just a normal tuple, we don't want that
    if sys.version_info < (2, 6):
        ret = Struct({
            'args': ret[0],
            'varargs': ret[1],
            'keywords': ret[2],
            'defaults': ret[3]
        })

    return ret

# ex:ts=4:et
