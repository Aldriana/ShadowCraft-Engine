# Simple test program to debug + play with subtlety models.

from calcs.rogue.Aldriana import AldrianasRogueDamageCalculator
from calcs.rogue.Aldriana import settings

from objects import buffs
from objects import race
from objects import stats
from objects import procs
from objects.rogue import rogue_talents
from objects.rogue import rogue_glyphs

from core import i18n

# Set up language. Use 'en_US', 'es_ES', 'fr' for specific languages.
test_language = 'local'
i18n.set_language(test_language)

# Set up buffs.
test_buffs = buffs.Buffs(
        'short_term_haste_buff',
        'stat_multiplier_buff',
        'crit_chance_buff',
        'all_damage_buff',
        'melee_haste_buff',
        'attack_power_buff',
        'str_and_agi_buff',
        'armor_debuff',
        'physical_vulnerability_debuff',
        'spell_damage_debuff',
        'spell_crit_debuff',
        'bleed_damage_debuff',
        'agi_flask',
        'guild_feast'
    )

# Set up weapons.
test_mh = stats.Weapon(939.5, 1.8, 'dagger', 'landslide')
test_oh = stats.Weapon(730.5, 1.4, 'dagger', 'landslide')
test_ranged = stats.Weapon(1371.5, 2.2, 'thrown')

# Set up procs.
test_procs = procs.ProcsList('heroic_prestors_talisman_of_machination', 'fluid_death')

# Set up gear buffs.
test_gear_buffs = stats.GearBuffs('rogue_t11_2pc', 'leather_specialization', 'potion_of_the_tolvir')

# Set up a calcs object..
test_stats = stats.Stats(20, 4745, 190, 1100, 782, 754, 2116, 776, test_mh, test_oh, test_ranged, test_procs, test_gear_buffs)

# Initialize talents..
test_talents = rogue_talents.RogueTalents('0230030000000000000', '0020000000000000000', '0332031321310012321')

# Set up glyphs.
glyph_list = ['backstab', 'slice_and_dice', 'eviscerate']
test_glyphs = rogue_glyphs.RogueGlyphs(*glyph_list)

# Set up race.
test_race = race.Race('night_elf')

# Set up settings.
test_cycle = settings.SubtletyCycle(5)
test_settings = settings.Settings(test_cycle, response_time=1)

# Set up level 
test_level = 85

# Build a DPS object.
calculator = AldrianasRogueDamageCalculator(test_stats, test_talents, test_glyphs, test_buffs, test_race, test_settings, test_level)

# Compute EP values.
ep_values = calculator.get_ep().items()
ep_values.sort(key=lambda entry: entry[1], reverse=True)
max_len = max(len(entry[0]) for entry in ep_values)
for value in ep_values:
    print value[0] + ':' + ' ' * (max_len - len(value[0])), value[1]

print '---------'

# Compute talents ranking
talents_ranking, mandatory_talents = calculator.get_talents_ranking()
talents_ranking_values = talents_ranking.items()
talents_ranking_values.sort(key=lambda entry: entry[1], reverse=True)
max_len = max(len(entry[0]) for entry in talents_ranking_values)
for entry in talents_ranking_values:
    print entry[0] + ':' + ' ' * (max_len - len(entry[0])), entry[1]
for talent in mandatory_talents:
    print talent + ':' + ' ' * (max_len - len(talent)), _('imperative talent')

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

