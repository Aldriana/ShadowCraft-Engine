import gettext
import __builtin__

__builtin__._ = gettext.gettext

from calcs.rogue import RogueDamageCalculator
from core import exceptions


class InputNotModeledException(exceptions.InvalidInputException):
    # I'll return these when inputs don't make sense to the model.
    pass


class AldrianasRogueDamageCalculator(RogueDamageCalculator):
    ###########################################################################
    # Main DPS comparison function.  Calls the appropriate sub-function based
    # on talent tree.
    ###########################################################################

    def get_dps(self):
        if self.talents.is_assassination_rogue():
            self.init_assassination()
            return self.assassination_dps_estimate()
        elif self.talents.is_combat_rogue():
            return self.combat_dps_estimate()
        elif self.talents.is_subtlety_rogue():
            return self.subtlety_dps_estimate()
        else:
            raise InputNotModeledException(_('You must have 31 points in at least one talent tree.'))

    ###########################################################################
    # General object manipulation functions that we'll use multiple places.
    ###########################################################################

    PRECISION_REQUIRED = 10 ** -7

    def are_close_enough(self, old_dist, new_dist):
        for item in new_dist.keys():
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
        return average_hit * frequency

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
        cur_min_cp = 0
        ruthlessness_chance = self.talents.ruthlessness * .2
        cur_dist = {(0,0):(1-ruthlessness_chance), (1,0):ruthlessness_chance}
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
                        if dist_entry in new_dist:
                            new_dist[dist_entry] += move_prob * prob
                        else:
                            new_dist[dist_entry] = move_prob * prob
            cur_dist = new_dist

        return cur_dist

    def set_constants(self):
        # General setup that we'll use in all 3 cycles.  Called from 
        # init_<spec>().
        self.base_energy_regen = 10

        self.bonus_energy_regen = 0
        if self.settings.tricks_on_cooldown and not self.glyphs.tricks_of_the_trade:
            self.bonus_energy_regen -= 15./(30+self.settings.response_time)

        self.base_agility = self.stats.agi + self.buffs.buff_agi() + self.race.racial_agi
        for value, duration, cooldown in self.stats.gear_buffs.get_all_activated_agi_boosts():
            if cooldown is not None:
                self.base_agility += (value * duration) * 1.0 / (cooldown + self.settings.response_time)
            else:
                self.base_agility += (value * duration) * 1.0 / self.settings.duration

        self.agi_multiplier = self.buffs.stat_multiplier() * self.stats.gear_buffs.leather_specialization_multiplier()

        self.base_strength = self.stats.str + self.buffs.buff_str() + self.race.racial_str
        self.base_strength *= self.buffs.stat_multiplier()

        self.relentless_strikes_energy_return_per_cp = [0, 1.75, 3.5, 5][self.talents.relentless_strikes]

        self.base_speed_multiplier = 1.4 * self.buffs.melee_haste_multiplier() * self.get_heroism_haste_multiplier()

    def get_proc_damage_contribution(self, proc, proc_count, current_stats):
        base_damage = proc.value

        if proc.stat == 'spell_damage':
            multiplier = self.raid_settings_modifiers(is_spell=True)
            crit_multiplier = self.crit_damage_modifiers(is_spell=True)
            crit_rate = self.spell_crit_rate(crit=current_stats['crit'])
        elif proc.stat == 'physical_damage':
            multiplier = self.raid_settings_modifiers(is_physical=True)
            crit_multiplier = self.crit_damage_modifiers(is_physical=True)
            crit_rate = self.melee_crit_rate(agi=current_stats['agi'], crit=current_stats['crit'])
        else:
            return 0

        return base_damage * multiplier * (1 + crit_rate * (crit_multiplier - 1)) * proc_count

    def get_damage_breakdown(self, current_stats, attacks_per_second, crit_rates, damage_procs):
        # Vendetta may want to be handled elsewhere.
        average_ap = current_stats['ap'] + 2 * current_stats['agi'] + self.base_strength
        average_ap *= self.buffs.attack_power_multiplier()

        damage_breakdown = {}

        (mh_base_damage, mh_crit_damage) = self.mh_damage(average_ap)
        mh_hit_rate = self.dual_wield_mh_hit_chance() - self.GLANCE_RATE - crit_rates['mh_autoattacks']
        average_mh_hit = self.GLANCE_RATE * self.GLANCE_MULTIPLIER * mh_base_damage + mh_hit_rate * mh_base_damage + crit_rates['mh_autoattacks'] * mh_crit_damage
        mh_dps = average_mh_hit * attacks_per_second['mh_autoattacks']

        (oh_base_damage, oh_crit_damage) = self.oh_damage(average_ap)
        oh_hit_rate = self.dual_wield_oh_hit_chance() - self.GLANCE_RATE - crit_rates['oh_autoattacks']
        average_oh_hit = self.GLANCE_RATE * self.GLANCE_MULTIPLIER * oh_base_damage + oh_hit_rate * oh_base_damage + crit_rates['oh_autoattacks'] * oh_crit_damage
        oh_dps = average_oh_hit * attacks_per_second['oh_autoattacks']

        damage_breakdown['autoattack'] = (mh_dps + oh_dps) * self.vendetta_mult

        if 'mutilate' in attacks_per_second:
            mh_mutilate_dps = self.get_dps_contribution(self.mh_mutilate_damage(average_ap), crit_rates['mutilate'], attacks_per_second['mutilate'])
            oh_mutilate_dps = self.get_dps_contribution(self.oh_mutilate_damage(average_ap), crit_rates['mutilate'], attacks_per_second['mutilate'])
            damage_breakdown['mutilate'] = (mh_mutilate_dps + oh_mutilate_dps) * self.vendetta_mult

        if 'backstab' in attacks_per_second:
            damage_breakdown['backstab'] = self.get_dps_contribution(self.backstab_damage(average_ap), crit_rates['backstab'], attacks_per_second['backstab']) * self.vendetta_mult

        if 'rupture_ticks' in attacks_per_second:
            rupture_dps = 0
            for i in xrange(1,6):
                rupture_dps += self.get_dps_contribution(self.rupture_tick_damage(average_ap, i), crit_rates['rupture_ticks'], attacks_per_second['rupture_ticks'][i])
            damage_breakdown['rupture'] = rupture_dps * self.vendetta_mult

        if 'envenom' in attacks_per_second:
            envenom_dps = 0
            for i in xrange(1,6):
                envenom_dps += self.get_dps_contribution(self.envenom_damage(average_ap, i), crit_rates['envenom'], attacks_per_second['envenom'][i])
            damage_breakdown['envenom'] = envenom_dps * self.vendetta_mult

        if 'venomous_wounds' in attacks_per_second:
            damage_breakdown['venomous_wounds'] = self.get_dps_contribution(self.venomous_wounds_damage(average_ap), crit_rates['venomous_wounds'], attacks_per_second['venomous_wounds']) * self.vendetta_mult

        if 'instant_poison' in attacks_per_second:
            damage_breakdown['instant_poison'] = self.get_dps_contribution(self.instant_poison_damage(average_ap), crit_rates['instant_poison'], attacks_per_second['instant_poison']) * self.vendetta_mult

        if 'deadly_poison' in attacks_per_second:
            damage_breakdown['deadly_poison'] = self.get_dps_contribution(self.deadly_poison_tick_damage(average_ap), crit_rates['deadly_poison'], attacks_per_second['deadly_poison']) * self.vendetta_mult

        for proc in damage_procs:
            damage_breakdown[proc.proc_name] = self.get_proc_damage_contribution(proc, attacks_per_second[proc.proc_name], current_stats)

        return damage_breakdown

    def get_mh_procs_per_second(self, proc, attacks_per_second, crit_rates):
        triggers_per_second = 0
        if proc.procs_off_auto_attacks():
            if proc.procs_off_crit_only():
                triggers_per_second += attacks_per_second['mh_autoattack_hits'] * crit_rates['mh_autoattacks']
            else:
                triggers_per_second += attacks_per_second['mh_autoattack_hits']
        if proc.procs_off_strikes():
            for ability in ('mutilate', 'backstab', 'revealing_strike', 'sinister_strike', 'ambush', 'hemorrhage'):
                if ability in attacks_per_second:
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

        if proc.is_ppm():
            return triggers_per_second * proc.ppm * self.stats.mh.speed / 60.
        else:
            return triggers_per_second * proc.proc_chance

    def get_oh_procs_per_second(self, proc, attacks_per_second, crit_rates):
        triggers_per_second = 0
        if proc.procs_off_auto_attacks():
            if proc.procs_off_crit_only():
                triggers_per_second += attacks_per_second['oh_autoattack_hits'] * crit_rates['oh_autoattacks']
            else:
                triggers_per_second += attacks_per_second['oh_autoattack_hits']
        if proc.procs_off_strikes():
            if 'mutilate' in attacks_per_second:
                if proc.procs_off_crit_only():
                    triggers_per_second += attacks_per_second['mutilate'] * crit_rates['mutilate']
                else:
                    triggers_per_second += attacks_per_second['mutilate']

        if proc.is_ppm():
            return triggers_per_second * proc.ppm * self.stats.oh.speed / 60.
        else:
            return triggers_per_second * proc.proc_chance

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

        if proc.is_ppm():
            if triggers_per_second == 0:
                return 0
            else:
                raise InputNotModeledException(_('PPMs that also proc off spells are not yet modeled.'))
        else:
            return triggers_per_second * proc.proc_chance

    def get_procs_per_second(self, proc, attacks_per_second, crit_rates):
        # TODO: Include damaging proc hits in figuring out how often everything else procs.
        if getattr(proc, 'mh_only', False):
            procs_per_second = self.get_mh_procs_per_second(proc, attacks_per_second, crit_rates)
        elif getattr(proc, 'oh_only', False):
            procs_per_second = self.get_oh_procs_per_second(proc, attacks_per_second, crit_rates)
        else:
            procs_per_second = self.get_mh_procs_per_second(proc, attacks_per_second, crit_rates) + self.get_oh_procs_per_second(proc, attacks_per_second, crit_rates) + self.get_other_procs_per_second(proc, attacks_per_second, crit_rates)

        return procs_per_second

    def set_uptime(self, proc, attacks_per_second, crit_rates):
        procs_per_second = self.get_procs_per_second(proc, attacks_per_second, crit_rates)

        if proc.icd:
            proc.uptime = proc.duration / (proc.icd + 1. / procs_per_second)
        else:
            # See http://elitistjerks.com/f31/t20747-advanced_rogue_mechanics_discussion/#post621369
            # for the derivation of this formula.
            if procs_per_second >= 1 and proc.duration >= 1:
                proc.uptime = proc.max_stacks
            else:
                q = 1 - procs_per_second
                Q = q ** proc.duration
                P = 1 - Q
                proc.uptime = P * (1 - P ** proc.max_stacks) / Q

    def update_with_damaging_proc(self, proc, attacks_per_second, crit_rates):
        if proc.stat == 'spell_damage':
            attacks_per_second[proc.proc_name] = self.get_procs_per_second(proc, attacks_per_second, crit_rates) * self.spell_hit_chance()
        elif proc.stat == 'physical_damage':
            attacks_per_second[proc.proc_name] = self.get_procs_per_second(proc, attacks_per_second, crit_rates) * self.one_hand_melee_hit_chance()

    def compute_damage(self, attack_counts_function):
        # TODO: Wierd procs.
        #
        # TODO: Crit cap
        #
        # TODO: Hit/Exp procs

        current_stats = {
            'agi': self.base_agility * self.agi_multiplier,
            'ap': self.stats.ap + 140,
            'crit': self.stats.crit,
            'haste': self.stats.haste,
            'mastery': self.stats.mastery
        }

        active_procs = []
        damage_procs = []

        for proc_info in self.stats.procs.get_all_procs_for_stat():
            if proc_info.stat in current_stats and not proc_info.is_ppm():
                active_procs.append(proc_info)
            if proc_info.stat in ('spell_damage', 'physical_damage'):
                damage_procs.append(proc_info)

        mh_landslide = self.stats.mh.landslide
        if mh_landslide:
            mh_landslide.mh_only = True
            active_procs.append(mh_landslide)

        mh_hurricane = self.stats.mh.hurricane
        if mh_hurricane:
            mh_hurricane.mh_only = True
            active_procs.append(mh_hurricane)

        oh_landslide = self.stats.oh.landslide
        if oh_landslide:
            oh_landslide.oh_only = True
            active_procs.append(oh_landslide)

        oh_hurricane = self.stats.oh.hurricane
        if oh_hurricane:
            oh_hurricane.oh_only = True
            active_procs.append(oh_hurricane)

        attacks_per_second, crit_rates = attack_counts_function(current_stats)

        while True:
            current_stats = {
                'agi': self.base_agility,
                'ap': self.stats.ap + 140,
                'crit': self.stats.crit,
                'haste': self.stats.haste,
                'mastery': self.stats.mastery
            }

            for proc in damage_procs:
                if not proc.icd:
                    self.update_with_damaging_proc(proc, attacks_per_second, crit_rates)

            for proc in active_procs:
                if not proc.icd:
                    self.set_uptime(proc, attacks_per_second, crit_rates)
                    current_stats[proc.stat] += proc.uptime * proc.value

            current_stats['agi'] *= self.agi_multiplier

            old_attacks_per_second = attacks_per_second
            attacks_per_second, crit_rates = attack_counts_function(current_stats)

            if self.are_close_enough(old_attacks_per_second, attacks_per_second):
                break

        for proc in active_procs:
            if proc.icd:
                self.set_uptime(proc, attacks_per_second, crit_rates)
                if proc.stat == 'agi':
                    current_stats[proc.stat] += proc.uptime * proc.value * self.agi_multiplier
                else:
                    current_stats[proc.stat] += proc.uptime * proc.value

        attacks_per_second, crit_rates = attack_counts_function(current_stats)

        for proc in damage_procs:
            self.update_with_damaging_proc(proc, attacks_per_second, crit_rates)

        return self.get_damage_breakdown(current_stats, attacks_per_second, crit_rates ,damage_procs)

    ###########################################################################
    # Assassination DPS functions
    ###########################################################################

    def init_assassination(self):
        # Call this before calling any of the assassination_dps functions
        # directly.  If you're just calling get_dps, you can ignore this as it
        # happens automatically; however, if you're going to pull a damage
        # breakdown or other sub-result, make sure to call this, as it
        # initializes many values that are needed to perform the calculations.

        if self.settings.cycle._cycle_type != 'assassination':
            raise InputNotModeledException(_('You must specify an assassination cycle to match your assassination spec.'))
        if self.stats.mh.type != 'dagger' or self.stats.oh.type != 'dagger':
            raise InputNotModeledException(_('Assassination modeling requires daggers in both hands'))

        if self.settings.mh_poison + self.settings.oh_poison not in ['ipdp', 'dpip']:
            raise InputNotModeledException(_('Assassination modeling requires instant poison on one weapon and deadly on the other'))

        # These talents have huge, hard-to-model implications on cycle and will
        # always be taken in any serious DPS build.  Hence, I'm not going to
        # worry about modeling them for the foreseeable future.
        if self.talents.master_poisoner != 1:
            raise InputNotModeledException(_('Assassination modeling requires one point in Master Poisoner'))
        if self.talents.cut_to_the_chase != 3:
            raise InputNotModeledException(_('Assassination modeling requires three points in Cut to the Chase'))

        self.set_constants()

        self.rupture_energy_cost = 25 / self.one_hand_melee_hit_chance()
        self.envenom_energy_cost = 35 / self.one_hand_melee_hit_chance()

        if self.talents.overkill:
            self.base_energy_regen += 60 / (180. + self.settings.response_time)

        if self.talents.cold_blood:
            self.bonus_energy_regen += 25./(120+self.settings.response_time)

        if self.talents.vendetta:
            if self.glyphs.vendetta:
                self.vendetta_mult = 1.06
            else:
                self.vendetta_mult = 1.05
        else:
            self.vendetta_mult = 1

    def assassination_dps_estimate(self):
        mutilate_dps = self.assassination_dps_estimate_mutilate() * (1 - self.settings.time_in_execute_range)
        backstab_dps = self.assassination_dps_estimate_backstab() * self.settings.time_in_execute_range
        return backstab_dps + mutilate_dps

    def assassination_dps_estimate_backstab(self):
        return sum(self.assassination_dps_breakdown_backstab().values())

    def assassination_dps_estimate_mutilate(self):
        return sum(self.assassination_dps_breakdown_mutilate().values())

    def assassination_dps_breakdown(self):
        mutilate_dps_breakdown = self.assassination_dps_breakdown_mutilate()
        backstab_dps_breakdown = self.assassination_dps_breakdown_backstab()

        mutilate_weight = 1 - self.settings.time_in_execute_range
        backstab_weight = self.settings.time_in_execute_range

        dps_breakdown = {}
        for source, quantity in mutilate_dps_breakdown.items():
            dps_breakdown[source] = quantity * mutilate_weight

        for source, quantity in backstab_dps_breakdown.items():
            if source in dps_breakdown:
                dps_breakdown[source] += quantity * backstab_weight
            else:
                dps_breakdown[source] = quantity * backstab_weight

        return dps_breakdown

    def assassination_dps_breakdown_mutilate(self):
        self.mutilate_energy_cost = 48 + 12 / self.one_hand_melee_hit_chance()
        if self.glyphs.mutilate:
            self.mutilate_energy_cost -= 5

        return self.compute_damage(self.assassination_attack_counts_mutilate)

    def assassination_dps_breakdown_backstab(self):
        return self.compute_damage(self.assassination_attack_counts_backstab)

    def assassination_attack_counts_mutilate(self, current_stats):
        base_melee_crit_rate = self.melee_crit_rate(agi=current_stats['agi'], crit=current_stats['crit'])
        base_spell_crit_rate = self.spell_crit_rate(crit=current_stats['crit'])

        haste_multiplier = self.stats.get_haste_multiplier_from_rating(current_stats['haste'])

        energy_regen = self.base_energy_regen * haste_multiplier
        energy_regen += self.bonus_energy_regen
        energy_regen_with_rupture = energy_regen + 1.5 * self.talents.venomous_wounds

        attack_speed_multiplier = self.base_speed_multiplier * haste_multiplier

        mutilate_crit_rate = base_melee_crit_rate + self.stats.gear_buffs.rogue_t11_2pc_crit_bonus() + .05 * self.talents.puncturing_wounds
        if mutilate_crit_rate > 1:
            mutilate_crit_rate = 1.

        crit_rates = {
            'mh_autoattacks': min(base_melee_crit_rate, self.dual_wield_mh_hit_chance() - self.GLANCE_RATE),
            'oh_autoattacks': min(base_melee_crit_rate, self.dual_wield_oh_hit_chance() - self.GLANCE_RATE),
            'mutilate': mutilate_crit_rate,
            'envenom': base_melee_crit_rate,
            'rupture_ticks': base_melee_crit_rate,
            'venomous_wounds': base_spell_crit_rate,
            'instant_poison': base_spell_crit_rate,
            'deadly_poison': base_spell_crit_rate
        }

        seal_fate_proc_rate = 1 - (1 - mutilate_crit_rate * .5 * self.talents.seal_fate) ** 2
        cp_per_mut = {2: 1 - seal_fate_proc_rate, 3: seal_fate_proc_rate}
        cp_distribution = self.get_cp_distribution_for_cycle(cp_per_mut, self.settings.cycle.min_envenom_size_mutilate)

        # This cycle need a *lot* of work, but in the interest of getting some
        # sort of numbers out of this, I'm going to go with ye olde cheap hack
        # for the moment.

        muts_per_finisher = 0
        cp_per_finisher = 0
        finisher_size_breakdown = [0, 0, 0, 0, 0, 0]
        for (cps, muts), probability in cp_distribution.items():
            muts_per_finisher += muts * probability
            cp_per_finisher += cps * probability
            finisher_size_breakdown[cps] += probability

        energy_for_rupture = muts_per_finisher * self.mutilate_energy_cost + self.rupture_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
        rupture_downtime = .5 * energy_for_rupture / energy_regen
        average_rupture_length = 2 * (3 + cp_per_finisher + 2 * self.glyphs.rupture)
        average_cycle_length = rupture_downtime + average_rupture_length

        energy_for_envenoms = average_rupture_length * energy_regen_with_rupture - .5 * energy_for_rupture
        envenom_energy_cost = muts_per_finisher * self.mutilate_energy_cost + self.envenom_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
        envenoms_per_cycle = energy_for_envenoms / envenom_energy_cost

        attacks_per_second = {}

        envenoms_per_second = envenoms_per_cycle / average_cycle_length
        attacks_per_second['rupture'] = 1 / average_cycle_length
        attacks_per_second['mutilate'] = (envenoms_per_second + attacks_per_second['rupture']) * muts_per_finisher

        if self.talents.cold_blood:
            envenoms_per_cold_blood = 120 * envenoms_per_second
            crit_rates['envenom'] = ((envenoms_per_cold_blood - 1) * crit_rates['envenom'] + 1) / envenoms_per_cold_blood

        attacks_per_second['envenom'] = [finisher_chance * envenoms_per_second for finisher_chance in finisher_size_breakdown]

        attacks_per_second['rupture_ticks'] = [0, 0, 0, 0, 0, 0]
        for i in xrange(1, 6):
            ticks_per_rupture = 3 + i + 2 * self.glyphs.rupture
            attacks_per_second['rupture_ticks'][i] = ticks_per_rupture * attacks_per_second['rupture'] * finisher_size_breakdown[i]

        total_rupture_ticks = sum(attacks_per_second['rupture_ticks'])
        attacks_per_second['venomous_wounds'] = total_rupture_ticks * .3 * self.talents.venomous_wounds * self.spell_hit_chance()

        attacks_per_second['mh_autoattacks'] = attack_speed_multiplier / self.stats.mh.speed
        attacks_per_second['oh_autoattacks'] = attack_speed_multiplier / self.stats.oh.speed

        attacks_per_second['mh_autoattack_hits'] = attacks_per_second['mh_autoattacks'] * self.dual_wield_mh_hit_chance()
        attacks_per_second['oh_autoattack_hits'] = attacks_per_second['oh_autoattacks'] * self.dual_wield_oh_hit_chance()

        total_mh_hits_per_second = attacks_per_second['mh_autoattack_hits'] + attacks_per_second['mutilate'] + envenoms_per_second + attacks_per_second['rupture']
        total_oh_hits_per_second = attacks_per_second['oh_autoattack_hits'] + attacks_per_second['mutilate']

        if self.settings.mh_poison == 'ip':
            ip_base_proc_rate = .3 * self.stats.mh.speed / 1.4
        else:
            ip_base_proc_rate = .3 * self.stats.oh.speed / 1.4

        ip_envenom_proc_rate = ip_base_proc_rate * 1.5

        dp_base_proc_rate = .5
        dp_envenom_proc_rate = dp_base_proc_rate + .15

        envenom_uptime = min(sum([(1+cps) * attacks_per_second['envenom'][cps] for cps in xrange(1,6)]), 1)
        avg_ip_proc_rate = ip_base_proc_rate * (1 - envenom_uptime) + ip_envenom_proc_rate * envenom_uptime
        avg_dp_proc_rate = dp_base_proc_rate * (1 - envenom_uptime) + dp_envenom_proc_rate * envenom_uptime

        if self.settings.mh_poison == 'ip':
            mh_poison_procs = avg_ip_proc_rate * total_mh_hits_per_second
            oh_poison_procs = avg_dp_proc_rate * total_oh_hits_per_second
        else:
            mh_poison_procs = avg_dp_proc_rate * total_mh_hits_per_second
            oh_poison_procs = avg_ip_proc_rate * total_oh_hits_per_second

        attacks_per_second['instant_poison'] = (mh_poison_procs + oh_poison_procs) * self.spell_hit_chance()
        attacks_per_second['deadly_poison'] = 1./3

        return attacks_per_second, crit_rates

    def assassination_attack_counts_backstab(self, current_stats):
        base_melee_crit_rate = self.melee_crit_rate(agi=current_stats['agi'], crit=current_stats['crit'])
        base_spell_crit_rate = self.spell_crit_rate(crit=current_stats['crit'])

        haste_multiplier = self.stats.get_haste_multiplier_from_rating(current_stats['haste'])

        energy_regen = self.base_energy_regen * haste_multiplier
        energy_regen += self.bonus_energy_regen
        energy_regen_with_rupture = energy_regen + 1.5 * self.talents.venomous_wounds

        attack_speed_multiplier = self.base_speed_multiplier * haste_multiplier

        backstab_crit_rate = base_melee_crit_rate + self.stats.gear_buffs.rogue_t11_2pc_crit_bonus() + .1 * self.talents.puncturing_wounds
        if backstab_crit_rate > 1:
            backstab_crit_rate = 1.

        crit_rates = {
            'mh_autoattacks': min(base_melee_crit_rate, self.dual_wield_mh_hit_chance() - self.GLANCE_RATE),
            'oh_autoattacks': min(base_melee_crit_rate, self.dual_wield_oh_hit_chance() - self.GLANCE_RATE),
            'backstab': backstab_crit_rate,
            'envenom': base_melee_crit_rate,
            'rupture_ticks': base_melee_crit_rate,
            'venomous_wounds': base_spell_crit_rate,
            'instant_poison': base_spell_crit_rate,
            'deadly_poison': base_spell_crit_rate
        }

        backstab_energy_cost = 48 + 12 / self.one_hand_melee_hit_chance()
        backstab_energy_cost -= 15 * self.talents.murderous_intent
        if self.glyphs.backstab:
            backstab_energy_cost -= 5 * backstab_crit_rate

        seal_fate_proc_rate = backstab_crit_rate * .5 * self.talents.seal_fate
        cp_per_backstab = {1: 1-seal_fate_proc_rate, 2: seal_fate_proc_rate}
        cp_distribution = self.get_cp_distribution_for_cycle(cp_per_backstab, self.settings.cycle.min_envenom_size_backstab)

        # This cycle need a *lot* of work, but in the interest of getting some
        # sort of numbers out of this, I'm going to go with ye olde cheap hack
        # for the moment.

        bs_per_finisher = 0
        cp_per_finisher = 0
        finisher_size_breakdown = [0, 0, 0, 0, 0, 0]
        for (cps, bs), probability in cp_distribution.items():
            bs_per_finisher += bs * probability
            cp_per_finisher += cps * probability
            finisher_size_breakdown[cps] += probability

        energy_for_rupture = bs_per_finisher * backstab_energy_cost + self.rupture_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
        rupture_downtime = .5 * energy_for_rupture / energy_regen
        average_rupture_length = 2 * (3 + cp_per_finisher + 2 * self.glyphs.rupture)
        average_cycle_length = rupture_downtime + average_rupture_length

        energy_for_envenoms = average_rupture_length * energy_regen_with_rupture - .5 * energy_for_rupture
        envenom_energy_cost = bs_per_finisher * backstab_energy_cost + self.envenom_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
        envenoms_per_cycle = energy_for_envenoms / envenom_energy_cost

        attacks_per_second = {}

        envenoms_per_second = envenoms_per_cycle / average_cycle_length
        attacks_per_second['rupture'] = 1 / average_cycle_length
        attacks_per_second['backstab'] = (envenoms_per_second + attacks_per_second['rupture']) * bs_per_finisher

        if self.talents.cold_blood:
            envenoms_per_cold_blood = 120 * envenoms_per_second
            crit_rates['envenom'] = ((envenoms_per_cold_blood - 1) * crit_rates['envenom'] + 1) / envenoms_per_cold_blood

        attacks_per_second['envenom'] = [finisher_chance * envenoms_per_second for finisher_chance in finisher_size_breakdown]

        attacks_per_second['rupture_ticks'] = [0, 0, 0, 0, 0, 0]
        for i in xrange(1, 6):
            ticks_per_rupture = 3 + i + 2 * self.glyphs.rupture
            attacks_per_second['rupture_ticks'][i] = ticks_per_rupture * attacks_per_second['rupture'] * finisher_size_breakdown[i]

        total_rupture_ticks = sum(attacks_per_second['rupture_ticks'])
        attacks_per_second['venomous_wounds'] = total_rupture_ticks * .3 * self.talents.venomous_wounds * self.spell_hit_chance()

        attacks_per_second['mh_autoattacks'] = attack_speed_multiplier / self.stats.mh.speed
        attacks_per_second['oh_autoattacks'] = attack_speed_multiplier / self.stats.oh.speed

        attacks_per_second['mh_autoattack_hits'] = attacks_per_second['mh_autoattacks'] * self.dual_wield_mh_hit_chance()
        attacks_per_second['oh_autoattack_hits'] = attacks_per_second['oh_autoattacks'] * self.dual_wield_oh_hit_chance()

        total_mh_hits_per_second = attacks_per_second['mh_autoattack_hits'] + attacks_per_second['backstab'] + envenoms_per_second + attacks_per_second['rupture']
        total_oh_hits_per_second = attacks_per_second['oh_autoattack_hits']

        if self.settings.mh_poison == 'ip':
            ip_base_proc_rate = .3 * self.stats.mh.speed / 1.4
        else:
            ip_base_proc_rate = .3 * self.stats.oh.speed / 1.4

        ip_envenom_proc_rate = ip_base_proc_rate * 1.5

        dp_base_proc_rate = .5
        dp_envenom_proc_rate = dp_base_proc_rate + .15

        envenom_uptime = min(sum([(1+cps) * attacks_per_second['envenom'][cps] for cps in xrange(1,6)]), 1)
        avg_ip_proc_rate = ip_base_proc_rate * (1 - envenom_uptime) + ip_envenom_proc_rate * envenom_uptime
        avg_dp_proc_rate = dp_base_proc_rate * (1 - envenom_uptime) + dp_envenom_proc_rate * envenom_uptime

        if self.settings.mh_poison == 'ip':
            mh_poison_procs = avg_ip_proc_rate * total_mh_hits_per_second
            oh_poison_procs = avg_dp_proc_rate * total_oh_hits_per_second
        else:
            mh_poison_procs = avg_dp_proc_rate * total_mh_hits_per_second
            oh_poison_procs = avg_ip_proc_rate * total_oh_hits_per_second

        attacks_per_second['instant_poison'] = (mh_poison_procs + oh_poison_procs) * self.spell_hit_chance()
        attacks_per_second['deadly_poison'] = 1./3

        return attacks_per_second, crit_rates
