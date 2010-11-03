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

    def talents_modifiers(self, opportunity=False, coup_de_grace=False,
                          executioner=False, aggression=False,
                          improved_sinister_strike=False, vile_poisons=False,
                          improved_ambush=False, potent_poisons=False,
                          assassins_resolve=True, mastery=None):
        # This function gets called in every ability affected by talents
        # Parameters are booleans distinguishing which talents affect the
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
            base_modifier += .035 * self.stats.get_mastery_from_rating(mastery)
        if assassins_resolve and self.talents.is_assassination_rogue() and (self.stats.mh.type == 'dagger'):
            base_modifier *= 1.15
        # Passing Sanguinary Vein without talent parameter (it affects all damage)
        # nor is_bleeding since the target will most likely be bleeding from
        # refreshed ruptures in subtletly builds.
        base_modifier *= (1 + .05 * self.talents.subtlety.sanguinary_vein)

        return base_modifier

    def crit_damage_modifiers(self, lethality=False, is_spell=False):
        if is_spell:
            base_modifier = 1.5
        else:
            base_modifier = 2

        if lethality:
            crit_damage_bonus_modifier = 1 + .1 * self.talents.assassination.lethality
        else:
            crit_damage_bonus_modifier = 1

        crit_damage_modifier = self.stats.gear_buffs.metagem_crit_multiplier()

        # The obscure formulae for the different crit enhancers can be found here
        # http://elitistjerks.com/f31/t13300-shaman_relentless_earthstorm_ele/#post404567
        total_modifier = 1 + (base_modifier * crit_damage_modifier - 1) * crit_damage_bonus_modifier

        return total_modifier

    def mh_damage(self, ap):
        weapon_damage = self.stats.mh.damage(ap)
        multiplier = self.talents_modifiers(assassins_resolve=True)
        multiplier *= self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers()

        damage = weapon_damage * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def oh_damage(self, ap):
        weapon_damage = self.stats.oh.damage(ap)
        multiplier = self.talents_modifiers(assassins_resolve=True)
        multiplier *= self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers()

        damage = self.oh_penalty() * weapon_damage * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def backstab_damage(self, ap):
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.talents_modifiers(opportunity=True, aggression=True)
        multiplier *= self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(lethality=True)
        percentage_damage_bonus = 2
        if self.talents.is_subtlety_rogue():
            percentage_damage_bonus += .25

        damage = percentage_damage_bonus * (weapon_damage + 345) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def mh_mutilate_damage(self, ap, is_poisoned=True):
        mh_weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.talents_modifiers(opportunity=True)
        multiplier *= self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(lethality=True)

        mh_damage = 1.5 * (mh_weapon_damage + 201) * multiplier

        if is_poisoned:
            mh_damage *= 1.2

        crit_mh_damage = mh_damage * crit_multiplier

        return mh_damage, crit_mh_damage

    def oh_mutilate_damage(self, ap, is_poisoned=True):
        oh_weapon_damage = self.stats.oh.normalized_damage(ap)
        multiplier = self.talents_modifiers(opportunity=True)
        multiplier *= self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(lethality=True)

        oh_damage = 1.5 * (self.oh_penalty() * oh_weapon_damage + 201) * multiplier

        if is_poisoned:
            oh_damage *= 1.2

        crit_oh_damage = oh_damage * crit_multiplier

        return oh_damage, crit_oh_damage

    def sinister_strike_damage(self, ap):
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.talents_modifiers(aggression=True, improved_sinister_strike=True)
        multiplier *= self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(lethality=True)

        damage = (weapon_damage + 200) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def hemorrhage_damage(self):
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(lethality=True)

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

        damage = percentage_damage_bonus * weapon_damage * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def ambush_damage(self, ap):
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.talents_modifiers(opportunity=True, improved_ambush=True)
        multiplier *= self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers()

        if self.stats.mh.type == 'dagger':
            damage = (2.7493 * weapon_damage + 367 * 2.75) * multiplier
        else:
            damage = (1.9 * weapon_damage + 367 * 1.9) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def revealing_strike_damage(self, ap):
        weapon_damage = self.stats.mh.damage(ap)
        multiplier = self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers()

        damage = 1.25 * weapon_damage * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def venomous_wounds_damage(self, ap, mastery):
        multiplier = self.talents_modifiers(potent_poisons=True, assassins_resolve=False, mastery=mastery)
        multiplier *= self.buffs.spell_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        damage = (363 + .135 * ap) * multiplier
            # need values for lvl 85
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def main_gauche(self, ap):
        weapon_damage = self.stats.oh.normalized_damage(ap)
        multiplier = self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers()

        damage = self.oh_penalty() * weapon_damage * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def instant_poison_damage(self, ap, mastery):
        multiplier = self.talents_modifiers(potent_poisons=True, vile_poisons=True,
                                       assassins_resolve=False, mastery=mastery)
        multiplier *= self.buffs.spell_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        low_end_damage = (300 + 0.09 * ap) * multiplier
        high_end_damage = (400 + 0.09 * ap) * multiplier
        average_damage = (low_end_damage + high_end_damage) / 2
            # pulled from the assassination spreadsheet; need values for lvl 85
        average_crit_damage = average_damage * crit_multiplier

        return average_damage, average_crit_damage

    def deadly_poison_tick_damage(self, ap, mastery, dp_stacks=5):
        multiplier = self.talents_modifiers(potent_poisons=True, vile_poisons = True,
                                       assassins_resolve=False, mastery=mastery)
        multiplier *= self.buffs.spell_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        tick_damage = ((296 + .108 * ap) * dp_stacks / 4) * multiplier
            # pulled from the assassination spreadsheet; need values for lvl 85
        crit_tick_damage = tick_damage * crit_multiplier

        return tick_damage, crit_tick_damage

    def wound_poison_damage(self, ap, mastery):
        multiplier = self.talents_modifiers(potent_poisons=True, vile_poisons = True,
                                       assassins_resolve=False, mastery=mastery)
        multiplier *= self.buffs.spell_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        damage = (231 + .036 * ap) * multiplier
            # pulled from the combat spreadsheet; need values for lvl 85
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def garrote_damage(self, ap):
        multiplier = self.talents_modifiers(opportunity=True, assassins_resolve=False)
        multiplier *= self.buffs.bleed_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers()

        tick_damage = (133 +  ap * 1 * 0.07) * multiplier
        crit_tick_damage = tick_damage * crit_multiplier

        return tick_damage, crit_tick_damage

    def rupture_tick_damage(self, ap, cp):
        # Assassasin's resolve was tested on melee, poisons, weapon strikes and
        # ap strikes, not bleeds. Although there's no reason to believe it doesn't
        # affect bleeds, I'm setting it to false until some testing is done
        multiplier = self.talents_modifiers(executioner=True, assassins_resolve=False)
        multiplier *= self.buffs.bleed_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers()

        ap_multiplier_tuple = (0, .015, .024, .03, .03428571, .0375)
        tick_damage = (142 + 20 * cp + ap_multiplier_tuple[cp] * ap) * multiplier
        crit_tick_damage = tick_damage * crit_multiplier

        # leaving full duration damage formulas in comments just in case
        # this value is usefull somehow somewhen somewhere
        # duration = (6 + cp * 2)
        # if self.glyphs.rupture():
        #     duration +=4
        # damage = tick_damage * .5 * duration

        return tick_damage, crit_tick_damage

    def eviscerate_damage(self, ap, cp):
        multiplier = self.talents_modifiers(coup_de_grace=True, aggression=True, executioner=True)
        multiplier *= self.buffs.physical_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers()

        ap_multiplier_tuple = (0, .091, .182, .273, .364, .455)
        low_end_damage = (183 + 536 * cp + ap_multiplier_tuple[cp] * ap) * multiplier
        high_end_damage = (549 + 536 * cp + ap_multiplier_tuple[cp] * ap) * multiplier
        average_damage = (low_end_damage + high_end_damage) / 2
        average_crit_damage = average_damage * crit_multiplier

        return average_damage, average_crit_damage

    def envenom_damage(self, ap, cp):
        # Envemom has a dependency on dp_charges too; but being unlikely to be used out of builds
        # with master poisoner I'm not including that for the moment
        multiplier = self.talents_modifiers(coup_de_grace=True, executioner=True, assassins_resolve=False)
        multiplier *= self.buffs.spell_damage_multiplier()
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        damage = (241 * cp + .09 * cp * ap) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

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
