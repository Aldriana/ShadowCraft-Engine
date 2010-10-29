class DamageCalculator(object):
    # This method holds the general interface for a damage calculator - the
    # sorts of parameters and calculated values that will be need by many (or
    # most) classes if they implement a damage calculator using this framework.
    # Not saying that will happen, but I want to leave my options open.
    # Any calculations that are specific to a particular class should go in
    # calcs.<class>.<Class>DamageCalculator instead - for an example, see 
    # calcs.rogue.RogueDamageCalculator

    # If someone wants to have __init__ take a player level as well and use it
    # to initialize these to a level-dependent value, they're welcome to.  At
    # the moment I'm hardcoding them to level 85 values.
    MELEE_HIT_RATING_CONVERSION = 120.109001159667969
    SPELL_HIT_RATING_CONVERSION = 102.445999145507812
    CRIT_RATING_CONVERSION = 179.279998779296875
    HASTE_RATING_CONVERSION = 128.057006835937500
    EXPERTISE_RATING_CONVERSION = 30.027200698852539 * 4
    MASTERY_RATING_CONVERSION = 179.279998779296875
    ARMOR_MITIGATION_PARAMETER = 26070.

    # Similarly, if you want to include an opponents level and initialize these
    # in a level-dependant way, go ahead.
    TARGET_BASE_ARMOR = 11977.
    BASE_ONE_HAND_MISS_RATE = 8.
    BASE_DW_MISS_RATE = 27.
    BASE_SPELL_MISS_RATE = 17.
    BASE_DODGE_CHANCE = 6.5
    BASE_PARRY_CHANCE = 14.

    def __init__(self, stats, talents, glyphs, buffs, settings=None):
        self.stats = stats
        self.talents = talents
        self.glyphs = glyphs
        self.buffs = buffs
        self.settings = settings

    def get_dps(self):
        # Overwrite this function with your calculations/simulations/whatever;
        # this is what callers will (initially) be looking at.
        pass

    def armor_mitigation_multiplier(self, armor):
        # Pass an armor value in to get the armor mitigation multiplier for
        # that armor value.
        return self.ARMOR_MITIGATION_PARAMETER / (self.ARMOR_MITIGATION_PARAMETER + armor)

    def armor_mitigate(self, damage, armor):
        # Pass in raw physical damage and armor value, get armor-mitigated
        # damage value.
        return damage * self.armor_mitigation_multiplier(armor)

    # These four hit functions need to be adjusted for the draenei racial at
    # some point, but, as usual, I'm being lazy.
    def melee_hit_chance(self, base_miss_chance, dodgeable, parryable):
        miss_chance = base_miss_chance - self.stats.hit / self.MELEE_HIT_RATING_CONVERSION
        if miss_chance < 0:
            miss_chance = 0.

        if dodgeable:
            dodge_chance = self.BASE_DODGE_CHANCE - self.stats.expertise / self.EXPERTISE_RATING_CONVERSION
            if dodge_chance < 0:
                dodge_chance = 0
        else:
            dodge_chance = 0

        if parryable:
            parry_chance = self.BASE_PARRY_CHANCE - self.stats.expertise / self.EXPERTISE_RATING_CONVERSION
            if parry_chance < 0:
                parry_chance = 0
        else:
            parry_chance = 0

        return 1 - (miss_chance + dodge_chance + parry_chance) / 100

    def one_hand_melee_hit_chance(self, dodgeable=True, parryable=False):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        return self.melee_hit_chance(self.BASE_ONE_HAND_MISS_RATE, dodgeable, parryable)

    def two_hand_melee_hit_chance(self, dodgeable=True, parryable=False):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        return self.melee_hit_chance(self.BASE_DW_MISS_RATE, dodgeable, parryable)

    def spell_hit_chance(self):
        miss_chance = self.BASE_SPELL_MISS_RATE - self.stats.hit / self.SPELL_HIT_RATING_CONVERSION

    def get_crit_from_rating(self, rating=None):
        # In case you're wondering why we're messing around with None instead
        # of just defaulting it to self.stats.crit in the first place, its
        # because default values are set when the function is defined, not when
        # it is run; hence, this is necessary to pick up changes when gear is
        # changed while reusing the same object.
        if rating is None:
            rating = self.stats.crit
        return rating / self.CRIT_RATING_CONVERSION

    def get_haste_multiplier_from_rating(self, rating=None):
        # See note on get_crit_from_rating.
        if rating is None:
            rating = self.stats.haste
        return 1 + rating / (100 * self.HASTE_RATING_CONVERSION)

    def get_mastery_from_rating(self, rating=None):
        # See note on get_crit_from_rating.
        if rating is None:
            rating = self.stats.mastery
        return 8 + rating / self.MASTERY_RATING_CONVERSION

    def stat_multiplier(self):
        if self.buffs.stat_multiplier_buff:
            return 1.05
        return 1

    def all_damage_multiplier(self):
        if self.buffs.all_damage_buff:
            return 1.03
        else:
            return 1

    def spell_damage_multiplier(self):
        if self.buffs.spell_damage_debuff:
            return 1.08 * self.all_damage_multiplier()
        else:
            return self.all_damage_multiplier()

    def physical_damage_multiplier(self):
        if self.buffs.physical_vulnerability_debuff:
            return 1.04 * self.all_damage_multiplier()
        else:
            return self.all_damage_multiplier()

    def bleed_damage_multiplier(self):
        if self.buffs.bleed_damage_debuff:
            return 1.3 * self.all_damage_multiplier()
        else:
            return self.all_damage_multiplier()

    def attack_power_multiplier(self):
        if self.buffs.attack_power_buff:
            return 1.1
        else:
            return 1

    def melee_haste_multiplier(self):
        if self.buffs.melee_haste_buff:
            return 1.1
        else:
            return 1

    def buff_str(self):
        if self.buffs.str_and_agi_buff:
            return 1395
        else:
            return 0

    def buff_agi(self):
        if self.buffs.str_and_agi_buff:
            return 1395
        else:
            return 0

    def buff_all_crit(self):
        if self.buffs.crit_chance_buff:
            return 5
        else:
            return 0

    def buff_melee_crit(self):
        return self.buff_all_crit()

    def buff_spell_crit(self):
        if self.buffs.spell_crit_debuff:
            return 5 + self.buff_all_crit()
        else:
            return self.buff_all_crit()

    def target_armor(self):
        if self.buffs.armor_debuff:
            return .88 * self.TARGET_BASE_ARMOR
        else:
            return self.TARGET_BASE_ARMOR
