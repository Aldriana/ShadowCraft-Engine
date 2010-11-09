import unittest
import sys
sys.path.append(".")

from calcs_tests import DamageCalculatorTest
from calcs_tests.rogue_tests import TestRogueDamageCalculator, TestRogueDamageCalculatorLevels
from calcs_tests.rogue_tests.Aldriana_tests import TestAldrianasRogueDamageCalculator
from objects_tests.buffs_tests import TestBuffsTrue, TestBuffsFalse
from objects_tests.stats_tests import TestStats, TestWeapon
from objects_tests.procs_tests import TestProcsList, TestProc, TestPPMProc
from objects_tests.rogue_tests.rogue_glyphs_tests import TestRogueGlyphs
from objects_tests.rogue_tests.rogue_talents_tests import TestAssassinationTalents,\
TestCombatTalents, TestSubtletyTalents, TestRogueTalents

if __name__ == "__main__":
    unittest.main()
