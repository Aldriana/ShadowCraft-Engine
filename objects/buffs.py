class Buffs(object):
    # Will need to add the caster/tank (de)buffs at some point if we want to
    # support other classes with this framework.

    allowed_buffs = frozenset([
        'short_term_haste_buff',            # Heroism/Blood Lust, Time Warp
        'stat_multiplier_buff',             # Mark of the Wild, Blessing of Kings
        'crit_chance_buff',                 # Leader of the Pack, HAT, Elemental Oath, Rampage
        'all_damage_buff',                  # Arcane Tactics, Communion, Ferocious Inspiration
        'melee_haste_buff',                 # Windfury, Improved Icy Talons
        'attack_power_buff',                # Trueshot, Unleashed Rage, Abomination's Might, Blessing of Might
        'str_and_agi_buff',                 # Horn of Winter, Strength of Earth, Battle Shout
        'armor_debuff',                     # Sunder, Expose Armor, Faerie Fire
        'physical_vulnerability_debuff',    # Brittle Bones, Savage Combat, Blood Frenzy
        'spell_damage_debuff',              # Ebon Plaguebringer, Master Poisoner, Earth and Moon, Curse of Elements
        'spell_crit_debuff',                # Critical Mass, Shadow and Flame
        'bleed_damage_debuff',              # Hemo, Mangle, Trauma
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
