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

    def __init__(self, str, agi, ap, crit, hit, exp, haste, mastery, mh, oh, ranged, procs, gear_buffs):
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
        self.gear_buffs = gear_buffs

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
    allowed_melee_enchants = frozenset([
        'hurricane',
        'landslide'
    ])

    def __init__(self, damage, speed, weapon_type, enchant=None):
        self.speed = speed
        self.weapon_dps = damage/speed
        self.type = weapon_type

        if self.type == 'thrown':
            self._normalization_speed = 2.1
        elif self.type in ['gun', 'bow', 'crossbow']:
            self._normalization_speed = 2.8
        elif self.type in ['2h_sword', '2h_mace', '2h_axe', 'polearm']:
            self._normalization_speed = 3.3
        elif self.type == 'dagger':
            self._normalization_speed = 1.7
        else:
            self._normalization_speed = 2.4

        if enchant is not None:
            assert self.is_melee() and enchant in self.allowed_melee_enchants
            setattr(self, enchant, True)

    def __getattr__(self, name):
        # Any enchant we haven't assigned a value to, we don't have.
        if name in self.allowed_melee_enchants:
            return False
        object.__getattribute__(self, name)

    def is_melee(self):
        return not self.type in frozenset(['gun', 'bow', 'crossbow', 'thrown'])

    def damage(self, ap=0):
        return self.speed * (self.weapon_dps + ap/14.)

    def normalized_damage(self, ap=0):
        return self.speed * self.weapon_dps + self._normalization_speed * ap/14.

class Procs(object):
    # For the moment I'm just going to take procs as a list of proc names;
    # we can worry about a more robust proc system later.
    #
    # Activated racials moved to race.Race, gear-based buffs that aren't
    # static stat increases moved to stats.GearBuffs. -Rac
    #
    # Will also need to build a decent list of procs to support at some point.
    allowed_procs = frozenset([
        'rogue_t11_4pc',
        'darkmoon_card_hurricane',
        'unheeded_warning',
        'fluid_death',                      #stacks on-hit, should be a proc
        'essence_of_the_cyclone',
        'heroic_left_eye_of_rajh',
        'left_eye_of_rajh',
        'heroic_key_to_the_endless_chamber',
        'key_to_the_endless_chamber',
    ])

    #Format is (stat,value,duration,proc rate,trigger,ICD)
    #None should be used to indicate unknown values
    #Assumed heroic trinkets have same proc chance/ICD as non-heroic
    proc_data = {
        'essence_of_the_cyclone':                  ('crit_rating', 1926, 10, None, 'melee_or_ranged_attack', None),
        'heroic_left_eye_of_rajh':                 ('agi', 1710, 10, None, 'melee_or_ranged_crit', None),
        'left_eye_of_rajh':                        ('agi', 1512, 10, None, 'melee_or_ranged_crit', None),
        'heroic_key_to_the_endless_chamber':       ('agi', 1710, 15, .1, 'melee_or_ranged_attack', 75),
        'key_to_the_endless_chamber':              ('agi', 1290, 15, .1, 'melee_or_ranged_attack', 75),
        'prestors_talisman_of_machination':        ('haste_rating', 1926, 15, .1, 'melee_or_ranged_attack', 75),
        'heroic_prestors_talisman_of_machination': ('haste_rating', 2178, 15, .1, 'melee_or_ranged_attack', 75)
    }

    proc_triggers = frozenset([
        'melee_or_ranged_attack',
        'melee_or_ranged_crit',
        'auto_attack',
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

    def get_all_procs_for_stat(self,stat):
        procs = []
        for proc in Procs.proc_data:
            if getattr(self,proc) and (Procs.proc_data[proc][0] == stat):
                procs.append(Procs.proc_data[proc][1:])
        return procs

    def get_all_agi_procs(self):
        return self.get_all_procs_for_stat('agi')

    def get_all_crit_rating_procs(self):
        return self.get_all_procs_for_stat('crit_rating')

#Catch-all for non-proc gear based buffs (static or activated)
class GearBuffs(object):
    allowed_buffs = frozenset([
        'leather_specialization',       #Increase %stat by 5%
        'chaotic_metagem',              #Increase critical damage by 3%
        'rogue_t11_2pc',                #Increase crit chance for BS, Mut, SS by 5%
        'engineer_glove_enchant',
        'unsolvable_riddle',
        'demon_panther',
        'potion_of_the_tolvir'
    ])

    #Format is (stat, value, duration, cool down) - duration and cool down in seconds
    activated_boosts = {
        'unsolvable_riddle':        ('agi', 1605, 20, 120),
        'demon_panther':            ('agi', 1425, 20, 120),
        'potion_of_the_tolvir':     ('agi', 1200, 25, None),
        'engineer_glove_enchant':   ('haste_rating', 340, 12, 60)
    }

    def __init__(self, *args):
        for arg in args:
            if arg in self.allowed_buffs:
                setattr(self, arg, True)

    def __getattr__(self, name):
        # Any gear buff we haven't assigned a value to, we don't have.
        if name in self.allowed_buffs:
            return False
        object.__getattribute__(self, name)

    def metagem_crit_multiplier(self):
        if self.chaotic_metagem:
            return 1.03
        else:
            return 1

    def rogue_t11_2pc_crit_bonus(self):
        if self.rogue_t11_2pc:
            return .05
        else:
            return 0

    def leather_specialization_multiplier(self):
        if self.leather_specialization:
            return 1.05
        else:
            return 1

    def get_all_activated_agi_boosts(self):
        return self.get_all_activated_boosts_for_stat('agi')

    def get_all_activated_boosts_for_stat(self,stat):
        boosts = []
        for boost in GearBuffs.activated_boosts:
            if getattr(self,boost) and GearBuffs.activated_boosts[boost][0] == stat:
                boosts.append(GearBuffs.activated_boosts[boost][1:])

        return boosts

    #This is haste rating because the conversion to haste requires a level.
    #Too, if reported as a haste value, it must be added to the value from other rating correctly.
    #This does too, but reinforces the fact that it's rating.
    def get_all_activated_haste_rating_boosts(self):
        return self.get_all_activated_boosts_for_stat('haste_rating')

if __name__ == "__main__":
    test_buffs = GearBuffs('leather_specialization','unsolvable_riddle','demon_panther')
    print test_buffs.get_all_activated_haste_rating_boosts()
    print test_buffs.get_all_activated_agi_boosts()
    print test_buffs.leather_specialization_multiplier()
    print test_buffs.rogue_t11_2pc_crit_bonus()

    test_procs = Procs('unheeded_warning', 'essence_of_the_cyclone', 'left_eye_of_rajh')
    print test_procs.unheeded_warning
    print test_procs.fluid_death
    print test_procs.get_all_crit_rating_procs()
    print test_procs.get_all_agi_procs()
