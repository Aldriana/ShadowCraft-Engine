from calcs import DamageCalculator

class RogueDamageCalculator(DamageCalculator):
    # Functions of general use to rogue damage calculation go here.  If a
    # calculation will reasonably used for multiple classes, it should go in
    # calcs.DamageCalculator instead.  If its a specific intermediate
    # value useful to only your calculations, when you extend this you should
    # put the calculations in your object.  But there are things - like
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

    def assassins_resolve(self):
        return self.talents.is_assassination_rogue() and (self.stats.mh.type == 'dagger')


    def backstab_damage(self, ap):
        weapon_damage = self.stats.mh.normalized_damage(ap)

        opportunity_multiplier = 1 + .1 * (self.talents.subtlety.opportunity)
        aggression_multiplier = 1 + .05 * (self.talents.combat.aggression)
        damage = 2 * (weapon_damage + 345) * opportunity_multiplier * aggression_multiplier

        if self.assassins_resolve():
            damage *= 1.15

        return damage

    def mutilate_damage(self, ap, is_poisoned=True):
        mh_weapon_damage = self.stats.mh.normalized_damage(ap)
        oh_weapon_damage = self.stats.oh.normalized_damage(ap)

        opportunity_multiplier = 1 + .1 * (self.talents.subtlety.opportunity)

        # Including Assassin's Resolve without checking, as it's impossible to
        # mutilate without Assassin's Resolve being active.
        mh_damage = (1.5 * mh_weapon_damage + 201) * opportunity_multiplier * 1.15
        oh_damage = self.oh_penalty() * (1.5 * oh_weapon_damage + 201) * opportunity_multiplier * 1.15

        if is_poisoned:
            mh_damage *= 1.2
            oh_damage *= 1.2

        return mh_damage, oh_damage

    def melee_crit_rate(self, agi=None, crit=None):
        if agi == None:
            agi = self.stats.agi
        base_crit = self.AGI_CRIT_INTERCEPT + agi /  self.AGI_PER_CRIT
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
