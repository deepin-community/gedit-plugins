# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


import unittest
from services.yandex import Yandex
from unittest.mock import patch, MagicMock


class TestYandex(unittest.TestCase):

    @patch('urllib.request.urlopen')
    def test_translate_text(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = bytes('{"code":200,"lang":"ca-en","text":["Hello friends"]}', 'utf-8')
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        yandex = Yandex()
        yandex.set_api_key('our_key')
        translated = yandex.translate_text('Hola amics', 'ca|en')
        self.assertEqual('Hello friends', translated)
        url = "https://translate.yandex.net/api/v1.5/tr.json/translate?lang=ca-en&format=plain&key=our_key&text=Hola+amics"
        mock_urlopen.assert_called_with(url)


if __name__ == '__main__':
    unittest.main()
