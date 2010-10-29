class Buffs(object):
    # Will need to add the caster/tank (de)buffs at some point if we want to
    # support other classes with this framework.

    allowed_buffs = frozenset([
        'short_term_haste_buff',                # Heroism/Blood Lust, Time Warp
        'stat_multiplier_buff': 1.05,           # Mark of the Wild, Blessing of Kings
        'crit_chance_buff': 1.05,               # Leader of the Pack, HAT, Elemental Oath, Rampage
        'all_damage_buff': 1.03,                # Arcane Tactics, Communion, Ferocious Inspiration
        'melee_haste_buff': 1.1,                # Windfury, Improved Icy Talons
        'attack_power_buff': 1.1,               # Trueshot, Unleashed Rage, Abomination's Might, Blessing of Might
        'str_and_agi_buff': 1395,               # Horn of Winter, Strength of Earth, Battle Shout
        'armor_debuff': 0.88,                   # Sunder, Expose Armor, Faerie Fire
        'physical_vulnerability_debuff': 1.04,  # Brittle Bones, Savage Combat, Blood Frenzy
        'spell_damage_debuff': 1.08,            # Ebon Plaguebringer, Master Poisoner, Earth and Moon, Curse of Elements
        'spell_crit_debuff': 1.05,              # Critical Mass, Shadow and Flame
        'bleed_damage_debuff': 1.3,             # Hemo, Mangle, Trauma
    ])
    
    def __init__(self, *args):
        for buff in args:
            # A real exception would be good here as well.
            assert buff in self.allowed_buffs
            setattr(self, buff, True)

    def __getattr__(self, name):
        # Any buff we haven't assigned a value to, we don't have.
        if name in self.allowed_buffs:
            return False
        object.__getattribute__(self, name)
