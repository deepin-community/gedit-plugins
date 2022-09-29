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

from .apertium import Apertium
from .yandex import Yandex


class Services():

    APERTIUM_ID = 0
    YANDEX_ID = 1
    SERVICES = {APERTIUM_ID: "Apertium", YANDEX_ID: "Yandex"}

    @staticmethod
    def get_name(service_id):
        return Services.SERVICES[service_id]

    @staticmethod
    def get(service_id):
        if service_id == Services.APERTIUM_ID:
            return Apertium()
        elif service_id == Services.YANDEX_ID:
            return Yandex()

    @staticmethod
    def get_names_and_ids():
        return Services.SERVICES
