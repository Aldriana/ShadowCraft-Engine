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

    default_ep_stats = ['white_hit', 'yellow_hit', 'str', 'agi', 'haste',
        'crit', 'mastery', 'dodge_exp', 'spell_hit', 'spell_exp']
    normalize_ep_stat = 'ap'

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'level':
            self._set_constants_for_level()

    def _set_constants_for_level(self):
        super(RogueDamageCalculator, self)._set_constants_for_level()
        self.agi_per_crit = self.tools.get_agi_per_crit('rogue', self.level) * 100

        # These factors are taken from sc_spell_data.inc in SimulationCraft.
        # At some point we should automate the process to fetch them. Numbers
        # in comments show the id for the spell effect, not the spell itself.
        self.spell_scaling_for_level = self.tools.get_spell_scaling('rogue', self.level)
        self.bs_bonus_dmg =     self.get_factor(0.3070000112) # 30
        self.dsp_bonus_dmg =    self.get_factor(0.3899999857) # 123503
        self.mut_bonus_dmg =    self.get_factor(0.1790000051) # 1920, 17065
        self.ss_bonus_dmg =     self.get_factor(0.1780000031) # 535
        self.ambush_bonus_dmg = self.get_factor(0.5000000000) # 3612
        self.vw_base_dmg =      self.get_factor(0.5500000119) # 68389
        self.dp_base_dmg =      self.get_factor(0.6000000238) # 853
        self.ip_base_dmg =      self.get_factor(0.3129999936, 0.2800000012) # 126788
        self.wp_base_dmg =      self.get_factor(0.3129999936, 0.2800000012) # 3617
        self.garrote_base_dmg = self.get_factor(0.1180000007) # 280
        self.rup_base_dmg =     self.get_factor(0.1850000024) # 586
        self.rup_bonus_dmg =    self.get_factor(0.0260000005) # 586 - 'unknown' field
        self.evis_base_dmg =    self.get_factor(0.5929999948,  1.0000000000) # 622
        self.evis_bonus_dmg =   self.get_factor(0.7860000134) # 622 - 'unknown' field
        self.env_base_dmg =     self.get_factor(0.3210000098) # 22420
        self.ct_base_dmg =      self.get_factor(0.4760000110) # 50471
        self.fok_base_dmg =     self.get_factor(1.0000000000, 0.4000000060) # 44107
        self.st_base_dmg =      self.get_factor(1.0000000000) # 127100
        self.vw_percentage_dmg = .168
        self.dp_percentage_dmg = .213
        self.wp_percentage_dmg = .090
        self.ip_percentage_dmg = .109

    def get_factor(self, avg, delta=0):
        avg_for_level = avg * self.spell_scaling_for_level
        if delta == 0:
            return round(avg_for_level)
        else:
            min = round(avg_for_level * (1 - delta / 2))
            max = round(avg_for_level * (1 + delta / 2))
            return (min + max) / 2 # Not rounded: this is the average for us.

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
        if self.settings.is_combat_rogue():
            return .875
        else:
            return .5

    def get_modifiers(self, *args, **kwargs):
        # A note on stacking: both executioner and potent poisons are expected
        # to stack additively as per my notes on issue #12. In mists they don't
        # have anything to stack additively with.
        base_modifier = 1
        kwargs.setdefault('mastery', None)
        if 'executioner' in args and self.settings.is_subtlety_rogue():
            base_modifier += .03 * self.stats.get_mastery_from_rating(kwargs['mastery'])
        if 'potent_poisons' in args and self.settings.is_assassination_rogue():
            base_modifier += .035 * self.stats.get_mastery_from_rating(kwargs['mastery'])
        # Assassasins's Resolve
        if self.settings.is_assassination_rogue() and (self.stats.mh.type == 'dagger'):
            base_modifier *= 1.2
        # Sanguinary Vein
        kwargs.setdefault('is_bleeding', True)
        if kwargs['is_bleeding'] and self.settings.is_subtlety_rogue():
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
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        damage = 4.5 * (weapon_damage + self.dsp_bonus_dmg) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def mh_mutilate_damage(self, ap, armor=None):
        mh_weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        mh_damage = 2.0 * (mh_weapon_damage + self.mut_bonus_dmg) * mult
        crit_mh_damage = mh_damage * crit_mult

        return mh_damage, crit_mh_damage

    def oh_mutilate_damage(self, ap, armor=None):
        oh_weapon_damage = self.get_weapon_damage('oh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        oh_damage = 2.0 * (self.oh_penalty() * oh_weapon_damage + self.mut_bonus_dmg) * mult
        crit_oh_damage = oh_damage * crit_mult

        return oh_damage, crit_oh_damage

    def sinister_strike_damage(self, ap, armor=None, is_bleeding=True):
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        damage = 1.55 * (weapon_damage + self.ss_bonus_dmg) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def hemorrhage_damage(self, ap, armor=None, is_bleeding=True):
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        percentage_damage_bonus = [1.4, 2.03][self.stats.mh.type == 'dagger']

        damage = percentage_damage_bonus * weapon_damage * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def hemorrhage_tick_damage(self, ap, from_crit_hemo=False, armor=None, is_bleeding=True):
        # Call this function twice to get all four crit/non-crit hemo values.
        hemo_damage = self.hemorrhage_damage(ap, armor=armor, is_bleeding=is_bleeding)[from_crit_hemo]
        mult, crit_mult = self.get_modifiers('bleed')

        tick_conversion_factor = .5 / 8
        tick_damage = hemo_damage * mult * tick_conversion_factor

        return tick_damage, tick_damage #can't crit in 5.0 anymore, the lazy solution

    def ambush_damage(self, ap, armor=None, is_bleeding=True):
        #TODO clean up
        weapon_damage = self.get_weapon_damage('mh', ap)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        dagger_bonus = [1, 1.447][self.stats.mh.type == 'dagger']
        percentage_damage_bonus = 3.45 * dagger_bonus

        damage = percentage_damage_bonus * (weapon_damage + self.ambush_bonus_dmg) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def revealing_strike_damage(self, ap, armor=None):
        weapon_damage = self.get_weapon_damage('mh', ap, is_normalized=False)
        mult, crit_mult = self.get_modifiers('physical', armor=armor)

        damage = 1.35 * weapon_damage * mult
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

        oh_damage = self.oh_penalty() * oh_weapon_damage * mult
        crit_oh_damage = oh_damage * crit_mult

        return oh_damage, crit_oh_damage

    def deadly_poison_tick_damage(self, ap, mastery=None, is_bleeding=True):
        mult, crit_mult = self.get_modifiers('spell', 'potent_poisons', mastery=mastery, is_bleeding=is_bleeding)

        tick_damage = (self.dp_base_dmg + self.dp_percentage_dmg * ap) * mult
        crit_tick_damage = tick_damage * crit_mult

        return tick_damage, crit_tick_damage

    def deadly_instant_poison_damage(self, ap, mastery=None, is_bleeding=True):
        mult, crit_mult = self.get_modifiers('spell', 'potent_poisons', mastery=mastery, is_bleeding=is_bleeding)

        damage = (self.ip_base_dmg + self.ip_percentage_dmg * ap) * mult
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

    def rupture_tick_damage(self, ap, cp, mastery=None):
        #TODO: check the tick conversion logic
        mult, crit_mult = self.get_modifiers('bleed', 'executioner', mastery=mastery)

        ap_multiplier_tuple = (0, .025, .04, .05, .056, .062)
        tick_damage = (self.rup_base_dmg + self.rup_bonus_dmg * cp + ap_multiplier_tuple[cp] * ap) * mult
        crit_tick_damage = tick_damage * crit_mult

        return tick_damage, crit_tick_damage

    def eviscerate_damage(self, ap, cp, armor=None, mastery=None, is_bleeding=True):
        mult, crit_mult = self.get_modifiers('physical', 'executioner', mastery=mastery, armor=armor, is_bleeding=is_bleeding)

        damage = (self.evis_base_dmg + self.evis_bonus_dmg * cp + .16 * cp * ap) * mult
        crit_damage = damage * crit_mult
        
        return damage, crit_damage

    def envenom_damage(self, ap, cp, mastery=None):
        mult, crit_mult = self.get_modifiers('spell', 'executioner', 'potent_poisons', mastery=mastery)

        damage = (self.env_base_dmg * cp + .112 * cp * ap) * mult
        crit_damage = damage * crit_mult

        return damage, crit_damage

    def fan_of_knives_damage(self, ap, armor=None, is_bleeding=True):
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)
        
        damage = (self.fok_base_dmg + .14 * ap) * mult
        crit_damage = damage * crit_mult
        
        return damage, crit_damage

    def crimson_tempest_damage(self, ap, cp, armor=None, mastery=None):
        # TODO this doesn't look right
        mult, crit_mult = self.get_modifiers('physical', 'executioner', mastery=mastery, armor=armor)
        
        damage = (self.ct_base_dmg + .0275 * cp * ap) * mult
        crit_damage = damage * crit_mult
        
        return damage, crit_damage

    def crimson_tempest_tick_damage(self, ap, cp, armor=None, mastery=None, from_crit_ct=False):
        ct_damage = self.crimson_tempest_damage(ap, cp, armor=armor, mastery=mastery)[from_crit_ct]
        mult, crit_mult = self.get_modifiers('bleed', is_bleeding=True)

        tick_conversion_factor = .3 / 6
        tick_damage = ct_damage * mult * tick_conversion_factor

        return tick_damage, tick_damage

    def shiv_damage(self, ap, armor=None, is_bleeding=True):
        # TODO this doesn't look right
        oh_weapon_damage = self.get_weapon_damage('oh', ap, is_normalized=False)
        mult, crit_mult = self.get_modifiers('physical', armor=armor, is_bleeding=is_bleeding)

        oh_damage = .25 * (self.oh_penalty() * oh_weapon_damage) * mult
        crit_oh_damage = oh_damage * crit_mult

        return oh_damage, crit_oh_damage

    def throw_damage(self, ap, is_bleeding=True):
        mult, crit_mult = self.get_modifiers('physical', is_bleeding=is_bleeding)
        
        damage = (249.2595 + .05 * ap) * mult
        crit_damage = damage * crit_mult
        
        return damage, crit_damage

    def shuriken_toss_damage(self, ap, is_bleeding=True):
        # TODO verify data
        mult, crit_mult = self.get_modifiers('physical', is_bleeding=is_bleeding)
        
        damage = (self.st_base_dmg + .3 * ap) * mult
        crit_damage = damage * crit_mult
        
        return damage, crit_damage

    def get_formula(self, name):
        # TODO: Not finished
        formulas = {
            'backstab':              self.backstab_damage,
            'hemorrhage':            self.hemorrhage_damage,
            'sinister_strike':       self.sinister_strike_damage,
            'revealing_strike':      self.revealing_strike_damage,
            'main_gauche':           self.main_gauche_damage,
            'ambush':                self.ambush_damage,
            'eviscerate':            self.eviscerate_damage,
            'dispatch':              self.dispatch_damage,
            'mh_mutilate':           self.mh_mutilate_damage,
            'oh_mutilate':           self.oh_mutilate_damage,
            'mh_shadow_blade':       self.mh_shadow_blades_damage,
            'oh_shadow_blade':       self.oh_shadow_blades_damage,
            'venomous_wounds':       self.venomous_wounds_damage,
            'deadly_poison':         self.deadly_poison_tick_damage,
            'wound_poison':          self.wound_poison_damage,
            'deadly_instant_poison': self.deadly_instant_poison_damage
        }
        return formulas[name]

    def get_spell_stats(self, ability):
        base_cost = {
            'ambush':              (60, 'strike'),
            'backstab':            (35, 'strike'),
            'dispatch':            (30, 'strike'),
            'envenom':             (35, 'strike'),
            'eviscerate':          (35, 'strike'),
            'garrote':             (45, 'strike'),
            'hemorrhage':          (30, 'strike'),
            'mutilate':            (55, 'strike'),
            'recuperate':          (30, 'buff'),
            'revealing_strike':    (40, 'strike'),
            'rupture':             (25, 'strike'),
            'sinister_strike':     (40, 'strike'),
            'slice_and_dice':      (25, 'buff'),
            'tricks_of_the_trade': (15, 'buff'),
            # 'crimson_tempest':     (35, 'strike'),
            # 'deadly_throw':        (35, 'strike'),
            # 'expose_armor':        (25, 'strike'),
            # 'feint':               (20, 'buff'),
            # 'fan_of_knives':       (35, 'point_blank'),
            # 'shuriken_toss':       (20, 'strike'),
            # 'blind':               (15, 'debuff'),
            # 'burst_of_speed':      (60, 'buff'),
            # 'cheap_shot':          (40, 'debuff'),
            # 'dismantle':           (25, 'debuff'),
            # 'distract':            (30, 'debuff'),
            # 'gouge':               (45, 'debuff'),
            # 'kick':                (15, 'debuff'),
            # 'kidney_shot':         (25, 'debuff'),
            # 'sap':                 (35, 'debuff'),
            # 'shiv':                (20, 'strike'),
        }
        return base_cost[ability]

    def melee_crit_rate(self, agi=None, crit=None):
        if agi == None:
            agi = self.stats.agi
        base_crit = self.agi_crit_intercept + agi / self.agi_per_crit
        base_crit += self.stats.get_crit_from_rating(crit)
        return base_crit + self.buffs.buff_all_crit() + self.race.get_racial_crit() - self.melee_crit_reduction

    def spell_crit_rate(self, crit=None):
        base_crit = self.stats.get_crit_from_rating(crit)
        return base_crit + self.buffs.buff_all_crit() + self.buffs.buff_spell_crit() + self.race.get_racial_crit() - self.spell_crit_reduction
