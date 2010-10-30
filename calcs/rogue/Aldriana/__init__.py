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
        assert self.stats.mh.is_dagger
        assert self.stats.oh.is_dagger

        self.rupture_energy_cost = 25 / self.one_hand_melee_hit_chance()
        self.envenom_energy_cost = 35 / self.one_hand_melee_hit_chance()

        self.baseline_energy_regen = 10 * self.stats.get_haste_multiplier_from_rating()

        self.base_agility = self.stats.agi + self.buffs.buff_agi() # Need racial agi

    def assassination_dps_breakdown_mutilate(self):
        mutilate_energy_cost = 48 + 12/self.one_hand_melee_hit_chance() 
        if self.glyphs.mutilate:
            mutilate_energy_cost -= 5

    def assassination_dps_breakdown_backstab(self):
        pass
