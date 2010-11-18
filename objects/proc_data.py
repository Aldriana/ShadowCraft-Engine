# None should be used to indicate unknown values
# The Proc class takes these parameters:
# stat, value, duration, trigger, icd, proc_name, ppm=False, proc_chance=False, on_crit=False, max_stacks=1
# You can't set a value for both 'ppm' and 'proc_chance': one of them must be False
# Assumed heroic trinkets have same proc chance/ICD as non-heroic
# Allowed triggers are: 'all_spells_and_attacks', 'all_damaging_attacks', 'all_attacks', 'strikes',
# 'auto_attacks', 'damaging_spells', 'all_spells', 'healing_spells', 'all_periodic_damage',
# 'bleeds', 'spell_periodic_damage' and 'hots'
allowed_procs = {
    'heroic_grace_of_the_herald': {
        'stat': 'crit',
        'value': 1710,
        'duration': 10,
        'icd': 45,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Herald of Doom'
    },                                  # ICD is a guess and should be verified.
    'heroic_key_to_the_endless_chamber': {
        'stat': 'agi',
        'value': 1710,
        'duration': 15,
        'icd': 75,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Final Key'
    },
    'heroic_left_eye_of_rajh': {
        'stat': 'agi',
        'value': 1710,
        'duration': 10,
        'icd': 50,
        'proc_chance': .3,
        'trigger': 'all_attacks',
        'on_crit': True,
        'proc_name': 'Eye of Vengeance'
    },                                  # ICD is a guess and should be verified.
    'heroic_prestors_talisman_of_machination': {
        'stat': 'haste',
        'value': 2178,
        'duration': 15,
        'icd': 75,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Nefarious Plot'
    },
    'heroic_tias_grace': {
        'stat': 'agi',
        'value': 34,
        'duration': 15,
        'max_stacks': 10,
        'icd': None,
        'proc_chance': None,
        'trigger': 'all_attacks',
        'proc_name': 'Grace'
    },
    'darkmoon_card_hurricane': {
        'stat': 'spell_damage',
        'value': 5000,
        'duration': 0,
        'max_stacks': 0,
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_attacks',
        'proc_name': 'Lightning Strike'
    },                                  # PPM/ICD is a guess and should be verified.
    'essence_of_the_cyclone': {
        'stat': 'crit',
        'value': 1926,
        'duration': 10,
        'icd': 45,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Twisted'
    },                                  # ICD is a guess and should be verified.
    'fluid_death': {
        'stat': 'agi',
        'value': 38,
        'duration': 15,
        'max_stacks': 10,
        'icd': None,
        'proc_chance': 1,
        'trigger': 'all_attacks',
        'proc_name': 'River of Death'
    },
    'grace_of_the_herald': {
        'stat': 'crit',
        'value': 924,
        'duration': 10,
        'icd': 45,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Herald of Doom'
    },                                  # ICD is a guess and should be verified.
    'heart_of_the_vile': {
        'stat': 'crit',
        'value': 924,
        'duration': 10,
        'icd': 45,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Herald of Doom'
    },                                  # ICD is a guess and should be verified.
    'key_to_the_endless_chamber': {
        'stat': 'agi',
        'value': 1290,
        'duration': 15,
        'icd': 75,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Final Key'
    },
    'left_eye_of_rajh': {
        'stat': 'agi',
        'value': 1512,
        'duration': 10,
        'icd': 45,
        'proc_chance': .3,
        'trigger': 'all_attacks',
        'on_crit': True,
        'proc_name': 'Eye of Vengeance'
    },                                  # ICD is a guess and should be verified.
    'prestors_talisman_of_machination': {
        'stat': 'haste',
        'value': 1926,
        'duration': 15,
        'icd': 75,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Nefarious Plot'
    },
    'rogue_t11_4pc': {
        'stat': 'weird_proc',
        'value': 1,
        'duration': 15,
        'icd': None,
        'proc_chance': .01,
        'trigger': 'auto_attacks',
        'proc_name': 'Deadly Scheme'
    },
    'the_twilight_blade': {
        'stat': 'crit',
        'value': 185,
        'duration': 10,
        'max_stacks': 3,
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_attacks',
        'proc_name': 'The Deepest Night'
    },                                  # PPM/ICD is a guess and should be verified.
    'tias_grace': {
        'stat': 'agi',
        'value': 30,
        'duration': 15,
        'max_stacks': 10,
        'icd': None,
        'proc_chance': None,
        'trigger': 'all_attacks',
        'proc_name': 'Grace'
    },
    'unheeded_warning': {
        'stat': 'weird_proc',
        'value': .25,
        'duration': 10,
        'icd': 45,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Heedless Carnage'
    }                                   # ICD is a guess and should be verified.
}
