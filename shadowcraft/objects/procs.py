from shadowcraft.core import exceptions
from shadowcraft.objects import proc_data

class InvalidProcException(exceptions.InvalidInputException):
    pass


class Proc(object):
    allowed_behaviours = proc_data.behaviours

    def __init__(self, stat, value, duration, proc_name, behaviours, max_stacks=1, can_crit=True, stats=None):
        self.stat = stat
        if stats is not None:
            self.stats = set(stats)
        self.value = value
        self.can_crit = can_crit
        self.duration = duration
        self.max_stacks = max_stacks
        self.proc_name = proc_name
        self.proc_behaviours = {}
        for i in behaviours:
            if behaviours[i] in self.allowed_behaviours:
                self.proc_behaviours[i] = self.allowed_behaviours[behaviours[i]]
            else:
                raise InvalidProcException(_('Behaviour {behaviour}:{behaviour_name} is not allowed').format(behaviour=i, behaviour_name=behaviours[i]))
        self.behaviour_toggle = 'default'

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'behaviour_toggle':
            # Set behaviour attributes when this is modified.
            if value in self.proc_behaviours:
                self._set_behaviour(**self.proc_behaviours[value])
            else:
                raise InvalidProcException(_('Behaviour \'{behaviour}\' is not defined for {proc}').format(proc=self.proc_name, behaviour=value))

    def _set_behaviour(self, icd, trigger, proc_chance=False, ppm=False, on_crit=False, on_procced_strikes=True, real_ppm=False):
        # This could be merged with __setattr__; its sole purpose is
        # to clearly surface the parameters passed with the behaviours.
        self.proc_chance = proc_chance
        self.trigger = trigger
        self.icd = icd
        self.on_crit = on_crit
        self.ppm = ppm
        self.real_ppm=real_ppm
        self.on_procced_strikes = on_procced_strikes  # Main Gauche and its kin

    def procs_off_auto_attacks(self):
        if self.trigger in ('all_attacks', 'auto_attacks', 'all_spells_and_attacks', 'all_melee_attacks'):
            return True
        else:
            return False

    def procs_off_strikes(self):
        if self.trigger in ('all_attacks', 'strikes', 'all_spells_and_attacks', 'all_melee_attacks'):
            return True
        else:
            return False

    def procs_off_harmful_spells(self):
        if self.trigger in ('all_spells', 'damaging_spells', 'all_spells_and_attacks'):
            return True
        else:
            return False

    def procs_off_heals(self):
        if self.trigger in ('all_spells', 'healing_spells', 'all_spells_and_attacks'):
            return True
        else:
            return False

    def procs_off_periodic_spell_damage(self):
        if self.trigger in ('all_periodic_damage', 'periodic_spell_damage'):
            return True
        else:
            return False

    def procs_off_periodic_heals(self):
        if self.trigger == 'hots':
            return True
        else:
            return False

    def procs_off_bleeds(self):
        if self.trigger in ('all_periodic_damage', 'bleeds'):
            return True
        else:
            return False

    def procs_off_crit_only(self):
        if self.on_crit:
            return True
        else:
            return False

    def procs_off_apply_debuff(self):
        if self.trigger in ('all_spells_and_attacks', 'all_attacks', 'all_melee_attacks'):
            return True
        else:
            return False

    def procs_off_procced_strikes(self):
        if self.on_procced_strikes:
            return True
        else:
            return False

    def proc_rate(self, speed=None, haste=0.0):
        if self.is_ppm():
            if speed is None:
                raise InvalidProcException(_('Weapon speed needed to calculate the proc rate of {proc}').format(proc=self.proc_name))
            else:
                return self.ppm * speed / 60.
        elif self.is_real_ppm():
            if speed is None:
                raise InvalidProcException(_('Weapon speed needed to calculate the proc rate of {proc}').format(proc=self.proc_name))
            else:
                return haste * self.ppm / 60
        else:
            return self.proc_chance

    def is_ppm(self):
        if self.proc_chance not in (False, None) and self.ppm == False:
            return False
        elif self.real_ppm == True:
            return False
        elif self.ppm not in (False, None) and self.proc_chance == False:
            return True
        else:
            raise InvalidProcException(_('Invalid data for proc {proc}').format(proc=self.proc_name))
    
    def is_real_ppm(self):
        if self.real_ppm == True and (self.ppm not in (False, None)):
            return True
        elif self.real_ppm in (False, None):
            return False
        else:
            raise InvalidProcException(_('Invalid data for proc {proc}').format(proc=self.proc_name))

class ProcsList(object):
    allowed_procs = proc_data.allowed_procs

    def __init__(self, *args):
        for arg in args:
            if arg in self.allowed_procs:
                setattr(self, arg, Proc(**self.allowed_procs[arg]))
            else:
                raise InvalidProcException(_('No data for proc {proc}').format(proc=arg))

    def set_proc(self, proc):
        setattr(self, proc, Proc(**self.allowed_procs[proc]))

    def __getattr__(self, proc):
        # Any proc we haven't assigned a value to, we don't have.
        if proc in self.allowed_procs:
            return False
        object.__getattribute__(self, proc)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'level':
            self._set_constants_for_level()

    def _set_constants_for_level(self):
        self.set_swordguard_embroidery_value()

    def set_swordguard_embroidery_value(self):
        proc = getattr(self, 'swordguard_embroidery')
        values = [
            (90, 4000),
            (85, 1000),
            (80, 400),
            (1, 0)
        ]
        for level, value in values:
            if self.level >= level:
                self.allowed_procs['swordguard_embroidery']['value'] = value
                if proc:
                    proc.value = value
                break

    def get_all_procs_for_stat(self, stat=None):
        procs = []
        for proc_name in self.allowed_procs:
            proc = getattr(self, proc_name)
            if proc:
                if stat is None or proc.stat == stat:
                    procs.append(proc)

        return procs

    def get_all_damage_procs(self):
        procs = []
        for proc_name in self.allowed_procs:
            proc = getattr(self, proc_name)
            if proc:
                if proc.stat in ('spell_damage', 'physical_damage'):
                    procs.append(proc)

        return procs
