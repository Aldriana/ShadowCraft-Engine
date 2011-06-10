# None should be used to indicate unknown values
# The Proc class takes these parameters:
# stat, value, can_crit=True, duration, trigger, icd, proc_name, ppm=False, proc_chance=False, on_crit=False, max_stacks=1
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
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Herald of Doom'
    },
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
    },
    'heroic_matrix_restabilizer': {     # Proc_chance/ICD is a guess and should be verified.
        'stat': 'weird_proc',
        'value': 1730,
        'duration': 30,
        'icd': 150,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Matrix Restabilizer'
    },
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
        'proc_chance': 1,
        'trigger': 'all_attacks',
        'proc_name': 'Grace'
    },
    'darkmoon_card_hurricane': {
        'stat': 'spell_damage',
        'value': 7000,
        'can_crit': False,
        'duration': 0,
        'max_stacks': 0,
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_attacks',
        'proc_name': 'Lightning Strike'
    },
    'corens_chilled_chromium_coaster': {    # PPM/ICD is a guess and should be verified.
        'stat': 'ap',
        'value': 4000,
        'duration': 10,
        'max_stacks': 0,
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_attacks',
        'on_crit': True,
        'proc_name': 'Reflection of Torment'
    },
    'essence_of_the_cyclone': {
        'stat': 'crit',
        'value': 1926,
        'duration': 10,
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Twisted'
    },
    'heroic_essence_of_the_cyclone': {
        'stat': 'crit',
        'value': 2178,
        'duration': 10,
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Twisted'
    },
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
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Herald of Doom'
    },
    'heart_of_the_vile': {
        'stat': 'crit',
        'value': 924,
        'duration': 10,
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Herald of Doom'
    },
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
        'icd': 50,
        'proc_chance': .3,
        'trigger': 'all_attacks',
        'on_crit': True,
        'proc_name': 'Eye of Vengeance'
    },
    'rickets_magnetic_fireball': {      # Proc_chance/ICD is a guess and should be verified.
        'stat': 'physical_damage',
        'value': 500,
        'duration': 0,
        'max_stacks': 0,
        'icd': 120,
        'proc_chance': .2,
        'trigger': 'all_attacks',
        'proc_name': 'Magnetic Fireball'
    },
    'matrix_restabilizer': {            # Proc_chance/ICD is a guess and should be verified.
        'stat': 'weird_proc',
        'value': 1532,
        'duration': 30,
        'icd': 150,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Matrix Restabilizer'
    },
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
    'schnottz_medallion_of_command': {
        'stat': 'mastery',
        'value': 918,
        'duration': 20,
        'icd': 100,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Hardened Shell'
    },
    'swordguard_embroidery': {
        'stat': 'ap',
        'value': 1000,
        'duration': 15,
        'icd': 55,
        'proc_chance': .15,
        'trigger': 'all_attacks',
        'proc_name': 'Swordguard Embroidery'
    },
    'the_twilight_blade': {             # PPM/ICD is a guess and should be verified.
        'stat': 'crit',
        'value': 185,
        'duration': 10,
        'max_stacks': 3,
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_attacks',
        'proc_name': 'The Deepest Night'
    },
    'tias_grace': {
        'stat': 'agi',
        'value': 30,
        'duration': 15,
        'max_stacks': 10,
        'icd': None,
        'proc_chance': 1,
        'trigger': 'all_attacks',
        'proc_name': 'Grace'
    },
    'unheeded_warning': {
        'stat': 'extra_weapon_damage',
        'value': 680,
        'duration': 10,
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'proc_name': 'Heedless Carnage'
    }
}
