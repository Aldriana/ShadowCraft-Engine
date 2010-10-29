from objects import glyphs

class RogueGlyphs(glyphs.Glyphs):
    # Should put all of them in at some point, just added the ones that matter
    # for the initial set of calculations.
    
    allowed_glyphs = frozenset([
        'backstab', 'mutilate', 'rupture', 'slice_and_dice', 'vendetta',
        'tricks_of_the_trade',
    ])
