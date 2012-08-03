# None should be used to indicate unknown values
# The Proc class takes these parameters:
# stat, value, duration, proc_name, default_behaviour, max_stacks=1, can_crit=True, spell_behaviour=None
# Assumed heroic trinkets have the same behaviour as the non-heroic kin.
# behaviours must have a 'default' key so that the proc is properly initialized.
allowed_procs = {
    'rogue_poison': {
        'stat': 'weird_proc',
        'value': 0,
        'duration': 0,
        'proc_name': 'rogue_poison',
        'behaviours': {'default': 'rogue_poison'}
    },
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
    'heroic_matrix_restabilizer': {     # Proc_chance is a guess and should be verified.
        'stat': 'weird_proc',
        'value': 1834,
        'duration': 30,
        'proc_name': 'Matrix Restabilized',
        'behaviours': {'default': 'matrix_restabilizer'}
    },
    'heroic_nokaled_the_elements_of_death': {
        'stat': 'spell_damage',
        'value': 10800,
        'duration': 0,
        'max_stacks': 0,
        'proc_name': 'Iceblast Shadowblast Flameblast',
        'behaviours': {'default': 'nokaled_the_elements_of_death'}
    },
    'heroic_prestors_talisman_of_machination': {
        'stat': 'haste',
        'value': 2178,
        'duration': 15,
        'proc_name': 'Nefarious Plot',
        'behaviours': {'default': 'prestors_talisman_of_machination'}
    },
    'heroic_starcatcher_compass': {
        'stat': 'haste',
        'value': 3278,
        'duration': 20,
        'proc_name': 'Velocity',
        'behaviours': {'default': 'starcatcher_compass'}
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
    'heroic_vial_of_shadows': {         # Name is a compromise to avoid conflicts
        'stat': 'physical_damage',
        'value': 17050.5,
        'duration': 0,
        'max_stacks': 0,
        'proc_name': 'Lightning Strike (vial hc)',
        'behaviours': {'default': 'vial_of_shadows'}
    },
    'heroic_wrath_of_unchaining': {
        'stat': 'agi',
        'value': 99,
        'duration': 10,
        'max_stacks': 10,
        'proc_name': 'Combat Trance',
        'behaviours': {'default': 'wrath_of_unchaining'}
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
    'lfr_nokaled_the_elements_of_death': {
        'stat': 'spell_damage',
        'value': 8476,
        'duration': 0,
        'max_stacks': 0,
        'proc_name': 'Iceblast Shadowblast Flameblast',
        'behaviours': {'default': 'nokaled_the_elements_of_death'}
    },
    'lfr_starcatcher_compass': {
        'stat': 'haste',
        'value': 2573,
        'duration': 20,
        'proc_name': 'Velocity',
        'behaviours': {'default': 'starcatcher_compass'}
    },
    'lfr_vial_of_shadows': {            # Name is a compromise to avoid conflicts
        'stat': 'physical_damage',
        'value': 13382.5,
        'duration': 0,
        'max_stacks': 0,
        'proc_name': 'Lightning Strike (vial lfr)',
        'behaviours': {'default': 'vial_of_shadows'}
    },
    'lfr_wrath_of_unchaining': {
        'stat': 'agi',
        'value': 78,
        'duration': 10,
        'max_stacks': 10,
        'proc_name': 'Combat Trance',
        'behaviours': {'default': 'wrath_of_unchaining'}
    },
    'matrix_restabilizer': {            # Proc_chance is a guess and should be verified.
        'stat': 'weird_proc',
        'value': 1624,
        'duration': 30,
        'proc_name': 'Matrix Restabilized',
        'behaviours': {'default': 'matrix_restabilizer'}

    },
    'nokaled_the_elements_of_death': {
        'stat': 'spell_damage',
        'value': 9567.5,
        'duration': 0,
        'max_stacks': 0,
        'proc_name': 'Iceblast Shadowblast Flameblast',
        'behaviours': {'default': 'nokaled_the_elements_of_death'}
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
    'rogue_t11_4pc': {
        'stat': 'weird_proc',
        'value': 1,
        'duration': 15,
        'proc_name': 'Deadly Scheme',
        'behaviours': {'default': 'rogue_t11_4pc'}
    },
    'schnottz_medallion_of_command': {
        'stat': 'mastery',
        'value': 918,
        'duration': 20,
        'proc_name': 'Hardened Shell',
        'behaviours': {'default': 'schnottz_medallion_of_command'}
    },
    'starcatcher_compass': {
        'stat': 'haste',
        'value': 2904,
        'duration': 20,
        'proc_name': 'Velocity',
        'behaviours': {'default': 'starcatcher_compass'}
    },
    'swordguard_embroidery': {
        'stat': 'ap',
        'value': 1000,
        'duration': 15,
        'proc_name': 'Swordguard Embroidery',
        'behaviours': {'default': 'swordguard_embroidery'}
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
    'vial_of_shadows': {                # Name is a compromise to avoid conflicts
        'stat': 'physical_damage',
        'value': 15105.5,
        'duration': 0,
        'max_stacks': 0,
        'proc_name': 'Lightning Strike (vial n)',
        'behaviours': {'default': 'vial_of_shadows'}
    },
    'wrath_of_unchaining': {
        'stat': 'agi',
        'value': 88,
        'duration': 10,
        'max_stacks': 10,
        'proc_name': 'Combat Trance',
        'behaviours': {'default': 'wrath_of_unchaining'}
    },
    'jaws_of_retribution': {            # Legendary proc stage 1
        'stat': 'agi',
        'value': 2,
        'duration': 30,
        'max_stacks': 50,
        'proc_name': 'Suffering',
        'behaviours': {'default': 'rogue_t13_legendary_proc', 'assassination': 'rogue_t13_legendary_assassination', 'combat': 'rogue_t13_legendary_combat', 'subtlety': 'rogue_t13_legendary_subtlety'}
    },
    'maw_of_oblivion': {                # Legendary proc stage 2
        'stat': 'agi',
        'value': 5,
        'duration': 30,
        'max_stacks': 50,
        'proc_name': 'Nightmare',
        'behaviours': {'default': 'rogue_t13_legendary_proc', 'assassination': 'rogue_t13_legendary_assassination', 'combat': 'rogue_t13_legendary_combat', 'subtlety': 'rogue_t13_legendary_subtlety'}
    },
    'fangs_of_the_father': {            # Legendary proc stage 3. Given that the behaviour changes past the 30 stacks, this'll need an update
        'stat': 'agi',
        'value': 17,
        'duration': 30,
        'max_stacks': 50,
        'proc_name': 'Shadows of the Destroyer',
        'behaviours': {'default': 'rogue_t13_legendary_proc', 'assassination': 'rogue_t13_legendary_assassination', 'combat': 'rogue_t13_legendary_combat', 'subtlety': 'rogue_t13_legendary_subtlety'}
    }
}

allowed_melee_enchants = {
    'avalanche': {
        'stat': 'spell_damage',
        'value': 500,
        'duration': 0,
        'proc_name': 'Avalanche',
        'behaviours': {'default': 'avalanche_melee', 'spell': 'avalanche_spell'}
    },
    'hurricane': {
        'stat': 'haste',
        'value': 450,
        'duration': 12,
        'proc_name': 'Hurricane',
        'behaviours': {'default': 'hurricane_melee', 'spell': 'hurricane_spell'}
    },
    'landslide': {
        'stat': 'ap',
        'value': 1000,
        'duration': 12,
        'proc_name': 'Landslide',
        'behaviours': {'default': 'landslide'}
    },
    'windsong': { # Needs to be improved!
        'stat': 'weird_proc',
        'value': 1500,
        'duration': 12,
        'proc_name': 'Windsong',
        'behaviours': {'default': 'windsong'}
    },
    'dancing_steel': { # Needs to be improved!
        'stat': 'agi',
        'value': 1650,
        'value': 12,
        'proc_name': 'Dancing Steel',
        'behaviours': {'default': 'dancing_steel'}
    },
}

# The _set_behaviour method takes these parameters:
# trigger, icd, proc_chance=False, ppm=False, on_crit=False, on_procced_strikes=True
# You can't set a value for both 'ppm' and 'proc_chance': one must be False
# Allowed triggers are: 'all_spells_and_attacks', 'all_damaging_attacks',
# 'all_attacks', 'strikes', 'auto_attacks', 'damaging_spells', 'all_spells',
# 'healing_spells', 'all_periodic_damage', 'bleeds',
# 'spell_periodic_damage' and 'hots'.
behaviours = {
    'rogue_poison': {
        'icd': 0,
        'proc_chance': 1,
        'trigger': 'all_attacks'
    },
    'avalanche_melee': {
        'icd': 0,
        'ppm': 5,
        'trigger': 'all_attacks'
    },
    'avalanche_spell': {                    # As per EnhSim and SimCraft
        'icd': 10,
        'proc_chance': .25,
        'trigger': 'all_periodic_damage'
    },
    'hurricane_melee': {                    # Completely guessing at proc behavior.
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_spells_and_attacks',
    },
    'hurricane_spell': {
        'icd': 45,
        'proc_chance': .15,
        'trigger': 'all_spells'
    },
    'landslide': {                          # Completely guessing at proc behavior.
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_attacks'
    },
    'dancing_steel': { # Needs to be improved!
        'icd': 0,
        'ppm': 1,
        'trigger': 'all_attacks'
    },
    'windsong': { # Needs to be improved!
        'icd': 0,
        'ppm': 3,
        'trigger': 'all_attacks'
    },
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
    'matrix_restabilizer': {                # Proc_chance is a guess and should be verified.
        'icd': 105,
        'proc_chance': .1,
        'trigger': 'all_attacks'
    },
    'nokaled_the_elements_of_death': {
        'icd': None,
        'proc_chance': .07,
        'trigger': 'all_attacks',
        'on_procced_strikes': False
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
    'rogue_t11_4pc': {
        'icd': None,
        'proc_chance': .01,
        'trigger': 'auto_attacks'
    },
    'schnottz_medallion_of_command': {
        'icd': 100,
        'proc_chance': .1,
        'trigger': 'all_attacks'
    },
    'starcatcher_compass': {
        'icd': 115,
        'proc_chance': .15,
        'trigger': 'all_attacks'
    },
    'swordguard_embroidery': {
        'icd': 55,
        'proc_chance': .15,
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
    'vial_of_shadows': {                    # ICD should be verified.
        'icd': 25,
        'proc_chance': .15,
        'trigger': 'all_attacks'
    },
    'wrath_of_unchaining': {                # ICD should be verified.
        'icd': None,
        'proc_chance': 1,
        'trigger': 'all_attacks'
    },
    'rogue_t13_legendary_proc': {           # Must toggle behaviour to any of the other three, this one will trigger an exception.
        'icd': None,
        'proc_chance': 0,
        'trigger': 'all_attacks'
    },
    'rogue_t13_legendary_assassination': {
        'icd': None,
        'proc_chance': .235,
        'trigger': 'all_attacks'
    }, 
    'rogue_t13_legendary_combat': {
        'icd': None,
        'proc_chance': .095,
        'trigger': 'all_attacks'
    },
    'rogue_t13_legendary_subtlety': {
        'icd': None,
        'proc_chance': .275,
        'trigger': 'all_attacks'
    }
}
