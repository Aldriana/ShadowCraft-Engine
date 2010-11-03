import unittest
from objects import buffs
    
class TestBuffs(unittest.TestCase):
    def setUp(self):
        self.buffs = buffs.Buffs(
            'stat_multiplier_buff',
            'crit_chance_buff',
            'melee_haste_buff',
            'attack_power_buff',
            'str_and_agi_buff',
            'armor_debuff',
            'spell_damage_debuff',
            'spell_crit_debuff'
            )
    
    def test__getattr__(self):
        self.assertRaises(AttributeError, self.buffs.__getattr__, 'fake_buff')
        self.assertTrue(self.buffs.crit_chance_buff)
        self.assertFalse(self.buffs.bleed_damage_debuff)
    
    def test_stat_multiplier(self):
        self.assertEqual(self.buffs.stat_multiplier(), 1.05)
    
    