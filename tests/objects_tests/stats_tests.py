import unittest
from objects import stats
    
class TestStats(unittest.TestCase):
    def setUp(self):
        self.stats = stats.Stats(20, 3485, 190, 1517, 1086, 641, 899, 666, None, None, None, None, None)

    def test_stats(self):
        self.assertEqual(self.stats.agi, 3485)
    
    def test_get_mastery_from_rating(self):
        self.assertRaises(AssertionError, self.stats.get_mastery_from_rating, level=82)
        self.assertAlmostEqual(self.stats.get_mastery_from_rating(), 8 + 666/179.279998779296875)
        self.assertAlmostEqual(self.stats.get_mastery_from_rating(100),  8 + 100/179.279998779296875)
    
    def test_get_melee_hit_from_rating(self):
        self.assertRaises(AssertionError, self.stats.get_melee_hit_from_rating, level=82)
        self.assertAlmostEqual(self.stats.get_melee_hit_from_rating(), .01 * 1086/120.109001159667969)
        self.assertAlmostEqual(self.stats.get_melee_hit_from_rating(100), .01 * 100/120.109001159667969)
    
    def test_get_expertise_from_rating(self):
        self.assertRaises(AssertionError, self.stats.get_expertise_from_rating, level=82)
        self.assertAlmostEqual(self.stats.get_expertise_from_rating(), .01 * 641/(30.027200698852539*4))
        self.assertAlmostEqual(self.stats.get_expertise_from_rating(100), .01 * 100/(30.027200698852539*4))

    def test_get_spell_hit_from_rating(self):
        self.assertRaises(AssertionError, self.stats.get_spell_hit_from_rating, level=82)
        self.assertAlmostEqual(self.stats.get_spell_hit_from_rating(), .01 * 1086/102.445999145507812)
        self.assertAlmostEqual(self.stats.get_spell_hit_from_rating(100), .01 * 100/102.445999145507812)
    
    def test_get_crit_from_rating(self):
        self.assertRaises(AssertionError, self.stats.get_crit_from_rating, level=82)
        self.assertAlmostEqual(self.stats.get_crit_from_rating(), .01 * 1517/179.279998779296875)
        self.assertAlmostEqual(self.stats.get_crit_from_rating(100), .01 * 100/179.279998779296875)

    def test_get_haste_multiplier_from_rating(self):
        self.assertRaises(AssertionError, self.stats.get_haste_multiplier_from_rating, level=82)
        self.assertAlmostEqual(self.stats.get_haste_multiplier_from_rating(), 1 + .01 * 899/128.057006835937500)
        self.assertAlmostEqual(self.stats.get_haste_multiplier_from_rating(100), 1 + .01 * 100/128.057006835937500)
        
if __name__ == '__main__':
    unittest.main()

