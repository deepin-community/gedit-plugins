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

import urllib.request, urllib.parse, urllib.error
import json
import locale
from .service import Service

class Apertium(Service):

    g_language_codes = []
    g_language_names = []
    g_locales_names = {}

    DEFAULT_LANGUAGE_NAMES = ["Spanish -> English",
            "English -> Spanish",
            "Catalan -> English",
            "English -> Catalan"]

    DEFAULT_LANGUAGE_CODES = ["spa|eng",
            "eng|spa",
            "cat|eng",
            "eng|cat",
    ]


    @staticmethod
    def _clean_for_ut():
        Apertium.g_language_codes = []
        Apertium.g_language_names = []
        Apertium.g_locales_names = {}

    def get_default_language_codes(self):
        return 'eng|spa'

    def has_api_key(self):
        return False

    def set_api_key(self, key):
        pass

    def set_server(self, server):
        self.server = server

    def get_api_hint(self):
        pass

    def init(self):
        self._fetch_remote_language_names_and_pairs()
   
    def get_language_names(self):
        if len(Apertium.g_language_codes) > 0 and len(Apertium.g_language_names) > 0:
            return Apertium.g_language_names

        return self.DEFAULT_LANGUAGE_NAMES

    def get_language_codes(self):
        if len(Apertium.g_language_codes) > 0 and len(Apertium.g_language_names) > 0:
            return Apertium.g_language_codes

        return self.DEFAULT_LANGUAGE_CODES

    def _get_lang_from_langcountry(self, language):
        if language is not None:
            index = language.find("_")
            if index > 0:
                language = language[:index]

        return language

    def _get_user_locale(self):
        user_locale = locale.getdefaultlocale()[0]
        user_locale = self._get_lang_from_langcountry(user_locale)
        if user_locale is None:
            user_locale = 'en'
        return user_locale

    def _get_language_name(self, langcode, locales_names):
        if langcode in locales_names:
            language_name = locales_names[langcode]
        else:
            locale_no_country = self._get_lang_from_langcountry(langcode)
            country = langcode[len(locale_no_country) + 1:]

            language_name = '{0} ({1})'.format(locales_names[locale_no_country],
                                               country)
        return language_name

    def get_language_pair_name(self, source, target, locales_names=None):
        if locales_names is None:
            locales_names = Apertium.g_locales_names

        source = self._get_language_name(source, locales_names)
        target = self._get_language_name(target, locales_names)
        return '{0} -> {1}'.format(source, target)

    def _is_langcode_in_list(self, langcode, locales_names):
        if langcode not in locales_names:
            locale_no_country = self._get_lang_from_langcountry(langcode)
            if locale_no_country not in locales_names:
                return False
        return True

    def _add_missing_locale_names_in_english(self, locales, locales_names):
        locales_names_en = self._get_remote_language_names(locales, 'en')
        for l in locales_names_en:
            if l not in locales_names:
                locales_names[l] = locales_names_en[l]

        return locales_names


    def _fetch_remote_language_names_and_pairs(self):

        if len(Apertium.g_language_names) > 0:
            return

        try:
            language_names = []
            en_names_requested = False

            user_locale = self._get_user_locale()
            language_pair_source, language_pair_target, locales, language_codes = self._get_remote_language_pairs()
            locales_names = self._get_remote_language_names(locales, user_locale)

            for i in range(len(language_pair_source)):
                source = language_pair_source[i]
                target = language_pair_target[i]

                if en_names_requested is False and \
                   (self._is_langcode_in_list(source, locales_names) or\
                   self._is_langcode_in_list(target, locales_names)):
                    en_names_requested = True
                    locales_names = self._add_missing_locale_names_in_english(locales, locales_names)

                language_pair = self.get_language_pair_name(source, target, locales_names)
                language_names.append(language_pair)

            Apertium.g_locales_names = locales_names
            Apertium.g_language_names = language_names
            Apertium.g_language_codes = language_codes

        except Exception as e:
            print("_fetch_remote_language_names_and_pairs exception {0}".format(e))


    def _get_remote_language_pairs(self):
        url = "{0}/listPairs".format(self.server)

        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode("utf-8"))
        pairs = data['responseData']

        locales = set()
        language_pair_source = []
        language_pair_target = []
        language_codes = []

        for pair in pairs:
            source = pair['sourceLanguage']
            target = pair['targetLanguage']
            language_pair = '{0}|{1}'.format(source, target)
            language_pair_source.append(source)
            language_pair_target.append(target)
            locales.add(source)
            locales.add(target)
            language_codes.append(language_pair)

        return language_pair_source, language_pair_target, locales, language_codes
 
    def _get_remote_language_names(self, locales, user_locale):
        locales_string = ''
        for locale_code in locales:
            locales_string += locale_code + '+'

        url = "{0}/listLanguageNames?locale={1}&languages={2}".format(self.server,
                user_locale, locales_string)

        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode("utf-8"))

    def translate_text(self, text, language_pair):
        url = "{0}/translate?langpair={1}&markUnknown=no".format(self.server, language_pair)
        url += "&q=" + urllib.parse.quote_plus(text.encode('utf-8'))

        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode("utf-8"))
        translated = data['responseData']['translatedText']
        return translated

