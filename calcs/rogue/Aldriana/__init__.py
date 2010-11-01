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

    def assassination_dps_breakdown_mutilate(self):
        mutilate_energy_cost = 48 + 12 / self.one_hand_melee_hit_chance()
        if self.glyphs.mutilate:
            mutilate_energy_cost -= 5

        mutilate_base_crit_rate = self.base_melee_crit_rate + self.stats.gear_buffs.rogue_t11_2pc_crit_bonus() + .05 * self.talents.assassination.puncturing_wounds
        if mutilate_base_crit_rate > 1:
            mutilate_base_crit_rate = 1.

        seal_fate_proc_rate = 1 - (1 - mutilate_base_crit_rate * .5 * self.talents.assassination.seal_fate) ** 2
        cp_per_mut = {2: 1 - seal_fate_proc_rate, 3: seal_fate_proc_rate}
        self.get_cp_distribution_for_cycle(cp_per_mut, self.settings.cycle.min_envenom_size_mutilate)

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
