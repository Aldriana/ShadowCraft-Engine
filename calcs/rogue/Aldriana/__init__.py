import gettext
import __builtin__

__builtin__._ = gettext.gettext

from calcs.rogue import RogueDamageCalculator
from core import exceptions


class InputsNotModeledException(exceptions.InvalidInputException):
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

    PRECISION_REQUIRED = 10 ** -10

    def are_close_enough(self, old_stats, new_stats):
        for stat in old_stats.keys():
            if abs(new_stats[stat] - old_stats[stat]) > self.PRECISION_REQUIRED:
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
            raise InputNotModeledException(_('You must specify an assassination cycle to match your assination spec.'))
        if self.stats.mh.type != 'dagger' or self.stats.oh.type != 'dagger':
            raise InputNotModeledException(_('Assassination modeling requires daggers in both hands'))

        if self.settings.mh_poison + self.settings.oh_poison not in ['ipdp', 'dpip']:
            raise InputNotModeledException(_('Assassination modeling requires instant poison on one weapon and deadly on the other'))

        # These talents have huge, hard-to-model implications on cycle and will
        # always be taken in any serious DPS build.  Hence, I'm not going to
        # worry about modeling them for the foreseeable future.
        if self.talents.assassination.master_poisoner != 1:
            raise InputNotModeledException(_('Assassination modeling requires one point in Master Poisoner'))
        if self.talents.assassination.cut_to_the_chase != 3:
            raise InputNotModeledException(_('Assassination modeling requires three points in Cut to the Chase'))

        self.rupture_energy_cost = 25 / self.one_hand_melee_hit_chance()
        self.envenom_energy_cost = 35 / self.one_hand_melee_hit_chance()

        self.base_energy_regen = 10
        if self.talents.assassination.overkill:
            self.base_energy_regen += 60 / (180. + self.settings.response_time)

        self.bonus_energy_regen = 0
        if self.settings.tricks_on_cooldown and not self.glyphs.tricks_of_the_trade:
            self.bonus_energy_regen -= 15./(30+self.settings.response_time)
        if self.talents.assassination.cold_blood:
            self.bonus_energy_regen += 25./(120+self.settings.response_time)

        self.base_agility = self.stats.agi + self.buffs.buff_agi() + self.race.racial_agi
        for value, duration, cooldown in self.stats.gear_buffs.get_all_activated_agi_boosts():
            if cooldown is not None:
                self.base_agility += (value * duration) * 1.0 / (cooldown + self.settings.response_time)
            else:
                self.base_agility += (value * duration) * 1.0 / self.settings.duration

        self.base_strength = self.stats.str + self.buffs.buff_str() + self.race.racial_str
        self.base_strength *= self.buffs.stat_multiplier()

        self.relentless_strikes_energy_return_per_cp = [0, 1.75, 3.5, 5][self.talents.subtlety.relentless_strikes]

        self.base_speed_multiplier = 1.4 * self.buffs.melee_haste_multiplier() * self.get_heroism_haste_multiplier()

        if self.talents.assassination.vendetta:
            if self.glyphs.vendetta:
                self.vendetta_mult = 1.06
            else:
                self.vendetta_mult = 1.05
        else:
            self.vendetta_mult = 1

        self.agi_multiplier = self.buffs.stat_multiplier() * self.stats.gear_buffs.leather_specialization_multiplier()

    def assassination_dps_estimate(self):
        return self.assassination_dps_estimate_mutilate()

        # Backstab DPS cycle temporarily disabled while I work on procs + refactoring.
        #
        # mutilate_dps = self.assassination_dps_estimate_mutilate() * (1 - self.settings.time_in_execute_range)
        # backstab_dps = self.assassination_dps_estimate_backstab() * self.settings.time_in_execute_range
        # return backstab_dps + mutilate_dps

    def assassination_dps_estimate_backstab(self):
        return sum(self.assassination_dps_breakdown_backstab().values())

    def assassination_dps_estimate_mutilate(self):
        return sum(self.assassination_dps_breakdown_mutilate().values())

    def assassination_dps_breakdown(self):
        return self.assassination_dps_breakdown_mutilate()

        # Backstab DPS cycle temporarily disabled while I work on procs + refactoring.
        """
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
        """

    def assassination_dps_breakdown_mutilate(self):
        mutilate_energy_cost = 48 + 12 / self.one_hand_melee_hit_chance()
        if self.glyphs.mutilate:
            mutilate_energy_cost -= 5

        current_stats = {
            'agi': self.base_agility * self.agi_multiplier,
            'ap': self.stats.ap + 140,
            'crit': self.stats.crit,
            'haste': self.stats.haste,
            'mastery': self.stats.mastery
        }

        active_procs = []

        for proc_info in self.stats.procs.get_all_procs_for_stat():
            if proc_info.stat in current_stats and not proc_info.is_ppm():
                active_procs.append(proc_info)

        while True:
            melee_crit_rate = self.melee_crit_rate(agi=current_stats['agi'], crit=current_stats['crit'])

            haste_multiplier = self.stats.get_haste_multiplier_from_rating(current_stats['haste'])

            energy_regen = self.base_energy_regen * haste_multiplier
            energy_regen += self.bonus_energy_regen
            energy_regen_with_rupture = energy_regen + 1.5 * self.talents.assassination.venomous_wounds

            attack_speed_multiplier = self.base_speed_multiplier * haste_multiplier

            mutilate_crit_rate = melee_crit_rate + self.stats.gear_buffs.rogue_t11_2pc_crit_bonus() + .05 * self.talents.assassination.puncturing_wounds
            if mutilate_crit_rate > 1:
                mutilate_crit_rate = 1.

            seal_fate_proc_rate = 1 - (1 - mutilate_crit_rate * .5 * self.talents.assassination.seal_fate) ** 2
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

            energy_for_rupture = muts_per_finisher * mutilate_energy_cost + self.rupture_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
            rupture_downtime = .5 * energy_for_rupture / energy_regen
            average_rupture_length = 2 * (3 + cp_per_finisher + 2 * self.glyphs.rupture)
            average_cycle_length = rupture_downtime + average_rupture_length

            energy_for_envenoms = average_rupture_length * energy_regen_with_rupture - .5 * energy_for_rupture
            envenom_energy_cost = muts_per_finisher * mutilate_energy_cost + self.envenom_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
            envenoms_per_cycle = energy_for_envenoms / envenom_energy_cost

            envenoms_per_second = envenoms_per_cycle / average_cycle_length
            ruptures_per_second = 1 / average_cycle_length
            mutilates_per_second = (envenoms_per_second + ruptures_per_second) * muts_per_finisher

            envenom_size_breakdown = [finisher_chance * envenoms_per_second for finisher_chance in finisher_size_breakdown]
            rupture_tick_counts = [0, 0, 0, 0, 0, 0]
            for i in xrange(1, 6):
                ticks_per_rupture = 4 + i + 2 * self.glyphs.rupture
                rupture_tick_counts[i] = ticks_per_rupture * ruptures_per_second * finisher_size_breakdown[i]

            total_rupture_ticks = sum(rupture_tick_counts)
            venomous_wounds_per_second = total_rupture_ticks * .3 * self.talents.assassination.venomous_wounds * self.spell_hit_chance()

            mh_autoattacks_per_second = attack_speed_multiplier / self.stats.mh.speed
            oh_autoattacks_per_second = attack_speed_multiplier / self.stats.oh.speed

            mh_autoattack_hits_per_second = mh_autoattacks_per_second * self.dual_wield_mh_hit_chance()
            oh_autoattack_hits_per_second = oh_autoattacks_per_second * self.dual_wield_oh_hit_chance()

            total_mh_hits_per_second = mh_autoattack_hits_per_second + mutilates_per_second + envenoms_per_second + ruptures_per_second
            total_oh_hits_per_second = oh_autoattack_hits_per_second + mutilates_per_second
    
            if self.settings.mh_poison == 'ip':
                ip_base_proc_rate = .3 * self.stats.mh.speed / 1.4
            else:
                ip_base_proc_rate = .3 * self.stats.oh.speed / 1.4
    
            ip_envenom_proc_rate = ip_base_proc_rate * 1.5
    
            dp_base_proc_rate = .5
            dp_envenom_proc_rate = dp_base_proc_rate * 1.5
    
            envenom_uptime = min(envenoms_per_second * (cp_per_finisher + 1), 1)
            avg_ip_proc_rate = ip_base_proc_rate * (1 - envenom_uptime) + ip_envenom_proc_rate * envenom_uptime
            avg_dp_proc_rate = dp_base_proc_rate * (1 - envenom_uptime) + dp_envenom_proc_rate * envenom_uptime
    
            if self.settings.mh_poison == 'ip':
                mh_poison_procs = avg_ip_proc_rate * total_mh_hits_per_second
                oh_poison_procs = avg_dp_proc_rate * total_oh_hits_per_second
            else:
                mh_poison_procs = avg_dp_proc_rate * total_mh_hits_per_second
                oh_poison_procs = avg_ip_proc_rate * total_oh_hits_per_second

            ip_per_second = (mh_poison_procs + oh_poison_procs) * self.spell_hit_chance()
            dp_per_second = 1./3

            old_stats = current_stats

            current_stats = {
                'agi': self.base_agility,
                'ap': self.stats.ap + 140,
                'crit': self.stats.crit,
                'haste': self.stats.haste,
                'mastery': self.stats.mastery
            }

            # TODO: We're not accounting for procs with ICDs correctly here -
            # they're increasing their own proc rate, which is clearly bad.
            # But this will do for the first round of estimates.
            #
            # TODO: Crit procs aren't yet modeled.  Partly because the proc
            # object isn't really exposing that functionality yet.
            #
            # TODO: Weapon enchants
            #
            # TODO: Damage Procs
            #
            # TODO: Wierd procs.
            for proc in active_procs:
                triggers_per_second = 0
                if proc.procs_off_auto_attacks():
                    triggers_per_second += mh_autoattack_hits_per_second + oh_autoattack_hits_per_second
                if proc.procs_off_strikes():
                    triggers_per_second += 2 * mutilates_per_second + envenoms_per_second
                if proc.procs_off_harmful_spells():
                    triggers_per_second += ip_per_second + venomous_wounds_per_second
                if proc.procs_off_periodic_spell_damage():
                    triggers_per_second += dp_per_second
                if proc.procs_off_bleeds():
                    triggers_per_second += total_rupture_ticks
                if proc.procs_off_apply_debuff():
                    triggers_per_second += ruptures_per_second

                if proc.icd:
                    proc.uptime = proc.duration / (proc.icd + 1. / (triggers_per_second * proc.proc_chance))
                else:
                    # See http://elitistjerks.com/f31/t20747-advanced_rogue_mechanics_discussion/#post621369
                    # for the derivation of this formula.
                    q = 1 - proc.proc_chance
                    Q = q ** (proc.duration * triggers_per_second)
                    P = 1 - Q
                    proc.uptime = P * (1 - P ** proc.max_stacks) / Q

            for proc in active_procs:
                current_stats[proc.stat] += proc.uptime * proc.value

            current_stats['agi'] *= self.agi_multiplier

            if self.are_close_enough(old_stats, current_stats):
                break

        average_ap = current_stats['ap'] + 2 * current_stats['agi'] + self.base_strength
        average_ap *= self.buffs.attack_power_multiplier()

        spell_crit_rate = self.spell_crit_rate(current_stats['crit'])

        damage_breakdown = {}

        (mh_base_damage, mh_crit_damage) = self.mh_damage(average_ap)
        glance_rate = .24
        mh_crit_rate = min(self.dual_wield_mh_hit_chance() - glance_rate, melee_crit_rate)
        mh_hit_rate = self.dual_wield_mh_hit_chance() - glance_rate - mh_crit_rate
        average_mh_hit = glance_rate * .75 * mh_base_damage + mh_hit_rate * mh_base_damage + mh_crit_rate * mh_crit_damage
        mh_dps = average_mh_hit * mh_autoattacks_per_second

        (oh_base_damage, oh_crit_damage) = self.oh_damage(average_ap)
        glance_rate = .24
        oh_crit_rate = min(self.dual_wield_oh_hit_chance() - glance_rate, melee_crit_rate)
        oh_hit_rate = self.dual_wield_oh_hit_chance() - glance_rate - oh_crit_rate
        average_oh_hit = glance_rate * .75 * oh_base_damage + oh_hit_rate * oh_base_damage + oh_crit_rate * oh_crit_damage
        oh_dps = average_oh_hit * oh_autoattacks_per_second

        damage_breakdown['autoattack'] = (mh_dps + oh_dps) * self.vendetta_mult

        mh_mutilate_dps = self.get_dps_contribution(self.mh_mutilate_damage(average_ap), mutilate_crit_rate, mutilates_per_second)
        oh_mutilate_dps = self.get_dps_contribution(self.oh_mutilate_damage(average_ap), mutilate_crit_rate, mutilates_per_second)
        damage_breakdown['mutilate'] = (mh_mutilate_dps + oh_mutilate_dps) * self.vendetta_mult

        rupture_dps = 0
        for i in xrange(1,6):
            rupture_dps += self.get_dps_contribution(self.rupture_tick_damage(average_ap, i), melee_crit_rate, rupture_tick_counts[i])
        damage_breakdown['rupture'] = rupture_dps * self.vendetta_mult

        envenom_dps = 0
        envenom_crit_rate = melee_crit_rate
        if self.talents.assassination.cold_blood:
            envenoms_per_cold_blood = 120 * envenoms_per_second
            envenom_crit_rate = ((envenoms_per_cold_blood - 1) * envenom_crit_rate + 1) / envenoms_per_cold_blood

        for i in xrange(1,6):
            envenom_dps += self.get_dps_contribution(self.envenom_damage(average_ap, i), envenom_crit_rate, envenom_size_breakdown[i])
        damage_breakdown['envenom'] = envenom_dps * self.vendetta_mult

        damage_breakdown['venomous_wounds'] = self.get_dps_contribution(self.venomous_wounds_damage(average_ap), spell_crit_rate, venomous_wounds_per_second) * self.vendetta_mult
        damage_breakdown['instant_poison'] = self.get_dps_contribution(self.instant_poison_damage(average_ap), spell_crit_rate, ip_per_second) * self.vendetta_mult
        damage_breakdown['deadly_poison'] = self.get_dps_contribution(self.deadly_poison_tick_damage(average_ap), spell_crit_rate, dp_per_second) * self.vendetta_mult

        return damage_breakdown

    def assassination_dps_breakdown_backstab(self):
        backstab_base_crit_rate = self.base_melee_crit_rate + self.stats.gear_buffs.rogue_t11_2pc_crit_bonus() + .1 * self.talents.assassination.puncturing_wounds
        if backstab_base_crit_rate > 1:
            backstab_base_crit_rate = 1

        backstab_energy_cost = 48 + 12 / self.one_hand_melee_hit_chance()
        backstab_energy_cost -= 15 * self.talents.assassination.murderous_intent
        if self.glyphs.backstab:
            backstab_energy_cost -= 5 * backstab_base_crit_rate

        seal_fate_proc_rate = backstab_base_crit_rate * .5 * self.talents.assassination.seal_fate
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
        rupture_downtime = .5 * energy_for_rupture / self.baseline_energy_regen
        average_rupture_length = 2 * (3 + cp_per_finisher + 2 * self.glyphs.rupture)
        average_cycle_length = rupture_downtime + average_rupture_length

        energy_for_envenoms = average_rupture_length * self.energy_regen_rupture_up - .5 * energy_for_rupture
        envenom_energy_cost = bs_per_finisher * backstab_energy_cost + self.envenom_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
        envenoms_per_cycle = energy_for_envenoms / envenom_energy_cost

        envenoms_per_second = envenoms_per_cycle / average_cycle_length
        ruptures_per_second = 1 / average_cycle_length
        backstabs_per_second = (envenoms_per_second + ruptures_per_second) * bs_per_finisher

        envenom_size_breakdown = [finisher_chance * envenoms_per_second for finisher_chance in finisher_size_breakdown]
        rupture_tick_counts = [0, 0, 0, 0, 0, 0]
        for i in xrange(1, 6):
            ticks_per_rupture = 4 + i + 2 * self.glyphs.rupture
            rupture_tick_counts[i] = ticks_per_rupture * ruptures_per_second * finisher_size_breakdown[i]

        total_rupture_ticks = sum(rupture_tick_counts)
        venomous_wounds_per_second = total_rupture_ticks * .3 * self.talents.assassination.venomous_wounds * self.spell_hit_chance()

        mh_autoattacks_per_second = self.attack_speed_multiplier / self.stats.mh.speed
        oh_autoattacks_per_second = self.attack_speed_multiplier / self.stats.oh.speed

        total_mh_hits_per_second = mh_autoattacks_per_second * self.dual_wield_mh_hit_chance() + backstabs_per_second + envenoms_per_second + ruptures_per_second
        total_oh_hits_per_second = oh_autoattacks_per_second * self.dual_wield_oh_hit_chance()

        if self.settings.mh_poison == 'ip':
            ip_base_proc_rate = .3 * self.stats.mh.speed / 1.4
        else:
            ip_base_proc_rate = .3 * self.stats.oh.speed / 1.4

        ip_envenom_proc_rate = ip_base_proc_rate * 1.5

        dp_base_proc_rate = .5
        dp_envenom_proc_rate = dp_base_proc_rate * 1.5

        envenom_uptime = min(envenoms_per_second * (cp_per_finisher + 1), 1)
        avg_ip_proc_rate = ip_base_proc_rate * (1 - envenom_uptime) + ip_envenom_proc_rate * envenom_uptime
        avg_dp_proc_rate = dp_base_proc_rate * (1 - envenom_uptime) + dp_envenom_proc_rate * envenom_uptime

        if self.settings.mh_poison == 'ip':
            mh_poison_procs = avg_ip_proc_rate * total_mh_hits_per_second
            oh_poison_procs = avg_dp_proc_rate * total_oh_hits_per_second
        else:
            mh_poison_procs = avg_dp_proc_rate * total_mh_hits_per_second
            oh_poison_procs = avg_ip_proc_rate * total_oh_hits_per_second

        ip_per_second = (mh_poison_procs + oh_poison_procs) * self.spell_hit_chance()
        dp_per_second = 1./3

        damage_breakdown = {}

        (mh_base_damage, mh_crit_damage) = self.mh_damage(self.base_ap)
        glance_rate = .24
        mh_crit_rate = min(self.dual_wield_mh_hit_chance() - glance_rate, self.base_melee_crit_rate)
        mh_hit_rate = self.dual_wield_mh_hit_chance() - glance_rate - mh_crit_rate
        average_mh_hit = glance_rate * .75 * mh_base_damage + mh_hit_rate * mh_base_damage + mh_crit_rate * mh_crit_damage
        mh_dps = average_mh_hit * mh_autoattacks_per_second

        (oh_base_damage, oh_crit_damage) = self.oh_damage(self.base_ap)
        glance_rate = .24
        oh_crit_rate = min(self.dual_wield_oh_hit_chance() - glance_rate, self.base_melee_crit_rate)
        oh_hit_rate = self.dual_wield_oh_hit_chance() - glance_rate - oh_crit_rate
        average_oh_hit = glance_rate * .75 * oh_base_damage + oh_hit_rate * oh_base_damage + oh_crit_rate * oh_crit_damage
        oh_dps = average_oh_hit * oh_autoattacks_per_second

        damage_breakdown['autoattack'] = (mh_dps + oh_dps) * self.vendetta_mult
        damage_breakdown['backstab'] = self.get_dps_contribution(self.backstab_damage(self.base_ap), backstab_base_crit_rate, backstabs_per_second) * self.vendetta_mult

        rupture_dps = 0
        for i in xrange(1,6):
            rupture_dps += self.get_dps_contribution(self.rupture_tick_damage(self.base_ap, i), self.base_melee_crit_rate, rupture_tick_counts[i])
        damage_breakdown['rupture'] = rupture_dps * self.vendetta_mult

        envenom_dps = 0
        envenom_crit_rate = self.base_melee_crit_rate
        if self.talents.assassination.cold_blood:
            envenoms_per_cold_blood = 120 * envenoms_per_second
            envenom_crit_rate = ((envenoms_per_cold_blood - 1) * envenom_crit_rate + 1) / envenoms_per_cold_blood

        for i in xrange(1,6):
            envenom_dps += self.get_dps_contribution(self.envenom_damage(self.base_ap, i), envenom_crit_rate, envenom_size_breakdown[i])
        damage_breakdown['envenom'] = envenom_dps * self.vendetta_mult

        damage_breakdown['venomous_wounds'] = self.get_dps_contribution(self.venomous_wounds_damage(self.base_ap), self.spell_crit_rate(), venomous_wounds_per_second) * self.vendetta_mult
        damage_breakdown['instant_poison'] = self.get_dps_contribution(self.instant_poison_damage(self.base_ap), self.spell_crit_rate(), ip_per_second) * self.vendetta_mult
        damage_breakdown['deadly_poison'] = self.get_dps_contribution(self.deadly_poison_tick_damage(self.base_ap), self.spell_crit_rate(), dp_per_second) * self.vendetta_mult

        return damage_breakdown

    def get_cp_distribution_for_cycle(self, cp_distribution_per_move, target_cp_quantity):
        cur_min_cp = 0
        ruthlessness_chance = self.talents.assassination.ruthlessness * .2
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
