import unittest
from objects import race
    
class TestRace(unittest.TestCase):
    def setUp(self):
        self.race = race.Race('human')
    
    def test__init__(self):
        self.assertEqual(self.race.race_name, 'human')
        self.assertEqual(self.race.character_class, 'rogue')

    def test_set_racials(self):
        self.assertTrue(self.race.sword_1h_specialization)
        self.assertFalse(self.race.blood_fury_physical)

    def test_exceptions(self):
        self.assertRaises(race.InvalidRaceException, self.race.__setattr__, 'level', 81)
        self.assertRaises(race.InvalidRaceException, self.race.__init__, 'murloc')
        self.assertRaises(race.InvalidRaceException, self.race.__init__, 'undead', 'demon_hunter')
        
    def test__getattr__(self):
        racial_stats = (122, 206, 114, 46, 73)
        for i, stat in enumerate(['racial_str', 'racial_agi', 'racial_sta', 'racial_int', 'racial_spi']):
            self.assertEqual(getattr(self.race, stat), racial_stats[i])
        racial_stats = (122 - 4, 206 + 4, 114, 46, 73)
        night_elf = race.Race('night_elf')
        for i, stat in enumerate(['racial_str', 'racial_agi', 'racial_sta', 'racial_int', 'racial_spi']):
            self.assertEqual(getattr(night_elf, stat), racial_stats[i])

    def test_get_racial_expertise(self):
        self.assertTrue(abs(self.race.get_racial_expertise('1h_sword') - 0.0075) < 0.00000001)
        self.assertEqual(self.race.get_racial_expertise('1h_axe'), 0)

    def test_get_racial_crit(self):
        for weapon in ('thrown', 'gun', 'bow'):
            self.assertEqual(self.race.get_racial_crit(weapon), 0)
        troll = race.Race('troll')        
        self.assertEqual(troll.get_racial_crit('thrown'), 0.01)
        self.assertEqual(troll.get_racial_crit('bow'), 0.01)
        self.assertEqual(troll.get_racial_crit('gun'), 0)
        self.assertEqual(troll.get_racial_crit(), 0)
        worgen = race.Race('worgen')
        self.assertEqual(worgen.get_racial_crit(), 0.01)
        self.assertEqual(worgen.get_racial_crit('gun'), 0.01)
        self.assertEqual(worgen.get_racial_crit('axe'), 0.01)

    def test_get_racial_hit(self):
        self.assertEqual(self.race.get_racial_hit(), 0)
        draenei = race.Race('draenei')
        self.assertEqual(draenei.get_racial_hit(), 0.01)

    def test_get_racial_haste(self):
        self.assertEqual(self.race.get_racial_haste(), 0)
        goblin = race.Race('goblin')
        self.assertEqual(goblin.get_racial_haste(), 0.01)

    def test_get_racial_stat_boosts(self):
        self.assertEqual(len(self.race.get_racial_stat_boosts()), 0)
        orc = race.Race('orc')
        orc.level = 85;
        abilities = orc.get_racial_stat_boosts()
        self.assertEqual(len(abilities), 2)
        self.assertEqual(abilities[0]['duration'], 15)
        self.assertIn(abilities[1]['stat'], ('ap', 'sp'))
        self.assertNotEqual(abilities[0]['stat'],abilities[1]['stat'])
        if (abilities[0]['stat'] == 'ap'):
            self.assertEqual(abilities[0]['value'], 1170)
        else:
            self.assertEqual(abilities[0]['value'], 585)

    def test_goblin_racial(self):
        goblin = race.Race('goblin')
        goblin.level = 80
        self.assertTrue(goblin.rocket_barrage)
        self.assertAlmostEqual(goblin.activated_racial_data['rocket_barrage']['value'](goblin, 10, 10, 10), 172.8093)
