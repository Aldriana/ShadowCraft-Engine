import copy
import gettext
import __builtin__

__builtin__._ = gettext.gettext

from shadowcraft.calcs.rogue import RogueDamageCalculator
from shadowcraft.core import exceptions


class InputNotModeledException(exceptions.InvalidInputException):
    # I'll return these when inputs don't make sense to the model.
    pass


class AldrianasRogueDamageCalculator(RogueDamageCalculator):
    ###########################################################################
    # Main DPS comparison function.  Calls the appropriate sub-function based
    # on talent tree.
    ###########################################################################

    def get_dps(self):
        super(AldrianasRogueDamageCalculator, self).get_dps()
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

    ###########################################################################
    # General object manipulation functions that we'll use multiple places.
    ###########################################################################

    PRECISION_REQUIRED = 10 ** -7

    def are_close_enough(self, old_dist, new_dist):
        for item in new_dist:
            if item not in old_dist:
                return False
            elif not hasattr(new_dist[item], '__iter__'):
                if abs(new_dist[item] - old_dist[item]) > self.PRECISION_REQUIRED:
                    return False
            else:
                for index in range(len(new_dist[item])):
                    if abs(new_dist[item][index] - old_dist[item][index]) > self.PRECISION_REQUIRED:
                        return False
        return True

    def get_dps_contribution(self, damage_tuple, crit_rate, frequency):
        (base_damage, crit_damage) = damage_tuple
        average_hit = base_damage * (1 - crit_rate) + crit_damage * crit_rate
        crit_contribution = crit_damage * crit_rate
        return average_hit * frequency, crit_contribution * frequency

    ###########################################################################
    # General modeling functions for pulling information useful across all
    # models.
    ###########################################################################

    def heroism_uptime_per_fight(self):
        if not self.buffs.short_term_haste_buff:
            return 0

        total_uptime = 0
        remaining_duration = self.settings.duration
        while remaining_duration > 0:
            total_uptime += min(remaining_duration, 40)
            remaining_duration -= 600

        return total_uptime * 1.0 / self.settings.duration

    def get_heroism_haste_multiplier(self):
        # Just average-casing for now.  Should fix that at some point.
        return 1 + .3 * self.heroism_uptime_per_fight()

    def get_cp_distribution_for_cycle(self, cp_distribution_per_move, target_cp_quantity):
        time_spent_at_cp = [0, 0, 0, 0, 0, 0]
        cur_min_cp = 0
        ruthlessness_chance = self.talents.ruthlessness * .2
        cur_dist = {(0, 0): (1 - ruthlessness_chance), (1, 0): ruthlessness_chance}
        while cur_min_cp < target_cp_quantity:
            cur_min_cp += 1

            new_dist = {}
            for (cps, moves), prob in cur_dist.items():
                if cps >= cur_min_cp:
                    if (cps, moves) in new_dist:
                        new_dist[(cps, moves)] += prob
                    else:
                        new_dist[(cps, moves)] = prob
                else:
                    for (move_cp, move_prob) in cp_distribution_per_move.items():
                        total_cps = cps + move_cp
                        if total_cps > 5:
                            total_cps = 5
                        dist_entry = (total_cps, moves + 1)
                        time_spent_at_cp[total_cps] += move_prob * prob
                        if dist_entry in new_dist:
                            new_dist[dist_entry] += move_prob * prob
                        else:
                            new_dist[dist_entry] = move_prob * prob
            cur_dist = new_dist

        for (cps, moves), prob in cur_dist.items():
            time_spent_at_cp[cps] += prob

        total_weight = sum(time_spent_at_cp)
        for i in xrange(6):
            time_spent_at_cp[i] /= total_weight

        return cur_dist, time_spent_at_cp

    def get_snd_length(self, size):
        duration = 6 + 3 * size
        if self.glyphs.slice_and_dice:
            duration += 6
        return duration * (1 + .25 * self.talents.improved_slice_and_dice)

    def set_constants(self):
        # General setup that we'll use in all 3 cycles.
        self.bonus_energy_regen = 0
        if self.settings.tricks_on_cooldown and not self.glyphs.tricks_of_the_trade:
            self.bonus_energy_regen -= 15. / (30 + self.settings.response_time)
        if self.race.arcane_torrent:
            self.bonus_energy_regen += 15. / (120 + self.settings.response_time)

        self.base_stats = {
            'agi': self.stats.agi + self.buffs.buff_agi() + self.race.racial_agi,
            'ap': self.stats.ap + 140,
            'crit': self.stats.crit,
            'haste': self.stats.haste,
            'mastery': self.stats.mastery
        }

        for boost in self.race.get_racial_stat_boosts():
            if boost['stat'] in self.base_stats:
                self.base_stats[boost['stat']] += boost['value'] * boost['duration'] * 1.0 / (boost['cooldown'] + self.settings.response_time)

        if getattr(self.stats.gear_buffs, 'synapse_springs'):
            self.stats.gear_buffs.activated_boosts['synapse_springs']['stat'] = 'agi'

        for stat in self.base_stats:
            for boost in self.stats.gear_buffs.get_all_activated_boosts_for_stat(stat):
                if boost['cooldown'] is not None:
                    self.base_stats[stat] += (boost['value'] * boost['duration']) * 1.0 / (boost['cooldown'] + self.settings.response_time)
                else:
                    self.base_stats[stat] += (boost['value'] * boost['duration']) * 1.0 / self.settings.duration

        self.agi_multiplier = self.buffs.stat_multiplier() * self.stats.gear_buffs.leather_specialization_multiplier()

        self.base_strength = self.stats.str + self.buffs.buff_str() + self.race.racial_str
        self.base_strength *= self.buffs.stat_multiplier()

        self.relentless_strikes_energy_return_per_cp = [0, 1.75, 3.5, 5][self.talents.relentless_strikes]

        self.base_speed_multiplier = 1.4 * self.buffs.melee_haste_multiplier() * self.get_heroism_haste_multiplier()
        if self.race.berserking:
            self.base_speed_multiplier *= (1 + .2 * 10. / (180 + self.settings.response_time))
        if self.race.time_is_money:
            self.base_speed_multiplier *= 1.01

        self.strike_hit_chance = self.one_hand_melee_hit_chance()
        self.base_rupture_energy_cost = 20 + 5 / self.strike_hit_chance
        self.base_rupture_energy_cost *= self.stats.gear_buffs.rogue_t13_2pc_cost_multiplier()
        self.base_eviscerate_energy_cost = 28 + 7 / self.strike_hit_chance
        self.base_eviscerate_energy_cost *= self.stats.gear_buffs.rogue_t13_2pc_cost_multiplier()

        if self.stats.procs.heroic_matrix_restabilizer or self.stats.procs.matrix_restabilizer:
            self.set_matrix_restabilizer_stat(self.base_stats)

    def get_proc_damage_contribution(self, proc, proc_count, current_stats):
        if proc.stat == 'spell_damage':
            multiplier = self.raid_settings_modifiers('spell')
            crit_multiplier = self.crit_damage_modifiers(is_spell=True)
            crit_rate = self.spell_crit_rate(crit=current_stats['crit'])
        elif proc.stat == 'physical_damage':
            multiplier = self.raid_settings_modifiers('physical')
            crit_multiplier = self.crit_damage_modifiers(is_spell=False)
            crit_rate = self.melee_crit_rate(agi=current_stats['agi'], crit=current_stats['crit'])
        else:
            return 0, 0

        if proc.can_crit == False:
            crit_rate = 0

        proc_value = proc.value
        # Vial of Shadows scales with AP.
        vial_of_shadows_modifiers = {
            'heroic_vial_of_shadows': 1.016,
            'vial_of_shadows': .9,
            'lfr_vial_of_shadows': .797
            }
        for i in vial_of_shadows_modifiers:
            if proc is getattr(self.stats.procs, i):
                average_ap = current_stats['ap'] + 2 * current_stats['agi'] + self.base_strength
                proc_value += vial_of_shadows_modifiers[i] * average_ap

        average_hit = proc_value * multiplier
        average_damage = average_hit * (1 + crit_rate * (crit_multiplier - 1)) * proc_count
        crit_contribution = average_hit * crit_multiplier * crit_rate * proc_count
        return average_damage, crit_contribution

    def append_damage_on_use(self, average_ap, current_stats, damage_breakdown):
        on_use_damage_list = []
        for i in ('spell_damage', 'physical_damage'):
            on_use_damage_list += self.stats.gear_buffs.get_all_activated_boosts_for_stat(i)
        if self.race.rocket_barrage:
            rocket_barrage_dict = {'stat': 'spell_damage', 'cooldown': 120, 'name': 'Rocket Barrage'}
            rocket_barrage_dict['value'] = self.race.calculate_rocket_barrage(average_ap, 0, 0)
            on_use_damage_list.append(rocket_barrage_dict)

        for item in on_use_damage_list:
            if item['stat'] == 'physical_damage':
                modifier = self.raid_settings_modifiers('physical')
                crit_multiplier = self.crit_damage_modifiers(is_spell=False)
                crit_rate = self.melee_crit_rate(agi=current_stats['agi'], crit=current_stats['crit'])
                hit_chance = self.strike_hit_chance
            elif item['stat'] == 'spell_damage':
                modifier = self.raid_settings_modifiers('spell')
                crit_multiplier = self.crit_damage_modifiers(is_spell=True)
                crit_rate = self.spell_crit_rate(crit=current_stats['crit'])
                hit_chance = self.spell_hit_chance()
            average_hit = item['value'] * modifier
            frequency = 1. / (item['cooldown'] + self.settings.response_time)
            average_dps = average_hit * (1 + crit_rate * (crit_multiplier - 1)) * frequency * hit_chance
            crit_contribution = average_hit * crit_multiplier * crit_rate * frequency * hit_chance

            damage_breakdown[item['name']] = average_dps, crit_contribution

    def set_matrix_restabilizer_stat(self, base_stats):
        base_stats_for_matrix_restabilizer = {}
        for key in self.base_stats:
            if key in ('haste', 'mastery', 'crit'):
                base_stats_for_matrix_restabilizer[key] = self.base_stats[key]
        sorted_list = base_stats_for_matrix_restabilizer.keys()
        sorted_list.sort(cmp=lambda b, a: cmp(base_stats_for_matrix_restabilizer[a], base_stats_for_matrix_restabilizer[b]))

        if self.stats.procs.heroic_matrix_restabilizer:
            self.stats.procs.heroic_matrix_restabilizer.stat = sorted_list[0]
        if self.stats.procs.matrix_restabilizer:
            self.stats.procs.matrix_restabilizer.stat = sorted_list[0]

    def get_t12_2p_damage(self, damage_breakdown):
        crit_damage = 0
        for key in damage_breakdown:
            if key in ('mutilate', 'hemorrhage', 'backstab', 'sinister_strike', 'revealing_strike', 'main_gauche', 'ambush', 'killing_spree', 'envenom', 'eviscerate', 'autoattack'):
                average_damage, crit_contribution = damage_breakdown[key]
                crit_damage += crit_contribution
        for key in ('mut_munch', 'ksp_munch'):
            if damage_breakdown.has_key(key):
                average_damage, crit_contribution = damage_breakdown[key]
                crit_damage -= crit_contribution
                del damage_breakdown[key]

        return crit_damage * self.stats.gear_buffs.rogue_t12_2pc_damage_bonus(), 0

    def get_damage_breakdown(self, current_stats, attacks_per_second, crit_rates, damage_procs):
        average_ap = current_stats['ap'] + 2 * current_stats['agi'] + self.base_strength
        average_ap *= self.buffs.attack_power_multiplier()
        if self.talents.is_combat_rogue():
            average_ap *= 1.3
        average_ap *= (1 + .03 * self.talents.savage_combat)

        damage_breakdown = {}

        (mh_base_damage, mh_crit_damage) = self.mh_damage(average_ap)
        mh_hit_rate = self.dual_wield_mh_hit_chance() - self.GLANCE_RATE - crit_rates['mh_autoattacks']
        average_mh_hit = self.GLANCE_RATE * self.GLANCE_MULTIPLIER * mh_base_damage + mh_hit_rate * mh_base_damage + crit_rates['mh_autoattacks'] * mh_crit_damage
        crit_mh_hit = crit_rates['mh_autoattacks'] * mh_crit_damage
        mh_dps_tuple = average_mh_hit * attacks_per_second['mh_autoattacks'], crit_mh_hit * attacks_per_second['mh_autoattacks']

        (oh_base_damage, oh_crit_damage) = self.oh_damage(average_ap)
        oh_hit_rate = self.dual_wield_oh_hit_chance() - self.GLANCE_RATE - crit_rates['oh_autoattacks']
        average_oh_hit = self.GLANCE_RATE * self.GLANCE_MULTIPLIER * oh_base_damage + oh_hit_rate * oh_base_damage + crit_rates['oh_autoattacks'] * oh_crit_damage
        crit_oh_hit = crit_rates['oh_autoattacks'] * oh_crit_damage
        oh_dps_tuple = average_oh_hit * attacks_per_second['oh_autoattacks'], crit_oh_hit * attacks_per_second['oh_autoattacks']

        damage_breakdown['autoattack'] = mh_dps_tuple[0] + oh_dps_tuple[0], mh_dps_tuple[1] + oh_dps_tuple[1]

        for key in attacks_per_second.keys():
            if not attacks_per_second[key]:
                del attacks_per_second[key]

        if 'mutilate' in attacks_per_second:
            mh_dmg = self.mh_mutilate_damage(average_ap)
            oh_dmg = self.oh_mutilate_damage(average_ap)
            mh_mutilate_dps = self.get_dps_contribution(mh_dmg, crit_rates['mutilate'], attacks_per_second['mutilate'])
            oh_mutilate_dps = self.get_dps_contribution(oh_dmg, crit_rates['mutilate'], attacks_per_second['mutilate'])
            damage_breakdown['mutilate'] = mh_mutilate_dps[0] + oh_mutilate_dps[0], mh_mutilate_dps[1] + oh_mutilate_dps[1]
            if self.stats.gear_buffs.rogue_t12_2pc:
                p_double_crit = crit_rates['mutilate'] ** 2
                munch_per_sec = attacks_per_second['mutilate'] * p_double_crit
                damage_breakdown['mut_munch'] = 0, munch_per_sec * mh_dmg[1]

        if 'hemorrhage' in attacks_per_second:
            damage_breakdown['hemorrhage'] = self.get_dps_contribution(self.hemorrhage_damage(average_ap), crit_rates['hemorrhage'], attacks_per_second['hemorrhage'])

        if 'backstab' in attacks_per_second:
            damage_breakdown['backstab'] = self.get_dps_contribution(self.backstab_damage(average_ap), crit_rates['backstab'], attacks_per_second['backstab'])

        if 'sinister_strike' in attacks_per_second:
            damage_breakdown['sinister_strike'] = self.get_dps_contribution(self.sinister_strike_damage(average_ap), crit_rates['sinister_strike'], attacks_per_second['sinister_strike'])

        if 'revealing_strike' in attacks_per_second:
            damage_breakdown['revealing_strike'] = self.get_dps_contribution(self.revealing_strike_damage(average_ap), crit_rates['revealing_strike'], attacks_per_second['revealing_strike'])

        if 'main_gauche' in attacks_per_second:
            damage_breakdown['main_gauche'] = self.get_dps_contribution(self.main_gauche_damage(average_ap), crit_rates['main_gauche'], attacks_per_second['main_gauche'])

        if 'ambush' in attacks_per_second:
            damage_breakdown['ambush'] = self.get_dps_contribution(self.ambush_damage(average_ap), crit_rates['ambush'], attacks_per_second['ambush'])

        if 'mh_killing_spree' in attacks_per_second:
            mh_dmg = self.mh_killing_spree_damage(average_ap)
            oh_dmg = self.oh_killing_spree_damage(average_ap)
            mh_killing_spree_dps = self.get_dps_contribution(mh_dmg, crit_rates['killing_spree'], attacks_per_second['mh_killing_spree'])
            oh_killing_spree_dps = self.get_dps_contribution(oh_dmg, crit_rates['killing_spree'], attacks_per_second['oh_killing_spree'])
            damage_breakdown['killing_spree'] = mh_killing_spree_dps[0] + oh_killing_spree_dps[0], mh_killing_spree_dps[1] + oh_killing_spree_dps[1]
            if self.stats.gear_buffs.rogue_t12_2pc:
                p_double_crit = crit_rates['killing_spree'] ** 2
                munch_per_sec = attacks_per_second['mh_killing_spree'] * p_double_crit
                damage_breakdown['ksp_munch'] = 0, munch_per_sec * mh_dmg[1]

        if 'rupture_ticks' in attacks_per_second:
            average_dps = crit_dps = 0
            for i in xrange(1, 6):
                dps_tuple = self.get_dps_contribution(self.rupture_tick_damage(average_ap, i), crit_rates['rupture_ticks'], attacks_per_second['rupture_ticks'][i])
                average_dps += dps_tuple[0]
                crit_dps += dps_tuple[1]
            damage_breakdown['rupture'] = average_dps, crit_dps

        if 'garrote_ticks' in attacks_per_second:
            damage_breakdown['garrote'] = self.get_dps_contribution(self.garrote_tick_damage(average_ap), crit_rates['garrote'], attacks_per_second['garrote_ticks'])

        if 'envenom' in attacks_per_second:
            average_dps = crit_dps = 0
            for i in xrange(1, 6):
                dps_tuple = self.get_dps_contribution(self.envenom_damage(average_ap, i, current_stats['mastery']), crit_rates['envenom'], attacks_per_second['envenom'][i])
                average_dps += dps_tuple[0]
                crit_dps += dps_tuple[1]
            damage_breakdown['envenom'] = average_dps, crit_dps

        if 'eviscerate' in attacks_per_second:
            average_dps = crit_dps = 0
            for i in xrange(1, 6):
                dps_tuple = self.get_dps_contribution(self.eviscerate_damage(average_ap, i), crit_rates['eviscerate'], attacks_per_second['eviscerate'][i])
                average_dps += dps_tuple[0]
                crit_dps += dps_tuple[1]
            damage_breakdown['eviscerate'] = average_dps, crit_dps

        if 'venomous_wounds' in attacks_per_second:
            damage_breakdown['venomous_wounds'] = self.get_dps_contribution(self.venomous_wounds_damage(average_ap, mastery=current_stats['mastery']), crit_rates['venomous_wounds'], attacks_per_second['venomous_wounds'])

        if 'instant_poison' in attacks_per_second:
            damage_breakdown['instant_poison'] = self.get_dps_contribution(self.instant_poison_damage(average_ap, mastery=current_stats['mastery']), crit_rates['instant_poison'], attacks_per_second['instant_poison'])

        if 'deadly_poison' in attacks_per_second:
            damage_breakdown['deadly_poison'] = self.get_dps_contribution(self.deadly_poison_tick_damage(average_ap, mastery=current_stats['mastery']), crit_rates['deadly_poison'], attacks_per_second['deadly_poison'])

        if 'wound_poison' in attacks_per_second:
            damage_breakdown['wound_poison'] = self.get_dps_contribution(self.wound_poison_damage(average_ap, mastery=current_stats['mastery']), crit_rates['wound_poison'], attacks_per_second['wound_poison'])

        if 'hemorrhage_ticks' in attacks_per_second:
            dps_from_hit_hemo = self.get_dps_contribution(self.hemorrhage_tick_damage(average_ap, from_crit_hemo=False), crit_rates['hemorrhage'], attacks_per_second['hemorrhage_ticks'] * (1 - crit_rates['hemorrhage']))
            dps_from_crit_hemo = self.get_dps_contribution(self.hemorrhage_tick_damage(average_ap, from_crit_hemo=True), crit_rates['hemorrhage'], attacks_per_second['hemorrhage_ticks'] * crit_rates['hemorrhage'])
            damage_breakdown['hemorrhage_glyph'] = dps_from_hit_hemo[0] + dps_from_crit_hemo[0], dps_from_hit_hemo[1] + dps_from_crit_hemo[1]

        for proc in damage_procs:
            if proc.proc_name not in damage_breakdown:
                # Toss multiple damage procs with the same name (Avalanche):
                # attacks_per_second is already being updated with that key.
                damage_breakdown[proc.proc_name] = self.get_proc_damage_contribution(proc, attacks_per_second[proc.proc_name], current_stats)

        self.append_damage_on_use(average_ap, current_stats, damage_breakdown)

        if self.stats.gear_buffs.rogue_t12_2pc:
            damage_breakdown['burning_wounds'] = self.get_t12_2p_damage(damage_breakdown)

        return damage_breakdown

    def get_mh_procs_per_second(self, proc, attacks_per_second, crit_rates):
        triggers_per_second = 0
        if proc.procs_off_auto_attacks():
            if proc.procs_off_crit_only():
                triggers_per_second += attacks_per_second['mh_autoattacks'] * crit_rates['mh_autoattacks']
            else:
                triggers_per_second += attacks_per_second['mh_autoattack_hits']
        if proc.procs_off_strikes():
            for ability in ('mutilate', 'backstab', 'revealing_strike', 'sinister_strike', 'ambush', 'hemorrhage', 'mh_killing_spree', 'main_gauche'):
                if ability == 'main_gauche' and not proc.procs_off_procced_strikes():
                    pass
                elif ability in attacks_per_second:
                    if proc.procs_off_crit_only():
                        triggers_per_second += attacks_per_second[ability] * crit_rates[ability]
                    else:
                        triggers_per_second += attacks_per_second[ability]
            for ability in ('envenom', 'eviscerate'):
                if ability in attacks_per_second:
                    if proc.procs_off_crit_only():
                        triggers_per_second += sum(attacks_per_second[ability]) * crit_rates[ability]
                    else:
                        triggers_per_second += sum(attacks_per_second[ability])
        if proc.procs_off_apply_debuff():
            if 'rupture' in attacks_per_second:
                if not proc.procs_off_crit_only():
                    triggers_per_second += attacks_per_second['rupture']
            if 'garrote' in attacks_per_second:
                if not proc.procs_off_crit_only():
                    triggers_per_second += attacks_per_second['garrote']
            if 'hemorrhage_ticks' in attacks_per_second:
                if not proc.procs_off_crit_only():
                    triggers_per_second += attacks_per_second['hemorrhage']

        return triggers_per_second * proc.proc_rate(self.stats.mh.speed)

    def get_oh_procs_per_second(self, proc, attacks_per_second, crit_rates):
        triggers_per_second = 0
        if proc.procs_off_auto_attacks():
            if proc.procs_off_crit_only():
                triggers_per_second += attacks_per_second['oh_autoattacks'] * crit_rates['oh_autoattacks']
            else:
                triggers_per_second += attacks_per_second['oh_autoattack_hits']
        if proc.procs_off_strikes():
            for ability in ('mutilate', 'oh_killing_spree'):
                if ability in attacks_per_second:
                    if proc.procs_off_crit_only():
                        triggers_per_second += attacks_per_second[ability] * crit_rates[ability]
                    else:
                        triggers_per_second += attacks_per_second[ability]

        return triggers_per_second * proc.proc_rate(self.stats.oh.speed)

    def get_other_procs_per_second(self, proc, attacks_per_second, crit_rates):
        triggers_per_second = 0

        if proc.procs_off_harmful_spells():
            for ability in ('instant_poison', 'wound_poison', 'venomous_wounds'):
                if ability in attacks_per_second:
                    if proc.procs_off_crit_only():
                        triggers_per_second += attacks_per_second[ability] * crit_rates[ability]
                    else:
                        triggers_per_second += attacks_per_second[ability]
        if proc.procs_off_periodic_spell_damage():
            if 'deadly_poison' in attacks_per_second:
                if proc.procs_off_crit_only():
                    triggers_per_second += attacks_per_second['deadly_poison'] * crit_rates['deadly_poison']
                else:
                    triggers_per_second += attacks_per_second['deadly_poison']
        if proc.procs_off_bleeds():
            if 'rupture_ticks' in attacks_per_second:
                if proc.procs_off_crit_only():
                    triggers_per_second += sum(attacks_per_second['rupture_ticks']) * crit_rates['rupture']
                else:
                    triggers_per_second += sum(attacks_per_second['rupture_ticks'])
            if 'garrote_ticks' in attacks_per_second:
                if proc.procs_off_crit_only():
                    triggers_per_second += attacks_per_second['garrote_ticks'] * crit_rates['garrote']
                else:
                    triggers_per_second += attacks_per_second['garrote_ticks']
            if 'hemorrhage_ticks' in attacks_per_second:
                if proc.procs_off_crit_only():
                    triggers_per_second += attacks_per_second['hemorrhage_ticks'] * crit_rates['hemorrhage']
                else:
                    triggers_per_second += attacks_per_second['hemorrhage_ticks']
        if proc.is_ppm():
            if triggers_per_second == 0:
                return 0
            else:
                raise InputNotModeledException(_('PPMs that also proc off spells are not yet modeled.'))
        else:
            return triggers_per_second * proc.proc_rate()

    def get_procs_per_second(self, proc, attacks_per_second, crit_rates):
        # TODO: Include damaging proc hits in figuring out how often everything else procs.
        if getattr(proc, 'mh_only', False):
            procs_per_second = self.get_mh_procs_per_second(proc, attacks_per_second, crit_rates)
        elif getattr(proc, 'oh_only', False):
            procs_per_second = self.get_oh_procs_per_second(proc, attacks_per_second, crit_rates)
        else:
            procs_per_second = self.get_mh_procs_per_second(proc, attacks_per_second, crit_rates) + self.get_oh_procs_per_second(proc, attacks_per_second, crit_rates) + self.get_other_procs_per_second(proc, attacks_per_second, crit_rates)

        return procs_per_second

    def set_uptime_for_ramping_proc(self, proc, procs_per_second):
        time_for_one_stack = 1 / procs_per_second
        if time_for_one_stack * proc.max_stacks > self.settings.duration:
            max_stacks_reached = self.settings.duration * procs_per_second
            proc.uptime = max_stacks_reached / 2
        else:
            missing_stacks = proc.max_stacks * (proc.max_stacks + 1) / 2
            stack_time_lost = missing_stacks * time_for_one_stack
            proc.uptime = proc.max_stacks - stack_time_lost / self.settings.duration

    def set_uptime(self, proc, attacks_per_second, crit_rates):
        procs_per_second = self.get_procs_per_second(proc, attacks_per_second, crit_rates)

        if proc.icd:
            proc.uptime = proc.duration / (proc.icd + 1. / procs_per_second)
        else:
            if procs_per_second >= 1:
                self.set_uptime_for_ramping_proc(proc, procs_per_second)
            else:
            # See http://elitistjerks.com/f31/t20747-advanced_rogue_mechanics_discussion/#post621369
            # for the derivation of this formula.
                q = 1 - procs_per_second
                Q = q ** proc.duration
                if Q < .0001:
                    self.set_uptime_for_ramping_proc(proc, procs_per_second)
                else:
                    P = 1 - Q
                    proc.uptime = P * (1 - P ** proc.max_stacks) / Q

    def update_with_damaging_proc(self, proc, attacks_per_second, crit_rates):
        if proc.icd:
            frequency = 1. / (proc.icd + 0.5 / self.get_procs_per_second(proc, attacks_per_second, crit_rates))
        else:
            frequency = self.get_procs_per_second(proc, attacks_per_second, crit_rates)

        attacks_per_second.setdefault(proc.proc_name, 0)
        if proc.stat == 'spell_damage':
            attacks_per_second[proc.proc_name] += frequency * self.spell_hit_chance()
        elif proc.stat == 'physical_damage':
            attacks_per_second[proc.proc_name] += frequency * self.strike_hit_chance

    """
    def get_weapon_damage_bonus(self):
        # Unheeded Warning does not proc as weapon damage anymore. I'll leave
        # this here in case they implement anything alike.
        bonus = 0
        if self.stats.procs.unheeded_warning:
            proc = self.stats.procs.unheeded_warning
            bonus += proc.value * proc.uptime

        return bonus
    """

    def update_crit_rates_for_4pc_t11(self, attacks_per_second, crit_rates):
        t11_4pc_bonus = self.stats.procs.rogue_t11_4pc
        if t11_4pc_bonus:
            direct_damage_finisher = ''
            for key in ('envenom', 'eviscerate'):
                if key in attacks_per_second and sum(attacks_per_second[key]) != 0:
                    if direct_damage_finisher:
                        raise InputNotModeledException(_('Unable to model the 4pc T11 set bonus in a cycle that uses both eviscerate and envenom'))
                    direct_damage_finisher = key

            if direct_damage_finisher:
                procs_per_second = self.get_procs_per_second(t11_4pc_bonus, attacks_per_second, crit_rates)
                finisher_spacing = min(1 / sum(attacks_per_second[direct_damage_finisher]), t11_4pc_bonus.duration)
                p = 1 - (1 - procs_per_second) ** finisher_spacing
                crit_rates[direct_damage_finisher] = p + (1 - p) * crit_rates[direct_damage_finisher]

    def get_4pc_t12_multiplier(self):
        if self.settings.tricks_on_cooldown:
            tricks_uptime = 30. / (30 + self.settings.response_time)
            return 1 + self.stats.gear_buffs.rogue_t12_4pc_stat_bonus() * tricks_uptime / 3
        else:
            return 1.

    def get_rogue_t13_legendary_combat_multiplier(self):
        # This only deals with the SS/RvS damage increase.
        if self.stats.gear_buffs.rogue_t13_legendary or self.stats.procs.jaws_of_retribution or self.stats.procs.maw_of_oblivion or self.stats.procs.fangs_of_the_father:
            return 1.45
        else:
            return 1.

    def setup_unique_procs(self):
        # We need to set these behaviours before calling any other method.
        # The stage 3 will very likely need a different set of behaviours
        # once we figure the whole thing.
        for proc in ('jaws_of_retribution', 'maw_of_oblivion', 'fangs_of_the_father'):
            if getattr(self.stats.procs, proc):
                if self.talents.is_assassination_rogue():
                    spec = 'assassination'
                elif self.talents.is_combat_rogue():
                    spec = 'combat'
                elif self.talents.is_subtlety_rogue():
                    spec = 'subtlety'
                getattr(self.stats.procs, proc).behaviour_toggle = spec

        # Tie Nokaled to the MH (equipping it in the OH, as a rogue, is unlikely)
        for i in ('', 'heroic_', 'lfr_'):
            proc = getattr(self.stats.procs, ''.join((i, 'nokaled_the_elements_of_death')))
            if proc:
                setattr(proc, 'mh_only', True)

    def get_poison_counts(self, total_mh_hits, total_oh_hits, attacks_per_second):
        if self.settings.mh_poison == 'dp' or self.settings.oh_poison == 'dp':
            attacks_per_second['deadly_poison'] = 1. / 3

        if self.settings.mh_poison == 'ip':
            mh_proc_rate = self.stats.mh.speed / 7.
        elif self.settings.mh_poison == 'wp':
            mh_proc_rate = self.stats.mh.speed / 2.8
        else: # Deadly Poison
            mh_proc_rate = .3

        if self.settings.oh_poison == 'ip':
            oh_proc_rate = self.stats.oh.speed / 7.
        elif self.settings.oh_poison == 'wp':
            oh_proc_rate = self.stats.oh.speed / 2.8
        else: # Deadly Poison
            oh_proc_rate = .3

        mh_poison_procs = total_mh_hits * mh_proc_rate * self.spell_hit_chance()
        oh_poison_procs = total_oh_hits * oh_proc_rate * self.spell_hit_chance()

        poison_setup = ''.join((self.settings.mh_poison, self.settings.oh_poison))
        if poison_setup in ['ipip', 'ipdp', 'dpip']:
            attacks_per_second['instant_poison'] = mh_poison_procs + oh_poison_procs
        elif poison_setup in ['wpwp', 'wpdp', 'dpwp']:
            attacks_per_second['wound_poison'] = mh_poison_procs + oh_poison_procs
        elif poison_setup == 'ipwp':
            attacks_per_second['instant_poison'] = mh_poison_procs
            attacks_per_second['wound_poison'] = oh_poison_procs
        elif poison_setup == 'wpip':
            attacks_per_second['wound_poison'] = mh_poison_procs
            attacks_per_second['instant_poison'] = oh_poison_procs

    def compute_damage(self, attack_counts_function):
        # TODO: Crit cap
        #
        # TODO: Hit/Exp procs

        current_stats = {
            'agi': self.base_stats['agi'] * self.agi_multiplier,
            'ap': self.base_stats['ap'],
            'crit': self.base_stats['crit'],
            'haste': self.base_stats['haste'],
            'mastery': self.base_stats['mastery']
        }

        active_procs = []
        damage_procs = []
        weapon_damage_procs = []

        self.setup_unique_procs()

        for proc_info in self.stats.procs.get_all_procs_for_stat():
            if proc_info.stat in current_stats and not proc_info.is_ppm():
                active_procs.append(proc_info)
            elif proc_info.stat in ('spell_damage', 'physical_damage'):
                damage_procs.append(proc_info)
            elif proc_info.stat == 'extra_weapon_damage':
                weapon_damage_procs.append(proc_info)

        weapon_enchants = set([])
        for hand, enchant in [(x, y) for x in ('mh', 'oh') for y in ('landslide', 'hurricane', 'avalanche')]:
            proc = getattr(getattr(self.stats, hand), enchant)
            if proc:
                setattr(proc, '_'.join((hand, 'only')), True)
                if proc.stat in current_stats:
                    active_procs.append(proc)
                elif enchant == 'avalanche':
                    damage_procs.append(proc)

                if enchant not in weapon_enchants and enchant in ('hurricane', 'avalanche'):
                    weapon_enchants.add(enchant)
                    spell_component = copy.copy(proc)
                    delattr(spell_component, '_'.join((hand, 'only')))
                    spell_component.behaviour_toggle = 'spell'
                    if enchant == 'hurricane':
                        # This would heavily overestimate Hurricane by ignoring the refresh mechanic.
                        # active_procs.append(spell_component)
                        pass
                    elif enchant == 'avalanche':
                        damage_procs.append(spell_component)

        attacks_per_second, crit_rates = attack_counts_function(current_stats)

        for _loop in range(20):
            current_stats = {
                'agi': self.base_stats['agi'],
                'ap': self.base_stats['ap'],
                'crit': self.base_stats['crit'],
                'haste': self.base_stats['haste'],
                'mastery': self.base_stats['mastery']
            }

            self.update_crit_rates_for_4pc_t11(attacks_per_second, crit_rates)

            for proc in damage_procs:
                if not proc.icd:
                    self.update_with_damaging_proc(proc, attacks_per_second, crit_rates)

            for proc in active_procs:
                if not proc.icd:
                    self.set_uptime(proc, attacks_per_second, crit_rates)
                    current_stats[proc.stat] += proc.uptime * proc.value

            current_stats['agi'] *= self.agi_multiplier
            for stat in ('crit', 'haste', 'mastery'):
                current_stats[stat] *= self.get_4pc_t12_multiplier()

            old_attacks_per_second = attacks_per_second
            attacks_per_second, crit_rates = attack_counts_function(current_stats)

            if self.are_close_enough(old_attacks_per_second, attacks_per_second):
                break

        for proc in active_procs:
            if proc.icd:
                self.set_uptime(proc, attacks_per_second, crit_rates)
                if proc.stat == 'agi':
                    current_stats[proc.stat] += proc.uptime * proc.value * self.agi_multiplier
                elif proc.stat in ('crit', 'haste', 'mastery'):
                    current_stats[proc.stat] += proc.uptime * proc.value * self.get_4pc_t12_multiplier()
                else:
                    current_stats[proc.stat] += proc.uptime * proc.value

        attacks_per_second, crit_rates = attack_counts_function(current_stats)

        self.update_crit_rates_for_4pc_t11(attacks_per_second, crit_rates)

        for proc in damage_procs:
            self.update_with_damaging_proc(proc, attacks_per_second, crit_rates)

        for proc in weapon_damage_procs:
            self.set_uptime(proc, attacks_per_second, crit_rates)

        damage_breakdown = self.get_damage_breakdown(current_stats, attacks_per_second, crit_rates, damage_procs)

        # Discard the crit component.
        for key in damage_breakdown:
            damage_breakdown[key] = damage_breakdown[key][0]

        return damage_breakdown

    # This relies on set_uptime being called for the proc in compute_damage before any of the actual computation stuff is invoked.
    def unheeded_warning_bonus(self):
        proc = self.stats.procs.unheeded_warning
        if not proc:
            return 0        
        return proc.value * proc.uptime        

    ###########################################################################
    # Combat DPS functions
    ###########################################################################

    def combat_dps_estimate(self):
        return sum(self.combat_dps_breakdown().values())

    def combat_dps_breakdown(self):
        if self.settings.cycle._cycle_type != 'combat':
            raise InputNotModeledException(_('You must specify a combat cycle to match your combat spec.'))

        if self.settings.cycle.use_revealing_strike not in ('sometimes', 'always', 'never'):
            raise InputNotModeledException(_('Revealing strike usage must be set to always, sometimes, or never'))

        if not self.talents.revealing_strike and self.settings.cycle.use_revealing_strike != 'never':
            raise InputNotModeledException(_('Cannot specify revealing strike usage in cycle without taking the talent.'))

        self.set_constants()

        if self.talents.bandits_guile:
            self.max_bandits_guile_buff = 1.3
        else:
            self.max_bandits_guile_buff = 1

        self.base_revealing_strike_energy_cost = 32 + 8 / self.strike_hit_chance
        self.base_revealing_strike_energy_cost *= self.stats.gear_buffs.rogue_t13_2pc_cost_multiplier()
        self.base_sinister_strike_energy_cost = 36 + 9 / self.strike_hit_chance - 2 * self.talents.improved_sinister_strike
        self.base_sinister_strike_energy_cost *= self.stats.gear_buffs.rogue_t13_2pc_cost_multiplier()

        self.base_energy_regen = 12.5

        damage_breakdown = self.compute_damage(self.combat_attack_counts)
        for key in damage_breakdown:
            if key == 'killing_spree':
                if self.settings.cycle.ksp_immediately:
                    damage_breakdown[key] *= self.bandits_guile_multiplier * (1.2 + .1 * self.glyphs.killing_spree)
                else:
                    damage_breakdown[key] *= self.max_bandits_guile_buff * (1.2 + .1 * self.glyphs.killing_spree)
            elif key in ('sinister_strike', 'revealing_strike'):
                damage_breakdown[key] *= self.bandits_guile_multiplier
                damage_breakdown[key] *= self.get_rogue_t13_legendary_combat_multiplier()
            elif key == 'eviscerate':
                damage_breakdown[key] *= self.bandits_guile_multiplier * self.revealing_strike_multiplier
            elif key == 'rupture':
                damage_breakdown[key] *= self.bandits_guile_multiplier * self.ksp_multiplier * self.revealing_strike_multiplier
            elif key in ('autoattack', 'instant_poison', 'deadly_poison', 'main_gauche'):
                damage_breakdown[key] *= self.bandits_guile_multiplier * self.ksp_multiplier
            else:
                damage_breakdown[key] *= self.ksp_multiplier

        return damage_breakdown

    def combat_attack_counts(self, current_stats):
        attacks_per_second = {}

        base_melee_crit_rate = self.melee_crit_rate(agi=current_stats['agi'], crit=current_stats['crit'])
        base_spell_crit_rate = self.spell_crit_rate(crit=current_stats['crit'])

        haste_multiplier = self.stats.get_haste_multiplier_from_rating(current_stats['haste'])

        attack_speed_multiplier = self.base_speed_multiplier * haste_multiplier * (1 + .02 * self.talents.lightning_reflexes)

        attacks_per_second['mh_autoattacks'] = attack_speed_multiplier / self.stats.mh.speed
        attacks_per_second['oh_autoattacks'] = attack_speed_multiplier / self.stats.oh.speed

        attacks_per_second['mh_autoattack_hits'] = attacks_per_second['mh_autoattacks'] * self.dual_wield_mh_hit_chance()
        attacks_per_second['oh_autoattack_hits'] = attacks_per_second['oh_autoattacks'] * self.dual_wield_oh_hit_chance()

        main_gauche_proc_rate = .02 * self.stats.get_mastery_from_rating(current_stats['mastery']) * self.one_hand_melee_hit_chance()
        attacks_per_second['main_gauche'] = main_gauche_proc_rate * attacks_per_second['mh_autoattack_hits']

        autoattack_cp_regen = self.talents.combat_potency * (attacks_per_second['oh_autoattack_hits'] + attacks_per_second['main_gauche'])
        energy_regen = self.base_energy_regen * haste_multiplier + self.bonus_energy_regen + autoattack_cp_regen

        rupture_energy_cost = self.base_rupture_energy_cost - main_gauche_proc_rate * self.talents.combat_potency
        eviscerate_energy_cost = self.base_eviscerate_energy_cost - main_gauche_proc_rate * self.talents.combat_potency
        revealing_strike_energy_cost = self.base_revealing_strike_energy_cost - main_gauche_proc_rate * self.talents.combat_potency
        sinister_strike_energy_cost = self.base_sinister_strike_energy_cost - main_gauche_proc_rate * self.talents.combat_potency

        crit_rates = {
            'mh_autoattacks': min(base_melee_crit_rate, self.dual_wield_mh_hit_chance() - self.GLANCE_RATE),
            'oh_autoattacks': min(base_melee_crit_rate, self.dual_wield_oh_hit_chance() - self.GLANCE_RATE),
            'main_gauche': base_melee_crit_rate,
            'sinister_strike': base_melee_crit_rate + self.stats.gear_buffs.rogue_t11_2pc_crit_bonus(),
            'revealing_strike': base_melee_crit_rate,
            'eviscerate': base_melee_crit_rate + .1 * self.glyphs.eviscerate,
            'killing_spree': base_melee_crit_rate,
            'oh_killing_spree': base_melee_crit_rate,
            'mh_killing_spree': base_melee_crit_rate,
            'rupture_ticks': base_melee_crit_rate,
            'instant_poison': base_spell_crit_rate,
            'deadly_poison': base_spell_crit_rate,
            'wound_poison': base_spell_crit_rate
        }

        extra_cp_chance = 0
        if self.glyphs.sinister_strike:
            extra_cp_chance = .2

        cp_per_ss = {1: 1 - extra_cp_chance, 2: extra_cp_chance}
        FINISHER_SIZE = 5

        if self.settings.cycle.use_revealing_strike == 'never':
            cp_distribution = self.get_cp_distribution_for_cycle(cp_per_ss, FINISHER_SIZE)[0]

            rvs_per_finisher = 0
            ss_per_finisher = 0
            cp_per_finisher = 0
            finisher_size_breakdown = [0, 0, 0, 0, 0, 0]
            for (cps, ss), probability in cp_distribution.items():
                ss_per_finisher += ss * probability
                cp_per_finisher += cps * probability
                finisher_size_breakdown[cps] += probability
        elif self.settings.cycle.use_revealing_strike == 'sometimes':
            cp_distribution = self.get_cp_distribution_for_cycle(cp_per_ss, FINISHER_SIZE - 1)[0]

            rvs_per_finisher = 0
            ss_per_finisher = 0
            cp_per_finisher = 0
            finisher_size_breakdown = [0, 0, 0, 0, 0, 0]
            for (cps, ss), probability in cp_distribution.items():
                ss_per_finisher += ss * probability
                if cps < FINISHER_SIZE:
                    actual_cps = cps + 1
                    rvs_per_finisher += probability
                else:
                    actual_cps = cps
                cp_per_finisher += actual_cps * probability
                finisher_size_breakdown[actual_cps] += probability
        else:
            cp_distribution = self.get_cp_distribution_for_cycle(cp_per_ss, FINISHER_SIZE - 1)[0]

            rvs_per_finisher = 1
            ss_per_finisher = 0
            cp_per_finisher = 0
            finisher_size_breakdown = [0, 0, 0, 0, 0, 0]
            for (cps, ss), probability in cp_distribution.items():
                ss_per_finisher += ss * probability
                actual_cps = min(cps + 1, 5)
                cp_per_finisher += actual_cps * probability
                finisher_size_breakdown[actual_cps] += probability

        self.revealing_strike_multiplier = (1 + (.35 + .1 * self.glyphs.revealing_strike) * rvs_per_finisher)

        gcds_for_finisher = rvs_per_finisher + ss_per_finisher + 1
        cycles_per_second = 1 / (1.1 * gcds_for_finisher)

        """
        energy_cost_to_generate_cps = rvs_per_finisher * revealing_strike_energy_cost + ss_per_finisher * sinister_strike_energy_cost
        total_eviscerate_cost = energy_cost_to_generate_cps + eviscerate_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
        total_rupture_cost = energy_cost_to_generate_cps + rupture_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp

        ss_per_snd = (total_eviscerate_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp + 25) / sinister_strike_energy_cost
        snd_size = ss_per_snd * (1 + extra_cp_chance) + .2 * self.talents.ruthlessness
        snd_base_cost = 25 * self.stats.gear_buffs.rogue_t13_2pc_cost_multiplier()
        snd_cost = (ss_per_snd + .2 * self.talents.ruthlessness / (1 + extra_cp_chance)) * sinister_strike_energy_cost + snd_base_cost - snd_size * self.relentless_strikes_energy_return_per_cp

        snd_duration = self.get_snd_length(snd_size)

        energy_spent_on_snd = snd_cost / (snd_duration - self.settings.response_time)

        avg_rupture_gap = (total_rupture_cost - .5 * total_eviscerate_cost) / energy_regen
        avg_rupture_duration = 2 * (3 + 2 * self.glyphs.rupture + cp_per_finisher)
        if self.settings.cycle.use_rupture:
            attacks_per_second['rupture'] = 1 / (avg_rupture_duration + avg_rupture_gap)
        else:
            attacks_per_second['rupture'] = 0
        energy_spent_on_rupture = total_rupture_cost * attacks_per_second['rupture']

        energy_available_for_evis = energy_regen - energy_spent_on_snd - energy_spent_on_rupture
        evis_per_second = energy_available_for_evis / total_eviscerate_cost

        cp_spent_on_damage_finishers_per_second = (attacks_per_second['rupture'] + evis_per_second) * cp_per_finisher

        if self.talents.adrenaline_rush:
            ar_duration = 15 + 5 * self.glyphs.adrenaline_rush
            ar_duration += self.stats.gear_buffs.rogue_t13_4pc * 3
        else:
            ar_duration = 0

        ar_bonus_cp_regen = autoattack_cp_regen * .2
        ar_bonus_energy = ar_duration * (ar_bonus_cp_regen + 10 * haste_multiplier)
        ar_bonus_evis = ar_bonus_energy / total_eviscerate_cost
        ar_cooldown_self_reduction = ar_bonus_evis * cp_per_finisher * self.talents.restless_blades

        ar_actual_cooldown = (180 - ar_cooldown_self_reduction) / (1 + cp_spent_on_damage_finishers_per_second * self.talents.restless_blades) + self.settings.response_time
        total_evis_per_second = evis_per_second + ar_bonus_evis / ar_actual_cooldown

        ar_uptime = ar_duration / ar_actual_cooldown
        ar_autoattack_multiplier = 1 + .2 * ar_uptime

        for attack in ('mh_autoattacks', 'mh_autoattack_hits', 'oh_autoattacks', 'oh_autoattack_hits', 'main_gauche'):
            attacks_per_second[attack] *= ar_autoattack_multiplier

        total_restless_blades_benefit = (total_evis_per_second + attacks_per_second['rupture']) * cp_per_finisher * self.talents.restless_blades
        ksp_cooldown = 120 / (1 + total_restless_blades_benefit) + self.settings.response_time
        """

        total_evis_per_second = cycles_per_second
        for attack in ('mh_autoattacks', 'mh_autoattack_hits', 'oh_autoattacks', 'oh_autoattack_hits', 'main_gauche'):
            attacks_per_second[attack] *= 1.2

        attacks_per_second['sinister_strike'] = cycles_per_second * ss_per_finisher 
        attacks_per_second['revealing_strike'] = cycles_per_second * rvs_per_finisher
        attacks_per_second['main_gauche'] += (attacks_per_second['sinister_strike'] + attacks_per_second['revealing_strike'] + total_evis_per_second) * main_gauche_proc_rate

        if self.talents.bandits_guile:
            triggers_per_second = attacks_per_second['sinister_strike'] + attacks_per_second['revealing_strike']
            time_at_level = 4 / triggers_per_second
            self.bandits_guile_multiplier = 1 + .1 * (3 - 6 * time_at_level / 20)
        else:
            self.bandits_guile_multiplier = 1

        if not self.talents.killing_spree:
            attacks_per_second['mh_killing_spree'] = 5 * self.strike_hit_chance / ksp_cooldown
            attacks_per_second['oh_killing_spree'] = 5 * self.off_hand_melee_hit_chance() / ksp_cooldown
            ksp_uptime = 2. / ksp_cooldown

            ksp_buff = .2 + .1 * self.glyphs.killing_spree
            if self.settings.cycle.ksp_immediately:
                self.ksp_multiplier = 1 + ksp_uptime * ksp_buff
            else:
                self.ksp_multiplier = 1 + ksp_uptime * ksp_buff * self.max_bandits_guile_buff / self.bandits_guile_multiplier
        else:
            attacks_per_second['mh_killing_spree'] = 0
            attacks_per_second['oh_killing_spree'] = 0
            self.ksp_multiplier = 1

        attacks_per_second['eviscerate'] = [0,0,0,0,0,cycles_per_second]

        total_mh_hits = attacks_per_second['mh_autoattack_hits'] + attacks_per_second['sinister_strike'] + attacks_per_second['revealing_strike'] + attacks_per_second['mh_killing_spree'] + attacks_per_second['eviscerate'][5] + attacks_per_second['main_gauche']
        total_oh_hits = attacks_per_second['oh_autoattack_hits'] + attacks_per_second['oh_killing_spree']

        self.get_poison_counts(total_mh_hits, total_oh_hits, attacks_per_second)

        return attacks_per_second, crit_rates