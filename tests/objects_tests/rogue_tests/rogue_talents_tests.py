import unittest
from objects.rogue import rogue_talents

class TestAssassinationTalents(unittest.TestCase):
    # Tests for the abstract class objects.talents.TalentTree
    def setUp(self):
        self.talents = rogue_talents.AssassinationTalents('0333230113022110321')

    def test__getattr__(self):
        self.assertRaises(AttributeError, self.talents.__getattr__, 'fake_talent')
        talents = rogue_talents.AssassinationTalents()
        self.assertEqual(talents.vendetta, 0)

    def test__init__kwargs(self):
        talents = rogue_talents.AssassinationTalents(vendetta=1)
        self.assertEqual(talents.vendetta, 1)
        self.assertEqual(talents.cold_blood, 0)
        self.assertRaises(AttributeError, talents.__getattr__, 'fake_talent')


class TestCombatTalents(unittest.TestCase):
    pass


class TestSubtletyTalents(unittest.TestCase):
    pass


class TestRogueTalents(unittest.TestCase):
    def setUp(self):
        self.talents = rogue_talents.RogueTalents('0333230113022110321', '0020000000000000000', '2030030000000000000')

    def test(self):
        self.assertEqual(self.talents.assassination.vendetta, 1)
        self.assertEqual(self.talents.assassination.cold_blood, 1)
        self.assertEqual(self.talents.subtlety.relentless_strikes, 3)
        self.assertEqual(self.talents.combat.precision, 2)
        self.assertEqual(self.talents.combat.killing_spree, 0)

    def test_is_assassination_rogue(self):
        self.assertTrue(self.talents.is_assassination_rogue())

    def test_is_combat_rogue(self):
        self.assertFalse(self.talents.is_combat_rogue())

    def test_is_combat_rogue(self):
        self.assertFalse(self.talents.is_subtlety_rogue())
