import unittest

from objects.rogue import rogue_glyphs
    
class TestRogueGlyphs(unittest.TestCase):
    def setUp(self):
        self.glyphs = rogue_glyphs.RogueGlyphs('backstab', 'mutilate', 'rupture')

        
    def test__getattr__(self):
        self.assertRaises(AttributeError, self.glyphs.__getattr__, 'fake_glyph')
        self.assertTrue(self.glyphs.backstab)
        self.assertFalse(self.glyphs.slice_and_dice)
    
if __name__ == '__main__':
    unittest.main()
