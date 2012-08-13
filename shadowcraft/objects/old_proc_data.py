allowed_procs = {
    'heroic_grace_of_the_herald': {
        'stat': 'crit',
        'value': 1710,
        'duration': 10,
        'proc_name': 'Herald of Doom',
        'behaviours': {'default': 'grace_of_the_herald'}
    },
    'heroic_key_to_the_endless_chamber': {
        'stat': 'agi',
        'value': 1710,
        'duration': 15,
        'proc_name': 'Final Key',
        'behaviours': {'default': 'key_to_the_endless_chamber'}
    },
    'heroic_left_eye_of_rajh': {
        'stat': 'agi',
        'value': 1710,
        'duration': 10,
        'proc_name': 'Eye of Vengeance',
        'behaviours': {'default': 'left_eye_of_rajh'}
    },
    'heroic_prestors_talisman_of_machination': {
        'stat': 'haste',
        'value': 2178,
        'duration': 15,
        'proc_name': 'Nefarious Plot',
        'behaviours': {'default': 'prestors_talisman_of_machination'}
    },
    'heroic_the_hungerer': {
        'stat': 'haste',
        'value': 1730,
        'duration': 15,
        'proc_name': 'Devour',
        'behaviours': {'default': 'the_hungerer'}
    },
    'heroic_tias_grace': {
        'stat': 'agi',
        'value': 34,
        'duration': 15,
        'max_stacks': 10,
        'proc_name': 'Grace',
        'behaviours': {'default': 'tias_grace'}
    },
    'arrow_of_time': {
        'stat': 'haste',
        'value': 1149,
        'duration': 20,
        'proc_name': 'Arrow of Time',
        'behaviours': {'default': 'arrow_of_time'}
    },
    'darkmoon_card_hurricane': {
        'stat': 'spell_damage',
        'value': 7000,
        'can_crit': False,
        'duration': 0,
        'max_stacks': 0,
        'proc_name': 'Lightning Strike',
        'behaviours': {'default': 'darkmoon_card_hurricane'}
    },
    'corens_chilled_chromium_coaster': {
        'stat': 'ap',
        'value': 4000,
        'duration': 10,
        'max_stacks': 0,
        'proc_name': 'Reflection of Torment',
        'behaviours': {'default': 'corens_chilled_chromium_coaster'}
    },
    'essence_of_the_cyclone': {
        'stat': 'crit',
        'value': 1926,
        'duration': 10,
        'proc_name': 'Twisted',
        'behaviours': {'default': 'essence_of_the_cyclone'}
    },
    'heroic_essence_of_the_cyclone': {
        'stat': 'crit',
        'value': 2178,
        'duration': 10,
        'proc_name': 'Twisted',
        'behaviours': {'default': 'essence_of_the_cyclone'}
    },
    'fluid_death': {
        'stat': 'agi',
        'value': 38,
        'duration': 15,
        'max_stacks': 10,
        'proc_name': 'River of Death',
        'behaviours': {'default': 'fluid_death'}
    },
    'grace_of_the_herald': {
        'stat': 'crit',
        'value': 924,
        'duration': 10,
        'proc_name': 'Herald of Doom',
        'behaviours': {'default': 'grace_of_the_herald'}
    },
    'heart_of_the_vile': {
        'stat': 'crit',
        'value': 924,
        'duration': 10,
        'proc_name': 'Herald of Doom',
        'behaviours': {'default': 'heart_of_the_vile'}
    },
    'key_to_the_endless_chamber': {
        'stat': 'agi',
        'value': 1290,
        'duration': 15,
        'proc_name': 'Final Key',
        'behaviours': {'default': 'key_to_the_endless_chamber'}
    },
    'left_eye_of_rajh': {
        'stat': 'agi',
        'value': 1512,
        'duration': 10,
        'proc_name': 'Eye of Vengeance',
        'behaviours': {'default': 'left_eye_of_rajh'}
    },
    'prestors_talisman_of_machination': {
        'stat': 'haste',
        'value': 1926,
        'duration': 15,
        'proc_name': 'Nefarious Plot',
        'behaviours': {'default': 'prestors_talisman_of_machination'}
    },
    'rickets_magnetic_fireball_proc': { # ICD should be verified.
        'stat': 'physical_damage',
        'value': 500,
        'duration': 0,
        'max_stacks': 0,
        'proc_name': 'Magnetic Fireball',
        'behaviours': {'default': 'rickets_magnetic_fireball'}
    },
    'schnottz_medallion_of_command': {
        'stat': 'mastery',
        'value': 918,
        'duration': 20,
        'proc_name': 'Hardened Shell',
        'behaviours': {'default': 'schnottz_medallion_of_command'}
    },
    'the_hungerer': {
        'stat': 'haste',
        'value': 1532,
        'duration': 15,
        'proc_name': 'Devour',
        'behaviours': {'default': 'the_hungerer'}
    },
    'the_twilight_blade': {
        'stat': 'crit',
        'value': 185,
        'duration': 10,
        'max_stacks': 3,
        'proc_name': 'The Deepest Night',
        'behaviours': {'default': 'the_twilight_blade'}
    },
    'tias_grace': {
        'stat': 'agi',
        'value': 30,
        'duration': 15,
        'max_stacks': 10,
        'proc_name': 'Grace',
        'behaviours': {'default': 'tias_grace'}
    },
    'unheeded_warning': {
        'stat': 'ap',
        'value': 1926,
        'duration': 10,
        'proc_name': 'Heedless Carnage',
        'behaviours': {'default': 'unheeded_warning'}
    },   
}

behaviours = {
    'arrow_of_time': {
        'icd': 50,
        'proc_chance': .2,
        'trigger': 'all_attacks'
    },
    'corens_chilled_chromium_coaster': {    # ICD is a guess and should be verified.
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks',
        'on_crit': True
    },
    'darkmoon_card_hurricane': {
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_attacks'
    },
    'essence_of_the_cyclone': {
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks'
    },
    'fluid_death': {
        'icd': None,
        'proc_chance': 1,
        'trigger': 'all_attacks'
    },
    'grace_of_the_herald': {
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks'
    },
    'heart_of_the_vile': {
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks'
    },
    'key_to_the_endless_chamber': {
        'icd': 75,
        'proc_chance': .1,
        'trigger': 'all_attacks'
    },
    'left_eye_of_rajh': {
        'icd': 50,
        'proc_chance': .3,
        'trigger': 'all_attacks',
        'on_crit': True
    },
    'prestors_talisman_of_machination': {
        'icd': 75,
        'proc_chance': .1,
        'trigger': 'all_attacks'
    },
    'rickets_magnetic_fireball': {          # ICD should be verified.
        'icd': 120,
        'proc_chance': .2,
        'trigger': 'all_attacks'
    },
    'schnottz_medallion_of_command': {
        'icd': 100,
        'proc_chance': .1,
        'trigger': 'all_attacks'
    },
    'the_hungerer': {
        'icd': 60,
        'proc_chance': 1.,
        'trigger': 'all_attacks'
    },
    'the_twilight_blade': {                 # PPM/ICD is a guess and should be verified.
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_attacks'
    },
    'tias_grace': {
        'icd': None,
        'proc_chance': 1,
        'trigger': 'all_attacks'
    },
    'unheeded_warning': {
        'icd': 50,
        'proc_chance': .1,
        'trigger': 'all_attacks'
    },
}