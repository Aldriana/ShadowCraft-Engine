import unittest
from objects import stats
    
class TestStats(unittest.TestCase):
    def setUp(self):
        self.stats = stats.Stats(20, 3485, 190, 1517, 1086, 641, 899, 666, None, None, None, None, None)

    def test_stats(self):
        self.assertEqual(self.stats.agi, 3485)
    
    def test_set_constants_for_level(self):
        self.assertRaises(AssertionError, self.stats.__setattr__, 'level', 86)
    
    def test_get_mastery_from_rating(self):
        self.assertAlmostEqual(self.stats.get_mastery_from_rating(), 8 + 666 / 179.279998779296875)
        self.assertAlmostEqual(self.stats.get_mastery_from_rating(100),  8 + 100 / 179.279998779296875)
        self.stats.level = 80
        self.assertAlmostEqual(self.stats.get_mastery_from_rating(), 8 + 666 / 45.906)
        self.assertAlmostEqual(self.stats.get_mastery_from_rating(100),  8 + 100 / 45.906)
    
    def test_get_melee_hit_from_rating(self):
        self.assertAlmostEqual(self.stats.get_melee_hit_from_rating(), .01 * 1086 / 120.109001159667969)
        self.assertAlmostEqual(self.stats.get_melee_hit_from_rating(100), .01 * 100 / 120.109001159667969)
    
    def test_get_expertise_from_rating(self):
        self.assertAlmostEqual(self.stats.get_expertise_from_rating(), .01 * 641 / (30.027200698852539 * 4))
        self.assertAlmostEqual(self.stats.get_expertise_from_rating(100), .01 * 100 / (30.027200698852539 * 4))

    def test_get_spell_hit_from_rating(self):
        self.assertAlmostEqual(self.stats.get_spell_hit_from_rating(), .01 * 1086 / 102.445999145507812)
        self.assertAlmostEqual(self.stats.get_spell_hit_from_rating(100), .01 * 100 / 102.445999145507812)
    
    def test_get_crit_from_rating(self):
        self.assertAlmostEqual(self.stats.get_crit_from_rating(), .01 * 1517 / 179.279998779296875)
        self.assertAlmostEqual(self.stats.get_crit_from_rating(100), .01 * 100 / 179.279998779296875)

    def test_get_haste_multiplier_from_rating(self):
        self.assertAlmostEqual(self.stats.get_haste_multiplier_from_rating(), 1 + .01 * 899 / 128.057006835937500)
        self.assertAlmostEqual(self.stats.get_haste_multiplier_from_rating(100), 1 + .01 * 100 / 128.057006835937500)


class TestWeapon(unittest.TestCase):
    def setUp(self):
        self.mh = stats.Weapon(1000, 2.0, 'dagger', 'hurricane')
        self.ranged = stats.Weapon(1104, 2.0, 'thrown')
    
    def test___init__(self):
        self.assertAlmostEqual(self.mh._normalization_speed, 1.7)
        self.assertAlmostEqual(self.mh.speed, 2.0)
        self.assertAlmostEqual(self.mh.weapon_dps, 1000 / 2.0)
        self.assertEqual(self.mh.type, 'dagger')
        self.assertRaises(AssertionError, stats.Weapon, 1000, 2.0, 'thrown', 'fake_enchant')
        self.assertAlmostEqual(self.ranged._normalization_speed, 2.1)
        mh = stats.Weapon(1000, 1.8, 'dagger', 'hurricane')
        self.assertAlmostEqual(mh.hurricane.proc_chance, 1 * 1.8 / 60)
        oh = stats.Weapon(1000, 1.4, 'dagger', 'hurricane')
        self.assertAlmostEqual(mh.hurricane.proc_chance, 1 * 1.8 / 60)
        self.assertAlmostEqual(oh.hurricane.proc_chance, 1 * 1.4 / 60)

    def test__getattr__(self):
        self.assertTrue(self.mh.hurricane)
        self.assertFalse(self.mh.landslide)
        self.assertRaises(AttributeError, self.mh.__getattr__, 'fake_enchant')
    
    def test_is_melee(self):
        self.assertTrue(self.mh.is_melee())
        self.assertFalse(self.ranged.is_melee())
    
    def test_damage(self):
        self.assertAlmostEqual(self.mh.damage(1000), 2.0 * (1000 / 2.0 + 1000 / 14.0))
    
    def test_normalized_damage(self):
        self.assertAlmostEqual(self.mh.normalized_damage(1000), 1000 + (1.7 * 1000 / 14.0))


class TestGearBuffs(unittest.TestCase):
    def setUp(self):
        self.gear = stats.GearBuffs('chaotic_metagem', 'leather_specialization', 'rogue_t11_2pc', 'potion_of_the_tolvir', 'engineer_glove_enchant')
        self.gear_none = stats.GearBuffs()

    def test__getattr__(self):
        self.assertTrue(self.gear.chaotic_metagem)
        self.assertTrue(self.gear.leather_specialization)
        self.assertFalse(self.gear.unsolvable_riddle)
        self.assertRaises(AttributeError, self.gear.__getattr__, 'fake_gear_buff')

    def test_metagem_crit_multiplier(self):
        self.assertAlmostEqual(self.gear.metagem_crit_multiplier(), 1.03)
        self.assertAlmostEqual(self.gear_none.metagem_crit_multiplier(), 1.0)

    def test_rogue_t11_2pc_crit_bonus(self):
        self.assertAlmostEqual(self.gear.rogue_t11_2pc_crit_bonus(), 0.05)
        self.assertAlmostEqual(self.gear_none.rogue_t11_2pc_crit_bonus(), 0.0)

    def test_leather_specialization_multiplier(self):
        self.assertAlmostEqual(self.gear.leather_specialization_multiplier(), 1.05)
        self.assertAlmostEqual(self.gear_none.leather_specialization_multiplier(), 1.0)

    def test_get_all_activated_agi_boosts(self):
        self.assertEqual(len(self.gear.get_all_activated_agi_boosts()), 1)
        self.assertEqual(len(self.gear_none.get_all_activated_agi_boosts()), 0)

    def test_get_all_activated_boosts_for_stat(self):
        self.assertEqual(len(self.gear.get_all_activated_boosts_for_stat('agi')), 1)
        self.assertEqual(len(self.gear.get_all_activated_boosts_for_stat('haste_rating')), 1)
        self.assertEqual(len(self.gear.get_all_activated_boosts_for_stat('crit_rating')), 0)

    def test_get_all_activated_haste_rating_boosts(self):
        self.assertEqual(len(self.gear.get_all_activated_haste_rating_boosts()), 1)
        self.assertEqual(len(self.gear_none.get_all_activated_haste_rating_boosts()), 0)
