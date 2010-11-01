from objects import talents

class AssassinationTalents(talents.TalentTree):
    allowed_talents = {
        'deadly_momentum': 2,
        'coup_de_grace': 3,
        'lethality': 3,
        'ruthlessness': 3,
        'quickening': 2,
        'puncturing_wounds': 3,
        'blackjack': 2,
        'deadly_brew': 2,
        'cold_blood': 1,
        'vile_poisons': 3,
        'deadened_nerves': 3,
        'seal_fate': 2,
        'murderous_intent': 2,
        'overkill': 1,
        'master_poisoner': 1,
        'improved_expose_armor': 2,
        'cut_to_the_chase': 3,
        'venomous_wounds': 2,
        'vendetta': 1
    }

    def populate_talents_from_list(self, values_list):
        self.set_talent('deadly_momentum', values_list[0])
        self.set_talent('coup_de_grace', values_list[1])
        self.set_talent('lethality', values_list[2])
        self.set_talent('ruthlessness', values_list[3])
        self.set_talent('quickening', values_list[4])
        self.set_talent('puncturing_wounds', values_list[5])
        self.set_talent('blackjack', values_list[6])
        self.set_talent('deadly_brew', values_list[7])
        self.set_talent('cold_blood', values_list[8])
        self.set_talent('vile_poisons', values_list[9])
        self.set_talent('deadened_nerves', values_list[10])
        self.set_talent('seal_fate', values_list[11])
        self.set_talent('murderous_intent', values_list[12])
        self.set_talent('overkill', values_list[13])
        self.set_talent('master_poisoner', values_list[14])
        self.set_talent('improved_expose_armor', values_list[15])
        self.set_talent('cut_to_the_chase', values_list[16])
        self.set_talent('venomous_wounds', values_list[17])
        self.set_talent('vendetta', values_list[18])

class CombatTalents(talents.TalentTree):
    allowed_talents = {
        'improved_recuperate': 2,
        'improved_sinister_strike': 3,
        'precision': 3,
        'improved_slice_and_dice': 2,
        'improved_sprint': 2,
        'aggression': 3,
        'improved_kick': 2,
        'lightning_reflexes': 3,
        'revealing_strike': 1,
        'reinforced_leather': 2,
        'improved_gouge': 2,
        'combat_potency': 2,
        'blade_twisting': 2,
        'throwing_specialization': 2,
        'adrenaline_rush': 3,
        'savage_combat': 2,
        'bandits_guile': 3,
        'restless_blades': 2,
        'killing_spree': 1
    }

    def populate_talents_from_list(self, values_list):
        self.set_talent('improved_recuperate', values_list[0])
        self.set_talent('improved_sinister_strike', values_list[1])
        self.set_talent('precision', values_list[2])
        self.set_talent('improved_slice_and_dice', values_list[3])
        self.set_talent('improved_sprint', values_list[4])
        self.set_talent('aggression', values_list[5])
        self.set_talent('improved_kick', values_list[6])
        self.set_talent('lightning_reflexes', values_list[7])
        self.set_talent('revealing_strike', values_list[8])
        self.set_talent('reinforced_leather', values_list[9])
        self.set_talent('improved_gouge', values_list[10])
        self.set_talent('combat_potency', values_list[11])
        self.set_talent('blade_twisting', values_list[12])
        self.set_talent('throwing_specialization', values_list[13])
        self.set_talent('adrenaline_rush', values_list[14])
        self.set_talent('savage_combat', values_list[15])
        self.set_talent('bandits_guile', values_list[16])
        self.set_talent('restless_blades', values_list[17])
        self.set_talent('killing_spree', values_list[18])

class SubtletyTalents(talents.TalentTree):
    allowed_talents = {
        'nightstalker': 2,
        'improved_ambush': 3,
        'relentless_strikes': 3,
        'elusiveness': 2,
        'waylay': 2,
        'opportunity': 3,
        'initiative': 2,
        'energetic_recovery': 3,
        'find_weakness': 2,
        'hemorrhage': 1,
        'honor_among_thieves': 3,
        'premeditation': 1,
        'enveloping_shadows': 3,
        'cheat_death': 3,
        'preparation': 1,
        'sanguinary_vein': 2,
        'slaughter_from_the_shadows': 3,
        'serrated_blades': 2,
        'shadow_dance': 1
    }

    def populate_talents_from_list(self, values_list):
        self.set_talent('nightstalker', values_list[0])
        self.set_talent('improved_ambush', values_list[1])
        self.set_talent('relentless_strikes', values_list[2])
        self.set_talent('elusiveness', values_list[3])
        self.set_talent('waylay', values_list[4])
        self.set_talent('opportunity', values_list[5])
        self.set_talent('initiative', values_list[6])
        self.set_talent('energetic_recovery', values_list[7])
        self.set_talent('find_weakness', values_list[8])
        self.set_talent('hemorrhage', values_list[9])
        self.set_talent('honor_among_thieves', values_list[10])
        self.set_talent('premeditation', values_list[11])
        self.set_talent('enveloping_shadows', values_list[12])
        self.set_talent('cheat_death', values_list[13])
        self.set_talent('preparation', values_list[14])
        self.set_talent('sanguinary_vein', values_list[15])
        self.set_talent('slaughter_from_the_shadows', values_list[16])
        self.set_talent('serrated_blades', values_list[17])
        self.set_talent('shadow_dance', values_list[18])

class RogueTalents(object):
    # Might make sense to define a more general talent tree class that contains
    # some of this logic (as well as, for instance, a customized __getattr__
    # and __setattr__ functions to let you access talents by name without
    # needing to know what tree they're in) and then just extend it here;
    # not going to worry about it yet but it might be a sensible piece of 
    # cleanup if someone wants to tackle it.

    def __init__(self, assassination_string, combat_string, subtlety_string):
        self.assassination = AssassinationTalents(assassination_string)
        self.combat = CombatTalents(combat_string)
        self.subtlety = SubtletyTalents(subtlety_string)

        # Should be a real exception and not an assert, and may need to be
        # adjusted if we're going to allow calculations at multiple character
        # levels, but this will do for the moment.
        assert self.assassination.talents_in_tree() + self.combat.talents_in_tree() + self.subtlety.talents_in_tree() <= 41

    def is_assassination_rogue(self):
        return self.assassination.talents_in_tree() >= 31
    
    def is_combat_rogue(self):
        return self.combat.talents_in_tree() >= 31

    def is_subtlety_rogue(self):
        return self.subtlety.talents_in_tree() >= 31
