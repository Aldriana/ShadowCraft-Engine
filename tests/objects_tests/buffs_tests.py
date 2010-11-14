import unittest
from core import exceptions
from objects import buffs
    
class TestBuffsTrue(unittest.TestCase):
    def setUp(self):
        self.buffs = buffs.Buffs(*buffs.Buffs.allowed_buffs)
    
    def test_exception(self):
        self.assertRaises(buffs.InvalidBuffException, buffs.Buffs, 'fake_buff')
    
    def test__getattr__(self):
        self.assertRaises(AttributeError, self.buffs.__getattr__, 'fake_buff')
        self.assertTrue(self.buffs.crit_chance_buff)
    
    def test_stat_multiplier(self):
        self.assertEqual(self.buffs.stat_multiplier(), 1.05)
    
    def test_all_damage_multiplier(self):
        self.assertEqual(self.buffs.all_damage_multiplier(), 1.03)
    
    def test_spell_damage_multiplier(self):
        self.assertEqual(self.buffs.spell_damage_multiplier(), 1.08 * 1.03)
    
    def test_physical_damage_multiplier(self):
        self.assertEqual(self.buffs.physical_damage_multiplier(), 1.04 * 1.03)
    
    def test_bleed_damage_multiploer(self):
        self.assertEqual(self.buffs.bleed_damage_multiplier(), 1.30 * 1.03 * 1.04)
    
    def test_attack_power_multiplier(self):
        self.assertEqual(self.buffs.attack_power_multiplier(), 1.1)
    
    def test_melee_haste_multiplier(self):
        self.assertEqual(self.buffs.melee_haste_multiplier(), 1.1)
    
    def test_buff_str(self):
        self.assertEqual(self.buffs.buff_str(), 549)

    def test_buff_agi(self):
        self.assertEqual(self.buffs.buff_agi(), 549 + 90 + 300)
    
    def test_buff_all_crit(self):
        self.assertEqual(self.buffs.buff_all_crit(), 0.05)
    
    def test_buff_spell_crit(self):
        self.assertEqual(self.buffs.buff_spell_crit(), 0.05)
    
    def test_armor_reduction_multiplier(self):
        self.assertEqual(self.buffs.armor_reduction_multiplier(), 0.88)


class TestBuffsFalse(unittest.TestCase):
    def setUp(self):
        self.buffs = buffs.Buffs()
    
    def test__getattr__(self):
        self.assertRaises(AttributeError, self.buffs.__getattr__, 'fake_buff')
        self.assertFalse(self.buffs.bleed_damage_debuff)
    
    def test_stat_multiplier(self):
        self.assertEqual(self.buffs.stat_multiplier(), 1.0)
    
    def test_all_damage_multiplier(self):
        self.assertEqual(self.buffs.all_damage_multiplier(), 1.0)

    def test_spell_damage_multiplier(self):
        self.assertEqual(self.buffs.spell_damage_multiplier(), 1.0)
    
    def test_physical_damage_multiplier(self):
        self.assertEqual(self.buffs.physical_damage_multiplier(), 1.0)
    
    def test_bleed_damage_multiploer(self):
        self.assertEqual(self.buffs.bleed_damage_multiplier(), 1.0)
    
    def test_attack_power_multiplier(self):
        self.assertEqual(self.buffs.attack_power_multiplier(), 1.0)
    
    def test_melee_haste_multiplier(self):
        self.assertEqual(self.buffs.melee_haste_multiplier(), 1.0)
    
    def test_buff_str(self):
        self.assertEqual(self.buffs.buff_str(), 0)

    def test_buff_agi(self):
        self.assertEqual(self.buffs.buff_agi(), 0)
    
    def test_buff_all_crit(self):
        self.assertEqual(self.buffs.buff_all_crit(), 0.0)
    
    def test_buff_spell_crit(self):
        self.assertEqual(self.buffs.buff_spell_crit(), 0.0)
    
    def test_armor_reduction_multiplier(self):
        self.assertEqual(self.buffs.armor_reduction_multiplier(), 1.0)

class TestBuffsLevel(unittest.TestCase):
    def setUp(self):
        self.buffs = buffs.Buffs('str_and_agi_buff')
    
    def test(self):
        self.assertEqual(self.buffs.buff_agi(), 549)
        self.assertEqual(self.buffs.buff_str(), 549)
        self.buffs.level = 80
        self.assertEqual(self.buffs.buff_agi(), 155)
        self.assertEqual(self.buffs.buff_str(), 155)

    def test_exception(self):
        self.assertRaises(exceptions.InvalidLevelException, self.buffs.__setattr__, 'level', 86)
