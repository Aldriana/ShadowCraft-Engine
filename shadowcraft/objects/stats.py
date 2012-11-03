from shadowcraft.objects import procs
from shadowcraft.objects import proc_data
from shadowcraft.core import exceptions

class Stats(object):
    # For the moment, lets define this as raw stats from gear + race; AP is
    # only AP bonuses from gear and level.  Do not include multipliers like
    # Vitality and Sinister Calling; this is just raw stats.  See calcs page
    # rows 1-9 from my WotLK spreadsheets to see how these are typically
    # defined, though the numbers will need to updated for level 85.

    melee_hit_rating_conversion_values = {60:8.0, 70:12.6154, 80:26.232, 85:102.4457, 90:340.0}
    spell_hit_rating_conversion_values = {60:8.0, 70:12.6154, 80:26.232, 85:102.4457, 90:340.0}
    expertise_rating_conversion_values = {60:8.0, 70:12.6154, 80:26.232, 85:102.4457, 90:340.0}
    crit_rating_conversion_values = {60:14.0, 70:22.0769, 80:45.906, 85:179.28, 90:600.0}
    haste_rating_conversion_values = {60:10.0, 70:15.7692, 80:32.79, 85:128.057, 90:425.0}
    mastery_rating_conversion_values = {60:14, 70:22.0769, 80:45.906, 85:179.28, 90:600.0}
    pvp_power_rating_conversion_values = {60:1.0, 70:2.0, 80:4.0, 85:79.182, 90:265.0}
    pvp_resil_rating_conversion_values = {60:1.0, 70:2.0, 80:4.0, 85:79.98, 90:310.0}

    def __init__(self, mh, oh, procs, gear_buffs, str=0, agi=0, int=0, spirit=0, stam=0, ap=0, crit=0, hit=0, exp=0, haste=0, mastery=0, level=None, pvp_power=0, pvp_resil=0, pvp_target_armor=None):
        # This will need to be adjusted if at any point we want to support
        # other classes, but this is probably the easiest way to do it for
        # the moment.
        self.str = str
        self.agi = agi
        self.int = int
        self.spirit = spirit
        self.stam = stam
        self.ap = ap
        self.crit = crit
        self.hit = hit
        self.exp = exp
        self.haste = haste
        self.mastery = mastery
        self.mh = mh
        self.oh = oh
        self.procs = procs
        self.gear_buffs = gear_buffs
        self.level = level
        self.pvp_power = pvp_power
        self.pvp_resil = pvp_resil
        self.pvp_target_armor = pvp_target_armor

    def _set_constants_for_level(self):
        self.procs.level = self.level
        try:
            self.melee_hit_rating_conversion = self.melee_hit_rating_conversion_values[self.level]
            self.spell_hit_rating_conversion = self.spell_hit_rating_conversion_values[self.level]
            self.expertise_rating_conversion = self.expertise_rating_conversion_values[self.level]
            self.crit_rating_conversion = self.crit_rating_conversion_values[self.level]
            self.haste_rating_conversion = self.haste_rating_conversion_values[self.level]
            self.mastery_rating_conversion = self.mastery_rating_conversion_values[self.level]
            self.pvp_power_rating_conversion = self.pvp_power_rating_conversion_values[self.level]
            self.pvp_resil_rating_conversion = self.pvp_resil_rating_conversion_values[self.level]
        except KeyError:
            raise exceptions.InvalidLevelException(_('No conversion factor available for level {level}').format(level=self.level))

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'level' and value is not None:
            self._set_constants_for_level()
    
    def get_max_health(self, rating=None):
        if rating is None:
            rating = self.stam
        return rating * 14 - 260 + 146663 #assumed to be level 90 for now
    
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

    def get_spell_hit_from_rating(self, hit_rating=None, exp_rating=None):
        if hit_rating is None:
            hit_rating = self.hit
        if exp_rating is None:
            exp_rating = self.exp
        return hit_rating / (100 * self.spell_hit_rating_conversion) + exp_rating / (100 * self.expertise_rating_conversion)

    def get_crit_from_rating(self, rating=None):
        if rating is None:
            rating = self.crit
        return rating / (100 * self.crit_rating_conversion)

    def get_haste_multiplier_from_rating(self, rating=None):
        if rating is None:
            rating = self.haste
        return 1 + rating / (100 * self.haste_rating_conversion)
    
    def get_pvp_power_multiplier_from_rating(self, rating=None):
        if rating is None:
            rating = self.pvp_power
        return 1 + rating / (100 * self.pvp_power_rating_conversion)
    
    def get_pvp_resil_multiplier_from_rating(self, rating=None):
        if rating is None:
            rating = self.pvp_resil
        return 1 - 0.99 ** ( rating / self.pvp_power_rating_conversion ) + .4 # .4 is base resil

class Weapon(object):
    allowed_melee_enchants = proc_data.allowed_melee_enchants

    def __init__(self, damage, speed, weapon_type, enchant=None):
        self.speed = speed
        self.weapon_dps = damage * 1.0 / speed
        self.type = weapon_type
        if enchant is not None:
            self.set_enchant(enchant)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'type':
            self.set_normalization_speed()

    def set_normalization_speed(self):
        if self.type in ['gun', 'bow', 'crossbow']:
            self._normalization_speed = 2.8
        elif self.type in ['2h_sword', '2h_mace', '2h_axe', 'polearm']:
            self._normalization_speed = 3.3
        elif self.type == 'dagger':
            self._normalization_speed = 1.7
        else:
            self._normalization_speed = 2.4

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
    activated_boosts = {
        # Duration and cool down in seconds - name is mandatory for damage-on-use boosts
        'unsolvable_riddle':              {'stat': 'agi', 'value': 1605, 'duration': 20, 'cooldown': 120},
        'demon_panther':                  {'stat': 'agi', 'value': 1425, 'duration': 20, 'cooldown': 120},
        'skardyns_grace':                 {'stat': 'mastery', 'value': 1260, 'duration': 20, 'cooldown': 120},
        'heroic_skardyns_grace':          {'stat': 'mastery', 'value': 1425, 'duration': 20, 'cooldown': 120},
        'virmens_bite':                   {'stat': 'agi', 'value': 4000, 'duration': 25, 'cooldown': None}, #Cooldown = fight length
        'virmens_bite_prepot':            {'stat': 'agi', 'value': 4000, 'duration': 23, 'cooldown': None}, #guesstimate
        'potion_of_the_tolvir':           {'stat': 'agi', 'value': 1200, 'duration': 25, 'cooldown': None}, #Cooldown = fight length
        'potion_of_the_tolvir_prepot':    {'stat': 'agi', 'value': 1200, 'duration': 23, 'cooldown': None}, #Very rough guesstimate; actual modeling should be done with the opener sequence, alas, there's no such thing.
        'hyperspeed_accelerators':        {'stat': 'haste', 'value': 340, 'duration': 12, 'cooldown': 60},  #WotLK tinker
        'synapse_springs':                {'stat': 'varies', 'value': 'varies', 'duration': 10, 'cooldown': 60}, #Overwrite stat in the model for the highest of agi, str, int
        'tazik_shocker':                  {'stat': 'spell_damage', 'value': 4800, 'duration': 0, 'cooldown': 60, 'name': 'Tazik Shocker'},
        'lifeblood':                      {'stat': 'haste', 'value': 'varies', 'duration': 20, 'cooldown': 120},
        'heroic_jade_bandit_figurine':    {'stat': 'haste', 'value': 4059, 'duration': 15, 'cooldown': 60},
        'jade_bandit_figurine':           {'stat': 'haste', 'value': 3595, 'duration': 15, 'cooldown': 60},
        'lfr_jade_bandit_figurine':       {'stat': 'haste', 'value': 3184, 'duration': 15, 'cooldown': 60},
        'hawkmasters_talon':              {'stat': 'haste', 'value': 3595, 'duration': 15, 'cooldown': 60},
        'flashing_steel_talisman':        {'stat': 'agi', 'value': 4232, 'duration': 15, 'cooldown': 90},
        'gerps_perfect_arrow':            {'stat': 'agi', 'value': 3480, 'duration': 20, 'cooldown': 120},
        'ancient_petrified_seed':         {'stat': 'agi', 'value': 1277, 'duration': 15, 'cooldown': 60},
        'heroic_ancient_petrified_seed':  {'stat': 'agi', 'value': 1441, 'duration': 15, 'cooldown': 60},
        'rickets_magnetic_fireball':      {'stat': 'crit', 'value': 1700, 'duration': 20, 'cooldown': 120},
        'kiroptyric_sigil':               {'stat': 'agi', 'value': 2290, 'duration': 15, 'cooldown': 90},
        'heroic_kiroptyric_sigil':        {'stat': 'agi', 'value': 2585, 'duration': 15, 'cooldown': 90},  #Not available in-game
        'lfr_kiroptyric_sigil':           {'stat': 'agi', 'value': 2029, 'duration': 15, 'cooldown': 90},  #Not available in-game
    }

    other_gear_buffs = [
        'leather_specialization',       # Increase %stat by 5%
        'chaotic_metagem',              # Increase critical damage by 3%
        'rogue_t11_2pc',                # Increase crit chance for BS, Mut, SS by 5%
        'rogue_t12_2pc',                # Add 6% of melee crit damage as a fire DOT
        'rogue_t12_4pc',                # Increase crit/haste/mastery rating by 25% every TotT
        'rogue_t13_2pc',                # Decrease energy cost by 20% for 6secs every TotT
        'rogue_t13_4pc',                # ShD +2secs, AR +3secs, Vendetta +9secs
        'rogue_t13_legendary',          # Increase 45% damage on SS and RvS, used in case the rogue only equips the mh of a set.
        'rogue_t14_2pc',                # Venom Wound damage by 20%, Sinister Strike by 15%, Backstab by 10%
        'rogue_t14_4pc',                # Shadow Blades by +12s
        'mixology',
        'master_of_anatomy'
    ]

    allowed_buffs = frozenset(other_gear_buffs + activated_boosts.keys())

    def __init__(self, *args):
        for arg in args:
            if arg in self.allowed_buffs:
                setattr(self, arg, True)

    def __getattr__(self, name):
        # Any gear buff we haven't assigned a value to, we don't have.
        if name in self.allowed_buffs:
            return False
        object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'level':
            self._set_constants_for_level()

    def _set_constants_for_level(self):
        self.activated_boosts['synapse_springs']['value'] = self.tradeskill_bonus('synapse_springs')
        self.activated_boosts['lifeblood']['value'] = self.tradeskill_bonus('master_of_anatomy')

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

    def rogue_t12_2pc_damage_bonus(self):
        if self.rogue_t12_2pc:
            return .06
        else:
            return 0

    def rogue_t12_4pc_stat_bonus(self):
        if self.rogue_t12_4pc:
            return .25
        else:
            return 0

    def rogue_t13_2pc_cost_multiplier(self):
        if self.rogue_t13_2pc:
            return 1 / 1.05
        else:
            return 1

    def rogue_t14_2pc_damage_bonus(self, spell):
        if self.rogue_t14_2pc:
            bonus = {
                ('assassination', 'vw', 'venomous_wounds'): 0.2,
                ('combat', 'ss', 'sinister_strike'): 0.15,
                ('subtlety', 'bs', 'backstab'): 0.1
            }
            for spells in bonus.keys():
                if spell in spells:
                    return 1 + bonus[spells]
        return 1

    def rogue_t14_4pc_extra_time(self, is_combat=False):
        if is_combat:
            return self.rogue_t14_4pc * 6
        return self.rogue_t14_4pc * 12

    def leather_specialization_multiplier(self):
        if self.leather_specialization:
            return 1.05
        else:
            return 1

    def tradeskill_bonus(self, tradeskill='base'):
        # Hardcoded to use maxed tradeskills for the character level.
        tradeskills = ('skill', 'base', 'master_of_anatomy', 'lifeblood', 'synapse_springs')
        if self.level == 90:
            return (600, 320, 480, 2880, 2940)[tradeskills.index(tradeskill)]
        tradeskill_base_bonus = {
            (01, 60): (0, None, None, None, 0),
            (60, 70): (300, 9,   9,   70,   0),
            (70, 80): (375, 12,  12,  120,  0),
            (80, 85): (450, 20,  20,  240,  480),
            (85, 90): (525, 80,  80,  480,  480),
            (90, 95): (600, 320, 480, 2880, 2940)
        }

        for i, j in tradeskill_base_bonus.keys():
            if self.level in range(i, j):
                return tradeskill_base_bonus[(i, j)][tradeskills.index(tradeskill)]

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
