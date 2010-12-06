import gettext
import __builtin__

__builtin__._ = gettext.gettext

from shadowcraft.core import exceptions
from shadowcraft.calcs import armor_mitigation
from shadowcraft.objects.procs import InvalidProcException

class DamageCalculator(object):
    # This method holds the general interface for a damage calculator - the
    # sorts of parameters and calculated values that will be need by many (or
    # most) classes if they implement a damage calculator using this framework.
    # Not saying that will happen, but I want to leave my options open.
    # Any calculations that are specific to a particular class should go in
    # calcs.<class>.<Class>DamageCalculator instead - for an example, see
    # calcs.rogue.RogueDamageCalculator

    # If someone wants to have __init__ take a target level as well and use it
    # to initialize these to a level-dependent value, they're welcome to.  At
    # the moment I'm hardcoding them to level 85 values.
    TARGET_BASE_ARMOR = 11977.
    BASE_ONE_HAND_MISS_RATE = .08
    BASE_DW_MISS_RATE = .27
    BASE_SPELL_MISS_RATE = .17
    BASE_DODGE_CHANCE = .065
    BASE_PARRY_CHANCE = .14
    GLANCE_RATE = .24
    GLANCE_MULTIPLIER = .75

    # Override this in your class specfic subclass to list appropriate stats
    # possible values are agi, str, spi, int, white_hit, spell_hit, yellow_hit,
    # haste, crit, mastery, dodge_exp, parry_exp, oh_dodge_exp, mh_dodge_exp,
    # oh_parry_exp, mh_parry_exp
    default_ep_stats = []

    def __init__(self, stats, talents, glyphs, buffs, race, settings=None, level=85):
        self.stats = stats
        self.talents = talents
        self.glyphs = glyphs
        self.buffs = buffs
        self.race = race
        self.settings = settings
        self.level = level
        if self.stats.gear_buffs.mixology and self.buffs.agi_flask:
            self.stats.agi += 80
        if self.stats.gear_buffs.master_of_anatomy:
            self.stats.crit += 80

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'level':
            self._set_constants_for_level()

    def __getattr__(self, name):
        # Any status we haven't assigned a value to, we don't have.
        if name == 'calculating_ep':
            return False
        object.__getattribute__(self, name)

    def _set_constants_for_level(self):
        self.buffs.level = self.level
        self.stats.level = self.level
        self.race.level = self.level
        # calculate and cache the level-dependent armor mitigation parameter
        self.armor_mitigation_parameter = armor_mitigation.parameter(self.level)

    def ep_helper(self,stat):
        if stat not in ('dodge_exp', 'white_hit', 'spell_hit', 'yellow_hit', 'parry_exp', 'mh_dodge_exp', 'oh_dodge_exp', 'mh_parry_exp', 'oh_parry_exp'):
            setattr(self.stats, stat, getattr(self.stats, stat) + 1.)
        else:
            setattr(self, 'calculating_ep', stat)
        dps = self.get_dps()
        if stat not in ('dodge_exp', 'white_hit', 'spell_hit', 'yellow_hit', 'parry_exp', 'mh_dodge_exp', 'oh_dodge_exp', 'mh_parry_exp', 'oh_parry_exp'):
            setattr(self.stats, stat, getattr(self.stats, stat) - 1.)
        else:
            setattr(self, 'calculating_ep', False)

        return dps

    def get_ep(self, ep_stats=None):
        if not ep_stats:
            ep_stats = self.default_ep_stats
        ep_values = {}
        for stat in ep_stats:
            ep_values[stat] = 0
        baseline_dps = self.get_dps()
        ap_dps = self.ep_helper('ap')
        ap_dps_difference = ap_dps - baseline_dps
        for stat in ep_values.keys():
            dps = self.ep_helper(stat)
            ep_values[stat] = abs(dps - baseline_dps) / ap_dps_difference

        return ep_values

    def get_weapon_ep(self, speed_list=None, dps=False, enchants=False):
        weapons = ('mh', 'oh')
        if speed_list != None or dps == True:
            baseline_dps = self.get_dps()
            ap_dps = self.ep_helper('ap')

        for hand in weapons:
            ep_values = {}

            # Weapon dps EP
            if dps == True:
                getattr(self.stats, hand).weapon_dps += 1.
                new_dps = self.get_dps()
                ep = abs(new_dps - baseline_dps) / (ap_dps - baseline_dps)
                ep_values[hand + '_dps'] = ep
                getattr(self.stats, hand).weapon_dps -= 1.

            # Enchant EP
            if enchants == True:
                old_enchant = None
                for enchant in getattr(self.stats, hand).allowed_melee_enchants:
                    if getattr(getattr(self.stats, hand), enchant):
                        old_enchant = enchant
                for enchant in getattr(self.stats, hand).allowed_melee_enchants:
                    getattr(self.stats, hand).del_enchant()
                    no_enchant_dps = self.get_dps()
                    no_enchant_ap_dps = self.ep_helper('ap')
                    getattr(self.stats, hand).set_enchant(enchant)
                    new_dps = self.get_dps()
                    if new_dps != no_enchant_dps:
                        ep = abs(new_dps - no_enchant_dps) / (no_enchant_ap_dps - no_enchant_dps)
                        ep_values[hand + '_' + enchant] = ep
                    getattr(self.stats, hand).set_enchant(old_enchant)

            # Weapon speed EP
            if speed_list != None:
                old_speed = getattr(self.stats, hand).speed
                for speed in speed_list:
                    getattr(self.stats, hand).speed = speed
                    new_dps = self.get_dps()
                    ep = (new_dps - baseline_dps) / (ap_dps - baseline_dps)
                    ep_values[hand + '_' +  str(speed)] = ep
                    getattr(self.stats, hand).speed = old_speed

            if hand == 'mh':
                mh_ep_values = ep_values
            elif hand == 'oh':
                oh_ep_values = ep_values

        return mh_ep_values, oh_ep_values

    def get_other_ep(self, list):
        # This method computes ep for every other buff/proc not covered by
        # get_ep or get_weapon_ep. Weapon enchants, being tied to the
        # weapons they are on, are computed by get_weapon_ep.
        ep_values = {}
        baseline_dps = self.get_dps()
        ap_dps = self.ep_helper('ap')

        procs_list = []
        gear_buffs_list = []
        for i in list:
            if i in self.stats.procs.allowed_procs.keys():
                procs_list.append(i)
            elif i in self.stats.gear_buffs.allowed_buffs:
                gear_buffs_list.append(i)
            else:
                ep_values[i] = _('not allowed')

        for i in gear_buffs_list:
            # Note that activated abilites like trinkets, potions, or
            # engineering gizmos are handled as gear buffs by the engine.
            setattr(self.stats.gear_buffs, i, not getattr(self.stats.gear_buffs, i))
            new_dps = self.get_dps()
            ep_values[i] = abs(new_dps - baseline_dps) / (ap_dps - baseline_dps)
            setattr(self.stats.gear_buffs, i, not getattr(self.stats.gear_buffs, i))

        for i in procs_list:
            try:
                if getattr(self.stats.procs, i):
                    delattr(self.stats.procs, i)
                else:
                    self.stats.procs.set_proc(i)
                new_dps = self.get_dps()
                ep_values[i] = abs(new_dps - baseline_dps) / (ap_dps - baseline_dps)
                if getattr(self.stats.procs, i):
                    delattr(self.stats.procs, i)
                else:
                    self.stats.procs.set_proc(i)
            except InvalidProcException:
                # Data for these procs is not complete/correct
                ep_values[i] = _('not supported')
                delattr(self.stats.procs, i)

        return ep_values

    def get_glyphs_ranking(self, list=None):
        glyphs = []
        glyphs_ranking = {}
        baseline_dps = self.get_dps()

        if list == None:
            glyphs = self.glyphs.allowed_glyphs
        else:
            glyphs = list

        for i in glyphs:
            setattr(self.glyphs, i, not getattr(self.glyphs, i))
            new_dps = self.get_dps()
            if new_dps != baseline_dps:
                glyphs_ranking[i] = abs(new_dps - baseline_dps)
            setattr(self.glyphs, i, not getattr(self.glyphs, i))

        return glyphs_ranking

    def get_talents_ranking(self, list=None):
        talents_ranking = {}
        baseline_dps = self.get_dps()
        talent_list = []

        if list == None:
        # Build a list of talents that can be taken in the active spec
            for talent in self.talents.treeForTalent.keys():
                if self.talents.get_talent_tier(talent) <= 2:
                    talent_list.append(talent)
                elif talent in self.talents.spec.allowed_talents.keys():
                    talent_list.append(talent)
        else:
            talent_list = list

        for talent in talent_list:
            old_talent_value = getattr(self.talents, talent)
            if old_talent_value == 0:
                new_talent_value = 1
            else:
                new_talent_value = old_talent_value - 1

            self.talents.treeForTalent[talent].set_talent(talent, new_talent_value)
            try:
                new_dps = self.get_dps()
                # Disregard talents that don't affect dps
                if new_dps != baseline_dps:
                    talents_ranking[talent] = abs(new_dps - baseline_dps)
            except:
                talents_ranking[talent] = _('not implemented')
            self.talents.treeForTalent[talent].set_talent(talent, old_talent_value)

        main_tree_talents_ranking = {}
        off_trees_talents_ranking = {}
        for talent in talents_ranking:
            if talent in self.talents.spec.allowed_talents.keys():
                main_tree_talents_ranking[talent] = talents_ranking[talent]
            else:
                off_trees_talents_ranking[talent] = talents_ranking[talent]

        return main_tree_talents_ranking, off_trees_talents_ranking

    def get_dps(self):
        # Overwrite this function with your calculations/simulations/whatever;
        # this is what callers will (initially) be looking at.
        pass

    def get_spell_hit_from_talents(self):
        # Override this in your subclass to implement talents that modify spell hit chance
        return 0.

    def get_melee_hit_from_talents(self):
        # Override this in your subclass to implement talents that modify melee hit chance
        return 0.

    def get_all_activated_stat_boosts(self):
        racial_boosts = self.race.get_racial_stat_boosts()
        gear_boosts = self.stats.gear_buffs.get_all_activated_boosts()
        return racial_boosts + gear_boosts

    def armor_mitigation_multiplier(self, armor):
        return armor_mitigation.multiplier(armor, cached_parameter=self.armor_mitigation_parameter)

    def armor_mitigate(self, damage, armor):
        # Pass in raw physical damage and armor value, get armor-mitigated
        # damage value.
        return damage * self.armor_mitigation_multiplier(armor)

    def melee_hit_chance(self, base_miss_chance, dodgeable, parryable, weapon_type):
        hit_chance = self.stats.get_melee_hit_from_rating() + self.race.get_racial_hit() + self.get_melee_hit_from_talents()
        miss_chance = max(base_miss_chance - hit_chance,0)

        #Expertise represented as the reduced chance to be dodged or parried, not true "Expertise"
        expertise = self.stats.get_expertise_from_rating() + self.race.get_racial_expertise(weapon_type)

        if dodgeable:
            dodge_chance = max(self.BASE_DODGE_CHANCE - expertise, 0)
            if self.calculating_ep == 'dodge_exp':
                dodge_chance += self.stats.get_expertise_from_rating(1)
        else:
            dodge_chance = 0

        if parryable:
            parry_chance = max(self.BASE_PARRY_CHANCE - expertise, 0)
            if self.calculating_ep in ('parry_exp', 'dodge_exp'):
                parry_chance += self.stats.get_expertise_from_rating(1)
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
            hit_chance -= self.stats.get_melee_hit_from_rating(1)
        if (self.calculating_ep == 'mh_dodge_exp' and dodgeable) or (self.calculating_ep == 'mh_parry_exp' and parryable):
            hit_chance -= self.stats.get_expertise_from_rating(1)
        return hit_chance

    def off_hand_melee_hit_chance(self, dodgeable=True, parryable=False, weapon=None):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        if weapon == None:
            weapon = self.stats.oh
        hit_chance = self.melee_hit_chance(self.BASE_ONE_HAND_MISS_RATE, dodgeable, parryable, weapon.type)
        if self.calculating_ep == 'yellow_hit':
            hit_chance -= self.stats.get_melee_hit_from_rating(1)
        if (self.calculating_ep == 'oh_dodge_exp' and dodgeable) or (self.calculating_ep == 'oh_parry_exp' and parryable):
            hit_chance -= self.stats.get_expertise_from_rating(1)
        return hit_chance

    def dual_wield_mh_hit_chance(self, dodgeable=True, parryable=False):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        hit_chance = self.dual_wield_hit_chance(dodgeable, parryable, self.stats.mh.type)
        if (self.calculating_ep == 'mh_dodge_exp' and dodgeable) or (self.calculating_ep == 'mh_parry_exp' and parryable):
            hit_chance -= self.stats.get_expertise_from_rating(1)
        return hit_chance

    def dual_wield_oh_hit_chance(self, dodgeable=True, parryable=False):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        hit_chance = self.dual_wield_hit_chance(dodgeable, parryable, self.stats.oh.type)
        if (self.calculating_ep == 'oh_dodge_exp' and dodgeable) or (self.calculating_ep == 'oh_parry_exp' and parryable):
            hit_chance -= self.stats.get_expertise_from_rating(1)
        return hit_chance

    def dual_wield_hit_chance(self, dodgeable, parryable, weapon_type):
        hit_chance = self.melee_hit_chance(self.BASE_DW_MISS_RATE, dodgeable, parryable, weapon_type)
        if self.calculating_ep in ('yellow_hit','spell_hit','white_hit'):
            hit_chance -= self.stats.get_melee_hit_from_rating(1)
        return hit_chance

    def spell_hit_chance(self):
        hit_chance = 1 - max(self.BASE_SPELL_MISS_RATE - self.stats.get_spell_hit_from_rating() - self.get_spell_hit_from_talents() - self.race.get_racial_hit(), 0)
        if self.calculating_ep in ('yellow_hit', 'spell_hit'):
            hit_chance -= self.stats.get_spell_hit_from_rating(1)
        return hit_chance

    def buff_melee_crit(self):
        return self.buffs.buff_all_crit()

    def buff_spell_crit(self):
        return self.buffs.buff_spell_crit() + self.buffs.buff_all_crit()

    def target_armor(self, armor=None):
        # Passes base armor reduced by armor debuffs or overridden armor
        if armor is None:
            armor = self.TARGET_BASE_ARMOR
        return self.buffs.armor_reduction_multiplier() * armor

    def raid_settings_modifiers(self, is_spell=False, is_physical=False, is_bleed=False, armor=None):
        # This function wraps spell, bleed and physical debuffs from raid
        # along with all-damage buff and armor reduction. It should be called
        # from every damage dealing formula. Armor can be overridden if needed.
        if is_spell + is_bleed + is_physical != 1:
            raise exceptions.InvalidInputException(_('Attacks cannot benefit from more than one type of raid damage multiplier'))
        armor_override = self.target_armor(armor)
        if is_spell:
            return self.buffs.spell_damage_multiplier()
        elif is_bleed:
            return self.buffs.bleed_damage_multiplier()
        elif is_physical:
            return self.buffs.physical_damage_multiplier() * self.armor_mitigation_multiplier(armor_override)
