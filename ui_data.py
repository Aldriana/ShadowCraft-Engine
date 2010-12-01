import math

class Item(object):
    reforgable_stats = frozenset([
        'crit',
        'hit',
        'exp',
        'haste',
        'mastery'
    ])

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
    
    def reforgable_from(self):
        reforgable = []
        for stat in self.reforgable_stats:
            if getattr(self, stat) > 0:
                reforgable.append(stat)
        return reforgable
    
    def reforgable_to(self):
        reforgable = []
        for stat in self.reforgable_stats:
            if getattr(self, stat) == 0:
                reforgable.append(stat)
        return reforgable
    
    def reforge(self, from_stat, to_stat):
        reforged_value = math.floor(getattr(self, from_stat) * 0.4)
        setattr(self, from_stat, getattr(self, from_stat) - reforged_value)
        setattr(self, to_stat, reforged_value)

class Weapon(Item):
    def __init__(self, name, str=0, agi=0, ap=0, crit=0, hit=0, exp=0, haste=0, mastery=0, sockets=[], bonus_stat='', bonus_value=0, proc='', gear_buff='', damage=0, speed=0, type=''):
        super(Weapon, self).__init__(name, str, agi, ap, crit, hit, exp, haste, mastery, sockets, bonus_stat, bonus_value, proc, gear_buff)
        self.damage = damage
        self.speed = speed
        self.type = type

head = {
    'Agile Bio-Optic Killshades': {'agi': 301, 'mastery': 1, 'sockets': ['meta'], 'bonus_stat': 'agi', 'bonus_value': 20},    # missing cogwheels
    "(H)Membrane of C'Thun": {'agi': 325, 'exp': 197, 'exp': 257, 'mastery': 2, 'sockets': ['yellow', 'meta'], 'bonus_stat': 'haste', 'bonus_value': 30},
    "Membrane of C'Thun": {'agi': 281, 'exp': 168, 'exp': 228, 'mastery': 2, 'sockets': ['yellow', 'meta'], 'bonus_stat': 'haste', 'bonus_value': 30},
    "Tsanga's Helm": {'agi': 281, 'crit': 168, 'mastery': 228, 'mastery': 2, 'sockets': ['blue', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 30},
    "(H)Wind Dancer's Helmet": {'agi': 325, 'crit': 257, 'hit': 197, 'mastery': 2, 'sockets': ['blue', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 30, 'gear_buff': 'tier_11'},    # Tier 11
    "Wind Dancer's Helmet": {'agi': 281, 'crit': 228, 'hit': 168, 'mastery': 2, 'sockets': ['blue', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 30, 'gear_buff': 'tier_11'},    # Tier 11
    'Dunwald Winged Helm': {'agi': 268, 'exp': 178, 'mastery': 178},
    '(H)Helm of Numberless Shadows': {'agi': 242, 'crit': 162, 'hit': 182, 'mastery': 2, 'sockets': ['blue', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 30},
    'Helm of Secret Knowledge': {'agi': 208, 'crit': 117, 'exp': 171, 'mastery': 2, 'sockets': ['yellow', 'meta'], 'bonus_stat': 'mastery', 'bonus_value': 30},
    'Hood of the Crying Rogue': {'agi': 208, 'crit': 117, 'exp': 171, 'mastery': 2, 'sockets': ['yellow', 'meta'], 'bonus_stat': 'mastery', 'bonus_value': 30},
    'Mask of Vines': {'agi': 242, 'crit': 182, 'exp': 162, 'mastery': 2, 'sockets': ['blue', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 30},
    'Shocktrooper Hood': {'agi': 268, 'exp': 178, 'mastery': 178},
}
neck = {
    '(H)Necklace of Strife': {'agi': 215, 'exp': 143, 'mastery': 143},
    'Necklace of Strife': {'agi': 190, 'exp': 127, 'mastery': 127},
    'Acorn of the Daughter Tree': {'agi': 168, 'crit': 112, 'exp': 112},
    'Amulet of Dull Dreaming': {'agi': 168, 'crit': 112, 'exp': 112},
    '(H)Barnacle Pendant': {'agi': 168, 'exp': 120, 'exp': 98},
    'Brazen Elementium Medallion': {'agi': 138, 'crit': 112, 'exp': 102, 'mastery': 1, 'sockets': ['red'], 'bonus_stat': 'str', 'bonus_value': 10},    # str socket
    'Entwined Elementium Choker': {'agi': 148, 'crit': 65, 'exp': 128, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'mastery', 'bonus_value': 10},
    '(H)Mouth of the Earth': {'agi': 168, 'hit': 112, 'exp': 112},
    'Mouth of the Earth': {'agi': 149, 'hit': 100, 'exp': 100},
    'Nightrend Choker': {'agi': 149, 'crit': 100, 'exp': 100},
    '(H)Pendant of the Lightless Grotto': {'agi': 168, 'crit': 112, 'mastery': 112},
    'Pendant of Victorious Fury': {'agi': 149, 'exp': 105, 'mastery': 90},
    'Sweet Perfume Broach': {'agi': 168, 'crit': 101, 'exp': 119},
}
shoulders = {
    '(H)Poison Protocol Pauldrons': {'agi': 226, 'crit': 171, 'mastery': 191, 'mastery': 1, 'sockets': ['red']},
    'Poison Protocol Pauldrons': {'agi': 233, 'crit': 149, 'mastery': 169, 'mastery': 1, 'sockets': ['red']},
    "(H)Wind Dancer's Spaulders": {'agi': 266, 'crit': 171, 'exp': 191, 'mastery': 1, 'sockets': ['blue'], 'bonus_stat': 'agi', 'bonus_value': 10, 'gear_buff': 'tier_11'},    # Tier 11
    "Wind Dancer's Spaulders": {'agi': 233, 'crit': 149, 'exp': 169, 'mastery': 1, 'sockets': ['blue'], 'bonus_stat': 'agi', 'bonus_value': 10, 'gear_buff': 'tier_11'},    # Tier 11
    '(H)Caridean Epaulettes': {'agi': 205, 'exp': 150, 'exp': 130, 'mastery': 1, 'sockets': ['red'], 'bonus_stat': 'haste', 'bonus_value': 10},
    'Clandestine Spaulders': {'agi': 199, 'crit': 142, 'exp': 116},
    'Embrace of the Night': {'agi': 205, 'crit': 150, 'hit': 130, 'mastery': 1, 'sockets': ['blue'], 'bonus_stat': 'agi', 'bonus_value': 10},
    '(H)Thieving Spaulders': {'agi': 205, 'crit': 130, 'exp': 150, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'haste', 'bonus_value': 20},
}
back = {
    '(H)Cloak of Biting Chill': {'agi': 215, 'crit': 143, 'mastery': 143},
    'Cloak of Biting Chill': {'agi': 190, 'crit': 127, 'mastery': 127},
    'Viewless Wings': {'agi': 190, 'crit': 127, 'hit': 127},
    '(H)Cape of the Brotherhood': {'agi': 168, 'hit': 112, 'exp': 112},
    'Cloak of Beasts': {'agi': 149, 'hit': 114, 'mastery': 76},
    '(H)Cloak of Thredd': {'agi': 168, 'crit': 112, 'mastery': 112},
    '(H)Kaleki Cloak': {'agi': 168, 'hit': 85, 'mastery': 128},
    'Kaleki Cloak': {'agi': 149, 'hit': 76, 'mastery': 114},
    'Razor-Edged Cloak': {'agi': 168, 'crit': 125, 'mastery': 90},
    'Softwind Cape': {'agi': 168, 'hit': 112, 'exp': 112},
    '(H)Twitching Shadows': {'agi': 168, 'crit': 112, 'exp': 112},
}
chest = {
    "Assassin's Chestplate": {'agi': 341, 'crit': 253, 'hit': 183},
    "Morrie's Waywalker Wrap": {'agi': 301, 'crit': 198, 'mastery': 218, 'mastery': 2, 'sockets': ['red', 'yellow'], 'bonus_stat': 'mastery', 'bonus_value': 20},
    '(H)Sark of the Unwatched': {'agi': 345, 'crit': 227, 'exp': 247, 'mastery': 2, 'sockets': ['red', 'yellow'], 'bonus_stat': 'mastery', 'bonus_value': 20},
    'Sark of the Unwatched': {'agi': 301, 'crit': 198, 'mastery': 218, 'mastery': 2, 'sockets': ['red', 'yellow'], 'bonus_stat': 'mastery', 'bonus_value': 20},
    "(H)Wind Dancer's Tunic": {'agi': 345, 'exp': 217, 'exp': 257, 'mastery': 2, 'sockets': ['red', 'blue'], 'bonus_stat': 'agi', 'bonus_value': 20, 'gear_buff': 'tier_11'},    # Tier 11
    "Wind Dancer's Tunic": {'agi': 301, 'exp': 188, 'exp': 228, 'mastery': 2, 'sockets': ['red', 'blue'], 'bonus_stat': 'agi', 'bonus_value': 20, 'gear_buff': 'tier_11'},    # Tier 11
    '(H)Defias Brotherhood Vest': {'agi': 262, 'exp': 182, 'mastery': 182, 'mastery': 2, 'sockets': ['red', 'yellow'], 'bonus_stat': 'mastery', 'bonus_value': 20},
    '(H)Hieroglyphic Vest': {'agi': 262, 'crit': 182, 'exp': 182, 'mastery': 2, 'sockets': ['yellow', 'yellow'], 'bonus_stat': 'agi', 'bonus_value': 20},
    'Hieroglyphic Vest': {'agi': 228, 'crit': 158, 'exp': 158, 'mastery': 2, 'sockets': ['yellow', 'yellow'], 'bonus_stat': 'agi', 'bonus_value': 20},
    'Sly Fox Jerkin': {'agi': 228, 'crit': 178, 'mastery': 138, 'mastery': 2, 'sockets': ['red', 'blue'], 'bonus_stat': 'mastery', 'bonus_value': 20},
    'Tunic of Sinking Envy': {'agi': 262, 'crit': 202, 'hit': 162, 'mastery': 2, 'sockets': ['red', 'blue'], 'bonus_stat': 'crit', 'bonus_value': 20},
    '(H)Vest of Misshapen Hides': {'agi': 262, 'crit': 162, 'mastery': 202, 'mastery': 2, 'sockets': ['red', 'blue'], 'bonus_stat': 'mastery', 'bonus_value': 20},
    'Vest of Misshapen Hides': {'agi': 268, 'crit': 178, 'mastery': 178},

}
wrists = {
    '(H)Parasitic Bands': {'agi': 215, 'crit': 143, 'mastery': 143},
    'Parasitic Bands': {'agi': 190, 'crit': 127, 'mastery': 127},
    '(H)Double Dealing Bracers': {'agi': 168, 'crit': 112, 'mastery': 112},
    '(H)Poison Fang Bracers': {'agi': 168, 'hit': 112, 'exp': 112},
    'Poison Fang Bracers': {'agi': 149, 'hit': 100, 'exp': 100},
}
hands = {
    '(H)Double Attack Handguards': {'agi': 266, 'exp': 171, 'mastery': 191, 'mastery': 1, 'sockets': ['red'], 'bonus_stat': 'mastery', 'bonus_value': 10},
    'Double Attack Handguards': {'agi': 233, 'exp': 149, 'mastery': 169, 'mastery': 1, 'sockets': ['red'], 'bonus_stat': 'mastery', 'bonus_value': 10},
    "Liar's Handwraps": {'agi': 233, 'crit': 149, 'exp': 169, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'haste', 'bonus_value': 10},
    'Stormbolt Gloves': {'agi': 233, 'crit': 149, 'exp': 169, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'haste', 'bonus_value': 10},
    "(H)Wind Dancer's Gloves": {'agi': 266, 'hit': 171, 'exp': 191, 'mastery': 1, 'sockets': ['red'], 'bonus_stat': 'haste', 'bonus_value': 10, 'gear_buff': 'tier_11'},    # Tier 11
    "Wind Dancer's Gloves": {'agi': 233, 'hit': 149, 'exp': 169, 'mastery': 1, 'sockets': ['red'], 'bonus_stat': 'haste', 'bonus_value': 10, 'gear_buff': 'tier_11'},    # Tier 11
    '(H)Gloves of Haze': {'agi': 205, 'crit': 150, 'mastery': 130, 'mastery': 1, 'sockets': ['blue'], 'bonus_stat': 'crit', 'bonus_value': 10},
    'Sticky Fingers': {'agi': 205, 'exp': 130, 'mastery': 150, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'agi', 'bonus_value': 10},
}
waist = {
    'Belt of Nefarious Whispers': {'agi': 253, 'hit': 184, 'mastery': 144, 'mastery': 1, 'sockets': ['prismatic']},
    '(H)Dispersing Belt': {'agi': 226, 'crit': 171, 'exp': 191, 'mastery': 2, 'sockets': ['blue', 'prismatic'], 'bonus_stat': 'agi', 'bonus_value': 10},
    'Dispersing Belt': {'agi': 233, 'crit': 149, 'exp': 169, 'mastery': 2, 'sockets': ['blue', 'prismatic'], 'bonus_stat': 'agi', 'bonus_value': 10},
    'Belt of a Thousand Mouths': {'agi': 225, 'crit': 150, 'exp': 150, 'mastery': 1, 'sockets': ['prismatic']},
    'Quicksand Belt': {'agi': 205, 'crit': 130, 'hit': 150, 'mastery': 2, 'sockets': ['blue', 'prismatic'], 'bonus_stat': 'agi', 'bonus_value': 10},
    '(H)Red Beam Cord': {'agi': 205, 'crit': 130, 'exp': 150, 'mastery': 2, 'sockets': ['blue', 'prismatic'], 'bonus_stat': 'haste', 'bonus_value': 10},
    'Red Beam Cord': {'agi': 199, 'crit': 133, 'exp': 133, 'mastery': 2, 'sockets': ['blue', 'prismatic'], 'bonus_stat': 'haste', 'bonus_value': 10},
    'Sash of Musing': {'agi': 205, 'exp': 130, 'mastery': 150, 'mastery': 2, 'sockets': ['red', 'prismatic'], 'bonus_stat': 'mastery', 'bonus_value': 10},
}
legs = {
    "(H)Aberration's Leggings": {'agi': 345, 'crit': 257, 'exp': 217, 'mastery': 2, 'sockets': ['yellow', 'yellow'], 'bonus_stat': 'agi', 'bonus_value': 20},
    "Aberration's Leggings": {'agi': 301, 'crit': 228, 'exp': 188, 'mastery': 2, 'sockets': ['yellow', 'yellow'], 'bonus_stat': 'agi', 'bonus_value': 20},
    "(H)Wind Dancer's LegguardsRogue": {'agi': 345, 'crit': 217, 'mastery': 257, 'mastery': 2, 'sockets': ['yellow', 'blue'], 'bonus_stat': 'agi', 'bonus_value': 20, 'gear_buff': 'tier_11'},    # Tier 11
    "Wind Dancer's LegguardsRogue": {'agi': 301, 'crit': 188, 'mastery': 228, 'mastery': 2, 'sockets': ['yellow', 'blue'], 'bonus_stat': 'agi', 'bonus_value': 20, 'gear_buff': 'tier_11'},    # Tier 11
    "(H)Beauty's Chew Toy": {'agi': 262, 'hit': 162, 'exp': 202, 'mastery': 2, 'sockets': ['red', 'blue'], 'bonus_stat': 'haste', 'bonus_value': 20},
    "Garona's Finest Leggings": {'agi': 268, 'crit': 191, 'exp': 157},
    'Leggings of the Burrowing Mole': {'agi': 262, 'exp': 162, 'mastery': 202, 'mastery': 2, 'sockets': ['red', 'blue'], 'bonus_stat': 'agi', 'bonus_value': 20},
    'Leggings of the Impenitent': {'agi': 228, 'crit': 168, 'exp': 148, 'mastery': 2, 'sockets': ['red', 'yellow'], 'bonus_stat': 'crit', 'bonus_value': 20},
    "Shaw's Finest Leggings": {'agi': 268, 'crit': 191, 'exp': 157},
    'Swiftflight Leggings': {'agi': 228, 'crit': 168, 'exp': 148, 'mastery': 2, 'sockets': ['red', 'yellow'], 'bonus_stat': 'crit', 'bonus_value': 20},
}
feet = {
    "(H)Storm Rider's Boots": {'agi': 266, 'exp': 171, 'mastery': 191, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'mastery', 'bonus_value': 10},    # not tagged heroic in wowhead
    "Storm Rider's Boots": {'agi': 233, 'exp': 149, 'mastery': 169, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'mastery', 'bonus_value': 10},
    'Treads of Fleeting Joy': {'agi': 233, 'crit': 149, 'exp': 169, 'mastery': 1, 'sockets': ['blue'], 'bonus_stat': 'agi', 'bonus_value': 10},
    'Boots of the Hard Way': {'agi': 199, 'crit': 116, 'exp': 142},
    '(H)Boots of the Predator': {'agi': 205, 'crit': 150, 'hit': 130, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'crit', 'bonus_value': 10},
    "(H)Crafty's Gaiters": {'agi': 205, 'exp': 130, 'mastery': 150, 'mastery': 1, 'sockets': ['blue'], 'bonus_stat': 'mastery', 'bonus_value': 10},
    "Crafty's Gaiters": {'agi': 199, 'exp': 133, 'mastery': 133},
    "(H)VanCleef's Boots": {'agi': 205, 'exp': 150, 'mastery': 130, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'agi', 'bonus_value': 10},
}
rings = {
    'Gilnean Ring of Ruination': {'agi': 190, 'hit': 108, 'exp': 138},
    '(H)Lightning Conductor Band': {'agi': 215, 'crit': 143, 'hit': 143},
    'Lightning Conductor Band': {'agi': 190, 'crit': 127, 'hit': 127},
    'Signet of the Elder Council': {'agi': 190, 'exp': 127, 'mastery': 127},
    'Band of Blades': {'agi': 138, 'crit': 116, 'hit': 97, 'mastery': 1, 'sockets': ['yellow'], 'bonus_stat': 'hit', 'bonus_value': 10},
    "Elementium Destroyer's Ring": {'agi': 148, 'crit': 89, 'mastery': 114, 'mastery': 1, 'sockets': ['red'], 'bonus_stat': 'haste', 'bonus_value': 10},
    '(H)Mirage Ring': {'agi': 168, 'hit': 85, 'exp': 128},
    'Mirage Ring': {'agi': 149, 'hit': 76, 'exp': 114},
    '(H)Nautilus Ring': {'agi': 168, 'crit': 112, 'exp': 112},
    '(H)Ring of Blinding Stars': {'agi': 168, 'exp': 112, 'mastery': 112},
    'Ring of Blinding Stars': {'agi': 149, 'exp': 100, 'mastery': 100},
    '(H)Ring of Dun Algaz': {'agi': 168, 'crit': 120, 'hit': 98},
    'Ring of Dun Algaz': {'agi': 149, 'crit': 107, 'hit': 87},
    '(H)Skullcracker Ring': {'agi': 168, 'crit': 112, 'mastery': 112},
    '(H)Skullcracker Ring': {'agi': 168, 'crit': 112, 'exp': 112},
    "Terrath's Signet of Balance": {'agi': 168, 'hit': 112, 'mastery': 112},
}
ring1 = rings
ring2 = rings
trinkets = {
    '(H)Grace of the Herald': {'agi': 285, 'proc': 'heroic_grace_of_the_herald'},
    'Grace of the Herald': {'agi': 153, 'proc': 'grace_of_the_herald'},
    '(H)Key to the Endless Chamber': {'hit': 285, 'proc': 'heroic_key_to_the_endless_chamber'},
    'Key to the Endless Chamber': {'hit': 215, 'proc': 'key_to_the_endless_chamber'},
    '(H)Left Eye of Rajh': {'exp': 285, 'proc': 'heroic_left_eye_of_rajh'},
    'Left Eye of Rajh': {'exp': 252, 'proc': 'left_eye_of_rajh'},
    "(H)Prestor's Talisman of Machination": {'agi': 363, 'proc': 'heroic_prestors_talisman_of_machination'},
    "Prestor's Talisman of Machination": {'agi': 321, 'proc': 'prestors_talisman_of_machination'},
    "(H)Tia's Grace": {'mastery': 285, 'proc': 'heroic_tias_grace'},
    "Tia's Grace": {'mastery': 252, 'proc': 'tias_grace'},
    'Darkmoon Card: Hurricane ': {'agi': 321, 'proc': 'darkmoon_card_hurricane'},
    'Essence of the Cyclone': {'agi': 321, 'proc': 'essence_of_the_cyclone'},
    'Fluid Death ': {'hit': 321, 'proc': 'fluid_death'},
    'Heart of the Vile': {'agi': 234, 'proc': 'heart_of_the_vile'},
    'Unheeded Warning ': {'agi': 321, 'proc': 'unheeded_warning'},
    'Unsolvable Riddle': {'mastery': 321, 'proc': 'unsolvable_riddle', 'gear_buff': 'unsolvable_riddle'},
    'Figurine - Demon Panther ': {'hit': 285, 'proc': 'demon_panther ', 'gear_buff': 'demon_panther '},
}
trinket1 = trinkets
trinket2 = trinkets
melee_weapons = {
    '1.8d (H)Organic Lifeform Inverter': {'agi': 165, 'exp': 110, 'mastery': 110, 'damage': 939.5, 'speed': 1.8, 'type': 'dagger'},
    '1.8d Organic Lifeform Inverter': {'agi': 146, 'exp': 97, 'mastery': 97, 'damage': 832, 'speed': 1.8, 'type': 'dagger'},
    '1.4d Scaleslicer': {'agi': 146, 'hit': 97, 'exp': 97, 'damage': 647.5, 'speed': 1.4, 'type': 'dagger'},
    '1.8d The Twilight Blade': {'proc': 'the_twilight_blade', 'damage': 832, 'speed': 1.8, 'type': 'dagger'},
    "1.4d (H)Uhn'agh Fash, the Darkest Betrayal": {'agi': 165, 'crit': 110, 'exp': 110, 'damage': 750.5, 'speed': 1.4, 'type': 'dagger'},
    "1.4d Uhn'agh Fash, the Darkest Betrayal": {'agi': 146, 'crit': 97, 'exp': 97, 'damage': 647.5, 'speed': 1.4, 'type': 'dagger'},
    "1.4d (H)Barim's Main Gauche": {'agi': 129, 'crit': 86, 'mastery': 86, 'damage': 573.5, 'speed': 1.4, 'type': 'dagger'},
    "1.4d Barim's Main Gauche": {'agi': 115, 'crit': 76, 'mastery': 76, 'damage': 508, 'speed': 1.4, 'type': 'dagger'},
    '1.4d (H)Buzzer Blade': {'agi': 129, 'crit': 86, 'exp': 86, 'damage': 573.5, 'speed': 1.4, 'type': 'dagger'},
    '1.8d Dagger of Restless Nights': {'agi': 129, 'crit': 86, 'hit': 86, 'damage': 737, 'speed': 1.8, 'type': 'dagger'},
    '1.8d Elementium Shank': {'agi': 129, 'hit': 86, 'exp': 86, 'damage': 737.5, 'speed': 1.8, 'type': 'dagger'},
    '1.8d Laquered Lung-Leak Longknife': {'agi': 115, 'crit': 75, 'mastery': 78, 'damage': 653.5, 'speed': 1.8, 'type': 'dagger'},
    '1.8d (H)Meteor Shard': {'agi': 129, 'damage': 737.5, 'speed': 1.8, 'type': 'dagger'},    # not modeled proc
    '1.4d (H)Quicksilver Blade': {'agi': 129, 'exp': 86, 'mastery': 86, 'damage': 573.5, 'speed': 1.4, 'type': 'dagger'},
    "1.8d (H)Steelbender's Masterpiece": {'agi': 129, 'hit': 93, 'mastery': 76, 'damage': 737, 'speed': 1.8, 'type': 'dagger'},
    '1.4d Throat Slasher': {'agi': 129, 'crit': 86, 'hit': 86, 'damage': 573.5, 'speed': 1.4, 'type': 'dagger'},    # off hand
    '1.4d (H)Toxidunk Dagger': {'agi': 129, 'hit': 86, 'exp': 86, 'damage': 573.5, 'speed': 1.4, 'type': 'dagger'},
    '1.8d (H)Wicked Dagger': {'agi': 129, 'crit': 86, 'exp': 86, 'damage': 737.5, 'speed': 1.8, 'type': 'dagger'},
    '1.8d (H)Windwalker Blade': {'agi': 129, 'crit': 86, 'exp': 86, 'damage': 737, 'speed': 1.8, 'type': 'dagger'},
    '1.8d Windwalker Blade': {'agi': 115, 'crit': 76, 'exp': 76, 'damage': 653, 'speed': 1.8, 'type': 'dagger'},
    '2.6f (H)Claws of Torment': {'agi': 165, 'crit': 110, 'exp': 110, 'damage': 1356.5, 'speed': 2.6, 'type': 'fist'},    # main hand
    '2.6f Claws of Torment': {'agi': 146, 'crit': 97, 'exp': 97, 'damage': 1202, 'speed': 2.6, 'type': 'fist'},    # main hand
    '2.6f Crystalline Geoknife': {'agi': 115, 'crit': 76, 'exp': 76, 'damage': 943.5, 'speed': 2.6, 'type': 'fist'},    # main hand
    '2.6f (H)Fist of Pained Senses': {'agi': 129, 'crit': 86, 'exp': 86, 'damage': 1065, 'speed': 2.6, 'type': 'fist'},    # main hand
    '2.6f The Perforator': {'agi': 95, 'mastery': 1, 'sockets': ['red'], 'bonus_stat': 'mastery', 'bonus_value': 10, 'damage': 943.5, 'speed': 2.6, 'type': 'fist'},
    "2.6a (H)Crul'korak, the Lightning's Arc": {'agi': 165, 'crit': 110, 'exp': 110, 'damage': 1356.5, 'speed': 2.6, 'type': 'axe'},
    "2.6a Crul'korak, the Lightning's Arc": {'agi': 146, 'crit': 97, 'exp': 97, 'damage': 1202, 'speed': 2.6, 'type': 'axe'},
    # "2.6a (H)Maimgor's Bite": {'agi': 165, 'hit': 110, 'mastery': 110, 'damage': 1356.5, 'speed': 2.6, 'type': 'axe'},    # off hand
    # "2.6a Maimgor's Bite": {'agi': 146, 'hit': 97, 'mastery': 97, 'damage': 1202, 'speed': 2.6, 'type': 'axe'},    # off hand
    "2.6a Calder's Coated Carrion Carver": {'agi': 115, 'crit': 84, 'exp': 63, 'damage': 943.5, 'speed': 2.6, 'type': 'axe'},
    '2.6a Elementium Gutslicer': {'agi': 129, 'hit': 86, 'mastery': 86, 'damage': 1065, 'speed': 2.6, 'type': 'axe'},
    '2.6a (H)Lightning Whelk Axe': {'agi': 129, 'crit': 86, 'hit': 86, 'damage': 1065, 'speed': 2.6, 'type': 'axe'},
    '2.6a Ravening Slicer': {'agi': 129, 'exp': 86, 'mastery': 86, 'damage': 1065, 'speed': 2.6, 'type': 'axe'},
    # '2.6a Windslicer': {'agi': 129, 'crit': 86, 'mastery': 86, 'damage': 1065, 'speed': 2.6, 'type': 'axe'},    # off hand
    '2.6m (H)Hammer of Sparks': {'agi': 129, 'crit': 86, 'hit': 86, 'damage': 1065, 'speed': 2.6, 'type': 'mace'},
    '2.6m Hammer of Sparks': {'agi': 115, 'crit': 76, 'hit': 76, 'damage': 943.5, 'speed': 2.6, 'type': 'mace'},
    '2.6m (H)Heavy Geode Mace': {'agi': 129, 'hit': 86, 'exp': 86, 'damage': 1065, 'speed': 2.6, 'type': 'mace'},
    '2.6s (H)Fang of Twilight': {'agi': 165, 'crit': 110, 'mastery': 110, 'damage': 1356.5, 'speed': 2.6, 'type': 'sword'},
    '2.6s Fang of Twilight': {'agi': 146, 'crit': 97, 'mastery': 97, 'damage': 1202, 'speed': 2.6, 'type': 'sword'},
    '2.6s Krol Decapitator': {'agi': 146, 'hit': 86, 'exp': 105, 'damage': 1202, 'speed': 2.6, 'type': 'sword'},
    '2.7s (H)Cruel Barb': {'agi': 129, 'crit': 86, 'hit': 86, 'damage': 1106, 'speed': 2.7, 'type': 'sword'},
    "2.6s (H)Thief's Blade": {'agi': 129, 'exp': 86, 'mastery': 86, 'damage': 1065, 'speed': 2.6, 'type': 'sword'},
}
mainhand = melee_weapons
offhand = melee_weapons
ranged = {
    'Dragonwreck Throwing Axe': {'agi': 107, 'exp': 72, 'mastery': 72, 'damage': 1371.5, 'speed': 2.2, 'type': 'thrown'},
    'Spinerender': {'agi': 107, 'crit': 72, 'hit': 72, 'damage': 1371.5, 'speed': 2.2, 'type': 'thrown'},
    '(H)Slashing Thorns': {'agi': 95, 'crit': 63, 'hit': 63, 'damage': 1104.5, 'speed': 2, 'type': 'thrown'},
    'Slashing Thorns': {'agi': 84, 'crit': 56, 'hit': 56, 'damage': 978.5, 'speed': 2, 'type': 'thrown'},

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
    "Destructive Shadowspirit Diamond": (['meta'], {'crit': 54}),
    "Chaotic Shadowspirit Diamond": (['meta'], {'crit': 54, 'gear_buff': ['chaotic_metagem']}),
    "Delicate Chimera's Eye": (['red'], {'agi': 67}),
    "Delicate Inferno Ruby": (['red'], {'agi': 40}),
    "Adept Ember Topaz": (['red', 'yellow'], {'agi': 20, 'mastery': 20}),
    "Deft Ember Topaz": (['red', 'yellow'], {'agi': 20, 'haste': 20}),
    "Glinting Demonseye": (['red', 'blue'], {'agi': 20, 'hit': 20}),
    "Rigid Ocean Sapphire": (['blue'], {'hit': 40})
}