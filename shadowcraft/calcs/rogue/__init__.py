import gettext
import __builtin__

__builtin__._ = gettext.gettext

from shadowcraft.calcs import DamageCalculator
from shadowcraft.core import exceptions

class RogueDamageCalculator(DamageCalculator):
    # Functions of general use to rogue damage calculation go here. If a
    # calculation will reasonably used for multiple classes, it should go in
    # calcs.DamageCalculator instead. If its a specific intermediate
    # value useful to only your calculations, when you extend this you should
    # put the calculations in your object. But there are things - like
    # backstab damage as a function of AP - that (almost) any rogue damage
    # calculator will need to know, so things like that go here.

    # Factors for levels other than 90 haven't been checked.
    bs_bonus_dmg_values =         {80:310, 81:317, 82:324, 83:331, 84:338, 85:345, 90:1053}
    dsp_bonus_dmg_values =        {85:1, 90:1340}
    mut_bonus_dmg_values =        {80:180, 85:201, 90:446}
    ss_bonus_dmg_values =         {80:180, 81:184, 82:188, 83:192, 84:196, 85:200, 90:388}
    ambush_bonus_dmg_values =     {80:330, 81:338, 82:345, 83:353, 84:360, 85:368, 90:1000}
    vw_base_dmg_values =          {80:363, 85:675, 90:1} # Needs testing
    vw_percentage_dmg_values =    {80:.135, 85:.176, 90:.1} # Needs testing
    ip_base_dmg_values =          {80:350, 85:352, 90:1} # Secondary effect of DP. Needs testing
    dp_base_dmg_values =          {80:296, 85:540, 90:1} # Needs testing
    dp_percentage_dmg_values =    {80:.108, 85:.14, 90:.1} # Needs testing
    wp_base_dmg_values =          {80:231, 85:276, 90:1} # Needs testing
    wp_percentage_dmg_values =    {80:.036, 85:.04, 90:.01} # Needs testing
    garrote_base_dmg_values =     {80:119, 81:122, 82:125, 83:127, 84:130, 85:133, 90:147}
    rup_base_dmg_values =         {80:127, 81:130, 82:133, 83:136, 84:139, 85:142, 90:231}
    rup_bonus_dmg_values =        {80:18, 81:19, 82:19, 83:19, 84:20, 85:20, 90:32}
    evis_base_dmg_values =        {80:329, 81:334, 82:339, 83:344, 84:349, 85:354, 90:590.5}
    evis_bonus_dmg_values =       {80:481, 81:488, 82:495, 83:503, 84:510, 85:517, 90:862}
    env_base_dmg_values =         {80:216, 81:221, 82:226, 83:231, 84:236, 85:241, 90:400}
    agi_per_crit_values =         {80:83.15 * 100, 81:109.18 * 100, 82:143.37 * 100, 83:188.34 * 100, 84:247.3 * 100, 85:324.72 * 100, 90:1259.51806640625 * 100}
    AGI_CRIT_INTERCEPT =          -.00295
    MELEE_CRIT_REDUCTION =        .03 # 1% * level_diff
    SPELL_CRIT_REDUCTION =        .03

    default_ep_stats = ['white_hit', 'spell_hit', 'yellow_hit', 'str', 'agi', 'haste',
        'crit', 'mastery', 'dodge_exp']
    normalize_ep_stat = 'ap'

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'level':
            self._set_constants_for_level()

    def _set_constants_for_level(self):
        super(RogueDamageCalculator, self)._set_constants_for_level()
        try:
            self.bs_bonus_dmg =          self.bs_bonus_dmg_values[self.level]
            self.dsp_bonus_dmg =         self.dsp_bonus_dmg_values[self.level]
            self.mut_bonus_dmg =         self.mut_bonus_dmg_values[self.level]
            self.ss_bonus_dmg =          self.ss_bonus_dmg_values[self.level]
            self.ambush_bonus_dmg =      self.ambush_bonus_dmg_values[self.level]
            self.vw_base_dmg =           self.vw_base_dmg_values[self.level]
            self.vw_percentage_dmg =     self.vw_percentage_dmg_values[self.level]
            self.ip_base_dmg =           self.ip_base_dmg_values[self.level]
            self.dp_base_dmg =           self.dp_base_dmg_values[self.level]
            self.dp_percentage_dmg =     self.dp_percentage_dmg_values[self.level]
            self.wp_base_dmg =           self.wp_base_dmg_values[self.level]
            self.wp_percentage_dmg =     self.wp_percentage_dmg_values[self.level]
            self.garrote_base_dmg =      self.garrote_base_dmg_values[self.level]
            self.rup_base_dmg =          self.rup_base_dmg_values[self.level]
            self.rup_bonus_dmg =         self.rup_bonus_dmg_values[self.level]
            self.evis_base_dmg =         self.evis_base_dmg_values[self.level]
            self.evis_bonus_dmg =        self.evis_bonus_dmg_values[self.level]
            self.env_base_dmg =          self.env_base_dmg_values[self.level]
            self.agi_per_crit =          self.agi_per_crit_values[self.level]
        except KeyError as e:
            print e
            raise exceptions.InvalidLevelException(_('No {spell_name} formula available for level {level}').format(spell_name=str(e), level=self.level))

    def get_weapon_damage_bonus(self):
        # Override this in your modeler to implement weapon damage boosts
        # such as Unheeded Warning.
        return 0

    def get_weapon_damage(self, hand, ap, is_normalized=True):
        weapon = getattr(self.stats, hand)
        if is_normalized:
            damage = weapon.normalized_damage(ap) + self.get_weapon_damage_bonus()
        else:
            damage = weapon.damage(ap) + self.get_weapon_damage_bonus()
        return damage

    def oh_penalty(self):
        if self.settings.cycle._cycle_type == 'combat':
            return .875
        else:
            return .5

    def get_modifiers(self, *args, **kwargs):
        base_modifier = 1
        kwargs.setdefault('mastery', None)
        if 'executioner' in args and self.settings.cycle._cycle_type == 'subtlety':
            base_modifier += .025 * self.stats.get_mastery_from_rating(kwargs['mastery'])
        if 'potent_poisons' in args and self.settings.cycle._cycle_type == 'assassination':
            base_modifier += .035 * self.stats.get_mastery_from_rating(kwargs['mastery'])
        # Assassasins's Resolve
        if self.settings.cycle._cycle_type == 'assassination' and (self.stats.mh.type == 'dagger'):
            base_modifier *= 1.2
        # Sanguinary Vein
        kwargs.setdefault('is_bleeding', True)
        if kwargs['is_bleeding'] == True and self.settings.cycle._cycle_type == 'subtlety':
            base_modifier *= 1.25
        # Raid modifiers
        kwargs.setdefault('armor', None)
        ability_type_check = 0
        for i in ['physical', 'bleed', 'spell']:
            if i in args:
                ability_type_check += 1
                base_modifier *= self.raid_settings_modifiers(i, kwargs['armor'])
        assert ability_type_check == 1

        crit_modifier = self.crit_damage_modifiers()

        return base_modifier, crit_modifier

    def mh_damage(self, ap, armor=None, is_bleeding=True):
        weapon_damage = self.get_weapon_damage('mh', ap, is_normalized=False)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        damage = weapon_damage * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def oh_damage(self, ap, armor=None, is_bleeding=True):
        weapon_damage = self.get_weapon_damage('oh', ap, is_normalized=False)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        damage = self.oh_penalty() * weapon_damage * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def backstab_damage(self, ap, armor=None, is_bleeding=True):
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        damage = 2.75 * (weapon_damage + self.bs_bonus_dmg) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def dispatch_damage(self, ap, armor=None):
        # needs testing: is it normalized?
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        damage = 3.5 * (weapon_damage + self.dsp_bonus_dmg) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def mh_mutilate_damage(self, ap, armor=None):
        mh_weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        mh_damage = 2. * (mh_weapon_damage + self.mut_bonus_dmg) * mult
        crit_mh_damage = mh_damage * crit_mult

        return mh_damage, crit_mh_damage

    def oh_mutilate_damage(self, ap, armor=None):
        oh_weapon_damage = self.get_weapon_damage('oh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        oh_damage = 2 * (self.oh_penalty() * oh_weapon_damage + self.mut_bonus_dmg) * mult
        crit_oh_damage = oh_damage * crit_mult

        return oh_damage, crit_oh_damage

    def sinister_strike_damage(self, ap, armor=None, is_bleeding=True):
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        damage = 1.75 * (weapon_damage + self.ss_bonus_dmg) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def hemorrhage_damage(self, ap, armor=None, is_bleeding=True):
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        percentage_damage_bonus = [1.4, 2.03][self.stats.mh.type == 'dagger']

        damage = percentage_damage_bonus * weapon_damage * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def hemorrhage_tick_damage(self, ap, from_crit_hemo=False, armor=None):
        # Call this function twice to get all four crit/non-crit hemo values.
        hemo_damage = self.hemorrhage_damage(ap, armor=armor)[from_crit_hemo]
        mult, crit_mult = self.get_modifiers('bleed')

        tick_conversion_factor = .4 / 8
        tick_damage = hemo_damage * mult * tick_conversion_factor
        crit_tick_damage = tick_damage * crit_mult

        return tick_damage, crit_tick_damage

    def ambush_damage(self, ap, armor=None, is_bleeding=True):
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        dagger_bonus = [1, 1.447][self.stats.mh.type == 'dagger']
        percentage_damage_bonus = 2.45 * dagger_bonus
        bonus_dmg = self.ambush_bonus_dmg * dagger_bonus

        damage = percentage_damage_bonus * (weapon_damage + self.ambush_bonus_dmg) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def revealing_strike_damage(self, ap, armor=None):
        weapon_damage = self.get_weapon_damage('mh', ap, is_normalized=False)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        damage = 1.5 * weapon_damage * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def venomous_wounds_damage(self, ap, mastery=None):
        mult, crit_mult = self.get_modifiers('spell', 'potent_poisons', mastery=mastery)

        damage = (self.vw_base_dmg + self.vw_percentage_dmg * ap) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def main_gauche_damage(self, ap, armor=None):
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        damage = 1.2 * weapon_damage * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def mh_killing_spree_damage(self, ap, armor=None):
        mh_weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        mh_damage = mh_weapon_damage * mult
        crit_mh_damage = mh_damage * crit_mult

        return mh_damage, crit_mh_damage

    def oh_killing_spree_damage(self, ap, armor=None):
        oh_weapon_damage = self.get_weapon_damage('oh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        oh_damage = self.oh_penalty() * oh_weapon_damage * mult
        crit_oh_damage = oh_damage * crit_mult

        return oh_damage, crit_oh_damage

    def mh_shadow_blades_damage(self, ap, is_bleeding=True):
        # TODO: normalized? percentage modifier? confirmed master poisoner stacks.
        mh_weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('spell', is_bleeding=is_bleeding)

        mh_damage = mh_weapon_damage * mult
        crit_mh_damage = mh_damage * crit_mult

        return mh_damage, crit_mh_damage

    def oh_shadow_blades_damage(self, ap, is_bleeding=True):
        # TODO
        oh_weapon_damage = self.get_weapon_damage('oh', ap)
        mult, crit_mult = self.get_modifiers('spell', is_bleeding=is_bleeding)

        oh_damage = oh_weapon_damage * mult
        crit_mh_damage = oh_damage * crit_mult

        return oh_damage, crit_oh_damage

    def instant_poison_damage(self, ap, mastery=None, is_bleeding=True):
        # Deprecated
        mult, crit_mult = self.get_modifiers('spell', 'potent_poisons', mastery=mastery, is_bleeding=is_bleeding)

        damage = (self.ip_base_dmg + 0.09 * ap) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def deadly_poison_tick_damage(self, ap, mastery=None, is_bleeding=True):
        mult, crit_mult = self.get_modifiers('spell', 'potent_poisons', mastery=mastery, is_bleeding=is_bleeding)

        # doesn't have charges
        tick_damage = ((self.dp_base_dmg + self.dp_percentage_dmg * ap) * 1.25) * mult
        crit_tick_damage = tick_damage * crit_mult

        return tick_damage, crit_tick_damage

    def deadly_instant_poison_damage(self, ap, mastery=None, is_bleeding=True):
        # TODO http://www.wowdb.com/spells/113780-deadly-poison
        mult, crit_mult = self.get_modifiers('spell', 'potent_poisons', mastery=mastery, is_bleeding=is_bleeding)

        damage = None
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def wound_poison_damage(self, ap, mastery=None, is_bleeding=True):
        mult, crit_mult = self.get_modifiers('spell', 'potent_poisons', mastery=mastery, is_bleeding=is_bleeding)

        damage = (self.wp_base_dmg + self.wp_percentage_dmg * ap) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def garrote_tick_damage(self, ap):
        mult, crit_mult = self.get_modifiers('bleed')

        tick_damage = (self.garrote_base_dmg + ap * 1 * 0.078) * mult
        crit_tick_damage = tick_damage * crit_mult

        return tick_damage, crit_tick_damage

    def rupture_tick_damage(self, ap, cp):
        mult, crit_mult = self.get_modifiers('bleed', 'executioner')

        ap_multiplier_tuple = (0, .025, .04, .05, .056, .062)
        tick_damage = (self.rup_base_dmg + self.rup_bonus_dmg * cp + ap_multiplier_tuple[cp] * ap) * mult
        crit_tick_damage = tick_damage * crit_mult

        # leaving full duration damage formulas in comments just in case
        # this value is usefull somehow somewhen somewhere
        # duration = (6 + cp * 2)
        #     if self.glyphs.rupture():
        # duration +=4
        # damage = tick_damage * .5 * duration

        return tick_damage, crit_tick_damage

    def eviscerate_damage(self, ap, cp, armor=None, is_bleeding=True):
        mult, crit_mult = self.get_modifiers('physical', 'executioner', is_bleeding=is_bleeding)

        damage = (self.evis_base_dmg + self.evis_bonus_dmg * cp + .16 * cp * ap) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def envenom_damage(self, ap, cp, mastery=None):
        mult, crit_mult = self.get_modifiers('spell', 'executioner', 'potent_poisons', mastery=mastery)

        damage = (self.env_base_dmg * cp + .112 * cp * ap) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def fan_of_knives_damage(self, ap, is_bleeding=True):
        # TODO
        pass

    def crimson_tempest_damage(self, ap, cp, mastery=None, is_bleeding=True):
        # TODO
        pass

    def shiv_damage(self, ap, is_bleeding=True):
        pass

    def throw_damage(self, ap, is_bleeding=True):
        if self.talents.shuriken_toss:
            return self.shuriken_toss_damage(ap, is_bleeding=is_bleeding)
        pass

    def shuriken_toss_damage(self, ap, is_bleeding=True):
        pass

    def gouge_damage(self, ap, is_bleeding=True):
        pass

    def melee_crit_rate(self, agi=None, crit=None):
        if agi == None:
            agi = self.stats.agi
        base_crit = self.AGI_CRIT_INTERCEPT + agi / self.agi_per_crit
        base_crit += self.stats.get_crit_from_rating(crit)
        return base_crit + self.buffs.buff_all_crit() + self.race.get_racial_crit() - self.MELEE_CRIT_REDUCTION

    def spell_crit_rate(self, crit=None):
        base_crit = self.stats.get_crit_from_rating(crit)
        return base_crit + self.buffs.buff_all_crit() + self.buffs.buff_spell_crit() + self.race.get_racial_crit() - self.SPELL_CRIT_REDUCTION
