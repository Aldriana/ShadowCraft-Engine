import unittest
import sys
sys.path.append(".")

from calcs_tests import DamageCalculatorTest
from objects_tests.buffs_tests import TestBuffsTrue, TestBuffsFalse
from objects_tests.stats_tests import TestStats, TestWeapon
from objects_tests.rogue_tests.rogue_glyphs_tests import TestRogueGlyphs

if __name__ == "__main__":
    unittest.main()