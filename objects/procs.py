from core import exceptions
from objects import proc_data

class InvalidProcException(exceptions.InvalidInputException):
    pass


class Proc(object):
    def __init__(self, stat, value, duration, trigger, icd, proc_name, ppm=False, proc_chance=False, on_crit=False, max_stacks=1,):
        self.stat = stat
        self.value = value
        self.duration = duration
        self.proc_chance = proc_chance
        self.trigger = trigger
        self.icd = icd
        self.max_stacks = max_stacks
        self.on_crit = on_crit
        self.proc_name = proc_name
        self.ppm = ppm

    def procs_off_auto_attacks(self):
        if self.trigger in ('all_attacks', 'auto_attacks', 'all_spells_and_attacks'):
            return True
        else:
            return False

    def procs_off_strikes(self):
        if self.trigger in ('all_attacks', 'strikes', 'all_spells_and_attacks'):
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
        if self.trigger in ('all_spells_and_attacks', 'all_attacks'):
            return True
        else:
            return False

    def proc_rate(self, speed=None):
        if self.is_ppm():
            if speed == None:
                raise InvalidProcException(_('Weapon speed needed to calculate the proc rate of {proc}').format(proc=self.proc_name))
            else:
                return self.ppm * speed / 60.
        else:
            return self.proc_chance

    def is_ppm(self):
        if self.proc_chance not in (False, None) and self.ppm == False:
            return False
        elif self.ppm not in (False, None) and self.proc_chance == False:
            return True
        else:
            raise InvalidProcException(_('Invalid data for proc {proc}').format(proc=self.proc_name))

class ProcsList(object):
    allowed_procs = proc_data.allowed_procs

    def __init__(self, *args):
        for arg in args:
            if arg in self.allowed_procs:
                setattr(self, arg, Proc(**self.allowed_procs[arg]))
            else:
                # Throw invalid input exception here
                raise InvalidProcException(_('No data for proc {proc}').format(proc=arg))

    def __getattr__(self, proc):
        # Any proc we haven't assigned a value to, we don't have.
        if proc in self.allowed_procs:
            return False
        object.__getattribute__(self, proc)

    def get_all_procs_for_stat(self, stat=None):
        procs = []
        for proc_name in self.allowed_procs:
            proc = getattr(self, proc_name)
            if proc:
                if stat == None or proc.stat == stat:
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
