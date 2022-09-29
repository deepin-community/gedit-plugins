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

from gi.repository import Gio


class Settings():

    TRANSLATE_KEY_BASE = 'org.gnome.gedit.plugins.translate'
    OUTPUT_TO_DOCUMENT = 'output-to-document'
    LANGUAGE_PAIR = 'language-pair'
    SERVICE = 'service'
    API_KEY = 'api-key'
    APERTIUM_SERVER_KEY = 'apertium-server'

    def __init__(self):
        self._settings = Gio.Settings.new(self.TRANSLATE_KEY_BASE)

    def get_language_pair(self):
        return self._settings.get_string(self.LANGUAGE_PAIR)

    def get_service(self):
        return self._settings.get_uint(self.SERVICE)

    def get_apikey(self):
        return self._settings.get_string(self.API_KEY)

    def get_output_document(self):
        return self._settings.get_boolean(self.OUTPUT_TO_DOCUMENT)

    def set_language_pair(self, language_pair):
        self._settings.set_string(self.LANGUAGE_PAIR, language_pair)

    def set_service(self, service_id):
        self._settings.set_uint(self.SERVICE, service_id)

    def set_apikey(self, text):
        self._settings.set_string(self.API_KEY, text)

    def set_output_document(self, document):
        self._settings.set_boolean(self.OUTPUT_TO_DOCUMENT, document)

    def get_apertium_server(self):
        return self._settings.get_string(self.APERTIUM_SERVER_KEY)
