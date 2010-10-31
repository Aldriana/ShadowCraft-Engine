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
    
    ARMOR_MITIGATION_PARAMETER = 26070.

    # Similarly, if you want to include an opponents level and initialize these
    # in a level-dependant way, go ahead.
    TARGET_BASE_ARMOR = 11977.
    BASE_ONE_HAND_MISS_RATE = .08
    BASE_DW_MISS_RATE = .27
    BASE_SPELL_MISS_RATE = .17
    BASE_DODGE_CHANCE = .065
    BASE_PARRY_CHANCE = .14

    def __init__(self, stats, talents, glyphs, buffs, race, settings=None):
        self.stats = stats
        self.talents = talents
        self.glyphs = glyphs
        self.buffs = buffs
        self.race = race
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
    # Afaik this racial is removed with Cata? - Rac
    # It's still a self-buff for draenei, and while rogues can't be draenei
    # this is in the part of the code that other classes might someday use.
    #
    # It also just occurred to me that these need to be adjusted (and broken
    # down by hand) to deal with the case where, for instance, a gnome is using
    # a dagger in one hand and an axe in the other.  Won't matter for mutilate
    # (which is what I'm doing first) but it could come up for, say, subtlety.
    def melee_hit_chance(self, base_miss_chance, dodgeable, parryable):
        miss_chance = base_miss_chance - self.stats.get_melee_hit_from_rating()
        if miss_chance < 0:
            miss_chance = 0.

        if dodgeable:
            dodge_chance = self.BASE_DODGE_CHANCE - self.stats.get_expertise_from_rating()
            if dodge_chance < 0:
                dodge_chance = 0
        else:
            dodge_chance = 0

        if parryable:
            parry_chance = self.BASE_PARRY_CHANCE - self.stats.get_expertise_from_rating()
            if parry_chance < 0:
                parry_chance = 0
        else:
            parry_chance = 0

        return 1 - (miss_chance + dodge_chance + parry_chance)

    def one_hand_melee_hit_chance(self, dodgeable=True, parryable=False):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        return self.melee_hit_chance(self.BASE_ONE_HAND_MISS_RATE, dodgeable, parryable)

    def dual_wield_melee_hit_chance(self, dodgeable=True, parryable=False):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        return self.melee_hit_chance(self.BASE_DW_MISS_RATE, dodgeable, parryable)

    def spell_hit_chance(self):
        miss_chance = self.BASE_SPELL_MISS_RATE - self.get_spell_hit_from_rating()
        if miss_chance < 0:
            return 0
        else:
            return miss_chance

    def buff_melee_crit(self):
        return self.buffs.buff_all_crit()

    def buff_spell_crit(self):
        return self.buffs.buff_spell_crit() + self.buffs.buff_all_crit()

    def target_armor(self):
        return self.buffs.armor_reduction_multiplier() * self.TARGET_BASE_ARMOR

