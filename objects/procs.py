class Proc(object):
    def __init__(self, stat, value, duration, proc_chance, trigger, icd, max_stacks, procs_off_debuff=False):
        self.stat = stat
        self.value = value
        self.duration = duration
        self.proc_chance = proc_chance
        self.trigger = trigger
        self.icd = icd
        self.max_stacks = max_stacks
        self.procs_off_debuff = procs_off_debuff

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

    def procs_off_apply_debuff(self):
        if self.procs_off_debuff:
            return True
        else:
            return False

    def is_ppm(self):
        return False

class PPMProc(Proc):
    # Calculate proc_rate for a ppm proc assuming self.proc_chance is the # procs/minute
    # and speed is the number of seconds between proc events. Result is percent chance of proc per event.
    def __init__(self, stat, value, duration, ppm, trigger, icd, max_stacks, procs_off_debuff=False):
        self.stat = stat
        self.value = value
        self.duration = duration
        self.ppm = ppm
        self.trigger = trigger
        self.icd = icd
        self.max_stacks = max_stacks
        self.procs_off_debuff = procs_off_debuff

    def proc_rate(self, speed):
        return self.ppm * speed / 60.

    def is_ppm(self):
        return True

class ProcsList(object):
    # Format is (stat, value per stack, duration, proc rate, trigger, ICD, max stacks, [procs on debuff application])
    # None should be used to indicate unknown values
    # Assumed heroic trinkets have same proc chance/ICD as non-heroic
    allowed_procs = {
        'heroic_grace_of_the_herald':               Proc('crit', 1710, 10, None, 'all_attacks', None, 1),
        'heroic_key_to_the_endless_chamber':        Proc('agi', 1710, 15, .1, 'all_attacks', 75, 1),
        'heroic_left_eye_of_rajh':                  Proc('agi', 1710, 10, None, 'crits', None, 1),
        'heroic_prestors_talisman_of_machination':  Proc('haste', 2178, 15, .1, 'all_attacks', 75, 1),
        'darkmoon_card_hurricane':                  Proc('spell_damage', 5000, 0, None, 'all_attacks', None, 0),
        'essence_of_the_cyclone':                   Proc('crit', 1926, 10, None, 'all_attacks', None, 1),
        'fluid_death':                              Proc('agi', 38, 15, None, 'all_attacks',None,10),
        'grace_of_the_herald':                      Proc('crit', 924, 10, None, 'all_attacks', None, 1),
        'heart_of_the_vile':                        Proc('crit', 924, 10, None, 'all_attacks', None, 1),
        'hurricane':                                PPMProc('haste', 450, 12, 1, 'all_spells_and_attacks', 0, 1),
        'key_to_the_endless_chamber':               Proc('agi', 1290, 15, .1, 'all_attacks', 75, 1),
        'landslide':                                PPMProc('ap', 1000, 12, None, 'all_attacks', None, 1),
        'left_eye_of_rajh':                         Proc('agi', 1512, 10, None, 'crits', None, 1),
        'prestors_talisman_of_machination':         Proc('haste', 1926, 15, .1, 'all_attacks', 75, 1),
        'rogue_t11_4pc':                            Proc('weird_proc', 1, 15, .01, 'auto_attacks', None, None),
        'the_twilight_blade':                       Proc('crit', 185, 10, None, 'all_attacks', None, 3),
        'unheeded_warning':                         Proc('weird_proc', .25, 10, None, 'all_attacks', None, 1),
    }

##    proc_triggers = frozenset([
##        'all_spells_and_attacks',
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
                setattr(self,arg,self.allowed_procs[arg])
            else:
                # Throw invalid input exception here
                assert False, "No data for proc '%(proc)s'" % {'proc': arg}

    def __getattr__(self, proc):
        # Any proc we haven't assigned a value to, we don't have.
        if proc in self.allowed_procs:
            return False
        object.__getattribute__(self, proc)

    def get_all_procs_for_stat(self,stat=None):
        procs = []
        for proc in self.allowed_procs:
            if getattr(self,proc):
                if stat == None or self.allowed_procs[proc].stat == stat:
                    procs.append(self.allowed_procs[proc])

        return procs

    def get_all_damage_procs(self):
        procs = []
        for proc in self.allowed_procs:
            if getattr(self,proc):
                if self.allowed_procs[proc].stat in ('spell_damage', 'physical_damage'):
                    procs.append(self.allowed_procs[proc])

        return procs
