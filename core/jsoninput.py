import json
from calcs.rogue.Aldriana import AldrianasRogueDamageCalculator
from calcs.rogue.Aldriana import settings
from core import exceptions
from objects import buffs
from objects import procs
from objects import race
from objects import stats
from objects.rogue import rogue_glyphs
from objects.rogue import rogue_talents

class InvalidJSONException(exceptions.InvalidInputException):
    pass

def from_json(json_string, character_class='rogue'):
    j = json.loads(json_string)
    try: 
        race_object = race.Race(str(j['race']), character_class=character_class)
        level = int(j['level'])
    
        s = j['settings']
        settings_type = s['type']
        if settings_type == 'assassination':
            # AssassinationCycle(self, min_envenom_size_mutilate=4, min_envenom_size_backstab=5, prioritize_rupture_uptime_mutilate=True, prioritize_rupture_uptime_backstab=True):
            c = s.get('cycle', {})
            cycle = settings.AssassinationCycle(c.get('min_envenom_size_mutilate', 4), c.get('min_envenom_size_backstab', 5),
                c.get('prioritize_rupture_uptime_mutilate', True), c.get('prioritize_rupture_uptime_backstab', True))
            # Settings(cycle, time_in_execute_range=.35, tricks_on_cooldown=True, response_time=.5, mh_poison='ip', oh_poison='dp', duration=300):
            settings_object = settings.Settings(cycle, s.get('time_in_execute_range', .35), s.get('tricks_on_cooldown', True),
                s.get('response_time', .5), s.get('mh_poison', 'ip'), s.get('oh_poison', 'dp'), s.get('duration', 300))
    
        stats_dict = j['stats']
        # Weapon(damage, speed, weapon_type, enchant=None):
        mh_dict = stats_dict['mh']
        mh = stats.Weapon(mh_dict['damage'], mh_dict['speed'], mh_dict['type'], mh_dict.get('enchant'))
        oh_dict = stats_dict['oh']
        oh = stats.Weapon(oh_dict['damage'], oh_dict['speed'], oh_dict['type'], oh_dict.get('enchant'))
        ranged_dict = stats_dict['ranged']
        ranged = stats.Weapon(ranged_dict['damage'], ranged_dict['speed'], ranged_dict['type'], ranged_dict.get('enchant'))
        procs_list = procs.ProcsList(*stats_dict['procs'])
        gear_buffs = stats.GearBuffs(*stats_dict['gear_buffs'])
        # Stats(str, agi, ap, crit, hit, exp, haste, mastery, mh, oh, ranged, procs, gear_buffs, level=85):
        def s(stat):
            return int(stats_dict[stat])
        stats_object = stats.Stats(s('str'), s('agi'), s('ap'), s('crit'), s('hit'), s('exp'), s('haste'), s('mastery'), 
            mh, oh, ranged, procs_list, gear_buffs, level)
        glyphs = rogue_glyphs.RogueGlyphs(*j['glyphs'])
        talents = rogue_talents.RogueTalents(*j['talents'])
        buffs_object = buffs.Buffs(*j['buffs'])
    except KeyError as e:
        raise InvalidJSONException(_("Missing required input {key}").format(key=str(e)))
    # Calculator(stats, talents, glyphs, buffs, race, settings=None, level=85):
    return AldrianasRogueDamageCalculator(stats_object, talents, glyphs, buffs_object, race_object, settings=settings_object, level=level)


if __name__ == '__main__':
    json_string = """{
        "level": 85, 
        "stats": {
            "str": 20,
            "agi": 4756, 
            "ap": 190, 
            "crit": 1022, 
            "hit": 1329, 
            "exp": 159, 
            "haste": 1291, 
            "mastery": 1713, 
            "gear_buffs": [
                "rogue_t11_2pc", 
                "leather_specialization", 
                "potion_of_the_tolvir", 
                "chaotic_metagem"
            ], 
            "procs": [
                "heroic_prestors_talisman_of_machination", 
                "fluid_death", 
                "rogue_t11_4pc"
            ], 
            "mh": {
                "type": "dagger", 
                "speed": 1.8, 
                "damage": 939.5, 
                "enchant": "landslide"
            },
            "oh": {
                "type": "dagger", 
                "speed": 1.3999999999999999, 
                "damage": 730.5, 
                "enchant": "landslide"
            }, 
            "ranged": {
                "type": "thrown", 
                "speed": 2.2000000000000002, 
                "damage": 1371.5
            }
        },
        "buffs": [
            "short_term_haste_buff", 
            "stat_multiplier_buff", 
            "crit_chance_buff", 
            "all_damage_buff", 
            "melee_haste_buff", 
            "attack_power_buff", 
            "str_and_agi_buff", 
            "armor_debuff", 
            "physical_vulnerability_debuff", 
            "spell_damage_debuff", 
            "spell_crit_debuff", 
            "bleed_damage_debuff", 
            "agi_flask", 
            "guild_feast"
        ], 
        "settings": {
            "type": "assassination", 
            "response_time": 1
        }, 
        "talents": [
            "0333230113022110321", 
            "0020000000000000000", 
            "2030030000000000000"
        ], 
        "race": "night_elf", 
        "glyphs": [
            "backstab", 
            "mutilate", 
            "rupture"
        ]
    }"""


    calculator = from_json(json_string)
    # Compute EP values.
    ep_values = calculator.get_ep().items()
    ep_values.sort(key=lambda entry: entry[1], reverse=True)
    max_len = max(len(entry[0]) for entry in ep_values)
    for value in ep_values:
        print value[0] + ':' + ' ' * (max_len - len(value[0])), value[1]

    print '---------'

    # Compute DPS Breakdown.
    dps_breakdown = calculator.get_dps_breakdown().items()
    dps_breakdown.sort(key=lambda entry: entry[1], reverse=True)
    max_len = max(len(entry[0]) for entry in dps_breakdown)
    total_dps = sum(entry[1] for entry in dps_breakdown)
    for entry in dps_breakdown:
        print entry[0] + ':' + ' ' * (max_len - len(entry[0])), entry[1]

    print '-' * (max_len + 15)

    print ' ' * (max_len + 1), total_dps, _("total damage per second.")

