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

    def __init__(self, stats, talents, glyphs, buffs, race, settings=None, level=85):
        self.stats = stats
        self.talents = talents
        self.glyphs = glyphs
        self.buffs = buffs
        self.race = race
        self.settings = settings
        self.level = level

    def __getattr__(self, name):
        # Any status we haven't assigned a value to, we don't have.
        if name == 'calculating_ep':
            return False
        object.__getattribute__(self, name)

    def ep_helper(self,stat):
        if stat not in ('dodge_cap','white_hit','spell_hit','yellow_hit','parry_cap'):
            setattr(self.stats, stat, getattr(self.stats,stat) + 1.)
        else:
            setattr(self,'calculating_ep',stat)
        dps = DamageCalculator.get_dps(self)
        if stat not in ('dodge_cap','white_hit','spell_hit','yellow_hit','parry_cap'):
            setattr(self.stats, stat, getattr(self.stats,stat) - 1.)
        else:
            setattr(self, 'calculating_ep', False)

        return dps

    def get_ep(self):
        ep_values = {'white_hit':0, 'spell_hit':0, 'yellow_hit':0,
                     'str':0, 'agi':0, 'haste':0, 'crit':0,
                     'mastery':0, 'dodge_cap':0, 'parry_cap':0}
        baseline_dps = DamageCalculator.get_dps(self)
        ap_dps = self.ep_helper('ap')
        ap_dps_difference = ap_dps - baseline_dps
        for stat in ep_values.keys():
            dps = self.ep_helper(stat)
            ep_values[stat] = abs(dps - baseline_dps) / ap_dps_difference

        return ep_values

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

    def melee_hit_chance(self, base_miss_chance, dodgeable, parryable, weapon_type):
        hit_chance = (self.stats.get_melee_hit_from_rating() + self.race.get_racial_hit())
        miss_chance = max(base_miss_chance - hit_chance,0)
       
        #Expertise represented as the reduced chance to be dodged or parried, not true "Expertise"
        expertise = (self.stats.get_expertise_from_rating() + self.race.get_racial_expertise(weapon_type))

        if dodgeable:
            dodge_chance = max(self.BASE_DODGE_CHANCE - expertise, 0)
            if self.calculating_ep == 'dodge_cap':
                dodge_chance += self.stats.get_expertise_from_rating(1,self.level)
        else:
            dodge_chance = 0

        if parryable:
            parry_chance = max(self.BASE_PARRY_CHANCE - expertise, 0)
            if self.calculating_ep in ('parry_cap','dodge_cap'):
                parry__chance += self.stats.get_expertise_from_rating(1,self.level)
        else:
            parry_chance = 0

        return 1 - (miss_chance + dodge_chance + parry_chance)

    def one_hand_melee_hit_chance(self, dodgeable=True, parryable=False, weapon=None):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        if weapon == None:
            weapon = self.stats.mh
        hit_chance = self.melee_hit_chance(self.BASE_ONE_HAND_MISS_RATE, dodgeable, parryable, weapon.type)
        if self.calculating_ep == 'yellow_hit':
            hit_chance -= self.stats.get_melee_hit_from_rating(1,self.level)
        return hit_chance

    def dual_wield_mh_hit_chance(self, dodgeable=True, parryable=False):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        return self.dual_wield_hit_chance(dodgeable,parryable,self.stats.mh.type)

    def dual_wield_oh_hit_chance(self, dodgeable=True, parryable=False):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        return self.dual_wield_hit_chance(dodgeable,parryable,self.stats.oh.type)

    def dual_wield_hit_chance(self,dodgeable,parryable,weapon_type):
        hit_chance = self.melee_hit_chance(self.BASE_DW_MISS_RATE, dodgeable, parryable, weapon_type)
        if self.calculating_ep in ('yellow_hit','spell_hit','white_hit'):
            hit_chance -= self.stats.get_melee_hit_from_rating(1,self.level)
        return hit_chance

    def spell_hit_chance(self):
        hit_chance = 1 - max(self.BASE_SPELL_MISS_RATE - self.get_spell_hit_from_rating(),0)
        if self.calculating_ep in ('yellow_hit', 'spell_hit'):
            hit_chance -= self.stats.get_spell_hit_from_rating(1,self.level)
        return hit_chance

    def buff_melee_crit(self):
        return self.buffs.buff_all_crit()

    def buff_spell_crit(self):
        return self.buffs.buff_spell_crit() + self.buffs.buff_all_crit()

    def target_armor(self):
        return self.buffs.armor_reduction_multiplier() * self.TARGET_BASE_ARMOR
