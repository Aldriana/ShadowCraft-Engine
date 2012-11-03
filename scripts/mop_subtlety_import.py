# Simple test program to debug + play with subtlety models.
from os import path
import sys
from import_character import CharacterData
from char_info import charInfo 
#sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))

from shadowcraft.calcs.rogue.Aldriana import AldrianasRogueDamageCalculator
from shadowcraft.calcs.rogue.Aldriana import settings

from shadowcraft.objects import buffs
from shadowcraft.objects import race
from shadowcraft.objects import stats
from shadowcraft.objects import procs
from shadowcraft.objects import proc_data
from shadowcraft.objects import talents
from shadowcraft.objects import glyphs

from shadowcraft.core import i18n

# Set up language. Use 'en_US', 'es_ES', 'fr' for specific languages.
test_language = 'local'
i18n.set_language(test_language)

key = 1
while key < len(sys.argv):
    terms = sys.argv[key].split(':')
    charInfo[ terms[0] ] = terms[1]
    key += 1

print "Loading " + charInfo['name'] + " of " + charInfo['region'] + "-" + charInfo['realm'] + "\n"
character_data = CharacterData(charInfo['region'], charInfo['realm'], charInfo['name'], verbose=charInfo['verbose'])
character_data.do_import()


# Set up level/class/race
test_level = 90
test_race = race.Race(character_data.get_race())
test_class = 'rogue'

# Set up buffs.
test_buffs = buffs.Buffs(
        'short_term_haste_buff',
        'stat_multiplier_buff',
        'crit_chance_buff',
        'mastery_buff',
        'melee_haste_buff',
        'attack_power_buff',
        'armor_debuff',
        'physical_vulnerability_debuff',
        'spell_damage_debuff',
        'agi_flask_mop',
        'food_300_agi'
    )

# Set up weapons.

test_mh = stats.Weapon(*character_data.get_mh())
test_oh = stats.Weapon(*character_data.get_oh())

# Set up procs.
character_procs = character_data.get_procs()
character_procs_allowed = filter(lambda p: p in proc_data.allowed_procs, character_procs)

#not_allowed_procs = set(character_procs) - set(character_procs_allowed)
#print not_allowed_procs

test_procs = procs.ProcsList(*character_procs_allowed)

# Set up a calcs object..
lst = character_data.get_gear_stats()

# Set up gear buffs.
character_gear_buffs = character_data.get_gear_buffs() + ['leather_specialization', 'virmens_bite', 'virmens_bite_prepot']
if character_data.has_chaotic_metagem():
    character_gear_buffs.append('chaotic_metagem')
test_gear_buffs = stats.GearBuffs(*character_gear_buffs)

test_stats = stats.Stats(test_mh, test_oh, test_procs, test_gear_buffs, **lst)

# Initialize talents..
if charInfo['talents'] == None:
    charInfo['talents'] = character_data.get_talents()
test_talents = talents.Talents(charInfo['talents'], test_class, test_level)

# Set up glyphs.
glyph_list = character_data.get_glyphs()
test_glyphs = glyphs.Glyphs(test_class, *glyph_list)

# Set up settings.
raid_crits_per_second = 5
hemo_interval = 24 #'always', 'never', 24, 25, 26...
if not character_data.get_mh_type() == 'dagger' and not test_talents.shuriken_toss:
    if not hemo_interval == 'always':
        print "\nALERT: Viable dagger cycle not found, forced rotation to strictly Hemo \n"
    hemo_interval = 'always'
test_cycle = settings.SubtletyCycle(raid_crits_per_second, use_hemorrhage=hemo_interval)
test_settings = settings.Settings(test_cycle, response_time=.5, duration=360, dmg_poison='dp', utl_poison='lp', is_pvp=charInfo['pvp'],
                                  stormlash=charInfo['stormlash'], shiv_interval=charInfo['shiv'])

# Build a DPS object.
calculator = AldrianasRogueDamageCalculator(test_stats, test_talents, test_glyphs, test_buffs, test_race, test_settings, test_level)

# Compute EP values.
ep_values = calculator.get_ep()

# Compute DPS Breakdown.
dps_breakdown = calculator.get_dps_breakdown()
total_dps = sum(entry[1] for entry in dps_breakdown.items())
talent_ranks = calculator.get_talents_ranking()
heal_sum, heal_table = calculator.get_self_healing(dps_breakdown=dps_breakdown)


def max_length(dict_list):
    max_len = 0
    for i in dict_list:
        dict_values = i.items()
        if max_len < max(len(entry[0]) for entry in dict_values):
            max_len = max(len(entry[0]) for entry in dict_values)

    return max_len

def pretty_print(dict_list):
    max_len = max_length(dict_list)

    for i in dict_list:
        dict_values = i.items()
        dict_values.sort(key=lambda entry: entry[1], reverse=True)
        for value in dict_values:
            if ("{0:.2f}".format(float(value[1])/total_dps)) != '0.00':
                print value[0] + ':' + ' ' * (max_len - len(value[0])), str(value[1]) + ' ('+str( "{0:.2f}".format(100*float(value[1])/total_dps) )+'%)'
            else:
                print value[0] + ':' + ' ' * (max_len - len(value[0])), str(value[1])
        print '-' * (max_len + 15)

dicts_for_pretty_print = [
    ep_values,
    talent_ranks,
    heal_table,
    dps_breakdown
]
pretty_print(dicts_for_pretty_print)
print ' ' * (max_length(dicts_for_pretty_print) + 1), total_dps, _("total damage per second.")
