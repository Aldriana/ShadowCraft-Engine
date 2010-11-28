from shadowcraft.objects import glyphs

class RogueGlyphs(glyphs.Glyphs):
    # Should put all of them in at some point, just added the ones that matter
    # for the initial set of calculations.
    
    allowed_glyphs = frozenset([
        # Prime
        'adrenaline_rush',
        'backstab',
        'eviscerate',
        'hemorrhage',
        'killing_spree',
        'mutilate',
        'revealing_strike',
        'rupture',
        'shadow_dance',
        'sinister_strike',
        'slice_and_dice',
        'vendetta',
        # Major
        'ambush',
        'blade_flurry',
        'blind',
        'cloak_of_shadows',
        'crippling_poison',
        'deadly_throw',
        'evasion',
        'expose_armor',
        'fan_of_knives',
        'feint',
        'garrote',
        'gouge',
        'kick',
        'preparation',
        'sap',
        'sprint',
        'tricks_of_the_trade',
        'vanish',
        # Minor
        'blurred_speed',
        'distract',
        'pick_lock',
        'pick_pocket',
        'poisons',
        'safe_fall'
    ])
