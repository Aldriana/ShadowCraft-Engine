import calcs
import unittest
from core import exceptions
from calcs import armor_mitigation

class TestArmorMitigation(unittest.TestCase):
    def test_thresholds(self):
        self.assertRaises(exceptions.InvalidLevelException, armor_mitigation.lookup_parameters, 0)
        self.assertEqual(1,  armor_mitigation.lookup_parameters(1)[0])
        self.assertEqual(1,  armor_mitigation.lookup_parameters(59)[0])
        self.assertEqual(60, armor_mitigation.lookup_parameters(60)[0])
        self.assertEqual(60, armor_mitigation.lookup_parameters(80)[0])
        self.assertEqual(81, armor_mitigation.lookup_parameters(81)[0])
    
    def test_parameter_spot_checks(self):
        self.assertAlmostEqual( 5882.5, armor_mitigation.parameter(60))
        self.assertAlmostEqual(10557.5, armor_mitigation.parameter(70))
        self.assertAlmostEqual(15232.5, armor_mitigation.parameter(80))
        self.assertAlmostEqual(26070.0, armor_mitigation.parameter(85))

    def test_mitigation_spot_checks(self):
        self.assertAlmostEqual(0.4441, armor_mitigation.mitigation(4700,  60), 4)
        self.assertAlmostEqual(0.4217, armor_mitigation.mitigation(7700,  70), 4)
        self.assertAlmostEqual(0.4109, armor_mitigation.mitigation(10623, 80), 4)
        self.assertAlmostEqual(0.3148, armor_mitigation.mitigation(11977, 85), 4)

    def test_mitigation_cached_parameter(self):
        self.assertAlmostEqual(0.4441, armor_mitigation.mitigation(4700,  60, 5882.5), 4)
        self.assertAlmostEqual(0.4217, armor_mitigation.mitigation(7700,  70, 10557.5), 4)
        self.assertAlmostEqual(0.4109, armor_mitigation.mitigation(10623, 80, 15232.5), 4)
        self.assertAlmostEqual(0.3148, armor_mitigation.mitigation(11977, 85, 26070.0), 4)

    def test_multiplier_spot_checks(self):
        self.assertAlmostEqual(1 - 0.4441, armor_mitigation.multiplier(4700,  60), 4)
        self.assertAlmostEqual(1 - 0.4217, armor_mitigation.multiplier(7700,  70), 4)
        self.assertAlmostEqual(1 - 0.4109, armor_mitigation.multiplier(10623, 80), 4)
        self.assertAlmostEqual(1 - 0.3148, armor_mitigation.multiplier(11977, 85), 4)

    def test_multiplier_cached_paramter(self):
        self.assertAlmostEqual(1 - 0.4441, armor_mitigation.multiplier(4700,  60, 5882.5), 4)
        self.assertAlmostEqual(1 - 0.4217, armor_mitigation.multiplier(7700,  70, 10557.5), 4)
        self.assertAlmostEqual(1 - 0.4109, armor_mitigation.multiplier(10623, 80, 15232.5), 4)
        self.assertAlmostEqual(1 - 0.3148, armor_mitigation.multiplier(11977, 85, 26070.0), 4)
