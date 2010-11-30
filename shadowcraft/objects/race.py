from shadowcraft.core import exceptions

class InvalidRaceException(exceptions.InvalidInputException):
    pass

class Race(object):
    rogue_base_stats = {
        80:(113,189,105,43,67),
        85:(122,206,114,46,73)
    }

    #(ap,sp)
    blood_fury_bonuses = {
        80: { 'ap': 330, 'sp': 165},
        85: { 'ap': 1170, 'sp': 585},
    }

    #Arguments are ap, spellpower:fire, and int
    #This is the formula according to wowhead, with a probable typo corrected
    def calculate_rocket_barrage(self, ap, spfi, int):
        return 1 + 0.25 * ap + .429 * spfi + self.level * 2 + int * 0.50193

    racial_stat_offset = {
        "human":        (0,0,0,0,0),
        "night_elf":    (-4,4,0,0,0),
        "dwarf":        (5,-4,1,-1,-1),
        "gnome":        (-5,2,0,3,0),
        "draenei":      (1,-3,0,0,2),
        "worgen":       (3,2,0,-4,-1),
        "orc":          (3,-3,1,-3,2),
        "undead":       (-1,-2,0,-2,5),
        "tauren":       (5,-4,1,-4,2),
        "troll":        (1,2,0,-4,1),
        "blood_elf":    (-3,2,0,3,-2),
        "goblin":       (-3,2,0,3,-2),
    }

    allowed_racials = frozenset([
        "axe_specialization",       #Orc
        "fist_specialization",      #Orc
        "mace_specialization",      #Human, Dwarf
        "stoneform",                #Dwarf
        "expansive_mind",           #Gnome
        "dagger_specialization",    #Gnome
        "sword_1h_specialization",  #Gnome, Human
        "human_spirit",             #Human
        "sword_2h_specialization",  #Human
        "quickness",                #Night Elf
        "heroic_presence",          #Draenei
        "viciousness",              #Worgen
        "blood_fury_physical",      #Orc
        "blood_fury_spell",         #Orc
        "command",                  #Orc
        "endurance",                #Tauren
        "berserking",               #Troll
        "regeneration",             #Troll
        "beast_slaying",            #Troll
        "throwing_specialization",  #Troll
        "bow_specialization",       #Troll
        "gun_specialization",       #Dwarf
        "arcane_torrent",           #Blood Elf
        "rocket_barrage",           #Goblin
        "time_is_money"             #Goblin
    ])

    activated_racial_data = {
        #Blood fury values are set when level is set
        'blood_fury_physical':      {'stat': "ap", 'value': 0, 'duration': 15, 'cooldown': 120},    #level-based ap increase
        'blood_fury_spell':         {'stat': "sp", 'value': 0, 'duration': 15, 'cooldown': 120},                                    #level-based sp increase
        'berserking':               {'stat': "haste_multiplier", 'value': 1.2, 'duration': 10, 'cooldown': 180},                    #20% haste increase for 10 seconds, 3 minute cd
        'arcane_torrent':           {'stat': "energy", 'value': 15, 'duration': 0, 'cooldown': 120},                                #gain 15 energy (or 15 runic power or 6% mana), 2 minute cd
        'rocket_barrage':           {'stat': "damage", 'value': calculate_rocket_barrage, 'duration': 0, 'cooldown': 120}      #deal formula-based damage, 2 min cd
    }

    racials_by_race = {
                "human":        ["mace_specialization", "sword_1h_specialization", "sword_2h_specialization", "human_spirit"],
                "night_elf":    ["quickness"],
                "dwarf":        ["stoneform", "gun_specialization", "mace_specialization"],
                "gnome":        ["expansive_mind", "dagger_specialization", "sword_1h_specialization"],
                "draenei":      ["heroic_presence"],
                "worgen":       ["viciousness"],
                "orc":          ["blood_fury_physical", "blood_fury_spell", "mace_specialization", "axe_specialization"],
                "undead":       [],
                "tauren":       ["endurance"],
                "troll":        ["regeneration", "beast_slaying", "throwing_specialization", "bow_specialization", "berserking"],
                "blood_elf":    ["arcane_torrent"],
                "goblin":       ["rocket_barrage", "time_is_money"],
    }

    #Note this allows invalid class-race combos
    def __init__(self, race, character_class="rogue", level=85):
        self.character_class = str.lower(character_class)
        self.race_name = str.lower(race)
        if self.race_name not in Race.racial_stat_offset:
            raise InvalidRaceException(_('Unsupported race {race}').format(race=self.race_name))
        if self.character_class == "rogue":
            self.stat_set = Race.rogue_base_stats
        else:
            raise InvalidRaceException(_('Unsupported class {character_class}').format(character_class=self.character_class))
        self.level = level
        self.set_racials()

    def set_racials(self):
        racials = Race.racials_by_race[self.race_name]
        for racial in racials:
            setattr(self, racial, True)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'level':
            self._set_constants_for_level()
    
    def _set_constants_for_level(self):
        try:
            self.stats = self.stat_set[self.level]
            self.activated_racial_data["blood_fury_physical"]["value"] = self.blood_fury_bonuses[self.level]["ap"]
            self.activated_racial_data["blood_fury_spell"]["value"] = self.blood_fury_bonuses[self.level]["sp"]
            self.stats = map(sum, zip(self.stats, Race.racial_stat_offset[self.race_name]))
        except KeyError as e:
            raise InvalidRaceException(_('Unsupported class/level combination {character_class}/{level}').format(character_class=self.character_class, level=self.level))

    def __getattr__(self, name):
        # Any racial we haven't assigned a value to, we don't have.
        if name in self.allowed_racials:
            return False
        elif name == 'racial_str':
            return self.stats[0]
        elif name == 'racial_agi':
            return self.stats[1]
        elif name == 'racial_sta':
            return self.stats[2]
        elif name == 'racial_int':
            return self.stats[3]
        elif name == 'racial_spi':
            return self.stats[4]
        else:
            object.__getattribute__(self, name)

    def get_racial_expertise(self, weapon_type):
        if weapon_type in ['1h_axe', '2h_axe', 'fist']:
            if self.axe_specialization:
                return .0075
        elif weapon_type == '1h_sword':
            if self.sword_1h_specialization:
                return .0075
        elif weapon_type == '2h_sword': 
            if self.sword_2h_specialization:
                return .0075
        elif weapon_type in ['1h_mace', '2h_mace']:
            if self.mace_specialization:
                return .0075
        elif weapon_type == 'dagger':
            if self.dagger_specialization:
                return .0075

        return 0

    def get_racial_crit(self, weapon_type=None):
        crit_bonus = 0
        if self.viciousness:
            crit_bonus = .01
        elif not weapon_type is None:
            if weapon_type == 'thrown' and self.throwing_specialization:
                crit_bonus = .01
            elif weapon_type == 'gun' and self.gun_specialization:
                crit_bonus = .01
            elif weapon_type == 'bow'and self.bow_specialization:
                crit_bonus = .01

        return crit_bonus

    def get_racial_hit(self):
        hit_bonus = 0
        if self.heroic_presence:
            hit_bonus = .01

        return hit_bonus

    def get_racial_haste(self):
        haste_bonus = 0
        if self.time_is_money:
            haste_bonus = .01

        return haste_bonus

    def get_racial_stat_boosts(self):
        racial_boosts = []
        #Only the orc racial is a straight stat boost
        if getattr(self, "blood_fury_physical"):
            racial_boosts += [self.activated_racial_data["blood_fury_physical"], self.activated_racial_data["blood_fury_spell"]]
        return racial_boosts