from shadowcraft.core import exceptions

class InvalidRaceException(exceptions.InvalidInputException):
    pass

class Race(object):
    rogue_base_stats = {
        80: (113, 189, 105, 43, 67),
        85: (122, 206, 114, 46, 73),
        90: (132, 225, 123, 48, 77)
    }

    #(ap,sp)
    blood_fury_bonuses = {
        80: {'ap': 346, 'sp': 173},
        85: {'ap': 1344, 'sp': 672},
        90: {'ap': 4514, 'sp': 2257}
    }

    #Arguments are ap, spellpower:fire, and int
    #This is the formula according to wowhead, with a probable typo corrected
    def calculate_rocket_barrage(self, ap, spfi, int):
        return 1 + 0.25 * ap + .429 * spfi + self.level * 2 + int * 0.50193

    racial_stat_offset = {
        "human":        (0, 0, 0, 0, 0),
        "night_elf":    (-4, 4, 0, 0, 0),
        "dwarf":        (5, -4, 1, -1, -1),
        "gnome":        (-5, 2, 0, 3, 0),
        "draenei":      (1, -3, 0, 0, 2),
        "worgen":       (3, 2, 0, -4, -1),
        "pandaren":     (0, -2, 1, -1, 2),
        "orc":          (3, -3, 1, -3, 2),
        "undead":       (-1, -2, 0, -2, 5),
        "tauren":       (5, -4, 1, -4, 2),
        "troll":        (1, 2, 0, -4, 1),
        "blood_elf":    (-3, 2, 0, 3, -2),
        "goblin":       (-3, 2, 0, 3, -2),
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
        "shadowmeld",               #Night Elf
        "heroic_presence",          #Draenei
        "viciousness",              #Worgen
        "blood_fury_physical",      #Orc
        "blood_fury_spell",         #Orc
        "command",                  #Orc
        "endurance",                #Tauren
        "berserking",               #Troll
        "regeneration",             #Troll
        "beast_slaying",            #Troll
        "ranged_specialization",    #Troll, Dwarf
        "arcane_torrent",           #Blood Elf
        "rocket_barrage",           #Goblin
        "time_is_money",            #Goblin
        "epicurean",                #Pandaren
        "touch_of_the_grave",       #Undead
        "cannibalize",              #Undead
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
        "night_elf":    ["quickness", "shadowmeld"],
        "dwarf":        ["stoneform", "ranged_specialization", "mace_specialization"],
        "gnome":        ["expansive_mind", "dagger_specialization", "sword_1h_specialization"],
        "draenei":      ["heroic_presence"],
        "worgen":       ["viciousness"],
        "orc":          ["blood_fury_physical", "blood_fury_spell", "fist_specialization", "axe_specialization"],
        "undead":       ["touch_of_the_grave", "cannibalize"],
        "tauren":       ["endurance"],
        "troll":        ["regeneration", "beast_slaying", "ranged_specialization", "berserking"],
        "blood_elf":    ["arcane_torrent"],
        "goblin":       ["rocket_barrage", "time_is_money"],
        "pandaren":     ["epicurean"]
    }

    #Note this allows invalid class-race combos
    def __init__(self, race, character_class="rogue", level=85):
        self.character_class = str.lower(character_class)
        self.race_name = race
        if self.race_name not in Race.racial_stat_offset.keys():
            raise InvalidRaceException(_('Unsupported race {race}').format(race=self.race_name))
        if self.character_class == "rogue":
            self.stat_set = Race.rogue_base_stats
        else:
            raise InvalidRaceException(_('Unsupported class {character_class}').format(character_class=self.character_class))
        self.level = level
        self.set_racials()

    def set_racials(self):
        # Set all racials, so we don't invoke __getattr__ all the time
        for race, racials in Race.racials_by_race.items():
            for racial in racials:
                setattr(self, racial, False)
        for racial in Race.racials_by_race[self.race_name]:
            setattr(self, racial, True)
        setattr(self, "racial_str", self.stats[0])
        setattr(self, "racial_agi", self.stats[1])
        setattr(self, "racial_sta", self.stats[2])
        setattr(self, "racial_int", self.stats[3])
        setattr(self, "racial_spi", self.stats[4])

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
        elif weapon_type in ['bow', 'crossbow', 'gun']:
            if self.ranged_specialization:
                return .0075

        return 0

    def get_racial_crit(self, weapon_type=None):
        crit_bonus = 0
        if self.viciousness:
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
