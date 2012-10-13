# -*- coding: utf-8 -*-
from wowapi.api import WoWApi

try:
    import unittest2 as unittest
except ImportError:
    import unittest as unittest

wowapi = WoWApi()
class Test_Regions(unittest.TestCase):
    def test_region_us(self):
        realm = wowapi.get_realm('us')
        self.assertGreater(len(realm['data']['realms']),1)

    def test_region_eu(self):
        realm = wowapi.get_realm('eu')
        self.assertGreater(len(realm['data']['realms']),1)

    def test_region_kr(self):
        realm = wowapi.get_realm('kr')
        self.assertGreater(len(realm['data']['realms']),1)

    def test_region_tw(self):
        realm = wowapi.get_realm('tw')
        self.assertGreater(len(realm['data']['realms']),1)

    def test_region_cn(self):
        realm = wowapi.get_realm('cn')
        self.assertGreater(len(realm['data']['realms']),1)