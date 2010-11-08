from calcs import DamageCalculator

class RogueDamageCalculator(DamageCalculator):
    # Functions of general use to rogue damage calculation go here. If a
    # calculation will reasonably used for multiple classes, it should go in
    # calcs.DamageCalculator instead. If its a specific intermediate
    # value useful to only your calculations, when you extend this you should
    # put the calculations in your object. But there are things - like
    # backstab damage as a function of AP - that (almost) any rogue damage
    # calculator will need to know, so things like that go here.

    DEFAULT_LEVEL = 85
    BS_BONUS_DMG =          {80:310, 81:317, 82:324, 83:331, 84:338, 85:345}
    MUT_BONUS_DMG =         {80:180, 85:201}
    SS_BONUS_DMG =          {80:180, 81:184, 82:188, 83:192, 84:196, 85:200}
    AMBUSH_BONUS_DMG =      {80:330, 81:338, 82:345, 83:353, 84:360, 85:368}
    VW_BASE_DMG =           {80:363, 85:675}
    VW_PERCENTAGE_DMG =     {80:.135, 85:.176}
    IP_LOW_BASE_DMG =       {80:300, 85:303}
    IP_HIGH_BASE_DMG =      {80:400, 85:401}
    DP_BASE_DMG =           {80:296, 85:540}
    DP_PERCENTAGE_DMG =     {80:.108, 85:.14}
    WP_BASE_DMG =           {80:231, 85:231}            # missing lvl-85 data
    WP_PERCENTAGE_DMG =     {80:.036, 85:.036}          # missing lvl-85 data
    GARROTE_BASE_DMG =      {80:119, 81:122, 82:125, 83:127, 84:130, 85:133}
    RUP_BASE_DMG =          {80:127, 81:130, 82:133, 83:136, 84:139, 85:142}
    RUP_BONUS_DMG =         {80:18, 81:19, 82:19, 83:19, 84:20, 85:20}
    EVIS_BASE_HIGH_DMG =    {80:493, 81:501, 82:508, 83:516, 84:523, 85:531}
    EVIS_BASE_LOW_DMG =     {80:165, 81:167, 82:170, 83:172, 84:175, 85:177}
    EVIS_BONUS_DMG =        {80:481, 81:488, 82:495, 83:503, 84:510, 85:517}
    ENV_BONUS_DMG =         {80:216, 81:221, 82:226, 83:231, 84:236, 85:241}
    AGI_PER_CRIT =          {80:83.15 * 100, 81:109.18 * 100, 82:143.37 * 100, 83:188.34 * 100, 84:247.3 * 100, 85:324.72 * 100}
    AGI_CRIT_INTERCEPT =    {80:-.00295, 85:-.00295}    # missing lvl-80 data
    MELEE_CRIT_REDUCTION = .048
    SPELL_CRIT_REDUCTION = .021

    def level_check(self, level, level_dict, spell_name):
        if level not in level_dict:
            assert False, "No %(spell_name)s formula available for level %(level)d" % {'spell_name': spell_name, 'level': level}
        else:
            return True
                
    def get_spell_hit_from_talents(self):
        return .02 * self.talents.combat.precision

    def get_melee_hit_from_talents(self):
        return .02 * self.talents.combat.precision
    
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
            base_modifier += cdg_tuple[self.talents.assassination.coup_de_grace]
        if executioner and self.talents.is_subtlety_rogue():
            base_modifier += .02 * self.stats.get_mastery_from_rating(mastery)
        if aggression:
            aggression_tuple = (0, .07, .14, .2)
            base_modifier += aggression_tuple[self.talents.combat.aggression]
        if improved_sinister_strike:
            base_modifier += .1 * (self.talents.combat.improved_sinister_strike)
        if vile_poisons:
            vp_tuple = (0, .07, .14, .2)
            base_modifier += vp_tuple[self.talents.assassination.vile_poisons]
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
        # This formula may need to be splited in two and bring the meta and
        # base_modifier to the general object if/when we start to
        # support another classes
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

    def mh_damage(self, ap, armor=None):
        weapon_damage = self.stats.mh.damage(ap)
        multiplier = self.talents_modifiers(assassins_resolve=True)
        multiplier *= self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers()

        damage = weapon_damage * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def oh_damage(self, ap, armor=None):
        weapon_damage = self.stats.oh.damage(ap)
        multiplier = self.talents_modifiers(assassins_resolve=True)
        multiplier *= self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers()

        damage = self.oh_penalty() * weapon_damage * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def backstab_damage(self, ap, armor=None):
        self.level_check(self.level, self.BS_BONUS_DMG, "backstab")
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.talents_modifiers(opportunity=True, aggression=True)
        multiplier *= self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers(lethality=True)
        percentage_damage_bonus = 2
        if self.talents.is_subtlety_rogue():
            percentage_damage_bonus += .25

        damage = percentage_damage_bonus * (weapon_damage + self.BS_BONUS_DMG[self.level]) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def mh_mutilate_damage(self, ap, is_poisoned=True, armor=None):
        self.level_check(self.level, self.MUT_BONUS_DMG, "mutilate")
        mh_weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.talents_modifiers(opportunity=True)
        multiplier *= self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers(lethality=True)

        mh_damage = 1.5 * (mh_weapon_damage + self.MUT_BONUS_DMG[self.level]) * multiplier

        if is_poisoned:
            mh_damage *= 1.2

        crit_mh_damage = mh_damage * crit_multiplier

        return mh_damage, crit_mh_damage

    def oh_mutilate_damage(self, ap, is_poisoned=True, armor=None):
        self.level_check(self.level, self.MUT_BONUS_DMG, "mutilate")
        oh_weapon_damage = self.stats.oh.normalized_damage(ap)
        multiplier = self.talents_modifiers(opportunity=True)
        multiplier *= self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers(lethality=True)

        oh_damage = 1.5 * (self.oh_penalty() * oh_weapon_damage + self.MUT_BONUS_DMG[self.level]) * multiplier

        if is_poisoned:
            oh_damage *= 1.2

        crit_oh_damage = oh_damage * crit_multiplier

        return oh_damage, crit_oh_damage

    def sinister_strike_damage(self, ap, armor=None):
        self.level_check(self.level, self.SS_BONUS_DMG, "sinister strike")
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.talents_modifiers(aggression=True, improved_sinister_strike=True)
        multiplier *= self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers(lethality=True)

        damage = (weapon_damage + self.SS_BONUS_DMG[self.level]) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def hemorrhage_damage(self, armor=None):
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.raid_settings_modifiers(is_physical=True, armor=armor)
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

    def ambush_damage(self, ap, armor=None):
        self.level_check(self.level, self.AMBUSH_BONUS_DMG, "ambush")
        weapon_damage = self.stats.mh.normalized_damage(ap)
        multiplier = self.talents_modifiers(opportunity=True, improved_ambush=True)
        multiplier *= self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers()

        if self.stats.mh.type == 'dagger':
            damage = (2.7493 * weapon_damage + self.AMBUSH_BONUS_DMG[self.level] * 2.75) * multiplier
        else:
            damage = (1.9 * weapon_damage + self.AMBUSH_BONUS_DMG[self.level] * 1.9) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def revealing_strike_damage(self, ap, armor=None):
        weapon_damage = self.stats.mh.damage(ap)
        multiplier = self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers()

        damage = 1.25 * weapon_damage * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def venomous_wounds_damage(self, ap, mastery=None):
        self.level_check(self.level, self.VW_BASE_DMG, "venomous wounds")
        self.level_check(self.level, self.VW_PERCENTAGE_DMG, "venomous wounds")
        multiplier = self.talents_modifiers(potent_poisons=True, assassins_resolve=False, mastery=mastery)
        multiplier *= self.raid_settings_modifiers(is_spell=True)
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        damage = (self.VW_BASE_DMG[self.level] + self.VW_PERCENTAGE_DMG[self.level] * ap) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def main_gauche(self, ap, armor=None):
        weapon_damage = self.stats.oh.normalized_damage(ap)
        multiplier = self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers()

        damage = self.oh_penalty() * weapon_damage * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def instant_poison_damage(self, ap, mastery=None):
        self.level_check(self.level, self.IP_LOW_BASE_DMG, "Instant Poison")
        self.level_check(self.level, self.IP_HIGH_BASE_DMG, "Instant Poison")
        multiplier = self.talents_modifiers(potent_poisons=True, vile_poisons=True,
                                       assassins_resolve=False, mastery=mastery)
        multiplier *= self.raid_settings_modifiers(is_spell=True)
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        low_end_damage = (self.IP_LOW_BASE_DMG[self.level] + 0.09 * ap) * multiplier
        high_end_damage = (self.IP_HIGH_BASE_DMG[self.level] + 0.09 * ap) * multiplier
        average_damage = (low_end_damage + high_end_damage) / 2
        average_crit_damage = average_damage * crit_multiplier

        return average_damage, average_crit_damage

    def deadly_poison_tick_damage(self, ap, mastery=None, dp_stacks=5):
        self.level_check(self.level, self.DP_BASE_DMG, "Deadly Poison")
        self.level_check(self.level, self.DP_PERCENTAGE_DMG, "Deadly Poison")
        multiplier = self.talents_modifiers(potent_poisons=True, vile_poisons = True,
                                       assassins_resolve=False, mastery=mastery)
        multiplier *= self.raid_settings_modifiers(is_spell=True)
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        tick_damage = ((self.DP_BASE_DMG[self.level] + self.DP_PERCENTAGE_DMG[self.level] * ap) * dp_stacks / 4) * multiplier
        crit_tick_damage = tick_damage * crit_multiplier

        return tick_damage, crit_tick_damage

    def wound_poison_damage(self, ap, mastery=None):
        self.level_check(self.level, self.WP_BASE_DMG, "Wound Poison")
        self.level_check(self.level, self.WP_PERCENTAGE_DMG, "Wound Poison")
        multiplier = self.talents_modifiers(potent_poisons=True, vile_poisons = True,
                                       assassins_resolve=False, mastery=mastery)
        multiplier *= self.raid_settings_modifiers(is_spell=True)
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        damage = (self.WP_BASE_DMG[self.level] + self.WP_PERCENTAGE_DMG[self.level] * ap) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def garrote_tick_damage(self, ap):
        self.level_check(self.level, self.GARROTE_BASE_DMG, "Garrote")
        multiplier = self.talents_modifiers(opportunity=True, assassins_resolve=False)
        multiplier *= self.raid_settings_modifiers(is_bleed=True)
        crit_multiplier = self.crit_damage_modifiers()

        tick_damage = (self.GARROTE_BASE_DMG[self.level] +  ap * 1 * 0.07) * multiplier
        crit_tick_damage = tick_damage * crit_multiplier

        return tick_damage, crit_tick_damage

    def rupture_tick_damage(self, ap, cp):
        self.level_check(self.level, self.RUP_BASE_DMG, "Rupture")
        self.level_check(self.level, self.RUP_BONUS_DMG, "Rupture")
        # Assassasin's resolve was tested on melee, poisons, weapon strikes and
        # ap strikes, not bleeds. Although there's no reason to believe it doesn't
        # affect bleeds, I'm setting it to false until some testing is done
        multiplier = self.talents_modifiers(executioner=True, assassins_resolve=False)
        multiplier *= self.raid_settings_modifiers(is_bleed=True)
        crit_multiplier = self.crit_damage_modifiers()

        ap_multiplier_tuple = (0, .015, .024, .03, .03428571, .0375)
        tick_damage = (self.RUP_BASE_DMG[self.level] + self.RUP_BONUS_DMG[self.level] * cp + ap_multiplier_tuple[cp] * ap) * multiplier
        crit_tick_damage = tick_damage * crit_multiplier

        # leaving full duration damage formulas in comments just in case
        # this value is usefull somehow somewhen somewhere
        # duration = (6 + cp * 2)
        #     if self.glyphs.rupture():
        # duration +=4
        # damage = tick_damage * .5 * duration

        return tick_damage, crit_tick_damage

    def eviscerate_damage(self, ap, cp, armor=None):
        self.level_check(self.level, self.EVIS_BASE_LOW_DMG, "Eviscerate")
        self.level_check(self.level, self.EVIS_BASE_HIGH_DMG, "Eviscerate")
        self.level_check(self.level, self.EVIS_BONUS_DMG, "Eviscerate")
        multiplier = self.talents_modifiers(coup_de_grace=True, aggression=True, executioner=True)
        multiplier *= self.raid_settings_modifiers(is_physical=True, armor=armor)
        crit_multiplier = self.crit_damage_modifiers()

        ap_multiplier_tuple = (0, .091, .182, .273, .364, .455)
        low_end_damage = (self.EVIS_BASE_LOW_DMG[self.level] + self.EVIS_BONUS_DMG[self.level] * cp + ap_multiplier_tuple[cp] * ap) * multiplier
        high_end_damage = (self.EVIS_BASE_HIGH_DMG[self.level] + self.EVIS_BONUS_DMG[self.level] * cp + ap_multiplier_tuple[cp] * ap) * multiplier
        average_damage = (low_end_damage + high_end_damage) / 2
        average_crit_damage = average_damage * crit_multiplier

        return average_damage, average_crit_damage

    def envenom_damage(self, ap, cp):
        # Envemom has a dependency on dp_charges too; but being unlikely to be used out of builds
        # with master poisoner I'm not including that for the moment
        self.level_check(self.level, self.ENV_BONUS_DMG, "Envenom")
        multiplier = self.talents_modifiers(coup_de_grace=True, executioner=True, assassins_resolve=False)
        multiplier *= self.raid_settings_modifiers(is_spell=True)
        crit_multiplier = self.crit_damage_modifiers(is_spell=True)

        damage = (self.ENV_BONUS_DMG[self.level] * cp + .09 * cp * ap) * multiplier
        crit_damage = damage * crit_multiplier

        return damage, crit_damage

    def melee_crit_rate(self, agi=None, crit=None):
        self.level_check(self.level, self.AGI_CRIT_INTERCEPT, "Agi per Crit")
        self.level_check(self.level, self.AGI_PER_CRIT, "Agi per Crit")
        if agi == None:
            agi = self.stats.agi
        base_crit = self.AGI_CRIT_INTERCEPT[self.level] + agi / self.AGI_PER_CRIT[self.level]
        base_crit += self.stats.get_crit_from_rating(crit)
        return base_crit + self.buffs.buff_all_crit() - self.MELEE_CRIT_REDUCTION

    def spell_crit_rate(self, crit=None):
        base_crit = self.stats.get_crit_from_rating(crit)
        return base_crit + self.buffs.buff_all_crit() + self.buffs.buff_spell_crit() - self.SPELL_CRIT_REDUCTION

    # Not strictly speaking rogue-specific, but given that the base object
    # doesn't currently have any notion of whether you'd dual-wielding or not
    # (and this calculation depends on that), I'm going to leave this here
    # until we figure out how to handle that.
    #
    # Also has a dependency on (target_level - attacker_level), but ignoring
    # that for now.
    def crit_cap(self):
        return self.dual_wield_melee_hit_chance - .24
