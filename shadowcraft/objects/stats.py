from shadowcraft.objects import procs
from shadowcraft.core import exceptions

class Stats(object):
    # For the moment, lets define this as raw stats from gear + race; AP is
    # only AP bonuses from gear and level.  Do not include multipliers like
    # Vitality and Sinister Calling; this is just raw stats.  See calcs page
    # rows 1-9 from my WotLK spreadsheets to see how these are typically
    # defined, though the numbers will need to updated for level 85.

    melee_hit_rating_conversion_values = {60:9.37931, 70:14.7905, 80:30.7548, 81:40.3836, 82:53.0304, 83:69.6653, 84:91.4738, 85:120.109001159667969}
    spell_hit_rating_conversion_values = {60:8, 70:12.6154, 80:26.232, 81:34.4448, 82:45.2318, 83:59.4204, 84:78.0218, 85:102.445999145507812}
    crit_rating_conversion_values = {60:14, 70:22.0769, 80:45.906, 81:60.2784, 82:79.1556, 83:103.986, 84:136.53799, 85:179.279998779296875}
    haste_rating_conversion_values = {60:10, 70:15.7692, 80:32.79, 81:43.056, 82:56.5397, 83:74.2755, 84:97.5272, 85:128.057006835937500}
    expertise_rating_conversion_values = {60:2.34483 * 4, 70:3.69761 * 4, 80:7.68869 * 4, 81:10.0959 * 4, 82:13.2576 * 4, 83:17.4163 * 4, 84:22.8685 * 4, 85:30.027200698852539 * 4}
    mastery_rating_conversion_values = {60:14, 70:22.0769, 80:45.906, 81:60.2784, 82:79.1556, 83:103.986, 84:136.53799, 85:179.279998779296875}

    def __init__(self, str, agi, ap, crit, hit, exp, haste, mastery, mh, oh, ranged, procs, gear_buffs, level=85):
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
        self.level = level

    def _set_constants_for_level(self):
        try:
            self.melee_hit_rating_conversion = self.melee_hit_rating_conversion_values[self.level]
            self.spell_hit_rating_conversion = self.spell_hit_rating_conversion_values[self.level]
            self.crit_rating_conversion = self.crit_rating_conversion_values[self.level]
            self.haste_rating_conversion = self.haste_rating_conversion_values[self.level]
            self.expertise_rating_conversion = self.expertise_rating_conversion_values[self.level]
            self.mastery_rating_conversion = self.mastery_rating_conversion_values[self.level]
        except KeyError:
            raise exceptions.InvalidLevelException(_('No conversion factor available for level {level}').format(level=self.level))
    
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'level':
            self._set_constants_for_level()

    def get_mastery_from_rating(self, rating=None):
        if rating is None:
            rating = self.mastery
        return 8 + rating / self.mastery_rating_conversion

    def get_melee_hit_from_rating(self, rating=None):
        if rating is None:
            rating = self.hit
        return rating / (100 * self.melee_hit_rating_conversion)

    def get_expertise_from_rating(self, rating=None):
        if rating is None:
            rating = self.exp
        return rating / (100 * self.expertise_rating_conversion)

    def get_spell_hit_from_rating(self, rating=None):
        if rating is None:
            rating = self.hit
        return rating / (100 * self.spell_hit_rating_conversion)

    def get_crit_from_rating(self, rating=None):
        if rating is None:
            rating = self.crit
        return rating / (100 * self.crit_rating_conversion)

    def get_haste_multiplier_from_rating(self, rating=None):
        if rating is None:
            rating = self.haste
        return 1 + rating / (100 * self.haste_rating_conversion)

class Weapon(object):
    allowed_melee_enchants = {  # Completely guessing at proc behavior.  Also at the proc name.
        'hurricane': {
            'stat': 'haste',
            'value': 450,
            'duration': 12,
            'icd': 0,
            'ppm': 1,
            'trigger': 'all_spells_and_attacks',
            'proc_name': 'Hurricane'
        },
        'landslide': {          # Completely guessing at proc behavior.
            'stat':'ap',
            'value': 1000,
            'duration': 12,
            'icd': 0,
            'ppm': 1,
            'trigger': 'all_attacks',
            'proc_name': 'Landslide'
        }
    }

    def __init__(self, damage, speed, weapon_type, enchant=None):
        self.speed = speed
        self.weapon_dps = damage * 1.0 / speed
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
            self.set_enchant(enchant)

    def set_enchant(self, enchant):
        if enchant == None:
            self.del_enchant()
        else:
            if self.is_melee():
                if enchant in self.allowed_melee_enchants:
                    self.del_enchant()
                    proc = procs.Proc(**self.allowed_melee_enchants[enchant])
                    setattr(self, enchant, proc)
                else:
                    raise exceptions.InvalidInputException(_('Enchant {enchant} is not allowed.').format(enchant=enchant))
            else:
                raise exceptions.InvalidInputException(_('Only melee weapons can be enchanted with {enchant}.').format(enchant=enchant))

    def del_enchant(self):
        for i in self.allowed_melee_enchants:
            if getattr(self, i):
                delattr(self, i)

    def __getattr__(self, name):
        # Any enchant we haven't assigned a value to, we don't have.
        if name in self.allowed_melee_enchants:
            return False
        object.__getattribute__(self, name)

    def is_melee(self):
        return not self.type in frozenset(['gun', 'bow', 'crossbow', 'thrown'])

    def damage(self, ap=0):
        return self.speed * (self.weapon_dps + ap / 14.)

    def normalized_damage(self, ap=0):
        return self.speed * self.weapon_dps + self._normalization_speed * ap / 14.

# Catch-all for non-proc gear based buffs (static or activated)
class GearBuffs(object):
    allowed_buffs = frozenset([
        'leather_specialization',       # Increase %stat by 5%
        'chaotic_metagem',              # Increase critical damage by 3%
        'rogue_t11_2pc',                # Increase crit chance for BS, Mut, SS by 5%
        'engineer_glove_enchant',
        'unsolvable_riddle',
        'demon_panther',
        'skardyns_grace',
        'heroic_skardyns_grace',
        'potion_of_the_tolvir',
        'lifeblood',
        'mixology',
        'master_of_anatomy',
    ])

    # Format is (stat, value, duration, cool down) - duration and cool down in seconds
    activated_boosts = {
        'unsolvable_riddle':        {'stat': 'agi', 'value': 1605, 'duration': 20, 'cooldown': 120},
        'demon_panther':            {'stat': 'agi', 'value': 1425, 'duration': 20, 'cooldown': 120},
        'skardyns_grace':           {'stat': 'mastery', 'value': 1260, 'duration': 20, 'cooldown': 120},
        'heroic_skardyns_grace':    {'stat': 'mastery', 'value': 1425, 'duration': 20, 'cooldown': 120},
        'potion_of_the_tolvir':     {'stat': 'agi', 'value': 1200, 'duration': 25, 'cooldown': None}, #Cooldown = fight length
        'engineer_glove_enchant':   {'stat': 'haste', 'value': 340, 'duration': 12, 'cooldown': 60},
        'lifeblood':                {'stat': 'haste', 'value': 480, 'duration': 20, 'cooldown': 120},
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

    def get_all_activated_boosts_for_stat(self, stat=None):
        boosts = []
        for boost in GearBuffs.activated_boosts:
            if getattr(self, boost) and (stat is None or GearBuffs.activated_boosts[boost]['stat'] == stat):
                boosts.append(GearBuffs.activated_boosts[boost])

        return boosts

    def get_all_activated_boosts(self):
        return self.get_all_activated_boosts_for_stat()

    #This is haste rating because the conversion to haste requires a level.
    #Too, if reported as a haste value, it must be added to the value from other rating correctly.
    #This does too, but reinforces the fact that it's rating.
    def get_all_activated_haste_rating_boosts(self):
        return self.get_all_activated_boosts_for_stat('haste')
