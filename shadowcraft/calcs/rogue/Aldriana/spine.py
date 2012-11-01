import copy
import gettext
import __builtin__

__builtin__._ = gettext.gettext

from shadowcraft.calcs.rogue import RogueDamageCalculator
from shadowcraft.core import exceptions


class InputNotModeledException(exceptions.InvalidInputException):
    # I'll return these when inputs don't make sense to the model.
    pass


class SpineRogueDamageCalculator(RogueDamageCalculator):
    ###########################################################################
    # Main DPS comparison function.  Calls the appropriate sub-function based
    # on talent tree.
    ###########################################################################

    def get_dps(self):
        super(SpineRogueDamageCalculator, self).get_dps()
        if self.talents.is_assassination_rogue():
            self.init_assassination()
            return self.assassination_dps_estimate()
        elif self.talents.is_combat_rogue():
            return self.combat_dps_estimate()
        elif self.talents.is_subtlety_rogue():
            return self.subtlety_dps_estimate()
        else:
            raise InputNotModeledException(_('You must have 31 points in at least one talent tree.'))

    def get_dps_breakdown(self):
        if self.talents.is_assassination_rogue():
            self.init_assassination()
            return self.assassination_dps_breakdown()
        elif self.talents.is_combat_rogue():
            return self.combat_dps_breakdown()
        elif self.talents.is_subtlety_rogue():
            return self.subtlety_dps_breakdown()
        else:
            raise InputNotModeledException(_('You must have 31 points in at least one talent tree.'))

    def get_dps_contribution(self, damage_tuple, crit_rate, frequency):
        (base_damage, crit_damage) = damage_tuple
        average_hit = base_damage * (1 - crit_rate) + crit_damage * crit_rate
        return average_hit * frequency

    def set_constants(self):
        # General setup that we'll use in all 3 cycles.
        self.bonus_energy_regen = 0

        self.base_stats = {
            'agi': self.stats.agi + self.buffs.buff_agi() + self.race.racial_agi,
            'ap': self.stats.ap + 140,
            'crit': self.stats.crit,
            'haste': self.stats.haste,
            'mastery': self.stats.mastery
        }

        self.agi_multiplier = self.buffs.stat_multiplier() * self.stats.gear_buffs.leather_specialization_multiplier()
        self.base_stats['agi'] *= self.agi_multiplier

        self.base_strength = self.stats.str + self.buffs.buff_str() + self.race.racial_str
        self.base_strength *= self.buffs.stat_multiplier()

        self.base_speed_multiplier = 1.4 * self.buffs.melee_haste_multiplier()

        self.strike_hit_chance = self.one_hand_melee_hit_chance(dodgeable=False)
        self.base_rupture_energy_cost = 20 + 5 / self.strike_hit_chance
        self.base_eviscerate_energy_cost = 28 + 7 / self.strike_hit_chance

    def subtlety_dps_breakdown(self):
        self.set_constants()
        self.base_stats['agi'] *= 1.3
    
        haste_multiplier = self.stats.get_haste_multiplier_from_rating(self.base_stats['haste'])
        eps =  haste_multiplier* 10 + 4
    
        mastery_snd_speed = 1 + .4 * (1 + .02 * self.stats.get_mastery_from_rating(self.base_stats['mastery']))
        attack_speed_multiplier = self.buffs.melee_haste_multiplier() * haste_multiplier * mastery_snd_speed
        
        base_melee_crit_rate = self.melee_crit_rate(agi=self.base_stats['agi'], crit=self.base_stats['crit'])
        base_spell_crit_rate = self.spell_crit_rate(crit=self.base_stats['crit'])
        backstab_crit_rate = base_melee_crit_rate + .1 * self.talents.puncturing_wounds
        if backstab_crit_rate > 1:
            backstab_crit_rate = 1.
    
        ambush_crit_rate = base_melee_crit_rate + .2 * self.talents.improved_ambush
        if ambush_crit_rate > 1:
            ambush_crit_rate = 1
    
        crit_rates = {
            'mh_autoattacks': min(base_melee_crit_rate, self.dual_wield_mh_hit_chance() - self.GLANCE_RATE),
            'oh_autoattacks': min(base_melee_crit_rate, self.dual_wield_oh_hit_chance() - self.GLANCE_RATE),
            'eviscerate': base_melee_crit_rate + .1 * self.glyphs.eviscerate,
            'backstab': backstab_crit_rate,
            'ambush': ambush_crit_rate,
            'instant_poison': base_spell_crit_rate,
            'deadly_poison': base_spell_crit_rate
        }
    
        total_energy = 100 + 20 * eps
        backstab_cost = 40.
        if self.glyphs.backstab:
            backstab_cost -= 5 * backstab_crit_rate
        
        """
        (Vanish)
        Ambush                    28
        Evis                       3
        (SD)
        Ambush                    28
        Ambush                    28
        Evis                       3
        Ambush                    28
        (Tricks Buff Drops)
        Ambush                    40
        Evis                      10
        Ambush                    40
        Ambush                    40
        Evis                      10
    
        Total:                    258
        
        then: some BS, and Evis, BS till end.
        """
    
        total_energy -= 268
        attack_counts = {'ss_ambush': 1,
                         'mos_ambush': 5,
                         'mos_eviscerate': 3,
                         'ambush': 1,
                         'eviscerate': 2,
                         'backstab': total_energy / 40.}
    
        total_mh_hits = sum(attack_counts.values())
    
        attack_counts['mh_autoattacks'] = 20 * attack_speed_multiplier / self.stats.mh.speed
        attack_counts['oh_autoattacks'] = 20 * attack_speed_multiplier / self.stats.oh.speed
    
        attack_counts['mh_autoattack_hits'] = attack_counts['mh_autoattacks'] * self.dual_wield_mh_hit_chance(dodgeable=False)
        attack_counts['oh_autoattack_hits'] = attack_counts['oh_autoattacks'] * self.dual_wield_oh_hit_chance(dodgeable=False)
    
        total_mh_hits += attack_counts['mh_autoattack_hits']
        total_oh_hits = attack_counts['oh_autoattack_hits']
    
        attack_counts['instant_poison'] = (total_mh_hits * self.stats.mh.speed / 7. + total_oh_hits * .3) * self.spell_hit_chance() - 5
        attack_counts['dp_stack_ticks'] = 30 - 1000 / (total_oh_hits * self.spell_hit_chance()) / 3
    
    
        current_stats = self.base_stats
        attacks_per_second = attack_counts
        average_ap = current_stats['ap'] + 2 * current_stats['agi'] + self.base_strength
        average_ap *= self.buffs.attack_power_multiplier()
    
        damage_breakdown = {}
    
        (mh_base_damage, mh_crit_damage) = self.mh_damage(average_ap)
        mh_hit_rate = self.dual_wield_mh_hit_chance(dodgeable=False) - self.GLANCE_RATE - crit_rates['mh_autoattacks']
        average_mh_hit = self.GLANCE_RATE * self.GLANCE_MULTIPLIER * mh_base_damage + mh_hit_rate * mh_base_damage + crit_rates['mh_autoattacks'] * mh_crit_damage
        crit_mh_hit = crit_rates['mh_autoattacks'] * mh_crit_damage
        mh_dps_tuple = average_mh_hit * attacks_per_second['mh_autoattacks'], crit_mh_hit * attacks_per_second['mh_autoattacks']
    
        (oh_base_damage, oh_crit_damage) = self.oh_damage(average_ap)
        oh_hit_rate = self.dual_wield_oh_hit_chance(dodgeable=False) - self.GLANCE_RATE - crit_rates['oh_autoattacks']
        average_oh_hit = self.GLANCE_RATE * self.GLANCE_MULTIPLIER * oh_base_damage + oh_hit_rate * oh_base_damage + crit_rates['oh_autoattacks'] * oh_crit_damage
        crit_oh_hit = crit_rates['oh_autoattacks'] * oh_crit_damage
        oh_dps_tuple = average_oh_hit * attacks_per_second['oh_autoattacks'], crit_oh_hit * attacks_per_second['oh_autoattacks']
    
        damage_breakdown['autoattack'] = mh_dps_tuple[0] + oh_dps_tuple[0]
        damage_breakdown['autoattack'] *= 1.03 # Master of Subtlety
    
        damage_breakdown['backstab'] = self.get_dps_contribution(self.backstab_damage(average_ap), crit_rates['backstab'], attacks_per_second['backstab'])
    
        damage_breakdown['ambush'] = self.get_dps_contribution(self.ambush_damage(average_ap), crit_rates['ambush'], attacks_per_second['ambush'])
        damage_breakdown['ambush'] += 1.4 * self.get_dps_contribution(self.ambush_damage(average_ap), crit_rates['ambush'], attacks_per_second['ss_ambush'])
        damage_breakdown['ambush'] += 1.1 * self.get_dps_contribution(self.ambush_damage(average_ap), crit_rates['ambush'], attacks_per_second['mos_ambush'])

        damage_breakdown['eviscerate'] = self.get_dps_contribution(self.eviscerate_damage(average_ap, 5), crit_rates['eviscerate'], attacks_per_second['eviscerate'])
        damage_breakdown['eviscerate'] += 1.1 * self.get_dps_contribution(self.eviscerate_damage(average_ap, 5), crit_rates['eviscerate'], attacks_per_second['mos_eviscerate'])
    
        armor_value = self.target_armor()
        armor_reduction = .3
        find_weakness_damage_boost = self.armor_mitigation_multiplier(armor_reduction * armor_value) / self.armor_mitigation_multiplier(armor_value)
        for key in damage_breakdown:
            damage_breakdown[key] *= find_weakness_damage_boost
    
        damage_breakdown['instant_poison'] = self.get_dps_contribution(self.instant_poison_damage(average_ap, mastery=current_stats['mastery']), crit_rates['instant_poison'], attacks_per_second['instant_poison'])
    
        damage_breakdown['deadly_poison'] = self.get_dps_contribution(self.deadly_poison_tick_damage(average_ap, mastery=current_stats['mastery']), crit_rates['deadly_poison'], attacks_per_second['dp_stack_ticks'])
        return damage_breakdown
    
    def subtlety_dps_estimate(self):
        return sum(self.subtlety_dps_breakdown().values())