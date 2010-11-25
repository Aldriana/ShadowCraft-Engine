import calcs
import unittest
from core import exceptions
from objects import buffs
from objects import race
from objects import stats
from objects import procs
from objects import glyphs

class TestDamageCalculator(unittest.TestCase):
    def make_calculator(self, buffs_list, gear_buffs_list):
        test_buffs = buffs.Buffs(*buffs_list)
        test_gear_buffs = stats.GearBuffs(*gear_buffs_list)
        test_procs = procs.ProcsList()
        test_mh = stats.Weapon(737, 1.8, 'dagger', 'hurricane')
        test_oh = stats.Weapon(573, 1.4, 'dagger', 'hurricane')
        test_ranged = stats.Weapon(1104, 2.0, 'thrown')
        test_stats = stats.Stats(20, 3485, 190, 1517, 1086, 641, 899, 666, test_mh, test_oh, test_ranged, test_procs, test_gear_buffs)
        test_race = race.Race('night_elf')
        test_talents = None
        test_glyphs = glyphs.Glyphs()
        return calcs.DamageCalculator(test_stats, test_talents, test_glyphs, test_buffs, test_race)

    def setUp(self):
        self.calculator = self.make_calculator([], [])

    def test_melee_hit_chance(self):
        pass
    
    def test_one_hand_melee_hit_chance(self):
        self.assertAlmostEqual(
            self.calculator.one_hand_melee_hit_chance(dodgeable=False, parryable=False),
            1.0)
        self.assertAlmostEqual(
            self.calculator.one_hand_melee_hit_chance(dodgeable=True, parryable=False),
            1.0 - (0.065 - (641 / (30.027200698852539 * 4)) * 0.01))
        self.calculator.stats.exp = 0
        self.assertAlmostEqual(
            self.calculator.one_hand_melee_hit_chance(dodgeable=True, parryable=False),
            1.0 - 0.065)
        self.assertAlmostEqual(
            self.calculator.one_hand_melee_hit_chance(dodgeable=True, parryable=True),
            1.0 - 0.14 - 0.065)
        self.assertAlmostEqual(
            self.calculator.one_hand_melee_hit_chance(dodgeable=False, parryable=True),
            1.0 - 0.14)
        self.calculator.stats.hit = 0
        self.assertAlmostEqual(
            self.calculator.one_hand_melee_hit_chance(dodgeable=True, parryable=False),
            1.0 - 0.065 - 0.08)
    
    def test_dual_wield_mh_hit_chance(self):
        self.assertAlmostEqual(
            self.calculator.dual_wield_mh_hit_chance(dodgeable=False, parryable=False),
            1.0 - (0.27 - 0.01 * (1086 / 120.109001159667969)))
        self.calculator.stats.hit = 0
        self.calculator.stats.exp = 0
        self.assertAlmostEqual(
            self.calculator.dual_wield_mh_hit_chance(dodgeable=False, parryable=False),
            1.0 - 0.27)
        self.assertAlmostEqual(
            self.calculator.dual_wield_mh_hit_chance(dodgeable=True, parryable=False),
            1.0 - 0.27 - 0.065)
        self.assertAlmostEqual(
            self.calculator.dual_wield_mh_hit_chance(dodgeable=True, parryable=True),
            1.0 - 0.27 - 0.065 - 0.14)
        self.assertAlmostEqual(
            self.calculator.dual_wield_mh_hit_chance(dodgeable=False, parryable=True),
            1.0 - 0.27 - 0.14)
        
    def test_dual_wield_oh_hit_chance(self):
        pass
    
    def test_spell_hit_chance(self):
        self.assertAlmostEqual(self.calculator.spell_hit_chance(),
            1.0 - (0.17 - 0.01 * (1086 / 102.445999145507812)))
            
    def test_buff_melee_crit(self):
        pass
    
    def test_buff_spell_crit(self):
        pass
    
    def test_target_armor(self):
        pass

    def test_raid_settings_modifiers(self):
        self.assertRaises(exceptions.InvalidInputException, self.calculator.raid_settings_modifiers)

    def test_mixology_no_flask(self):
        test_calculator = self.make_calculator([], ['mixology'])
        self.assertEqual(test_calculator.stats.agi, self.calculator.stats.agi)

    def test_mixology(self):
        test_calculator = self.make_calculator(['agi_flask'], ['mixology'])
        self.assertEqual(test_calculator.stats.agi, self.calculator.stats.agi + 80)

    def test_master_of_anatomy(self):
        test_calculator = self.make_calculator([], ['master_of_anatomy'])
        self.assertEqual(test_calculator.stats.crit, self.calculator.stats.crit + 80)
