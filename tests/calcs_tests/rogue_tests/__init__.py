import unittest
from calcs.rogue import RogueDamageCalculator
from objects import buffs, stats, procs, race
from objects.rogue import rogue_talents

class TestRogueDamageCalculator(unittest.TestCase):
    def setUp(self):
        test_buffs = buffs.Buffs(
            'stat_multiplier_buff',
            'crit_chance_buff',
            'melee_haste_buff',
            'attack_power_buff',
            'str_and_agi_buff',
            'armor_debuff',
            'spell_damage_debuff',
            'spell_crit_debuff'
            )
        test_mh = stats.Weapon(737, 1.8, 'dagger', 'hurricane')
        test_oh = stats.Weapon(573, 1.4, 'dagger', 'hurricane')
        test_ranged = stats.Weapon(1104, 2.0, 'thrown')
        test_procs = procs.ProcsList('darkmoon_card_hurricane')
        test_gear_buffs = stats.GearBuffs('chaotic_metagem')        
        test_stats = stats.Stats(20, 3485, 190, 1517, 1086, 641, 899, 666, test_mh, test_oh, test_ranged, test_procs, test_gear_buffs)
        test_race = race.Race('night_elf')
        test_talents = rogue_talents.RogueTalents('0333230113022110321', '0020000000000000000', '0030030000000000000')

        self.calc = RogueDamageCalculator(test_stats, test_talents, None, test_buffs, test_race)
    
    def test_get_spell_hit_from_talents(self):
        self.assertEqual(self.calc.get_spell_hit_from_talents(), .04)
        self.calc.talents.combat.precision = 0
        self.assertEqual(self.calc.get_spell_hit_from_talents(), .0)
    
    def test_get_melee_hit_from_talents(self):
        self.assertEqual(self.calc.get_melee_hit_from_talents(), .04)
        self.calc.talents.combat.precision = 3
        self.assertEqual(self.calc.get_melee_hit_from_talents(), .06)
    
    def test_oh_penalty(self):
        self.assertEqual(self.calc.oh_penalty(), 0.5)
    
    def test_talents_modifiers(self):
        pass
    
    def test_crit_damage_modifiers(self):
        pass
    
    def test_mh_damage(self):
        self.assertTrue(self.calc.mh_damage(0) < self.calc.mh_damage(1))
    
    def test_oh_damage(self):
        self.assertTrue(self.calc.oh_damage(0) < self.calc.oh_damage(1))
    
    def test_eviscerate_damage(self):
        self.assertTrue(self.calc.eviscerate_damage(0, 1) < self.calc.eviscerate_damage(1, 1))
        self.assertTrue(self.calc.eviscerate_damage(0, 1) < self.calc.eviscerate_damage(0, 2))
        self.assertRaises(IndexError, self.calc.eviscerate_damage, 0, 6)
    
    def test_instant_poison_damage(self):
        self.assertTrue(self.calc.instant_poison_damage(0) < self.calc.instant_poison_damage(1))
        self.assertTrue(self.calc.instant_poison_damage(0, mastery=0) < self.calc.instant_poison_damage(0, mastery=1))

class TestRogueDamageCalculatorLevels(TestRogueDamageCalculator):
    def setUp(self):
        super(TestRogueDamageCalculatorLevels, self).setUp()
        self.calc.level = 80
    