from calcs.rogue import RogueDamageCalculator

class AldrianasRogueDamageCalculator(RogueDamageCalculator):
    def get_dps(self):
        if self.talents.is_assassination_rogue():
            self.init_assassination()
            return self.assassination_dps_estimate()
        elif self.talents.is_combat_rogue():
            return self.combat_dps_estimate()
        elif self.talents.is_subtlety_rogue():
            return self.subtlety_dps_estimate()
        else:
            assert False # Add a real error message at some point.

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

    def init_assassination(self):
        # Call this before calling any of the assassination_dps functions
        # directly.  If you're just calling get_dps, you can ignore this as it
        # happens automatically; however, if you're going to pull a damage
        # breakdown or other sub-result, make sure to call this, as it 
        # initializes many values that are needed to perform the calculations.

        assert self.settings.cycle._cycle_type == 'assassination'
        assert self.stats.mh.type == 'dagger'
        assert self.stats.oh.type == 'dagger'

        self.rupture_energy_cost = 25 / self.one_hand_melee_hit_chance()
        self.envenom_energy_cost = 35 / self.one_hand_melee_hit_chance()

        self.baseline_energy_regen = 10 * self.stats.get_haste_multiplier_from_rating()
        self.energy_regen_rupture_up = self.baseline_energy_regen + 1.5 * self.talents.assassination.venomous_wounds

        self.base_agility = (self.stats.agi + self.buffs.buff_agi()) * self.stats.gear_buffs.leather_specialization_multiplier() + self.race.racial_agi
        self.base_agility *= self.buffs.stat_multiplier()
        self.base_melee_crit_rate = self.melee_crit_rate(self.base_agility)

        self.relentless_strikes_energy_return_per_cp = [0, 1.75, 3.5, 5][self.talents.subtlety.relentless_strikes]

        self.attack_speed_multiplier = 1.4 * self.buffs.melee_haste_multiplier() * self.stats.get_haste_multiplier_from_rating()

    def assassination_dps_breakdown_mutilate(self):
        mutilate_energy_cost = 48 + 12 / self.one_hand_melee_hit_chance()
        if self.glyphs.mutilate:
            mutilate_energy_cost -= 5

        mutilate_base_crit_rate = self.base_melee_crit_rate + self.stats.gear_buffs.rogue_t11_2pc_crit_bonus() + .05 * self.talents.assassination.puncturing_wounds
        if mutilate_base_crit_rate > 1:
            mutilate_base_crit_rate = 1.

        seal_fate_proc_rate = 1 - (1 - mutilate_base_crit_rate * .5 * self.talents.assassination.seal_fate) ** 2
        cp_per_mut = {2: 1 - seal_fate_proc_rate, 3: seal_fate_proc_rate}
        cp_distribution = self.get_cp_distribution_for_cycle(cp_per_mut, self.settings.cycle.min_envenom_size_mutilate)

        # This cycle need a *lot* of work, but in the interest of getting some
        # sort of numbers out of this, I'm going to go with ye olde cheap hack
        # for the moment.

        muts_per_finisher = 0
        cp_per_finisher = 0
        for (cps, muts), probability in cp_distribution.items():
            muts_per_finisher += muts * probability
            cp_per_finisher += cps * probability

        energy_for_rupture = muts_per_finisher * mutilate_energy_cost + self.rupture_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
        rupture_downtime = .5 * energy_for_rupture / self.baseline_energy_regen
        average_rupture_length = 2 * (3 + cp_per_finisher + 2 * self.glyphs.rupture)
        average_cycle_length = rupture_downtime + average_rupture_length

        energy_for_envenoms = average_rupture_length * self.energy_regen_rupture_up - .5 * energy_for_rupture
        envenom_energy_cost = muts_per_finisher * mutilate_energy_cost + self.envenom_energy_cost - cp_per_finisher * self.relentless_strikes_energy_return_per_cp
        envenoms_per_cycle = energy_for_envenoms / envenom_energy_cost

        envenoms_per_second = envenoms_per_cycle / average_cycle_length
        ruptures_per_second = 1 / average_cycle_length
        mutilates_per_second = (envenoms_per_second + ruptures_per_second) * muts_per_finisher

        ticks_per_rupture = average_rupture_length / 2
        venomous_wounds_per_second = ticks_per_rupture * ruptures_per_second * .3 * self.talents.assassination.venomous_wounds

        mh_autoattacks_per_second = self.attack_speed_multiplier / self.stats.mh.speed
        oh_autoattacks_per_second = self.attack_speed_multiplier / self.stats.oh.speed

        total_mh_hits_per_second = mh_autoattacks_per_second + mutilates_per_second + envenoms_per_second + ruptures_per_second
        total_oh_hits_per_second = oh_autoattacks_per_second + mutilates_per_second

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

        ip_per_second = mh_poison_procs + oh_poison_procs
        dp_per_second = 1./3

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
        self.get_cp_distribution_for_cycle(cp_per_backstab, self.settings.cycle.min_envenom_size_backstab)

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
