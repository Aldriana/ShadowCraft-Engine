from core import exceptions

class InvalidBuffException(exceptions.InvalidInputException):
    pass


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
        'agi_flask',                        # Flask of the Winds
        'guild_feast'                       # Seafood Magnifique Feast
    ])
    
    str_and_agi_buff_values = {80:155, 85:549}

    def __init__(self, *args, **kwargs):
        for buff in args:
            if buff not in self.allowed_buffs:
                raise InvalidBuffException(_('Invalid buff {buff}').format(buff=buff))
            setattr(self, buff, True)
        self.level = kwargs.get('level', 85)

    def __getattr__(self, name):
        # Any buff we haven't assigned a value to, we don't have.
        if name in self.allowed_buffs:
            return False
        object.__getattribute__(self, name)
    
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'level':
            self._set_constants_for_level()
    
    def _set_constants_for_level(self):
        try:
            self.str_and_agi_buff_bonus = self.str_and_agi_buff_values[self.level]
        except KeyError as e:
            raise exceptions.InvalidLevelException(_('No conversion factor available for level {level}').format(level=self.level))

    
    def stat_multiplier(self):
        if self.stat_multiplier_buff:
            return 1.05
        return 1

    def all_damage_multiplier(self):
        if self.all_damage_buff:
            return 1.03
        else:
            return 1

    def spell_damage_multiplier(self):
        if self.spell_damage_debuff:
            return 1.08 * self.all_damage_multiplier()
        else:
            return self.all_damage_multiplier()

    def physical_damage_multiplier(self):
        if self.physical_vulnerability_debuff:
            return 1.04 * self.all_damage_multiplier()
        else:
            return self.all_damage_multiplier()

    def bleed_damage_multiplier(self):
        if self.bleed_damage_debuff:
            return 1.3 * self.physical_damage_multiplier()
        else:
            return self.physical_damage_multiplier()

    def attack_power_multiplier(self):
        if self.attack_power_buff:
            return 1.1
        else:
            return 1

    def melee_haste_multiplier(self):
        if self.melee_haste_buff:
            return 1.1
        else:
            return 1

    def buff_str(self):
        if self.str_and_agi_buff:
            return self.str_and_agi_buff_bonus
        else:
            return 0

    def buff_agi(self):
        if self.agi_flask:
            flask_agi = 300
        else:
            flask_agi = 0

        if self.guild_feast:
            food_agi = 90
        else:
            food_agi = 0

        if self.str_and_agi_buff:
            return self.str_and_agi_buff_bonus + food_agi + flask_agi
        else:
            return 0 + food_agi + flask_agi

    def buff_all_crit(self):
        if self.crit_chance_buff:
            return .05
        else:
            return 0

    def buff_spell_crit(self):
        if self.spell_crit_debuff:
            return .05
        else:
            return 0

    def armor_reduction_multiplier(self):
        if self.armor_debuff:
            return 0.88 
        else:
            return 1
