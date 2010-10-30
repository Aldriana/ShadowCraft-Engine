class Stats(object):
    # For the moment, lets define this as raw stats from gear + race; AP is 
    # only AP bonuses from gear and level.  Do not include multipliers like
    # Vitality and Sinister Calling; this is just raw stats.  See calcs page
    # rows 1-9 from my WotLK spreadsheets to see how these are typically
    # defined, though the numbers will need to updated for level 85.

    DEFAULT_LEVEL = 85
    MELEE_HIT_RATING_CONVERSION = {85:120.109001159667969}
    SPELL_HIT_RATING_CONVERSION = {85:102.445999145507812}
    CRIT_RATING_CONVERSION = {85:179.279998779296875}
    HASTE_RATING_CONVERSION = {85:128.057006835937500}
    EXPERTISE_RATING_CONVERSION = {85:30.027200698852539 * 4}
    MASTERY_RATING_CONVERSION = {85:179.279998779296875}

    def __init__(self, str, agi, ap, crit, hit, exp, haste, mastery, mh, oh, ranged, procs):
        # This will need to be adjusted if at any point we want to support
        # other classes, but this is probably the easiest way to do it for
        # the moment.
        self.str = str
        self.agi = agi
        self.ap = ap
        self.crit = crit
        self.hit = hit
        self.exp = exp
        self.haste = haste
        self.mastery = mastery
        self.mh = mh
        self.oh = oh
        self.ranged = ranged
        self.procs = procs

    # As noted elsewhere, these asserts probably should be exceptions
    # once we have good agreement on how they will be caught/handled
    def get_mastery_from_rating(self, rating=None, level=DEFAULT_LEVEL):
        if level in self.MASTERY_RATING_CONVERSION:
            if rating is None:
                rating = self.mastery
            return 8 + rating / self.MASTERY_RATING_CONVERSION[level]
        else:
            assert False, "No conversion factor available for level %(level)d" % {'level': level}

    def get_melee_hit_from_rating(self, rating=None, level=DEFAULT_LEVEL):
        if level in self.MELEE_HIT_RATING_CONVERSION:
            if rating is None:
                rating = self.hit
            return rating / (100 * self.MELEE_HIT_RATING_CONVERSION[level])
        else:
            assert False, "No conversion factor available for level %(level)d" % {'level': level}

    def get_expertise_from_rating(self, rating=None, level=DEFAULT_LEVEL):
        if level in self.EXPERTISE_RATING_CONVERSION:
            if rating is None:
                rating = self.exp
            return rating / (100 * self.EXPERTISE_RATING_CONVERSION[level])
        else:
            assert False, "No conversion factor available for level %(level)d" % {'level': level}

    def get_spell_hit_from_rating(self, rating=None, level=DEFAULT_LEVEL):
        if level in self.SPELL_HIT_RATING_CONVERSION:
            if rating is None:
                rating = self.hit
            return rating / (100 * self.SPELL_HIT_RATING_CONVERSION[level])
        else:
            assert False, "No conversion factor available for level %(level)d" % {'level': level}

    def get_crit_from_rating(self, rating=None, level=DEFAULT_LEVEL):
        if level in self.CRIT_RATING_CONVERSION:
            if rating is None:
                rating = self.crit
            return rating / (100 * self.CRIT_RATING_CONVERSION[level])
        else:
            assert False, "No conversion factor available for level %(level)d" % {'level': level}

    def get_haste_multiplier_from_rating(self, rating=None, level=DEFAULT_LEVEL):
        if level in self.HASTE_RATING_CONVERSION:
            if rating is None:
                rating = self.haste
            return 1 + rating / (100 * self.HASTE_RATING_CONVERSION[level])
        else:
            assert False, "No conversion factor available for level %(level)d" % {'level': level}

class Weapon(object):
    def __init__(self, damage, speed, is_dagger=False, is_two_handed=False, is_thrown=False, is_ranged=False):
        self.average_damage =  damage
        self.speed = speed
        self.is_dagger = is_dagger
        self.is_two_handed = is_two_handed
        self.is_thrown = is_thrown
        self.is_ranged = is_ranged

        if is_thrown:
            self._normalization_speed = 2.1
        elif is_ranged:
            self._normalization_speed = 2.8
        elif is_two_handed:
            self._normalization_speed = 3.3
        elif is_dagger:
            self._normalization_speed = 1.7
        else:
            self._normalization_speed = 2.4

    def damage(self, ap=0):
        return self.average_damage + self.speed * ap/14.

    def normalized_damage(self, ap=0):
        return self.average_damage + self._normalization_speed * ap/14.

    def dps(self, ap=0):
        return self.average_damage / self.speed + ap/14.


class Procs(object):
    # For the moment I'm just going to take procs as a list of proc names;
    # we can worry about a more robust proc system later.
    #
    # Note that activated abilities (Eng gloves, etc.) should also go here -
    # this is the certified dumping ground for anything that's not a static
    # stat boost.  Which, now that I think about it, also includes metagems.
    # And set bonuses.  And racial abilities.  And some silly stuff like that. 
    # Probably should look into rewriting this in a more sensible fashion at
    # some point, but this will do for now.
    #
    # Will also need to build a decent list of procs to support at some point.
    allowed_procs = frozenset([
        'heroic_deaths_verdict',
        'heroic_sharpened_twilight_scale',
        'relentless_metagem',
        'chaotic_metagem'
    ])

    def __init__(self, *args):
        for arg in args:
            if arg in self.allowed_procs:
                setattr(self, arg, True)

    def __getattr__(self, name):
        # Any proc we haven't assigned a value to, we don't have.
        if name in self.allowed_procs:
            return False
        object.__getattribute__(self, name)
