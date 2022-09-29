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

import os
import sys

path = os.path.dirname(__file__)

if not path in sys.path:
    sys.path.insert(0, path)

import gi
gi.require_version('Gedit', '3.0')
gi.require_version('Gtk', '3.0')

from appactivatable import CommanderAppActivatable
from windowactivatable import CommanderWindowActivatable

# ex:ts=4:et
