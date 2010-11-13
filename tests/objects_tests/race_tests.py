import unittest
from objects import race
    
class TestRace(unittest.TestCase):
    def setUp(self):
        self.race = race.Race('human')
    
    def test__init__(self):
        self.assertEqual(self.race.race_name, 'human')
        self.assertEqual(self.race.character_class, 'rogue')

    def test_set_racials(self):
        tauren = race.Race('tauren')
        self.assertTrue(tauren.endurance)
        self.assertFalse(self.race.blood_fury)

    def test_exceptions(self):
        self.assertRaises(AssertionError, self.race.__setattr__, 'level', 81)
        self.assertRaises(AssertionError, self.race.__init__, 'murloc')
        self.assertRaises(AssertionError, self.race.__init__, 'undead', 'demon_hunter')
        
    def test__getattr__(self):
        human = race.Race('human')
        racial_stats = (122, 206, 114, 46, 73)
        for i, stat in enumerate(['racial_str', 'racial_agi', 'racial_sta', 'racial_int', 'racial_spi']):
            self.assertEqual(getattr(self.race, stat), racial_stats[i])
        racial_stats = (122 - 4, 206 + 4, 114, 46, 73)
        night_elf = race.Race('night_elf')
        for i, stat in enumerate(['racial_str', 'racial_agi', 'racial_sta', 'racial_int', 'racial_spi']):
            self.assertEqual(getattr(night_elf, stat), racial_stats[i])

    def test_get_racial_expertise(self):
        self.assertTrue(self.race.get_racial_expertise('1h_sword') - 0.0075 < 0.00000001)
        self.assertEqual(self.race.get_racial_expertise('1h_xe'), 0)

    def test_get_racial_crit(self):
        for weapon in ('thrown', 'gun', 'bow'):
            self.assertEqual(self.race.get_racial_crit(weapon), 0)
        troll = race.Race('troll')        
        self.assertEqual(troll.get_racial_crit('thrown'), 0.01)
        self.assertEqual(troll.get_racial_crit('bow'), 0.01)
        self.assertEqual(troll.get_racial_crit('gun'), 0)

    def test_get_racial_hit(self):
        self.assertEqual(self.race.get_racial_hit(), 0)
        draenei = race.Race('draenei')
        self.assertEqual(draenei.get_racial_hit(), 0.01)
