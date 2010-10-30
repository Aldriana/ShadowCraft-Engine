class Settings(object):
    # Settings object for AldrianasRogueDamageCalculator.

    def __init__(self, cycle, time_in_execute_range=.35, tricks_on_cooldown=True, response_time=.5, mh_poison = 'ip', oh_poison='dp'):
        self.cycle = cycle
        self.time_in_execute_range = time_in_execute_range
        self.tricks_on_cooldown = tricks_on_cooldown
        self.response_time = response_time
        self.mh_poison = mh_poison
        self.oh_poison = oh_poison


class Cycle(object):
    # Base class for cycle objects.  Can't think of anything that particularly
    # needs to go here yet, but it seems worth keeping options open in that
    # respect.

    # When subclassing, define _cycle_type to be one of 'assassination',
    # 'combat', or 'subtlety' - this is how the damage calculator makes sure
    # you have an appropriate cycle object to go with your talent trees, etc.
    _cycle_type = ''


class AssassinationCycle(Cycle):
    _cycle_type = 'assassination'

    def __init__(self, min_envenom_size_mutilate=4, min_rupture_size_mutilate=4, min_envenom_size_backstab=4, min_envenom_size_rupture=4)
        # Minimum number of combo points to spend on finishers of the given
        # type, during mutilate and backstab portions of the fight.  Rupture
        # will be done whenever we have that many CPs or more and rupture is
        # down; Envenom we will build until the condition is minimally
        # satisfied and then envenom.  That is: a 1+ envenom during Backstab
        # will always be 1 or 2 CPs, but an envenom can be as many as 5CPs if
        # you had been building for a larger envenom and happen to run out of
        # rupture uptime while at high CPs.  1+ rupture therefore represents
        # "keep Rupture up as much as possible, at the expense of trying to
        # make it any particular size".
        self.min_envenom_size_mutilate = min_envenom_size_mutilate
        self.min_rupture_size_mutilate = min_rupture_size_mutilate
        self.min_envenom_size_backstab = min_envenom_size_backstab
        self.min_rupture_size_backstab = min_rupture_size_backstab
