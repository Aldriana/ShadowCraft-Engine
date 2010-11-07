# This program basically exists to give a sample implementation using the
# framework that's been developed, and to allow me to test and debug my
# calculations as I go along.  At some point a more formal/organized test
# framework should be written - particularly if anyone else ever wants to build
# off this - but for the moment, this will suffice.

from calcs.rogue.Aldriana import AldrianasRogueDamageCalculator
from calcs.rogue.Aldriana import settings

from objects import buffs
from objects import race
from objects import stats
from objects.rogue import rogue_talents
from objects.rogue import rogue_glyphs


# Set up buffs and make sure things at least vaguely work.
test_buffs = buffs.Buffs(
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

assert test_buffs.crit_chance_buff
assert not test_buffs.short_term_haste_buff

# Set up weapons and make sure things at least vaguely work.
test_mh = stats.Weapon(737, 1.8, 'dagger', 'hurricane')
test_oh = stats.Weapon(573, 1.4, 'dagger', 'landslide')
test_ranged = stats.Weapon(1104, 2.0, 'thrown')

assert test_mh._normalization_speed == 1.7
assert test_oh._normalization_speed == 1.7
assert test_ranged._normalization_speed == 2.1
assert test_mh.hurricane
assert not test_oh.hurricane

# Set up procs and make sure things at least vaguely work.
test_procs = stats.Procs('darkmoon_card_hurricane')

assert test_procs.darkmoon_card_hurricane
assert not test_procs.fluid_death

# Set up gear buffs and make sure things at leat vaguely work
test_gear_buffs = stats.GearBuffs('chaotic_metagem', 'leather_specialization')
assert test_gear_buffs.chaotic_metagem
assert not test_gear_buffs.rogue_t11_2pc

# Set up a calcs object and make sure things at least vaguely work.  Stat
# values are currently pulled from a level 80 gear set, which I will fix as
# soon as I can find or put together a decent estimate of stats for, say, level
# 85 heroic dungeon gear.

test_stats = stats.Stats(20, 3485, 190, 1517, 1086, 641, 899, 666, test_mh, test_oh, test_ranged, test_procs, test_gear_buffs)

assert test_stats.mastery == 666


# Initialize talents and test.

test_talents = rogue_talents.RogueTalents('0333230113022110321', '0020000000000000000', '0030030000000000000')

assert test_talents.assassination.master_poisoner == 1
assert test_talents.combat.killing_spree == 0
assert test_talents.subtlety.opportunity == 3
assert test_talents.subtlety.shadow_dance == 0

# Set up glyphs and test.
glyph_list = ['backstab', 'mutilate', 'rupture']
test_glyphs = rogue_glyphs.RogueGlyphs(*glyph_list)

assert test_glyphs.backstab
assert not test_glyphs.vendetta


# Set up race and test
test_race = race.Race('night_elf')
assert test_race.racial_agi == 210
assert not test_race.get_racial_expertise('1h_sword')

# Set up settings.
test_cycle = settings.AssassinationCycle()
test_settings = settings.Settings(test_cycle, response_time=1)

# Set up level 
test_level = 85

# Build a DPS object, and test some functions.
calculator = AldrianasRogueDamageCalculator(test_stats, test_talents, test_glyphs, test_buffs, test_race, test_settings, test_level)

assert calculator.oh_penalty() == .5

ep_values = calculator.get_ep().items()
ep_values.sort(key=lambda entry: entry[1], reverse=True)
for value in ep_values:
    print value[0] + ':\t', value[1]

print '---------'

dps_breakdown = calculator.assassination_dps_breakdown().items()
dps_breakdown.sort(key=lambda entry: entry[1], reverse=True)
total_dps = sum(entry[1] for entry in dps_breakdown)
for entry in dps_breakdown:
    print entry[0] + ':\t', entry[1] / total_dps

print '---------'

print total_dps
