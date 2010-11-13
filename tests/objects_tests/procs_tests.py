import unittest
from objects import procs
    
class TestProcsList(unittest.TestCase):
    def setUp(self):
        self.procsList = procs.ProcsList('darkmoon_card_hurricane','heroic_left_eye_of_rajh')
    
    def test__init__(self):
        self.assertRaises(AssertionError, procs.ProcsList, 'fake_proc')
        self.procsList = procs.ProcsList('darkmoon_card_hurricane')
        self.assertEqual(len(self.procsList.get_all_procs_for_stat(stat=None)), 1)
    
    def test__getattr__(self):
        self.assertRaises(AttributeError, self.procsList.__getattr__, 'fake_proc')
        self.assertTrue(self.procsList.darkmoon_card_hurricane)
        self.assertFalse(self.procsList.fluid_death)
    
    def test_get_all_procs_for_stat(self):
        self.assertEqual(len(self.procsList.get_all_procs_for_stat(stat=None)), 2)
        self.procsList = procs.ProcsList()
        self.assertEqual(len(self.procsList.get_all_procs_for_stat(stat=None)), 0)
    
    def test_get_all_damage_procs(self):
        self.assertEqual(len(self.procsList.get_all_damage_procs()), 1)
        self.procsList = procs.ProcsList()
        self.assertEqual(len(self.procsList.get_all_damage_procs()), 0)


class TestProc(unittest.TestCase):
    def setUp(self):
        self.proc = procs.Proc(*procs.ProcsList.allowed_procs['prestors_talisman_of_machination'])
    
    def test__init__(self):
        self.assertEqual(self.proc.stat, 'haste')
        self.assertEqual(self.proc.value, 1926)
        self.assertEqual(self.proc.duration, 15)
        self.assertEqual(self.proc.proc_chance, .1)
        self.assertEqual(self.proc.trigger, 'all_attacks')
        self.assertEqual(self.proc.icd, 75)
        self.assertEqual(self.proc.max_stacks, 1)
    
    def test_procs_off_auto_attacks(self):
        self.assertTrue(self.proc.procs_off_auto_attacks())
    
    def test_procs_off_strikes(self):
        self.assertTrue(self.proc.procs_off_strikes())
    
    def test_procs_off_harmful_spells(self):
        self.assertFalse(self.proc.procs_off_harmful_spells())
    
    def test_procs_off_heals(self):
        self.assertFalse(self.proc.procs_off_heals())
    
    def test_procs_off_periodic_spell_damage(self):
        self.assertFalse(self.proc.procs_off_periodic_spell_damage())
    
    def test_procs_off_periodic_heals(self):
        self.assertFalse(self.proc.procs_off_periodic_heals())
    
    def test_procs_off_apply_debuff(self):
        self.assertTrue(self.proc.procs_off_apply_debuff())
    
    def test_procs_off_bleeds(self):
        self.assertFalse(self.proc.procs_off_bleeds())
    
    def test_procs_off_crit_only(self):
        self.assertFalse(self.proc.procs_off_crit_only())

    def test_is_ppm(self):
        self.assertFalse(self.proc.is_ppm())


class TestPPMProc(unittest.TestCase):
    def setUp(self):
        self.proc = procs.PPMProc('haste', 450, 12, 1, 'all_spells_and_attacks', 0, 1)
    
    def test__init__(self):
        self.assertEqual(self.proc.stat, 'haste')
        self.assertEqual(self.proc.value, 450)
        self.assertEqual(self.proc.duration, 12)
        self.assertEqual(self.proc.ppm, 1)
        self.assertEqual(self.proc.trigger, 'all_spells_and_attacks')
        self.assertEqual(self.proc.icd, 0)
        self.assertEqual(self.proc.max_stacks, 1)

    def test_is_ppm(self):
        self.assertTrue(self.proc.is_ppm())
