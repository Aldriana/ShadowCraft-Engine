from core import exceptions

class InvalidProcException(exceptions.InvalidInputException):
    pass


class Proc(object):
    def __init__(self, stat, value, duration, proc_chance, trigger, icd, max_stacks, on_crit, proc_name, ppm):
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
    # Calculate proc_rate for a ppm proc assuming self.ppm is the # procs/minute
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
    # None should be used to indicate unknown values
    # Assumed heroic trinkets have same proc chance/ICD as non-heroic
    allowed_procs = {
        'heroic_grace_of_the_herald':               {'stat': 'crit', 'value': 1710, 'duration': 10, 'max_stacks': 1,
                                                    'proc_chance': .1, 'ppm': None, 'icd': 45,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Herald of Doom'},         # ICD is a guess and should be verified.
        'heroic_key_to_the_endless_chamber':        {'stat': 'agi', 'value': 1710, 'duration': 15, 'max_stacks': 1,
                                                    'proc_chance': .1, 'ppm': None, 'icd': 75,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Final Key'},
        'heroic_left_eye_of_rajh':                  {'stat': 'agi', 'value': 1710, 'duration': 10, 'max_stacks': 1,
                                                    'proc_chance': .3, 'ppm': None, 'icd': 50,
                                                    'trigger': 'all_attacks', 'on_crit': True, 'proc_name': 'Eye of Vengeance'},        # ICD is a guess and should be verified.
        'heroic_prestors_talisman_of_machination':  {'stat': 'haste', 'value': 2178, 'duration': 15, 'max_stacks': 1,
                                                    'proc_chance': .1, 'ppm': None, 'icd': 75,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Nefarious Plot'},
        'heroic_tias_grace':                        {'stat': 'agi', 'value': 34, 'duration': 15, 'max_stacks': 10, 
                                                    'proc_chance': None, 'ppm': None, 'icd': None,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Grace'},
        'darkmoon_card_hurricane':                  {'stat': 'spell_damage', 'value': 5000, 'duration': 0, 'max_stacks': 0,
                                                    'proc_chance': False, 'ppm': 1, 'icd': 0,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Lightning Strike'},       # PPM/ICD is a guess and should be verified.
        'essence_of_the_cyclone':                   {'stat': 'crit', 'value': 1926, 'duration': 10, 'max_stacks': 1,
                                                    'proc_chance': .1, 'ppm': None, 'icd': 45,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Twisted'},                # ICD is a guess and should be verified.
        'fluid_death':                              {'stat': 'agi', 'value': 38, 'duration': 15, 'max_stacks': 10,
                                                    'proc_chance': 1, 'ppm': None, 'icd': None,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'River of Death'},
        'grace_of_the_herald':                      {'stat': 'crit', 'value': 924, 'duration': 10, 'max_stacks': 1,
                                                    'proc_chance': .1, 'ppm': None, 'icd': 45, 
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Herald of Doom'},         # ICD is a guess and should be verified.
        'heart_of_the_vile':                        {'stat': 'crit', 'value': 924, 'duration': 10, 'max_stacks': 1,
                                                    'proc_chance': .1, 'ppm': None, 'icd': 45,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Herald of Doom'},         # ICD is a guess and should be verified.
        'key_to_the_endless_chamber':               {'stat': 'agi', 'value': 1290, 'duration': 15, 'max_stacks': 1,
                                                    'proc_chance': .1, 'ppm': None, 'icd': 75,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Final Key'},
        'left_eye_of_rajh':                         {'stat': 'agi', 'value': 1512, 'duration': 10, 'max_stacks': 1,
                                                    'proc_chance': .3, 'ppm': None, 'icd': 45, 
                                                    'trigger': 'all_attacks', 'on_crit': True, 'proc_name': 'Eye of Vengeance'},        # ICD is a guess and should be verified.
        'prestors_talisman_of_machination':         {'stat': 'haste', 'value': 1926, 'duration': 15, 'max_stacks': 1,
                                                    'proc_chance': .1, 'ppm': None, 'icd': 75,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Nefarious Plot'},
        'rogue_t11_4pc':                            {'stat': 'weird_proc', 'value': 1, 'duration': 15, 'max_stacks': 1,
                                                    'proc_chance': .01, 'ppm': None, 'icd': None,
                                                    'trigger': 'auto_attacks', 'on_crit': False, 'proc_name': 'Deadly Scheme'},
        'the_twilight_blade':                       {'stat': 'crit', 'value': 185, 'duration': 10, 'max_stacks': 3,
                                                    'proc_chance': False, 'ppm': 1, 'icd': 0,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'The Deepest Night'},      # PPM/ICD is a guess and should be verified.
        'tias_grace':                               {'stat': 'agi', 'value': 30, 'duration': 15, 'max_stacks': 10,
                                                    'proc_chance': None, 'ppm': None, 'icd': None,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Grace'},
        'unheeded_warning':                         {'stat': 'weird_proc', 'value': .25, 'duration': 10, 'max_stacks': 1,
                                                    'proc_chance': .1, 'ppm': None, 'icd': 45,
                                                    'trigger': 'all_attacks', 'on_crit': False, 'proc_name': 'Heedless Carnage'}        # ICD is a guess and should be verified.
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
