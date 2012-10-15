# -*- coding: utf-8 -*-
from wowapi.api import WoWApi

try:
    import unittest2 as unittest
except ImportError:
    import unittest as unittest

wowapi = WoWApi()
class Test_Locales(unittest.TestCase):

    def test_locale_en_US(self):
        item = wowapi.get_item('us',25,None,'en_US')
        self.assertEqual(item['data']['name'],'Worn Shortsword')

    def test_locale_es_MX(self):
        item = wowapi.get_item('us',25,None,'es_MX')
        self.assertEqual(item['data']['name'],'Espada corta desgastada')

    def test_locale_en_GB(self):
        item = wowapi.get_item('eu',25,None,'en_GB')
        self.assertEqual(item['data']['name'],'Worn Shortsword')

    def test_locale_es_ES(self):
        item = wowapi.get_item('eu',25,None,'es_ES')
        self.assertEqual(item['data']['name'],'Espada corta desgastada')

    def test_locale_fr_FR(self):
        item = wowapi.get_item('eu',25,None,'fr_FR')
        self.assertEqual(item['data']['name'],u'Epée courte usée')

    def test_locale_ru_RU(self):
        item = wowapi.get_item('eu',25,None,'ru_RU')
        self.assertEqual(item['data']['name'],u'Иссеченный короткий меч')

    def test_locale_de_DE(self):
        item = wowapi.get_item('eu',25,None,'de_DE')
        self.assertEqual(item['data']['name'],'Abgenutztes Kurzschwert')

    def test_locale_ko_KR(self):
        item = wowapi.get_item('kr',25,None,'ko_KR')
        self.assertEqual(item['data']['name'],u'낡은 쇼트소드')

    def test_locale_zh_TW(self):
        item = wowapi.get_item('tw',25,None,'zh_TW')
        self.assertEqual(item['data']['name'],u'破損的短劍')

    def test_locale_zh_CN(self):
        item = wowapi.get_item('cn',25,None,'zh_CN')
        self.assertEqual(item['data']['name'],u'破损的短剑')

