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

from abc import ABCMeta, abstractmethod

class Service(metaclass=ABCMeta):

    @abstractmethod
    def translate_text(self, text, language_pair):
        pass

    @abstractmethod
    def get_language_names(self):
        pass

    @abstractmethod
    def get_language_codes(self):
        pass

    @abstractmethod
    def get_language_pair_name(self, source, target, locales_names=None):
        pass

    @abstractmethod
    def get_default_language_codes(self):
        pass

    @abstractmethod
    def has_api_key(self):
        pass

    @abstractmethod
    def get_api_hint(self):
        pass
    
    @abstractmethod    
    def set_api_key(self, key):
        pass

    @abstractmethod
    def set_server(self, server):
        pass
