from calcs.rogue import RogueDamageCalculator

class AldrianasRogueDamageCalculator(RogueDamageCalculator):
    def get_dps(self):
        if self.talents.is_assassination_rogue():
            return self.assassination_dps_estimate()
        elif self.talents.is_combat_rogue():
            return self.combat_dps_estimate()
        elif self.talents.is_subtlety_rogue():
            return self.subtlety_dps_estimate()
        else:
            assert False # Add a real error message at some point.

    def assassination_dps_estimate(self):
        # In progress.
        return 0
