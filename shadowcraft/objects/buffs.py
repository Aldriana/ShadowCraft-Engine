from shadowcraft.core import exceptions

class InvalidBuffException(exceptions.InvalidInputException):
    pass


class Buffs(object):

    allowed_buffs = frozenset([
        'short_term_haste_buff',            # Heroism/Blood Lust, Time Warp
        'stat_multiplier_buff',             # Mark of the Wild, Blessing of Kings, Legacy of the Emperor
        'crit_chance_buff',                 # Leader of the Pack, Legacy of the White Tiger, Arcane Brillance
        'melee_haste_buff',                 # Swiftblade's Cunning, Unholy Aura
        'attack_power_buff',                # Horn of Winter, Trueshot Aura, Battle Shout
        'mastery_buff',                     # Blessing of Might, Grace of Air
        'spell_haste_buff',                 # Moonkin Form, Shadowform
        'spell_power_buff',                 # Dark Intent, Arcane Brillance
        'stamina_buff',                     # PW: Fortitude, Blood Pact, Commanding Shout
        'armor_debuff',                     # Sunder, Expose Armor, Faerie Fire
        'physical_vulnerability_debuff',    # Brittle Bones, Ebon Plaguebringer, Judgments of the Bold, Colossus Smash
        'spell_damage_debuff',              # Master Poisoner, Curse of Elements
        'weakened_blows_debuff',
        'slow_casting_debuff',
        'mortal_wounds_debuff',
        'agi_flask',                        # Flask of the Winds (cata)
        'guild_feast',                      # Seafood Magnifique Feast (cata)
        'agi_flask_mop',                    # Flask of Spring Blossoms
        'food_250',                         # Pandaren Banquet
        'food_275',                         # Pandaren Banquet
        'food_300_agi'                      # Sea Mist Rice Noodles
    ])

    mast_buff_values = {80:268, 85:1042, 90:3500}

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
            self.mast_buff_bonus = self.mast_buff_values[self.level]
        except KeyError as e:
            raise exceptions.InvalidLevelException(_('No conversion factor available for level {level}').format(level=self.level))

    def stat_multiplier(self):
        return [1, 1.05][self.stat_multiplier_buff]

    def spell_damage_multiplier(self):
        return [1, 1.08][self.spell_damage_debuff]

    def physical_damage_multiplier(self):
        return [1, 1.04][self.physical_vulnerability_debuff]

    def bleed_damage_multiplier(self):
        return self.physical_damage_multiplier()

    def attack_power_multiplier(self):
        return [1, 1.1][self.attack_power_buff]

    def melee_haste_multiplier(self):
        return [1, 1.1][self.melee_haste_buff]

    def buff_str(self):
        return 0

    def buff_agi(self):
        if self.agi_flask_mop + self.agi_flask > 1:
            raise InvalidBuffException(_('You can only have one type of Flask active'))
        flask_agi = 0
        flask_agi += [0, 300][self.agi_flask]
        flask_agi += [0, 1000][self.agi_flask_mop]

        if self.guild_feast + self.food_250 + self.food_275 + self.food_300_agi > 1:
            raise InvalidBuffException(_('You can only have one type of Well Fed buff active'))
        food_agi = 0
        food_agi += [0, 90][self.guild_feast]
        food_agi += [0, 250][self.food_250]
        food_agi += [0, 275][self.food_275]
        food_agi += [0, 300][self.food_300_agi]

        return food_agi + flask_agi

    def buff_all_crit(self):
        return [0, .05][self.crit_chance_buff]

    def buff_spell_crit(self):
        return 0

    def armor_reduction_multiplier(self):
        return [1, .88][self.armor_debuff]

    def buff_mast(self):
        return [0, self.mast_buff_bonus][self.mastery_buff]
