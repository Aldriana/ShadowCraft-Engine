import unittest
from shadowcraft.calcs.rogue.Aldriana import AldrianasRogueDamageCalculator
from shadowcraft.calcs.rogue.Aldriana import settings

from shadowcraft.objects import buffs
from shadowcraft.objects import race
from shadowcraft.objects import stats
from shadowcraft.objects import procs
from shadowcraft.objects.rogue import rogue_talents
from shadowcraft.objects.rogue import rogue_glyphs

class TestAldrianasRogueDamageCalculator(unittest.TestCase):
    def test_get_ep(self):
        test_buffs = buffs.Buffs()
        test_mh = stats.Weapon(939.5, 1.8, 'dagger', 'landslide')
        test_oh = stats.Weapon(730.5, 1.4, 'dagger', 'landslide')
        test_ranged = stats.Weapon(1371.5, 2.2, 'thrown')
        test_procs = procs.ProcsList('heroic_prestors_talisman_of_machination', 'fluid_death', 'rogue_t11_4pc')
        test_gear_buffs = stats.GearBuffs('rogue_t11_2pc', 'leather_specialization', 'potion_of_the_tolvir', 'chaotic_metagem')
        test_stats = stats.Stats(20, 4756, 190, 1022, 1329, 597, 1189, 1377, test_mh, test_oh, test_ranged, test_procs, test_gear_buffs)
        test_talents = rogue_talents.RogueTalents('0333230113022110321', '0020000000000000000', '2030030000000000000')
        glyph_list = ['backstab', 'mutilate', 'rupture']
        test_glyphs = rogue_glyphs.RogueGlyphs(*glyph_list)
        test_race = race.Race('night_elf')
        test_cycle = settings.AssassinationCycle()
        test_settings = settings.Settings(test_cycle, response_time=1)
        test_level = 85
        calculator = AldrianasRogueDamageCalculator(test_stats, test_talents, test_glyphs, test_buffs, test_race, test_settings, test_level)
        ep_values = calculator.get_ep()
        self.assertTrue(ep_values['agi'] < 4.0)
        self.assertTrue(ep_values['agi'] > 2.0)
        self.assertTrue(ep_values['yellow_hit'] < 4.0)
        self.assertTrue(ep_values['yellow_hit'] > 1.0)
        self.assertTrue(ep_values['crit'] < 2.0)
        self.assertTrue(ep_values['crit'] > 0.0)
