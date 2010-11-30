class Item(object):
    def __init__(self, name, str=0, agi=0, ap=0, crit=0, hit=0, exp=0, haste=0, mastery=0, sockets=[], bonus_stat='', bonus_value=0, proc='', gear_buff=''):
        self.name = name
        self.str = str
        self.agi = agi
        self.ap = ap
        self.crit = crit
        self.hit = hit
        self.exp = exp
        self.haste = haste
        self.mastery = mastery
        self.sockets = sockets
        self.bonus_stat = bonus_stat
        self.bonus_value = bonus_value
        self.proc = proc
        self.gear_buff = gear_buff

class Weapon(Item):
    def __init__(self, name, str=0, agi=0, ap=0, crit=0, hit=0, exp=0, haste=0, mastery=0, sockets=[], bonus_stat='', bonus_value=0, proc='', gear_buff='', damage=0, speed=0, type=''):
        super(Weapon, self).__init__(name, str, agi, ap, crit, hit, exp, haste, mastery, sockets, bonus_stat, bonus_value, proc, gear_buff)
        self.damage = damage
        self.speed = speed
        self.type = type

head = {
    '(H)Helm of Numberless Shadows': {
        'agi': 242, 
        'crit': 162,
        'hit': 182,
        'sockets': ['blue', 'meta'],
        'bonus_stat': 'agi',
        'bonus_value': 30,
    }
}
neck = {
    '(H)Barnacle Pendant': {
        'agi': 168, 
        'exp': 120,
        'haste': 98, 
    }
}
shoulders = {
    '(H)Caridean Epaulettes': {
        'agi': 205, 
        'exp': 150,
        'haste': 130,
        'sockets': ['red'],
        'bonus_stat': 'haste',
        'bonus_value': 10,
    }
}
back = {
    'Cape of the Brotherhood': {
        'agi': 168, 
        'hit': 112, 
        'haste': 112,
    }
}
chest = {
    "Assassin's Chestplate": {
        'agi': 341,
        'crit': 253,
        'hit': 183,
    }
}
wrists = {
    '(H)Poison Fang Bracers': {
        'agi': 168, 
        'hit': 112, 
        'haste': 112, 
    }
}
hands = {
    'Stormbolt Gloves': {
        'agi': 233, 
        'crit': 149, 
        'haste': 169,
        'sockets': ['yellow'],
        'bonus_stat': 'haste',
        'bonus_value': 10,
    }
}
waist = {
    'Belt of Nefarious Whispers': {
        'agi': 253, 
        'hit': 184, 
        'mastery': 144,
        'sockets': ['prismatic'],
    }
}
legs = {
    "(H)Beauty's Chew Toy": {
        'agi': 262, 
        'hit': 162, 
        'haste': 202,
        'sockets': ['red', 'blue'],
        'bonus_stat': 'haste',
        'bonus_value': 20,
    }
}
feet = {
    "(H)Vancleef's Boots": {
        'agi': 205,
        'haste': 150, 
        'mastery': 130,
        'sockets': ['yellow'], 
        'bonus_stat': 'agi',
        'bonus_value': 10,
    }
}
rings = {
    "Terrath's Signet of Balance": {
        'agi': 168,
        'hit': 112,
        'mastery': 112, 
    },
    '(H)Mirage Ring': {
        'agi': 168, 
        'hit': 85, 
        'haste': 128, 
    }
}
ring1 = rings
ring2 = rings
trinkets = {
    'Unsolvable Riddle': {
        'mastery': 321, 
        'gear_buff': 'unsolvable_riddle'
    },
    'Figurine - Demon Panther': {
        'hit': 285, 
        'gear_buff': 'demon_panther'
    }
}
trinket1 = trinkets
trinket2 = trinkets
melee_weapons = {
    'Dagger of Restless Nights': {
        'agi': 129, 
        'crit': 86, 
        'hit': 86, 
        'damage': 737,
        'speed': 1.8,
        'type': 'dagger',
    },
    "Barim's Main Gauche": {
        'agi': 129, 
        'crit': 86, 
        'mastery': 86, 
        'damage': 573.5,
        'speed': 1.4,
        'type': 'dagger',
    }
}
mainhand = melee_weapons
offhand = melee_weapons
ranged = {
    '(H)Slashing Thorns': {
        'agi': 95, 
        'crit': 63, 
        'hit': 63, 
        'damage': 1104.0,
        'speed': 2.0,
        'type': 'thrown',
    }
}

default_talents = {
    'coup_de_grace': 3,
    'lethality': 3,
    'ruthlessness': 3,
    'quickness': 2,
    'puncturing_wounds': 3,
    'cold_blood': 1,
    'vile_poisons': 3,
    'deadened_nerves': 1,
    'seal_fate': 2,
    'murderous_intent': 2,
    'overkill': 1,
    'master_poisoner': 1,
    'cut_to_the_chase': 3,
    'venomous_wounds': 2,
    'vendetta': 1,
    'precision': 2,
    'nightstalker': 2,
    'relentless_strikes': 3,
    'opportunity': 3
}

enchants = {
    'head': {'Arcanum of the Ramkahen':{'agi': 60, 'haste': 35}},
    'shoulders': {
        'Greater Inscription of Shattered Crystal': {'agi': 50, 'mastery': 25},
        'Lesser Inscription of Shattered Crystal': {'agi': 30, 'mastery': 20}
    },
    'back': {
        'Greater Critical Strike': {'crit': 65}, 
        'Major Agility': {'agi': 22}
    },
    'chest': {'Peerless Stats': {'agi': 20, 'str': 20}},
    'wrists': {
        'Greater Speed': {'haste': 50}, 
        'Greater Expertise': {'exp': 50}, 
        'Precision': {'hit': 50}, 
        '(LW)Draconic Embossment':{'agi': 130}
    },
    'hands': {
        'Greater Mastery':{'mastery': 65},
        'Greater Expertise': {'exp': 50},
        'Haste': {'haste': 50}
    },
    'legs': {'Dragonbone': {'ap': 190, 'crit': 55}},
    'feet': {
        'Major Agility': {'agi': 35}, 
        'Mastery':{'mastery': 50},
        'Precision': {'hit': 50},
        'Haste': {'haste': 50}
    },
    'rings': {'dummy1': {}},
    'melee_weapons': {
        'Landslide': 'landslide',
        'Hurricane': 'hurricane'
    }
}

gems = {
    "Delicate Chimera's Eye": (['red'], {'agi': 67}),
    "Delicate Inferno Ruby": (['red'], {'agi': 40}),
    "Adept Ember Topaz": (['red', 'yellow'], {'agi': 20, 'mastery': 20}),
    "Deft Ember Topaz": (['red', 'yellow'], {'agi': 20, 'haste': 20}),
    "Glinting Demonseye": (['red', 'blue'], {'agi': 20, 'hit': 20}),
    "Rigid Ocean Sapphire": (['blue'], {'hit': 40})
}