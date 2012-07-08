talents = {
    'death_knight': (
        ('roiling_blood', 'plague_leech', 'unholy_blight'),
        ('lichborne', 'anti-magic_zone', 'purgatory'),
        ('deaths_advance', 'chilblains', 'asphyxiate'),
        ('death_pact', 'death_siphon', 'conversion'),
        ('blood_tap', 'runic_empowerment', 'runic_corruption'),
        ('gorefiends_grasp', 'remorseless_winter', 'desecrated_ground')
    ),
    'druid': (
        ('feline_swiftness', 'displacer_beast', 'wild_charge'),
        ('natures_swiftness', 'renewal', 'cenarion_ward'),
        ('faerie_swarm', 'mass_entanglement', 'typhoon'),
        ('soul_of_the_forest', 'incarnation', 'force_of_nature'),
        ('disorienting_roar', 'ursols_vortex', 'mighty_bash'),
        ('heart_of_the_wild', 'dream_of_cenarius', 'natures_vigil')
    ),
    'hunter': (
        ('posthaste', 'narrow_escape', 'crouching_tiger_hidden_chimera'),
        ('silencing_shot', 'wyvern_sting', 'binding_shot'),
        ('exhilaration', 'aspect_of_the_iron_hawk', 'spirit_bond'),
        ('fervor', 'readiness', 'thrill_of_the_hunt'),
        ('a_murder_of_crows', 'dire_beast', 'lynx_rush'),
        ('glaive_toss', 'powershot', 'barrage')
    ),
    'mage': (
        ('presence_of_mind', 'scorch', 'ice_floes'),
        ('temporal_shield', 'blazing_speed', 'ice_barrier'),
        ('ring_of_frost', 'ice_ward', 'frostjaw'),
        ('greater_invisibility', 'cauterize', 'cold_snap'),
        ('nether_tempest', 'living_bomb', 'frost_bomb'),
        ('invocation', 'rune_of_power', 'incanters_ward')
    ),
    'monk': (
        ('celerity', 'tigers_lust', 'momentum'),
        ('chi_wave', 'zen_sphere', 'chi_burst'),
        ('power_strikes', 'ascension', 'chi_brew'),
        ('deadly_reach', 'charging_ox_wave', 'leg_sweep'),
        ('healing_elixirs', 'dampen_harm', 'diffuse_magic'),
        ('rushing_jade_wind', 'invoke_xuen,_the_white_tiger', 'chi_torpedo')
    ),
    'paladin': (
        ('speed_of_light', 'long_arm_of_the_law', 'pursuit_of_justice'),
        ('fist_of_justice', 'repentance', 'burden_of_guilt'),
        ('selfless_healer', 'eternal_flame', 'sacred_shield'),
        ('hand_of_purity', 'unbreakable_spirit', 'clemency'),
        ('holy_avenger', 'sanctified_wrath', 'divine_purpose'),
        ('holy_prism', 'lights_hammer', 'execution_sentence')
    ),
    'priest': (
        ('void_tendrils', 'psyfiend', 'dominate_mind'),
        ('body_and_soul', 'angelic_feather', 'phantasm'),
        ('from_darkness_comes_light', 'mindbender', 'power_word:_solace'),
        ('desperate_prayer', 'spectral_guise', 'angelic_bulwark'),
        ('twist_of_fate', 'power_infusion', 'divine_insight'),
        ('cascade', 'divine_star', 'halo')
    ),
    'rogue': (
        ('nightstalker', 'subterfuge', 'shadow_focus'),
        ('deadly_throw', 'nerve_strike', 'combat_readiness'),
        ('cheat_death', 'leeching_poison', 'elusiveness'),
        ('preparation', 'shadowstep', 'burst_of_speed'),
        ('deadly_brew', 'paralytic_poison', 'dirty_tricks'),
        ('shuriken_toss', 'versatility', 'anticipation')
    ),
    'shaman': (
        ('natures_guardian', 'stone_bulwark_totem', 'astral_shift'),
        ('frozen_power', 'earthgrab_totem', 'windwalk_totem'),
        ('call_of_the_elements', 'totemic_restoration', 'totemic_projection'),
        ('elemental_mastery', 'ancestral_swiftness', 'echo_of_the_elements'),
        ('healing_tide_totem', 'ancestral_guidance', 'conductivity'),
        ('unleashed_fury', 'primal_elementalist', 'elemental_blast')
    ),
    'warlock': (
        ('dark_regeneration', 'soul_leech', 'harvest_life'),
        ('howl_of_terror', 'mortal_coil', 'shadowfury'),
        ('soul_link', 'sacrificial_pact', 'dark_bargain'),
        ('blood_fear', 'burning_rush', 'unbound_will'),
        ('grimoire_of_supremacy', 'grimoire_of_service', 'grimoire_of_sacrifice'),
        ('archimondes_vengeance', 'kiljaedens_cunning', 'mannoroths_fury')
    ),
    'warrior': (
        ('juggernaut', 'double_time', 'warbringer'),
        ('enraged_regeneration', 'second_wind', 'impending_victory'),
        ('staggering_shout', 'piercing_howl', 'disrupting_shout'),
        ('bladestorm', 'shockwave', 'dragon_roar'),
        ('mass_spell_reflection', 'safeguard', 'vigilance'),
        ('avatar', 'bloodbath', 'storm_bolt')
    ),
}

old_talents = frozenset([
    'ruthlessness', 'cold_blood', 'overkill',
    'lightning_reflexes', 'combat_potency', 'bandits_guile',
    'initiative', 'energetic_recovery',
])
