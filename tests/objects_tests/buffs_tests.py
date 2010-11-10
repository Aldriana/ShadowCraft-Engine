import unittest
from objects import buffs
    
class TestBuffsTrue(unittest.TestCase):
    def setUp(self):
        self.buffs = buffs.Buffs(
            'short_term_haste_buff',
            'stat_multiplier_buff',
            'crit_chance_buff', 
            'all_damage_buff',
            'melee_haste_buff',
            'attack_power_buff',
            'str_and_agi_buff',
            'armor_debuff',
            'physical_vulnerability_debuff',
            'spell_damage_debuff',
            'spell_crit_debuff',
            'bleed_damage_debuff',
            'agi_flask',
            'guild_feast'
            )
    
    def test__getattr__(self):
        self.assertRaises(AttributeError, self.buffs.__getattr__, 'fake_buff')
        self.assertTrue(self.buffs.crit_chance_buff)
    
    def test_stat_multiplier(self):
        self.assertEqual(self.buffs.stat_multiplier(), 1.05)
    
    def test_all_damage_multiplier(self):
        self.assertEqual(self.buffs.all_damage_multiplier(), 1.03)


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
