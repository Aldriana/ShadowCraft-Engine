import unittest
from calcs.rogue import RogueDamageCalculator
from objects import buffs
from objects import race
from objects import stats
from objects import procs
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
        self.calculator = RogueDamageCalculator(test_stats, test_talents, None, test_buffs, test_race)
    
    def test_get_spell_hit_from_talents(self):
        self.assertAlmostEqual(self.calculator.get_spell_hit_from_talents(), .04)
        self.calculator.talents.combat.precision = 0
        self.assertAlmostEqual(self.calculator.get_spell_hit_from_talents(), .0)
    
    def test_get_melee_hit_from_talents(self):
        self.assertAlmostEqual(self.calculator.get_melee_hit_from_talents(), .04)
        self.calculator.talents.combat.precision = 3
        self.assertAlmostEqual(self.calculator.get_melee_hit_from_talents(), .06)
    
    def test_oh_penalty(self):
        self.assertAlmostEqual(self.calculator.oh_penalty(), 0.5)
    
    def test_talents_modifiers_assassins_resolve(self):
        self.assertAlmostEqual(self.calculator.talents_modifiers(assassins_resolve=False), 1.0)
        self.assertAlmostEqual(self.calculator.talents_modifiers(), 1.15)
        self.calculator.stats.mh.type = '1h_axe'
        self.assertAlmostEqual(self.calculator.talents_modifiers(), 1.0)
    
    def test_talents_modifiers(self):
        self.assertAlmostEqual(self.calculator.talents_modifiers(opportunity=True), 1.15 * 1.3)
    
    def test_crit_damage_modifiers(self):
        self.assertAlmostEqual(self.calculator.crit_damage_modifiers(), 1 + (2 * 1.03 - 1) * 1)
        self.assertAlmostEqual(self.calculator.crit_damage_modifiers(is_spell=True), 1 + (1.5 * 1.03 - 1) * 1)
        self.assertAlmostEqual(self.calculator.crit_damage_modifiers(lethality=True), 1 + (2 * 1.03 - 1) * 1.3)        
    
    # Just do some basic checks for the individual abilities, increasing AP
    # should increase damage and similar for combo points.
    # The optional armor argument isn't tested for now.
    # Should probably compare damage and crit_damage individually so it can  
    # catch some error where crit_damage is lower even with higher AP.
    
    def test_mh_damage(self):
        self.assertTrue(self.calculator.mh_damage(0) < self.calculator.mh_damage(1))
    
    def test_oh_damage(self):
        self.assertTrue(self.calculator.oh_damage(0) < self.calculator.oh_damage(1))
    
    def test_backstab_damage(self):
        self.assertTrue(self.calculator.backstab_damage(0) < self.calculator.backstab_damage(1))
    
    def test_mh_mutilate_damage(self):
        self.assertTrue(self.calculator.mh_mutilate_damage(0) < self.calculator.mh_mutilate_damage(1))
        not_poisoned = self.calculator.mh_mutilate_damage(1, is_poisoned=False)
        poisoned = self.calculator.mh_mutilate_damage(1)
        self.assertAlmostEqual(not_poisoned[0] * 1.2, poisoned[0])
        self.assertAlmostEqual(not_poisoned[1] * 1.2, poisoned[1])

    def test_oh_mutilate_damage(self):
        self.assertTrue(self.calculator.oh_mutilate_damage(0) < self.calculator.oh_mutilate_damage(1))
        not_poisoned = self.calculator.oh_mutilate_damage(1, is_poisoned=False)
        poisoned = self.calculator.oh_mutilate_damage(1)
        self.assertAlmostEqual(not_poisoned[0] * 1.2, poisoned[0])
        self.assertAlmostEqual(not_poisoned[1] * 1.2, poisoned[1])

    def test_sinister_strike_damage(self):
        self.assertTrue(self.calculator.sinister_strike_damage(0) < self.calculator.sinister_strike_damage(1))
    
    def test_hemorrhage_damage(self):
        self.assertTrue(self.calculator.hemorrhage_damage(0) < self.calculator.hemorrhage_damage(1))
    
    def test_ambush_damage(self):
        self.assertTrue(self.calculator.ambush_damage(0) < self.calculator.ambush_damage(1))
    
    def test_revealing_strike_damage(self):
        self.assertTrue(self.calculator.revealing_strike_damage(0) < self.calculator.revealing_strike_damage(1))
    
    def test_venomous_wounds_damage(self):
        self.assertTrue(self.calculator.venomous_wounds_damage(0) < self.calculator.venomous_wounds_damage(1))
    
    def test_main_gauche(self):
        self.assertTrue(self.calculator.main_gauche(0) < self.calculator.main_gauche(1))

    def test_instant_poison_damage(self):
        self.assertTrue(self.calculator.instant_poison_damage(0) < self.calculator.instant_poison_damage(1))
        self.assertTrue(self.calculator.instant_poison_damage(0, mastery=0) < self.calculator.instant_poison_damage(0, mastery=1))

    def test_deadly_poison_tick_damage(self):
        # test mastery
        self.assertTrue(self.calculator.deadly_poison_tick_damage(0) < self.calculator.deadly_poison_tick_damage(1))
        self.assertTrue(self.calculator.deadly_poison_tick_damage(0, dp_stacks=1) < self.calculator.deadly_poison_tick_damage(0, dp_stacks=2))
        
    def test_wound_poison_damage(self):
        self.assertTrue(self.calculator.wound_poison_damage(0) < self.calculator.wound_poison_damage(1))
        self.assertTrue(self.calculator.wound_poison_damage(0, mastery=0) < self.calculator.wound_poison_damage(0, mastery=1))

    def test_garrote_tick_damage(self):
        self.assertTrue(self.calculator.garrote_tick_damage(0) < self.calculator.garrote_tick_damage(1))

    def test_rupture_tick_damage(self):
        self.assertTrue(self.calculator.rupture_tick_damage(0, 1) < self.calculator.rupture_tick_damage(1, 1))
        self.assertTrue(self.calculator.rupture_tick_damage(0, 1) < self.calculator.rupture_tick_damage(0, 2))
        self.assertRaises(IndexError, self.calculator.rupture_tick_damage, 0, 6)

    def test_eviscerate_damage(self):
        self.assertTrue(self.calculator.eviscerate_damage(0, 1) < self.calculator.eviscerate_damage(1, 1))
        self.assertTrue(self.calculator.eviscerate_damage(0, 1) < self.calculator.eviscerate_damage(0, 2))
        self.assertRaises(IndexError, self.calculator.eviscerate_damage, 0, 6)

    def test_envenom_damage(self):
        self.assertTrue(self.calculator.envenom_damage(0, 1) < self.calculator.envenom_damage(1, 1))
        self.assertTrue(self.calculator.envenom_damage(0, 1) < self.calculator.envenom_damage(0, 2))

    def test_melee_crit_rate(self):
        pass

    def test_spell_crit_rate(self):
        pass

    def test_crit_cap(self):
        pass


class TestRogueDamageCalculatorLevels(TestRogueDamageCalculator):
    def setUp(self):
        super(TestRogueDamageCalculatorLevels, self).setUp()
        self.calculator.level = 80
    
    def test_set_constants_for_level(self):
        self.assertRaises(AssertionError, self.calculator.__setattr__, 'level', 86)
