import gettext
import __builtin__

__builtin__._ = gettext.gettext

from shadowcraft.core import exceptions
from shadowcraft.calcs import armor_mitigation
from shadowcraft.objects import class_data
from shadowcraft.objects.procs import InvalidProcException

class DamageCalculator(object):
    # This method holds the general interface for a damage calculator - the
    # sorts of parameters and calculated values that will be need by many (or
    # most) classes if they implement a damage calculator using this framework.
    # Not saying that will happen, but I want to leave my options open.
    # Any calculations that are specific to a particular class should go in
    # calcs.<class>.<Class>DamageCalculator instead - for an example, see
    # calcs.rogue.RogueDamageCalculator

    TARGET_BASE_ARMOR_VALUES = {88:11977., 93:24835.}
    GLANCE_RATE = .24
    GLANCE_MULTIPLIER = .75

    # Override this in your class specfic subclass to list appropriate stats
    # possible values are agi, str, spi, int, white_hit, spell_hit, yellow_hit,
    # haste, crit, mastery, dodge_exp, parry_exp, oh_dodge_exp, mh_dodge_exp,
    # oh_parry_exp, mh_parry_exp
    default_ep_stats = []
    # normalize_ep_stat is the stat with value 1 EP, override in your subclass
    normalize_ep_stat = None

    def __init__(self, stats, talents, glyphs, buffs, race, settings=None, level=85, target_level=None):
        self.tools = class_data.Util()
        self.stats = stats
        self.talents = talents
        self.glyphs = glyphs
        self.buffs = buffs
        self.race = race
        self.settings = settings
        self.target_level = [target_level, level + 3][target_level is None]
        self.level_difference = max(self.target_level - level, 0)
        self.level = level
        if self.stats.gear_buffs.mixology and self.buffs.agi_flask:
            self.stats.agi += self.stats.gear_buffs.tradeskill_bonus()
        if self.stats.gear_buffs.master_of_anatomy:
            self.stats.crit += self.stats.gear_buffs.tradeskill_bonus()
        self._set_constants_for_class()
        
        self.base_one_hand_miss_rate = .03 + .015 * self.level_difference
        self.base_dw_miss_rate = self.base_one_hand_miss_rate + .19
        self.base_spell_miss_rate = .06 + .03 * self.level_difference
        self.base_dodge_chance = .03 + .015 * self.level_difference
        self.base_parry_chance = .03 + .015 * self.level_difference
        self.base_block_chance = .03 + .015 * self.level_difference

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
        self.stats.gear_buffs.level = self.level
        # calculate and cache the level-dependent armor mitigation parameter
        self.armor_mitigation_parameter = armor_mitigation.parameter(self.level)
        # target level dependent constants
        try:
            self.target_base_armor = self.TARGET_BASE_ARMOR_VALUES[self.target_level]
        except KeyError as e:
            raise exceptions.InvalidInputException(_('There\'s no armor value for a target level {level}').format(level=str(e)))
        self.melee_crit_reduction = .01 * self.level_difference
        self.spell_crit_reduction = .01 * self.level_difference

    def _set_constants_for_class(self):
        # These factors are class-specific. Generaly those go in the class module,
        # unless it's basic stuff like combat ratings or base stats that we can
        # datamine for all classes/specs at once.
        if self.talents.game_class != self.glyphs.game_class:
            raise exceptions.InvalidInputException(_('You must specify the same class for your talents and glyphs'))
        self.game_class = self.talents.game_class
        self.agi_crit_intercept = self.tools.get_agi_intercept(self.game_class)

    def ep_helper(self, stat):
        if stat not in ('dodge_exp', 'white_hit', 'spell_hit', 'yellow_hit', 'parry_exp', 'mh_dodge_exp', 'oh_dodge_exp', 'mh_parry_exp', 'oh_parry_exp', 'spell_exp'):
            setattr(self.stats, stat, getattr(self.stats, stat) + 1.)
        else:
            setattr(self, 'calculating_ep', stat)
        dps = self.get_dps()
        if stat not in ('dodge_exp', 'white_hit', 'spell_hit', 'yellow_hit', 'parry_exp', 'mh_dodge_exp', 'oh_dodge_exp', 'mh_parry_exp', 'oh_parry_exp', 'spell_exp'):
            setattr(self.stats, stat, getattr(self.stats, stat) - 1.)
        else:
            setattr(self, 'calculating_ep', False)

        return dps

    def get_ep(self, ep_stats=None, normalize_ep_stat=None):
        if not normalize_ep_stat:
            normalize_ep_stat = self.normalize_ep_stat
        if not ep_stats:
            ep_stats = self.default_ep_stats
        ep_values = {}
        for stat in ep_stats:
            ep_values[stat] = 0
        baseline_dps = self.get_dps()
        normalize_dps = self.ep_helper(normalize_ep_stat)
        normalize_dps_difference = normalize_dps - baseline_dps
        for stat in ep_values:
            dps = self.ep_helper(stat)
            ep_values[stat] = abs(dps - baseline_dps) / normalize_dps_difference

        return ep_values

    def get_weapon_ep(self, speed_list=None, dps=False, enchants=False, normalize_ep_stat=None):
        if not normalize_ep_stat:
            normalize_ep_stat = self.normalize_ep_stat
        weapons = ('mh', 'oh')
        if speed_list is not None or dps:
            baseline_dps = self.get_dps()
            normalize_dps = self.ep_helper(normalize_ep_stat)

        for hand in weapons:
            ep_values = {}

            # Weapon dps EP
            if dps:
                getattr(self.stats, hand).weapon_dps += 1.
                new_dps = self.get_dps()
                ep = abs(new_dps - baseline_dps) / (normalize_dps - baseline_dps)
                ep_values[hand + '_dps'] = ep
                getattr(self.stats, hand).weapon_dps -= 1.

            # Enchant EP
            if enchants:
                old_enchant = None
                for enchant in getattr(self.stats, hand).allowed_melee_enchants:
                    if getattr(getattr(self.stats, hand), enchant):
                        old_enchant = enchant
                for enchant in getattr(self.stats, hand).allowed_melee_enchants:
                    getattr(self.stats, hand).del_enchant()
                    no_enchant_dps = self.get_dps()
                    no_enchant_normalize_dps = self.ep_helper(normalize_ep_stat)
                    getattr(self.stats, hand).set_enchant(enchant)
                    new_dps = self.get_dps()
                    if new_dps != no_enchant_dps:
                        ep = abs(new_dps - no_enchant_dps) / (no_enchant_normalize_dps - no_enchant_dps)
                        ep_values[hand + '_' + enchant] = ep
                    getattr(self.stats, hand).set_enchant(old_enchant)

            # Weapon speed EP
            if speed_list is not None:
                old_speed = getattr(self.stats, hand).speed
                for speed in speed_list:
                    getattr(self.stats, hand).speed = speed
                    new_dps = self.get_dps()
                    ep = (new_dps - baseline_dps) / (normalize_dps - baseline_dps)
                    ep_values[hand + '_' + str(speed)] = ep
                    getattr(self.stats, hand).speed = old_speed

            if hand == 'mh':
                mh_ep_values = ep_values
            elif hand == 'oh':
                oh_ep_values = ep_values

        return mh_ep_values, oh_ep_values

    def get_other_ep(self, list, normalize_ep_stat=None):
        if not normalize_ep_stat:
            normalize_ep_stat = self.normalize_ep_stat
        # This method computes ep for every other buff/proc not covered by
        # get_ep or get_weapon_ep. Weapon enchants, being tied to the
        # weapons they are on, are computed by get_weapon_ep.
        ep_values = {}
        baseline_dps = self.get_dps()
        normalize_dps = self.ep_helper(normalize_ep_stat)

        procs_list = []
        gear_buffs_list = []
        for i in list:
            if i in self.stats.procs.allowed_procs:
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
            ep_values[i] = abs(new_dps - baseline_dps) / (normalize_dps - baseline_dps)
            setattr(self.stats.gear_buffs, i, not getattr(self.stats.gear_buffs, i))

        for i in procs_list:
            try:
                if getattr(self.stats.procs, i):
                    delattr(self.stats.procs, i)
                else:
                    self.stats.procs.set_proc(i)
                new_dps = self.get_dps()
                ep_values[i] = abs(new_dps - baseline_dps) / (normalize_dps - baseline_dps)
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
            try:
                new_dps = self.get_dps()
                if new_dps != baseline_dps:
                    glyphs_ranking[i] = abs(new_dps - baseline_dps)
            except:
                glyphs_ranking[i] = _('not implemented')
            setattr(self.glyphs, i, not getattr(self.glyphs, i))

        return glyphs_ranking

    def get_talents_ranking(self, list=None):
        talents_ranking = {}
        baseline_dps = self.get_dps()
        talent_list = []

        if list is None:
            talent_list = self.talents.get_allowed_talents_for_level()
        else:
            talent_list = list

        for talent in talent_list:
            setattr(self.talents, talent, not getattr(self.talents, talent))
            try:
                new_dps = self.get_dps()
                if new_dps != baseline_dps:
                    talents_ranking[talent] = abs(new_dps - baseline_dps)
            except:
                talents_ranking[talent] = _('not implemented')
            setattr(self.talents, talent, not getattr(self.talents, talent))

        return talents_ranking

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

    def melee_hit_chance(self, base_miss_chance, dodgeable, parryable, weapon_type, blockable=False):
        hit_chance = self.stats.get_melee_hit_from_rating() + self.race.get_racial_hit() + self.get_melee_hit_from_talents()
        miss_chance = max(base_miss_chance - hit_chance, 0)

        # Expertise represented as the reduced chance to be dodged, not true "Expertise".
        expertise = self.stats.get_expertise_from_rating() + self.race.get_racial_expertise(weapon_type)

        if dodgeable:
            dodge_chance = max(self.base_dodge_chance - expertise, 0)
            if self.calculating_ep == 'dodge_exp':
                dodge_chance += self.stats.get_expertise_from_rating(1)
        else:
            dodge_chance = 0

        if parryable:
            # Expertise will negate dodge and spell miss, *then* parry
            parry_expertise = max(expertise - self.base_dodge_chance, 0)
            parry_chance = max(self.base_parry_chance - parry_expertise, 0)
            if self.calculating_ep in ('parry_exp', 'dodge_exp'):
                parry_chance += self.stats.get_expertise_from_rating(1)
        else:
            parry_chance = 0

        block_chance = self.base_block_chance * blockable

        return (1 - (miss_chance + dodge_chance + parry_chance)) * (1 - block_chance)

    def melee_spells_hit_chance(self):
        hit_chance = self.melee_hit_chance(self.base_one_hand_miss_rate, dodgeable=False, parryable=False, weapon_type=None)
        if self.calculating_ep == 'yellow_hit':
            hit_chance -= self.stats.get_melee_hit_from_rating(1)
        return hit_chance

    def one_hand_melee_hit_chance(self, dodgeable=True, parryable=False, weapon=None):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        if weapon == None:
            weapon = self.stats.mh
        hit_chance = self.melee_hit_chance(self.base_one_hand_miss_rate, dodgeable, parryable, weapon.type)
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
        hit_chance = self.melee_hit_chance(self.base_one_hand_miss_rate, dodgeable, parryable, weapon.type)
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
        if self.calculating_ep == 'mh_dodge_exp' and (dodgeable or parryable):
            hit_chance -= self.stats.get_expertise_from_rating(1)
        return hit_chance

    def dual_wield_oh_hit_chance(self, dodgeable=True, parryable=False):
        # Most attacks by DPS aren't parryable due to positional negation. But
        # if you ever want to attacking from the front, you can just set that
        # to True.
        hit_chance = self.dual_wield_hit_chance(dodgeable, parryable, self.stats.oh.type)
        if self.calculating_ep == 'oh_dodge_exp' and (dodgeable or parryable):
            hit_chance -= self.stats.get_expertise_from_rating(1)
        return hit_chance

    def dual_wield_hit_chance(self, dodgeable, parryable, weapon_type):
        hit_chance = self.melee_hit_chance(self.base_dw_miss_rate, dodgeable, parryable, weapon_type)
        if self.calculating_ep in ('yellow_hit', 'spell_hit', 'white_hit'):
            hit_chance -= self.stats.get_melee_hit_from_rating(1)
        return hit_chance

    def spell_hit_chance(self):
        hit_chance = 1 - max(self.base_spell_miss_rate - self.stats.get_spell_hit_from_rating() - self.get_spell_hit_from_talents() - self.race.get_racial_hit(), 0)
        if self.calculating_ep in ('yellow_hit', 'spell_hit', 'spell_exp'):
            hit_chance -= self.stats.get_spell_hit_from_rating(1)
        return hit_chance

    def buff_melee_crit(self):
        return self.buffs.buff_all_crit()

    def buff_spell_crit(self):
        return self.buffs.buff_spell_crit() + self.buffs.buff_all_crit()

    def crit_damage_modifiers(self, crit_damage_bonus_modifier=1):
        # The obscure formulae for the different crit enhancers can be found here
        # http://elitistjerks.com/f31/t13300-shaman_relentless_earthstorm_ele/#post404567
        base_modifier = 2
        crit_damage_modifier = self.stats.gear_buffs.metagem_crit_multiplier()
        total_modifier = 1 + (base_modifier * crit_damage_modifier - 1) * crit_damage_bonus_modifier
        return total_modifier

    def target_armor(self, armor=None):
        # Passes base armor reduced by armor debuffs or overridden armor
        if armor is None:
            armor = self.target_base_armor
        return self.buffs.armor_reduction_multiplier() * armor

    def raid_settings_modifiers(self, attack_kind, armor=None):
        # This function wraps spell, bleed and physical debuffs from raid
        # along with all-damage buff and armor reduction. It should be called
        # from every damage dealing formula. Armor can be overridden if needed.
        if attack_kind not in ('physical', 'spell', 'bleed'):
            raise exceptions.InvalidInputException(_('Attacks must be categorized as physical, spell or bleed'))
        elif attack_kind == 'spell':
            return self.buffs.spell_damage_multiplier()
        elif attack_kind == 'bleed':
            return self.buffs.bleed_damage_multiplier()
        elif attack_kind == 'physical':
            armor_override = self.target_armor(armor)
            return self.buffs.physical_damage_multiplier() * self.armor_mitigation_multiplier(armor_override)
