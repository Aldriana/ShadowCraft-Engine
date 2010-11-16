from core import exceptions

class InvalidProcException(exceptions.InvalidInputException):
    pass


class Proc(object):
    def __init__(self, stat, value, duration, proc_chance, trigger, icd, max_stacks, on_crit, proc_name):
        self.stat = stat
        self.value = value
        self.duration = duration
        self.proc_chance = proc_chance
        self.trigger = trigger
        self.icd = icd
        self.max_stacks = max_stacks
        self.on_crit = on_crit
        self.proc_name = proc_name

    def procs_off_auto_attacks(self):
        if self.trigger in ('all_attacks', 'auto_attack', 'all_spells_and_attacks'):
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

    def is_ppm(self):
        return False

class PPMProc(Proc):
    # Calculate proc_rate for a ppm proc assuming self.proc_chance is the # procs/minute
    # and speed is the number of seconds between proc events. Result is percent chance of proc per event.
    def __init__(self, stat, value, duration, ppm, trigger, icd, max_stacks, on_crit, proc_name):
        self.stat = stat
        self.value = value
        self.duration = duration
        self.ppm = ppm
        self.trigger = trigger
        self.icd = icd
        self.max_stacks = max_stacks
        self.on_crit = on_crit
        self.proc_name = proc_name

    def proc_rate(self, speed):
        return self.ppm * speed / 60.

    def is_ppm(self):
        return True

class ProcsList(object):
    # Format is (stat, value per stack, duration, proc rate, trigger, ICD, max stacks, procs only on crit, name of the proc, [procs on debuff application])
    # None should be used to indicate unknown values
    # Assumed heroic trinkets have same proc chance/ICD as non-heroic
    allowed_procs = {
        'heroic_grace_of_the_herald':               ('crit', 1710, 10, .1, 'all_attacks', 45, 1, False, 'Herald of Doom'),                 # ICD is a guess and should be verified.
        'heroic_key_to_the_endless_chamber':        ('agi', 1710, 15, .1, 'all_attacks', 75, 1, False, 'Final Key'),
        'heroic_left_eye_of_rajh':                  ('agi', 1710, 10, .3, 'all_attacks', 50, 1, True, 'Eye of Vengeance'),               # ICD is a guess and should be verified.
        'heroic_prestors_talisman_of_machination':  ('haste', 2178, 15, .1, 'all_attacks', 75, 1, False, 'Nefarious Plot'),
        'heroic_tias_grace':                        ('agi', 34, 15, None, 'all_attacks', None, 10, False, 'Grace'),
        'darkmoon_card_hurricane':                  ('spell_damage', 5000, 0, None, 'all_attacks', None, 0, False, 'Lightning Strike'),    # Behavior still needs to be tested.  I expect 1 PPM with no ICD, but should be tested.
        'essence_of_the_cyclone':                   ('crit', 1926, 10, .1, 'all_attacks', 45, 1, False, 'Twisted'),                        # ICD is a guess and should be verified.
        'fluid_death':                              ('agi', 38, 15, 1, 'all_attacks', None, 10, False, 'River of Death'),
        'grace_of_the_herald':                      ('crit', 924, 10, .1, 'all_attacks', 45, 1, False, 'Herald of Doom'),                  # ICD is a guess and should be verified.
        'heart_of_the_vile':                        ('crit', 924, 10, .1, 'all_attacks', 45, 1, False, 'Herald of Doom'),                  # ICD is a guess and should be verified.
        'key_to_the_endless_chamber':               ('agi', 1290, 15, .1, 'all_attacks', 75, 1, False, 'Final Key'),
        'left_eye_of_rajh':                         ('agi', 1512, 10, .3, 'all_attacks', 45, 1, True, 'Eye of Vengeance'),               # ICD is a guess and should be verified.
        'prestors_talisman_of_machination':         ('haste', 1926, 15, .1, 'all_attacks', 75, 1, False, 'Nefarious Plot'),
        'rogue_t11_4pc':                            ('weird_proc', 1, 15, .01, 'auto_attacks', None, 1, False, 'Deadly Scheme'),
        'the_twilight_blade':                       ('crit', 185, 10, None, 'all_attacks', None, 3, False, 'The Deepest Night'),           # Behavior still needs to be tested.  I expect 1 PPM with no ICD, but should be tested.
        'tias_grace':                               ('agi', 30, 15, None, 'all_attacks', None, 10, False, 'Grace'),
        'unheeded_warning':                         ('weird_proc', .25, 10, .1, 'all_attacks', 45, 1, False, 'Heedless Carnage'),      # ICD is a guess and should be verified.
    }

##    proc_triggers = frozenset([
##        'all_spells_and_attacks',
##        'all_damaging_attacks',
##        'all_attacks',
##        'strikes',
##        'crits',    # Never seen a proc-on-auto-attack-crits, so I'm assuming this is both strikes and aa
##        'auto_attacks',
##        'damaging_spells',
##        'all_spells',
##        'healing_spells',
##        'all_periodic_damage',
##        'bleeds',
##        'spell_periodic_damage',
##       'hots'
##    ])

    def __init__(self, *args):
        for arg in args:
            if arg in self.allowed_procs:
                setattr(self, arg, Proc(*self.allowed_procs[arg]))
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
