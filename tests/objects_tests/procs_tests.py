import unittest
from objects import procs
    
class TestProcsList(unittest.TestCase):
    def setUp(self):
        self.procsList = procs.ProcsList('darkmoon_card_hurricane','heroic_left_eye_of_rajh')
    
    def test__init__(self):
        self.assertTrue(self.procsList.darkmoon_card_hurricane)
        self.assertFalse(self.procsList.fluid_death)
    
    def test__getattr__(self):
        pass
    
    def test_get_all_procs_for_stat(self):
        self.assertEqual(len(self.procsList.get_all_procs_for_stat(stat=None)), 2)
        self.procsList = procs.ProcsList()
        self.assertEqual(len(self.procsList.get_all_procs_for_stat(stat=None)), 0)
    
    def test_get_all_damage_procs(self):
        self.assertEqual(len(self.procsList.get_all_damage_procs()), 1)
        self.procsList = procs.ProcsList()
        self.assertEqual(len(self.procsList.get_all_damage_procs()), 0)
