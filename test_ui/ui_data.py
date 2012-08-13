# the following items had incorrect stats and should be corrected now
# necklace of strife
# wind dancer tunic
# dispersing belt
# storm rider's boots
# wind dancer gloves
# Uhn'agh Fash
# Poison Protocol Pauldrons
# Wind Dancer's Spaulders
# lots of necks/heads

import math

class Item(object):
    reforgable_stats = frozenset([
        'crit',
        'hit',
        'exp',
        'haste',
        'mastery'
    ])

    def __init__(self, name, id=0, str=0, agi=0, ap=0, crit=0, hit=0, exp=0, haste=0, mastery=0, sockets=[], bonus_stat='', bonus_value=0, proc='', gear_buff=''):
        self.name = name
        self.id = id
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
        print "before: " + from_stat + " = " + str(getattr(self, from_stat))
        print "        " + to_stat + " = " + str(getattr(self, to_stat))
        reforged_value = math.floor(getattr(self, from_stat) * 0.4)
        setattr(self, from_stat, getattr(self, from_stat) - reforged_value)
        setattr(self, to_stat, reforged_value)
        print "after: " + from_stat + " = " + str(getattr(self, from_stat))
        print "        " + to_stat + " = " + str(getattr(self, to_stat))

class Weapon(Item):
    def __init__(self, name, id=0, str=0, agi=0, ap=0, crit=0, hit=0, exp=0, haste=0, mastery=0, sockets=[], bonus_stat='', bonus_value=0, proc='', gear_buff='', damage=0, speed=0, type=''):
        super(Weapon, self).__init__(name, id, str, agi, ap, crit, hit, exp, haste, mastery, sockets, bonus_stat, bonus_value, proc, gear_buff)
        self.damage = damage
        self.speed = speed
        self.type = type

head = {
    # ----- 5.0 -----
    '(H)Helmet of the Thousandfold Blades': {'id': 87126, 'agi': 1140, 'exp': 755, 'mastery': 828, 'sockets': ['blue', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 180, 'gear_buff': 'tier_14'},
    '(H)Crown of Opportunistic Strikes': {'id': 87070, 'agi': 1054, 'crit': 702, 'haste': 782, 'sockets': ['red', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 180},
    'Helmet of the Thousandfold Blades': {'id': 85301, 'agi': 983, 'exp': 655, 'mastery': 720, 'sockets': ['blue', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 180, 'gear_buff': 'tier_14'},
    'Crown of Opportunistic Strikes': {'id': 86146, 'agi': 906, 'crit': 604, 'haste': 684, 'sockets': ['red', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 180},
    'Red Smoke Bandana': {'id': 89300, 'agi': 906, 'hit': 665, 'mastery': 616, 'sockets': ['blue', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 180},
    '(L)Helmet of the Thousandfold Blades': {'id': 86641, 'agi': 844, 'exp': 567, 'mastery': 624, 'sockets': ['blue', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 180, 'gear_buff': 'tier_14'},
    '(L)Crown of Opportunistic Strikes': {'id': 86804, 'agi': 775, 'crit': 517, 'haste': 597, 'sockets': ['red', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 180},
    'Windblast Helm': {'id': 81283, 'agi': 659, 'haste': 520, 'mastery': 440, 'sockets': ['red', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 180},
    'Soulburner Crown': {'id': 82853, 'agi': 659, 'hit': 537, 'crit': 410, 'sockets': ['red', 'meta'], 'bonus_stat': 'agi', 'bonus_value': 180},
}
neck = {
    # ----- 5.0 -----
    '(H)Choker of the Unleashed Storm': {'id': 86953, 'agi': 769, 'crit': 564, 'mastery': 426},
    '(H)Amulet of the Hidden Kings': {'id': 87045, 'agi': 720, 'haste': 502, 'exp': 445},
    'Choker of the Unleashed Storm': {'id': 86166, 'agi': 682, 'crit': 500, 'mastery': 377},
    'Amulet of the Hidden Kings': {'id': 86047, 'agi': 638, 'haste': 444, 'exp': 394},
    'Choker of the Klaxxi\'va': {'id': 89065, 'agi': 638, 'hit': 363, 'crit': 463},
    'Delicate Necklace of the Golden Lotus': {'id': 90593, 'agi': 638, 'crit': 426, 'mastery': 426},
    '(L)Choker of the Unleashed Storm': {'id': 86824, 'agi': 604, 'crit': 443, 'mastery': 334},
    '(L)Amulet of the Hidden Kings': {'id': 86776, 'agi': 566, 'haste': 394, 'exp': 349},
    'Don Guerrero\'s Glorious Choker': {'id': 90583, 'agi': 566, 'haste': 287, 'mastery': 430},
    'Scorched Scarlet Key': {'id': 81564, 'agi': 501, 'hit': 334, 'exp': 334},
    'Engraved Amber Pendant': {'id': 81271, 'agi': 501, 'crit': 344, 'haste': 318},
}
shoulders = {
    # ----- 5.0 -----
    '(H)Spaulders of the Thousandfold Blades': {'id': 87128, 'agi': 946, 'haste': 520, 'exp': 733, 'sockets': ['blue'], 'bonus_stat': 'agi', 'bonus_value': 60, 'gear_buff': 'tier_14'},
    '(H)Netherrealm Shoulderpads': {'id': 87033, 'agi': 881, 'exp': 690, 'mastery': 447, 'sockets': ['red'], 'bonus_stat': 'agi', 'bonus_value': 60},
    'Spaulders of the Thousandfold Blades': {'id': 85299, 'agi': 829, 'haste': 452, 'exp': 650, 'sockets': ['blue'], 'bonus_stat': 'agi', 'bonus_value': 60, 'gear_buff': 'tier_14'},
    'Netherrealm Shoulderpads': {'id': 85995, 'agi': 771, 'exp': 607, 'mastery': 391, 'sockets': ['red'], 'bonus_stat': 'agi', 'bonus_value': 60},
    'Imperion Spaulders': {'id': 89341, 'agi': 771, 'hit': 513, 'crit': 536, 'sockets': ['yellow'], 'bonus_stat': 'agi', 'bonus_value': 60},
    '(L)Spaulders of the Thousandfold Blades': {'id': 86639, 'agi': 725, 'haste': 391, 'exp': 576, 'sockets': ['blue'], 'bonus_stat': 'agi', 'bonus_value': 60, 'gear_buff': 'tier_14'},
    '(L)Netherrealm Shoulderpads': {'id': 86763, 'agi': 674, 'exp': 533, 'mastery': 342, 'sockets': ['red'], 'bonus_stat': 'agi', 'bonus_value': 60},
    'Doubtridden Shoulderpads': {'id': 81071, 'agi': 668, 'hit': 434, 'exp': 452},
    'Fizzy Spaulders': {'id': 81068, 'agi': 668, 'crit': 412, 'haste': 465},
}
back = {
    # ----- 5.0 -----
    '(H)Legbreaker Greatcloak': {'id': 86963, 'agi': 769, 'crit': 513, 'mastery': 513},
    '(H)Arrow Breaking Windcloak': {'id': 87044, 'agi': 720, 'haste': 399, 'exp': 529},
    'Legbreaker Greatcloak': {'id': 86173, 'agi': 682, 'crit': 454, 'mastery': 454},
    'Arrow Breaking Windcloak': {'id': 86082, 'agi': 638, 'haste': 353, 'exp': 468},
    'Blackguard Cape': {'id': 89076, 'agi': 638, 'hit': 444, 'mastery': 394},
    '(L)Legbreaker Greatcloak': {'id': 86831, 'agi': 604, 'crit': 402, 'mastery': 402},
    '(L)Arrow Breaking Windcloak': {'id': 86782, 'agi': 566, 'haste': 313, 'exp': 415},
    'Dory\'s Pageantry': {'id': 86782, 'agi': 566, 'hit': 377, 'crit': 377},
    'Aerial Bombardment Cloak': {'id': 81282, 'agi': 501, 'hit': 254, 'crit': 381},
    'Wind-soaked Drape': {'id': 81123, 'agi': 501, 'crit': 358, 'mastery': 293},
}
chest = {
    # ----- 5.0 -----
    '(H)Tunic of the Thousandfold Blades': {'id': 87124, 'agi': 1220, 'crit': 880, 'mastery': 800, 'sockets': ['yellow', 'yellow'], 'bonus_stat': 'mastery', 'bonus_value': 120, 'gear_buff': 'tier_14'},
    '(H)Chestguard of Total Annihilation': {'id': 87058, 'agi': 1134, 'crit': 698, 'haste': 833, 'sockets': ['red', 'yellow'], 'bonus_stat': 'agi', 'bonus_value': 120},
    'Tunic of the Thousandfold Blades': {'id': 85303, 'agi': 1063, 'crit': 775, 'mastery': 695, 'sockets': ['yellow', 'yellow'], 'bonus_stat': 'mastery', 'bonus_value': 120, 'gear_buff': 'tier_14'},
    'Chestguard of Total Annihilation': {'id': 86136, 'agi': 986, 'crit': 609, 'haste': 729, 'sockets': ['red', 'yellow'], 'bonus_stat': 'agi', 'bonus_value': 120},
    'Softfoot Silentwrap': {'id': 89431, 'agi': 986, 'hit': 554, 'exp': 761, 'sockets': ['blue', 'yellow'], 'bonus_stat': 'agi', 'bonus_value': 120},
    'Chestguard of Nemeses': {'id': 85788, 'agi': 1223, 'crit': 755, 'mastery': 852},
    '(L)Tunic of the Thousandfold Blades': {'id': 86643, 'agi': 924, 'crit': 683, 'mastery': 603, 'sockets': ['yellow', 'yellow'], 'bonus_stat': 'mastery', 'bonus_value': 120, 'gear_buff': 'tier_14'},
    'Greyshadow Chestguard': {'id': 85823, 'agi': 1015, 'crit': 660, 'mastery': 687},
    'Vulajin\'s Vicious Breastplate': {'id': 90585, 'agi': 855, 'crit': 557, 'mastery': 637, 'sockets': ['red', 'yellow'], 'bonus_stat': 'mastery', 'bonus_value': 20}, #bug? seems like bonus should be 120
    '(L)Chestguard of Total Annihilation': {'id': 86795, 'agi': 855, 'crit': 530, 'haste': 636, 'sockets': ['red', 'yellow'], 'bonus_stat': 'agi', 'bonus_value': 120},
    'Korloff\'s Raiment': {'id': 81573, 'agi': 899, 'hit': 456, 'crit': 683},
    'Nimbletoe Chestguard': {'id': 81080, 'agi': 899, 'crit': 609, 'haste': 584},
    'Delicate Chestguard of the Golden Lotus': {'id': 90597, 'agi': 899, 'crit': 660, 'mastery': 497},
    'Refurbished Zandalari Vestment': {'id': 89667, 'agi': 797, 'haste': 555, 'exp': 492},
}
wrists = {
    # ----- 5.0 -----
    '(H)Bracers of Unseen Strikes': {'id': 86954, 'agi': 769, 'crit': 487, 'haste': 528},
    '(H)Smooth Bettle Wristbands': {'id': 86995, 'agi': 769, 'exp': 414, 'mastery': 571},
    'Bracers of Unseen Strikes': {'id': 86163, 'agi': 682, 'crit': 432, 'haste': 468},
    'Smooth Bettle Wristbands': {'id': 86185, 'agi': 682, 'exp': 366, 'mastery': 506},
    'Quillpaw Family Bracers': {'id': 88884, 'agi': 638, 'hit': 426, 'crit': 426},
    '(L)Bracers of Unseen Strikes': {'id': 86821, 'agi': 604, 'crit': 383, 'haste': 414},
    '(L)Smooth Bettle Wristbands': {'id': 86843, 'agi': 604, 'exp': 325, 'mastery': 448},
    'Lightblade Bracer': {'id': 81700, 'agi': 501, 'crit': 363, 'mastery': 285},
    'Saboteur\'s Stabilizing Bracers': {'id': 81090, 'agi': 501, 'haste': 339, 'exp': 326},
}
hands = {
    # ----- 5.0 -----
    '(H)Gloves of the Thousandfold Blades': {'id': 87125, 'agi': 1026, 'hit': 724, 'crit': 616, 'gear_buff': 'tier_14'},
    '(H)Bonebreaker Gauntlets': {'id': 86964, 'agi': 946, 'hit': 495, 'haste': 730, 'sockets': ['blue'], 'bonus_stat': 'haste', 'bonus_value': 60},
    'Murderer\'s Gloves': {'id': 85828, 'agi': 909, 'crit': 615, 'mastery': 591},
    'Gloves of the Thousandfold Blades': {'id': 85302, 'agi': 909, 'hit': 641, 'crit': 546, 'gear_buff': 'tier_14'},
    'Bonebreaker Gauntlets': {'id': 86176, 'agi': 829, 'hit': 434, 'haste': 643, 'sockets': ['blue'], 'bonus_stat': 'haste', 'bonus_value': 60},
    'Fingers of the Loneliest Monk': {'id': 88744, 'agi': 851, 'exp': 593, 'mastery': 526},
    '(L)Bonebreaker Gauntlets': {'id': 86834, 'agi': 725, 'hit': 380, 'haste': 565, 'sockets': ['blue'], 'bonus_stat': 'haste', 'bonus_value': 60},
    '(L)Gloves of the Thousandfold Blades': {'id': 86642, 'agi': 805, 'hit': 568, 'crit': 484, 'gear_buff': 'tier_14'},
    'Greyshadow Gloves': {'id': 85824, 'agi': 754, 'crit': 490, 'mastery': 510},
    'Tombstone Gauntlets': {'id': 82858, 'agi': 668, 'hit': 349, 'haste': 502},
    'Hound Trainer\'s Gloves': {'id': 81695, 'agi': 668, 'exp': 391, 'mastery': 478},
}
waist = {
    # ----- 5.0 -----
    '(H)Stalker\'s Cord of Eternal Autumn': {'id': 87180, 'agi': 946, 'hit': 593, 'crit': 674, 'sockets': ['blue', 'prismatic'], 'bonus_stat': 'crit', 'bonus_value': 60},
    '(H)Tomb Raider\'s Girdle': {'id': 87022, 'agi': 801, 'haste': 598, 'exp': 498, 'sockets': ['yellow', 'blue', 'prismatic'], 'bonus_stat': 'exp', 'bonus_value': 120},
    'Stalker\'s Cord of Eternal Autumn': {'id': 86341, 'agi': 829, 'hit': 521, 'crit': 593, 'sockets': ['blue', 'prismatic'], 'bonus_stat': 'crit', 'bonus_value': 60},
    'Tomb Raider\'s Girdle': {'id': 85982, 'agi': 691, 'haste': 521, 'exp': 432, 'sockets': ['yellow', 'blue', 'prismatic'], 'bonus_stat': 'exp', 'bonus_value': 120},
    'Klaxxi Lash of the Borrower': {'id': 89060, 'agi': 771, 'crit': 391, 'mastery': 607, 'sockets': ['blue', 'prismatic'], 'bonus_stat': 'crit', 'bonus_value': 60},
    '(L)Stalker\'s Cord of Eternal Autumn': {'id': 86899, 'agi': 725, 'hit': 457, 'crit': 520, 'sockets': ['blue', 'prismatic'], 'bonus_stat': 'crit', 'bonus_value': 60},
    '(L)Tomb Raider\'s Girdle': {'id': 86750, 'agi': 594, 'haste': 452, 'exp': 373, 'sockets': ['yellow', 'blue', 'prismatic'], 'bonus_stat': 'exp', 'bonus_value': 120},
    'Icewrath Belt': {'id': 82823, 'agi': 668, 'crit': 401, 'mastery': 471},
    'Belt of Brazen Inebriation': {'id': 81135, 'agi': 668, 'hit': 412, 'exp': 465},
}
legs = {
    # ----- 5.0 -----
    '(H)Legguards of the Thousandfold Blades': {'id': 87127, 'agi': 1300, 'hit': 659, 'haste': 1009, 'sockets': ['red'], 'bonus_stat': 'agi', 'bonus_value': 60, 'gear_buff': 'tier_14'},
    '(H)Stoneflesh Leggings': {'id': 87013, 'agi': 1134, 'crit': 845, 'exp': 677, 'sockets': ['red', 'blue'], 'bonus_stat': 'agi', 'bonus_value':120},
    'Legguards of the Thousandfold Blades': {'id': 85300, 'agi': 1143, 'hit': 580, 'haste': 890, 'sockets': ['red'], 'bonus_stat': 'agi', 'bonus_value': 60, 'gear_buff': 'tier_14'},
    'Stoneflesh Leggings': {'id': 85926, 'agi': 986, 'crit': 740, 'exp': 590, 'sockets': ['red', 'blue'], 'bonus_stat': 'agi', 'bonus_value':120},
    'Dreadsworn Slayer Legs': {'id': 89090, 'agi': 1066, 'crit': 801, 'mastery': 594, 'sockets': ['red'], 'bonus_stat': 'agi', 'bonus_value':60},
    '(L)Legguards of the Thousandfold Blades': {'id': 86640, 'agi': 1004, 'hit': 509, 'haste': 784, 'sockets': ['red'], 'bonus_stat': 'agi', 'bonus_value': 60, 'gear_buff': 'tier_14'},
    '(L)Stoneflesh Leggings': {'id': 86743, 'agi': 855, 'crit': 646, 'exp': 514, 'sockets': ['red', 'blue'], 'bonus_stat': 'agi', 'bonus_value':120},
    'Wall-Breaker Legguards': {'id': 81091, 'agi': 899, 'exp': 584, 'mastery': 609},
    'Ghostwoven Legguards': {'id': 82851, 'agi': 899, 'crit': 497, 'haste': 660},
}
feet = {
    # ----- 5.0 -----
    '(H)Boots of the Still Breath': {'id': 86943, 'agi': 946, 'crit': 551, 'haste': 695, 'sockets': ['yellow'], 'bonus_stat': 'crit', 'bonus_value': 60},
    '(H)Treads of Deadly Secretions': {'id': 86984, 'agi': 946, 'exp': 568, 'mastery': 685, 'sockets': ['yellow'], 'bonus_stat': 'exp', 'bonus_value': 60},
    'Boots of the Still Breath': {'id': 86153, 'agi': 829, 'crit': 485, 'haste': 610, 'sockets': ['yellow'], 'bonus_stat': 'crit', 'bonus_value': 60},
    'Treads of Deadly Secretions': {'id': 86984, 'agi': 829, 'exp': 500, 'mastery': 602, 'sockets': ['yellow'], 'bonus_stat': 'exp', 'bonus_value': 60},
    'Tukka-Tuk\'s Hairy Boots': {'id': 88868, 'agi': 851, 'hit': 601, 'haste': 512},
    '(L)Boots of the Still Breath': {'id': 86811, 'agi': 725, 'crit': 426, 'haste': 535, 'sockets': ['yellow'], 'bonus_stat': 'crit', 'bonus_value': 60},
    '(L)Treads of Deadly Secretions': {'id': 86859, 'agi': 725, 'exp': 439, 'mastery': 528, 'sockets': ['yellow'], 'bonus_stat': 'exp', 'bonus_value': 60},
    'Dashing Strike Treads': {'id': 81688, 'agi': 668, 'crit': 391, 'mastery': 478},
    'Boots of Plummeting Death': {'id': 81249, 'agi': 668, 'haste': 434, 'exp': 452},
}
rings = {
    # ----- 5.0 -----
    '(HE)Regail\'s Band of the Endless': {'id': 90503, 'agi': 821, 'crit': 571, 'haste': 507},
    '(H)Painful Thorned Ring': {'id': 86974, 'agi': 769, 'exp': 438, 'mastery': 557},
    '(H)Regail\'s Band of the Endless': {'id': 87144, 'agi': 769, 'crit': 536, 'haste': 475},
    '(E)Regail\'s Band of the Endless': {'id': 90517, 'agi': 727, 'crit': 506, 'haste': 449},
    'Painful Thorned Ring': {'id': 86200, 'agi': 682, 'exp': 388, 'mastery': 494},
    'Regail\'s Band of the Endless': {'id': 86231, 'agi': 682, 'crit': 474, 'haste': 421},
    'Anji\'s Keepsake': {'id': 89070, 'agi': 638, 'hit': 323, 'haste': 485},
    '(L)Painful Thorned Ring': {'id': 86851, 'agi': 604, 'exp': 343, 'mastery': 437},
    '(L)Regail\'s Band of the Endless': {'id': 86869, 'agi': 604, 'crit': 420, 'haste': 373},
    'Perculia\'s Peculiar Signet': {'id': 90584, 'agi': 566, 'hit': 322, 'haste': 410},
    'Seal of Ghoulish Glee': {'id': 88168, 'agi': 535, 'hit': 313, 'crit': 382},
    'Pulled Grenade Pin': {'id': 81191, 'agi': 501, 'crit': 349, 'mastery': 309},
    'Signet of Dancing Jade': {'id': 81128, 'agi': 501, 'crit': 309, 'exp': 349},
    'Seal of Hateful Meditation': {'id': 81186, 'agi': 501, 'hit': 254, 'haste': 381},
}
ring1 = rings
ring2 = rings
trinkets = {
    # ----- 5.0 -----
    '(H)Terror in the Mists': {'id': 87167, 'agi': 1300, 'proc': 'heroic_terror_in_the_mists'},
    '(H)Jade Bandit Figurine': {'id': 87079, 'agi': 1218, 'proc': 'heroic_jade_bandit_figurine'},
    '(H)Bottle of Infinite Stars': {'id': 87057, 'mastery': 1218, 'proc': 'heroic_bottle_of_infinite_stars'},
    'Terror in the Mists': {'id': 86332, 'agi': 1152, 'proc': 'terror_in_the_mists'},
    'Jade Bandit Figurine': {'id': 86043, 'agi': 1079, 'proc': 'jade_bandit_figurine'},
    'Bottle of Infinite Stars': {'id': 86132, 'mastery': 1079, 'proc': 'bottle_of_infinite_stars'},
    "Hawkmaster's Talon": {'id': 89082, 'agi': 1079, 'proc': 'hawkmasters_talon'},
    '(L)Terror in the Mists': {'id': 86890, 'agi': 1021, 'proc': 'lfr_terror_in_the_mists'},
    '(L)Jade Bandit Figurine': {'id': 87079, 'agi': 956, 'proc': 'lfr_jade_bandit_figurine'},
    '(L)Bottle of Infinite Stars': {'id': 87057, 'mastery': 956, 'proc': 'lfr_bottle_of_infinite_stars'},
    'Relic of Xuen': {'id': 79328, 'agi': 956, 'proc': 'relic_of_xuen'},
    "Coren's Cold Chromium Coaster": {'id': 87574, 'crit': 904, 'proc': 'corens_cold_chromium_coaster'},
    'Flashing Steel Talisman' : {'id': 81265, 'hit': 847, 'proc': 'flashing_steel_talisman'},
    'Searing Words' : {'id': 81267, 'crit': 847, 'proc': 'searing_words'},
    'Windswept Pages' : {'id': 81125, 'agi': 847, 'proc': 'windswept_pages'},
    #'Shadow-Pan Dragon Gun' : {'id': 88995, 'proc': 'shadow_pan_dragon_gun'}, #worth modelling?
    'Zen Alchemist Stone': {'id': 75274, 'mastery': 751, 'proc': 'zen_alchemist_stone'},
}
trinket1 = trinkets
trinket2 = trinkets
melee_weapons = {
    # ----- 5.0 -----
    #daggers
    'd-(H)Spiritsever': {'id': 87166, 'agi': 592, 'exp': 337, 'mastery': 429, 'damage': 6733, 'speed': 1.8, 'type': 'dagger','sockets': ['sha'], 'bonus_stat': 'agi', 'bonus_value': 0},
    'd-(H)Dagger of the Seven Stars': {'id': 87012, 'agi': 554, 'hit': 324, 'haste': 396, 'damage': 6308, 'speed': 1.8, 'type': 'dagger'},
    'd-Spiritsever': {'id': 86391, 'agi': 524, 'exp': 298, 'mastery': 380, 'damage': 5965, 'speed': 1.8, 'type': 'dagger','sockets': ['sha'], 'bonus_stat': 'agi', 'bonus_value': 0},
    'd-Dagger of the Seven Stars': {'id': 85924, 'agi': 491, 'hit': 287, 'haste': 351, 'damage': 5588, 'speed': 1.8, 'type': 'dagger'},
    'd-(L)Spiritsever': {'id': 86910, 'agi': 464, 'exp': 264, 'mastery': 336, 'damage': 5284.5, 'speed': 1.8, 'type': 'dagger','sockets': ['sha'], 'bonus_stat': 'agi', 'bonus_value': 0},
    'd-(L)Dagger of the Seven Stars': {'id': 86741, 'agi': 435, 'hit': 254, 'haste': 311, 'damage': 4951, 'speed': 1.8, 'type': 'dagger'},
    'd-Tolakesh, Horn of the Black Ox': {'id': 87547, 'agi': 435, 'hit': 294, 'exp': 283, 'damage': 4951, 'speed': 1.8, 'type': 'dagger'},
    "d-Amber Slicer of Klaxxi'vess": {'id': 89393, 'agi': 385, 'haste': 261, 'mastery': 251, 'damage': 4386, 'speed': 1.8, 'type': 'dagger'},    
    "d-Koegler's Ritual Knife": {'id': 82813, 'agi': 385, 'hit': 201, 'mastery': 290, 'damage': 4386, 'speed': 1.8, 'type': 'dagger'},    
    'd-Mantid Trochanter': {'id': 81088, 'agi': 385, 'crit': 251, 'haste': 261, 'damage': 4386, 'speed': 1.8, 'type': 'dagger'},    
    'd-Masterwork Ghost Shard': {'id': 82974, 'agi': 385, 'crit': 283, 'mastery': 213, 'damage': 4386, 'speed': 1.8, 'type': 'dagger'},
    #swords, maces, fists, axes
    "f-(H)Claws of Shek'zeer": {'id': 86988, 'agi': 592, 'crit': 444, 'exp': 309, 'damage': 9725.5, 'speed': 2.6, 'type': 'fist','sockets': ['sha'], 'bonus_stat': 'agi', 'bonus_value': 0},    
    "f-(H)Gara'kal, Fist of the Spiritbinder": {'id': 87032, 'agi': 554, 'haste': 391, 'mastery': 333, 'damage': 9111.5, 'speed': 2.6, 'type': 'fist'},    
    "f-Claws of Shek'zeer": {'id': 86226, 'agi': 524, 'crit': 394, 'exp': 274, 'damage': 8616, 'speed': 2.6, 'type': 'fist','sockets': ['sha'], 'bonus_stat': 'agi', 'bonus_value': 0},    
    "f-Gara'kal, Fist of the Spiritbinder": {'id': 85994, 'agi': 491, 'haste': 347, 'mastery': 295, 'damage': 8072, 'speed': 2.6, 'type': 'fist'},    
    "f-(L)Claws of Shek'zeer": {'id': 86864, 'agi': 464, 'crit': 349, 'exp': 242, 'damage': 7633.5, 'speed': 2.6, 'type': 'fist','sockets': ['sha'], 'bonus_stat': 'agi', 'bonus_value': 0},    
    "f-(L)Gara'kal, Fist of the Spiritbinder": {'id': 86762, 'agi': 435, 'haste': 307, 'mastery': 261, 'damage': 7151, 'speed': 2.6, 'type': 'fist'},    
    "f-Ka'eng, Breath of the Shadow": {'id': 87543, 'agi': 355, 'crit': 287, 'exp': 187, 'damage': 7151, 'speed': 2.6, 'type': 'fist', 'sockets': ['blue'], 'bonus_stat': 'exp', 'bonus_value': 60},    
    "f-Claws of Gekkan": {'id': 81245, 'agi': 385, 'crit': 272, 'haste': 232, 'damage': 6335, 'speed': 2.6, 'type': 'fist'},    
    "f-Ner'onok's Razor Katar": {'id': 81286, 'agi': 385, 'hit': 257, 'exp': 257, 'damage': 6335, 'speed': 2.6, 'type': 'fist'},    
}
mainhand = melee_weapons
offhand = melee_weapons

default_talents = {
    #
}

enchants = {
    'head': {
        #'Arcanum of the Ramkahen':{'agi': 60, 'haste': 35}
    },
    'shoulders': {
        #'Greater Inscription of Shattered Crystal': {'agi': 50, 'mastery': 25},
        #'Lesser Inscription of Shattered Crystal': {'agi': 30, 'mastery': 20}
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
    "Fleet Mists Metagem": (['meta'], {'mastery': 432}),
    "Agile Mists Metagem": (['meta'], {'agi': 216, 'gear_buff': ['chaotic_metagem']}),
    "Delicate Mists Gem": (['red'], {'agi': 160}),
    "Adept Mists Gem": (['red', 'yellow'], {'agi': 80, 'mastery': 160}),
    "Deft Mists Gem": (['red', 'yellow'], {'agi': 80, 'haste': 160}),
    "Glinting Mists Gem": (['red', 'blue'], {'agi': 80, 'hit': 160}),
    "Rigid Mists Gem": (['blue'], {'hit': 320})
}