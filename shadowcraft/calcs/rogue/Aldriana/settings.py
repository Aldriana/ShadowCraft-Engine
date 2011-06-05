class Settings(object):
    # Settings object for AldrianasRogueDamageCalculator.

    def __init__(self, cycle, time_in_execute_range=.35, tricks_on_cooldown=True, response_time=.5, mh_poison = 'ip', oh_poison='dp', duration=300):
        self.cycle = cycle
        self.time_in_execute_range = time_in_execute_range
        self.tricks_on_cooldown = tricks_on_cooldown
        self.response_time = response_time
        self.mh_poison = mh_poison
        self.oh_poison = oh_poison
        self.duration = duration


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

    allowed_values = (1,2,3,4,5)

    def __init__(self, min_envenom_size_mutilate=4, min_envenom_size_backstab=5, prioritize_rupture_uptime_mutilate=True, prioritize_rupture_uptime_backstab=True):
        assert min_envenom_size_mutilate in self.allowed_values
        self.min_envenom_size_mutilate = min_envenom_size_mutilate

        assert min_envenom_size_backstab in self.allowed_values
        self.min_envenom_size_backstab = min_envenom_size_backstab

        # There are two fundamental ways you can manage rupture; one is to
        # reapply with whatever CP you have as soon as you can after the old
        # rupture drops; we will call this priorotizing uptime over size.
        # The second is to use ruptures that are the same size as your
        # envenoms, which we will call prioritizing size over uptime.  True
        # means the first of these options; False means the second.  
        # There are theoretically other things you can do (say, 4+ envenom and
        # 5+ ruptures) but such things are significantly harder to model so I'm
        # not going to worry about them until we have reason to believe they're
        # actually better.
        self.prioritize_rupture_uptime_mutilate = prioritize_rupture_uptime_mutilate
        self.prioritize_rupture_uptime_backstab = prioritize_rupture_uptime_backstab


class CombatCycle(Cycle):
    _cycle_type = 'combat'

    def __init__(self, use_rupture=True, use_revealing_strike='sometimes', ksp_immediately=False):
        self.use_rupture = bool(use_rupture)
        self.use_revealing_strike = use_revealing_strike # Allowed values are 'always' (on all damaging finishers), 'sometimes' (only at 4 cp), and 'never' (guess).
        self.ksp_immediately = bool(ksp_immediately) # Determines whether to KSp the instant it comes off cool or wait until Bandit's Guile stacks up.'

class SubtletyCycle(Cycle):
    _cycle_type = 'subtlety'

    def __init__(self, raid_crits_per_second, clip_recuperate=False, use_hemorrhage='never'):
        self.raid_crits_per_second = raid_crits_per_second
        self.clip_recuperate = clip_recuperate # Determines if you clip the previous recuperate or wait for it to drop before reapplying.
        self.use_hemorrhage = use_hemorrhage # Allowed values are 'always' (main CP generator), 'never' (default to backstab), or a number denoting the interval in seconds between applications.
