from calcs import DamageCalculator

class RogueDamageCalculator(DamageCalculator):
    # Functions of general use to rogue damage calculation go here. If a
    # calculation will reasonably used for multiple classes, it should go in
    # calcs.DamageCalculator instead. If its a specific intermediate
    # value useful to only your calculations, when you extend this you should
    # put the calculations in your object. But there are things - like
    # backstab damage as a function of AP - that (almost) any rogue damage
    # calculator will need to know, so things like that go here.

    # Will need to be adjusted when/if we add character level as an option.
    AGI_PER_CRIT = 324.72 * 100
    AGI_CRIT_INTERCEPT = -.00295

    def oh_penalty(self):
        if self.talents.is_combat_rogue():
            return .875
        else:
            return .5

    def talents_modifiers(opportunity=False, coup_de_grace=False,
                          executioner=False, aggression=False,
                          improved_sinister_strike=False, vile_poisons=False
                          improved_ambush=False, potent_poisons=False,
                          assassins_resolve=True, mastery=None):
        # This funcion gets called in every ability affected by talents
        # Parameters are boleans distinguisihing which talents affect the
        # spell in question. It returns the final modifier for their
        # respective additive/multiplicative values
        base_modifier = 1
        if opportunity:
            base_modifier += .1 * (self.talents.subtlety.opportunity)
        if coup_de_grace:
            cdg_tuple = (0, .07, .14, .2)
            base_modifier += cdg_tuple[self.talents.asssassination.coup_de_grace]
        if executioner and self.talents.is_subtlety_rogue():
            base_modifier += .025 * self.stats.get_mastery_from_rating(mastery)
        if aggression:
            base_modifier += .05 * (self.talents.combat.aggression)
        if improved_sinister_strike:
            base_modifier += .1 * (self.talents.combat.improved_sinister_strike)
        if vile_poisons:
            vp_tuple = (0, .07, .14, .2)
            base_modifier += vp_tuple[self.talents.asssassination.vile_poisons]
        if improved_ambush:
            base_modifier += .05 * (self.talents.subtlety.improved_ambush)
        if potent_poisons and self.talents.is_assassination_rogue():
            base_modifier += .025 * self.stats.get_mastery_from_rating(mastery)
        # Multiplicative modifiers may need to be handled in a more elegant way
        if assassins_resolve and self.talents.is_assassination_rogue() and (self.stats.mh.type == 'dagger'):
            base_modifier *= 1.15

        return base_modifier

    def backstab_damage(self, ap):
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = talents_modifiers(opportunity=True, aggression=True)
        percentage_damage_bonus = 2
        if self.talents.is_subtlety_rogue():
            percentage_damage_bonus += .25

        damage = percentage_damage_bonus * (weapon_damage + 345) * multiplier

        return damage

    def mutilate_damage(self, ap, is_poisoned=True):
        mh_weapon_damage = self.stats.mh.normalized_damage(ap)
        oh_weapon_damage = self.stats.oh.normalized_damage(ap)
        multiplier = talents_modifiers(opportunity=True)

        mh_damage = 1.5 * (mh_weapon_damage + 201) * multiplier
        oh_damage = 1.5 * (self.oh_penalty() * oh_weapon_damage + 201) * multiplier

        if is_poisoned:
            mh_damage *= 1.2
            oh_damage *= 1.2

        return mh_damage, oh_damage

    def sinister_strike_damage(self, ap):
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = talents_modifiers(aggression=True, improved_sinister_strike=True)

        damage = (weapon_damage + 200) * multiplier

        return damage

    def hemorrhage_damage(self):
        weapon_damage = self.stats.mh.normalized_damage(ap)

        if self.stats.mh.type == 'dagger':
            percentage_damage_bonus = 1.595
        else:
            percentage_damage_bonus = 1.1
        if self.talents.is_subtlety_rogue():
            percentage_damage_bonus += .25
            # This should probably be tested at some point to make sure there isn't
            # some weird interaction with the dagger-or-not logic - that is,
            # its possible that the computation the do internally would be
            # (1.1 + .25) * 1.45 rather than 1.1 * 1.45 + .25.

        damage = percentage_damage_bonus * weapon_damage

        return damage

    def ambush_damage(self, ap):
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = talents_modifiers(opportunity=True, improved_ambush=True)

        if self.stats.mh.type == 'dagger':
            damage = (2.7493 * weapon_damage + 367 * 2.75) * multiplier
        else:
            damage = (1.9 * weapon_damage + 367 * 1.9) * multiplier

        return damage

    def revealing_strike_damage(self, ap):
        weapon_damage = self.stats.mh.damage(ap)

        damage = 1.25 * weapon_damage

        return damage

    def venomous_wounds_damage(self, ap, mastery):
        multiplier = talents_modifiers(potent_poisons=True, assassins_resolve=False, mastery)

        damage = (363 + .135 * ap) * multiplier
        # need values for lvl 85

        return damage

    def instant_poison_damage(self, ap, mastery):
        multiplier = talents_modifiers(potent_poisons=True, vile_poisons = True,
                                       assassins_resolve=False, mastery)

        low_end_damage = (300 + 0.09 * ap) * multiplier
        high_end_damage = (400 + 0.09 * ap) * multiplier
        average_damage = ((300 + 400) / 2 + 0.09 * ap) * multiplier
        # pulled from the assassination spreadsheet; need values for lvl 85

        return low_end_damage, high_end_damage, average_damage

    def deadly_poison_damage(self, ap, mastery):
        # also dependancy on dp_stacks=5 but leaving it for now
        multiplier = talents_modifiers(potent_poisons=True, vile_poisons = True,
                                       assassins_resolve=False, mastery)

        damage = (296 + ,108 * ap) * multiplier
        # pulled from the assassination spreadsheet; need values for lvl 85

        return damage

    def wound_poison_damage(self, ap, mastery):
        multiplier = talents_modifiers(potent_poisons=True, vile_poisons = True,
                                       assassins_resolve=False, mastery)

        damage = (231 + ,036 * ap) * multiplier
        # pulled from the combat spreadsheet; need values for lvl 85

        return damage

    def garrote_damage(self, ap):
        multiplier = talents_modifiers(opportunity=True, assassins_resolve=False)

        damage = (133 +  ap * 1 * 0.07) * 6 * multiplier

        return damage

    def rupture_damage(self, ap, cp):
        # Assassasin's resolve was tested on melee, poisons, weapon strikes and
        # ap strikes, not bleeds. Although there's no reason to believe it doesn't
        # affect bleeds, I'm setting it to false until some testing is done
        multiplier = talents_modifiers(executioner=True, assassins_resolve=False)

        duration = (6 + cp * 2)
        if self.glyphs.rupture():
            duration +=4

        ap_multiplier_tuple = (0, .015, .024, .03, .03428571, .0375)
        tick_damage = (142 + 20 * cp + ap_multiplier_tuple[cp] * ap) * multiplier
        damage = tick_damage * .5 * duration

        return tick_damage, duration, damage

    def eviscerate_damage(self, ap, cp):
        multiplier = talents_modifiers(coup_de_grace=True, aggression=True, executioner=True)

        ap_multiplier_tuple = (0, .091, .182, .273, .364, .455)
        low_end_damage = (183 + 536 * cp + ap_multiplier_tuple[cp] * ap) * multiplier
        high_end_damage = (549 + 536 * cp + ap_multiplier_tuple[cp] * ap) * multiplier
        average_damage = ((183 + 549) / 2 + 536 * cp + ap_multiplier_tuple[cp] * ap) * multiplier

        return low_end_damage, high_end_damage, average_damage

    def envenom_damage(self, ap, cp):
        # Envemom has a dependency on dp_charges too; but being unlikely to be used out of builds
        # with master poisoner I'm not including that for the moment
        multiplier = talents_modifiers(coup_de_grace=True, executioner=True, assassins_resolve=False)

        damage = (241 * cp + .09 * cp * ap) * multiplier

        return damage

    def melee_crit_rate(self, agi=None, crit=None):
        if agi == None:
            agi = self.stats.agi
        base_crit = self.AGI_CRIT_INTERCEPT + agi / self.AGI_PER_CRIT
        base_crit += self.stats.get_crit_from_rating(crit)
        return base_crit + self.buffs.buff_all_crit()

    def spell_crit_rate(self, crit=None):
        base_crit += self.stats.get_crit_from_rating(crit)
        return base_crit + self.buffs.buff_all_crit() + self.buffs.buff_spell_crit()

    # Not strictly speaking rogue-specific, but given that the base object
    # doesn't currently have any notion of whether you'd dual-wielding or not
    # (and this calculation depends on that), I'm going to leave this here
    # until we figure out how to handle that.
    #
    # Also has a dependency on (target_level - attacker_level), but ignoring
    # that for now.
    def crit_cap(self):
        return self.dual_wield_melee_hit_chance - .24
