# Original Code by by Ayliex @ EJ ( https://github.com/postrov/sc-character-import )
# -*- coding: utf-8 -*-
from os import path
from types import *
import sys
import pprint
import shelve
import math

sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))

from wowapi.api import WoWApi

wowapi = WoWApi()
pp = pprint.PrettyPrinter(indent=4)


class ItemDB:
    def __init__(self):
        pass

    def get_item(self, id):
        return None

    def add_item(self, id, item):
        pass

    def close(self):
        pass



class SimpleItemDB(ItemDB):
    def __init__(self, path):
        self.path = path
        self.db = shelve.open(path, writeback = True)

    def get_item(self, id):
        str_id = str(id)
        if str_id in self.db:
            return self.db[str_id]
        else:
            return None

    def add_item(self, id, item):
        str_id = str(id)
        self.db[str_id] = item
        self.sync() # FIXME

    def close(self):
        self.db.close()

    def sync(self):
        self.db.sync()


item_db = SimpleItemDB('item_db')


def get_item_cached(region, id):
    cached_item = item_db.get_item(id)
    if cached_item:
        return cached_item
    else:
        item = wowapi.get_item(region, id)
        item_db.add_item(id, item)
        return item

class CharacterData:
    races = {1 : 'human',
             2 : 'orc',
             3 : 'dwarf',
             4 : 'night_elf',
             5 : 'undead',
             6 : 'tauren',
             7 : 'gnome',
             8 : 'troll',
             9 : 'goblin',
             10 : 'blood_elf',
             11 : 'draenei',
             22 : 'worgen',
             24 : 'pandaren', #Neutral
             25 : 'pandaren', #Alliance
             26 : 'pandaren', #Horde
    }
    statMap = {3:'agi', 4:'str', 5:'int', 6:'spirit', 7:'stam', 31:'hit', 32:'crit', 36:'haste', 37:'exp', 49:'mastery',
               35:'pvp_resil', 57:'pvp_power'}

    enchants = {4441 : 'windsong',
                4443 : 'elemental_force',
                4444 : 'dancing_steel',
                4416 : [{'stat':'agi', 'value':170}], # Enchant Bracer - Greater Agility
                4359 : [{'stat':'agi', 'value':180}], #Enchanting Perk
                4411 : [{'stat':'mastery', 'value':170}],
                4416 : [{'stat':'agi', 'value':170}],
                4419 : [{'stat':'agi', 'value':80}, {'stat':'str', 'value':80}, {'stat':'stam', 'value':80}],
                4421 : [{'stat':'hit', 'value':180}],
                4426 : [{'stat':'haste', 'value':175}], # Enchant Boots - Greater Haste
                4428 : [{'stat':'agi', 'value':140}], #Speed Boost
                4430 : [{'stat':'haste', 'value':170}],
                4431 : [{'stat':'exp', 'value':170}],
                4433 : [{'stat':'mastery', 'value':170}],
                4429 : [{'stat':'mastery', 'value':140}], # Pandaren's Step
                4804 : [{'stat':'agi', 'value':200}, {'stat':'crit', 'value':100}],
                4822 : [{'stat':'agi', 'value':285}, {'stat':'crit', 'value':165}],
                4875 : [{'stat':'agi', 'value':500}], #Leatherworking Perk
                4871 : [{'stat':'agi', 'value':170}, {'stat':'crit', 'value':100}],
                4880 : [{'stat':'agi', 'value':285}, {'stat':'crit', 'value':165}],
                4822 : [{'stat':'agi', 'value':285}, {'stat':'crit', 'value':165}], # Shadowleather Leg Armor
                4411 : [{'stat':'mastery', 'value':170}],
                4871 : [{'stat':'agi', 'value':170}, {'stat':'crit', 'value':100}],
                4427 : [{'stat':'hit', 'value':175}],
                4908 : [{'stat':'agi', 'value':120}, {'stat':'crit', 'value':80}], # Tiger Claw Inscrption
    }
    
    trinkets = {87057 : 'heroic_bottle_of_infinite_stars', 
                86132 : 'bottle_of_infinite_stars',
                87167 : 'heroic_terror_in_the_mists',
                79328 : 'relic_of_xuen',
                86791 : 'lfr_bottle_of_infinite_stars',
                86332 : 'terror_in_the_mists', 
                87079 : 'heroic_jade_bandit_figurine',
                75274 : 'zen_alchemist_stone',
                86890 : 'lfr_terror_in_the_mists', 
                89082 : 'hawkmasters_talon',
                86043 : 'jade_bandit_figurine',
                81267 : 'searing_words', 
                81265 : 'flashing_steel_talisman',
                81125 : 'windswept_pages',
                86772 : 'lfr_jade_bandit_figurine',
                87574 : 'corens_cold_chromium_coaster'}

    sets = {'t14' : {'pieces': {u'head'     : 'Helmet of the Thousandfold Blades',
                                u'shoulder' : 'Spaulders of the Thousandfold Blades',
                                u'chest'    : 'Tunic of the Thousandfold Blades',
                                u'hands'    : 'Gloves of the Thousandfold Blades',
                                u'legs'     : 'Legguards of the Thousandfold Blades'},
                     'set_bonus' : {2 : 'rogue_t14_2pc', 4 : 'rogue_t14_4pc'}}}

    glyphs = {# Major
              u'Glyph of Adrenaline Rush'          :     'adrenaline_rush',    
              u'Glyph of Ambush'                   :     'ambush',             
              u'Glyph of Blade Flurry'             :     'blade_flurry',       
              u'Glyph of Blind'                    :     'blind',              
              u'Glyph of Cheap Shot'               :     'cheap_shot',         
              u'Glyph of Cloak of Shadows'         :     'cloak_of_shadows',   
              u'Glyph of Crippling Poison'         :     'crippling_poison',   
              u'Glyph of Deadly Momentum'          :     'deadly_momentum',    
              u'Glyph of Debilitation'             :     'debilitation',       
              u'Glyph of Evasion'                  :     'evasion',            
              u'Glyph of Expose Armor'             :     'expose_armor',       
              u'Glyph of Feint'                    :     'feint',              
              u'Glyph of Garrote'                  :     'garrote',            
              u'Glyph of Gouge'                    :     'gouge',              
              u'Glyph of Kick'                     :     'kick',               
              u'Glyph of Recuperate'               :     'recuperate',         
              u'Glyph of Sap'                      :     'sap',                
              u'Glyph of Shadow Walk'              :     'shadow_walk',        
              u'Glyph of Shiv'                     :     'shiv',               
              u'Glyph of Smoke Bomb'               :     'smoke_bomb',         
              u'Glyph of Sprint'                   :     'sprint',             
              u'Glyph of Stealth'                  :     'stealth',            
              u'Glyph of Vanish'                   :     'vanish',             
              u'Glyph of Vendetta'                 :     'vendetta',           
              # Minor                             
              u'Glyph of Blurred Speed'            :     'blurred_speed',      
              u'Glyph of Decoy'                    :     'decoy',              
              u'Glyph of Detection'                :     'detection',          
              u'Glyph of Disguise'                 :     'disguise',           
              u'Glyph of Distract'                 :     'distract',           
              u'Glyph of Hemorrhage'               :     'hemorrhage',         
              u'Glyph of Killing Spree'            :     'killing_spree',      
              u'Glyph of Pick Lock'                :     'pick_lock',          
              u'Glyph of Pick Pocket'              :     'pick_pocket',        
              u'Glyph of Poisons'                  :     'poisons',            
              u'Glyph of Safe Fall'                :     'safe_fall',          
              u'Glyph of Tricks of the Trade'      :     'tricks_of_the_trade'}
    
    reforgeMap = {113: ('spirit', 'dodge_rating'),
                  114: ('spirit','parry_rating'),
                  115: ('spirit','hit'),
                  116: ('spirit','crit'),
                  117: ('spirit','haste'),
                  118: ('spirit','exp'),
                  119: ('spirit','mastery'),
                  120: ('dodge_rating','spirit'),
                  121: ('dodge_rating','parry_rating'),
                  122: ('dodge_rating','hit'),
                  123: ('dodge_rating','crit'),
                  124: ('dodge_rating','haste'),
                  125: ('dodge_rating','exp'),
                  126: ('dodge_rating','mastery'),
                  127: ('parry_rating','spirit'),
                  128: ('parry_rating','dodge_rating'),
                  129: ('parry_rating','hit'),
                  130: ('parry_rating','crit'),
                  131: ('parry_rating','haste'),
                  132: ('parry_rating','exp'),
                  133: ('parry_rating','mastery'),
                  134: ('hit','spirit'),
                  135: ('hit','dodge_rating'),
                  136: ('hit','parry_rating'),
                  137: ('hit','crit'),
                  138: ('hit','haste'),
                  139: ('hit','exp'),
                  140: ('hit','mastery'),
                  141: ('crit','spirit'),
                  142: ('crit','dodge_rating'),
                  143: ('crit','parry_rating'),
                  144: ('crit','hit'),
                  145: ('crit','haste'),
                  146: ('crit','exp'),
                  147: ('crit','mastery'),
                  148: ('haste','spirit'),
                  149: ('haste','dodge_rating'),
                  150: ('haste','parry_rating'),
                  151: ('haste','hit'),
                  152: ('haste','crit'),
                  153: ('haste','exp'),
                  154: ('haste','mastery'),
                  155: ('exp','spirit'),
                  156: ('exp','dodge_rating'),
                  157: ('exp','parry_rating'),
                  158: ('exp','hit'),
                  159: ('exp','crit'),
                  160: ('exp','haste'),
                  161: ('exp','mastery'),
                  162: ('mastery','spirit'),
                  163: ('mastery','dodge_rating'),
                  164: ('mastery','parry_rating'),
                  165: ('mastery','hit'),
                  166: ('mastery','crit'),
                  167: ('mastery','haste'),
                  168: ('mastery','exp'),
        }


    def __init__(self, region, realm, name, verbose=False):
        self.region = region
        self.realm = realm
        self.name = name
        self.verbose = verbose
        self.raw_data = None
        self.chaotic_metagem = False

    def do_import(self):
        self.raw_data = wowapi.get_character(self.region , self.realm, self.name, ['talents', 'items', 'stats'])

    def get_race(self):
        return CharacterData.races[self.raw_data[u'data'][u'race']]

    def get_weapon(self, weapon_data, item_data):
        weapon_info = weapon_data['data'][u'weaponInfo']
        weaponMap = {1:'axe', 2:'2h_axe', 3:'bow', 4:'rifle',5:'mace', 6:'2h_mace', 7:'polearm', 8:'sword', 9:'2H_sword', 10:'staff',
                     11:'exotic', 12:'2h_exotic', 13:'fist', 14:'misc', 15:'dagger', 16:'thrown', 17:'spear', 18:'xbow', 19:'wand',
                     20:'fishing_pole'}
        tmpItem = get_item_cached(self.region, item_data[u'id'])
        damage_info = weapon_info[u'damage']
        damage = (damage_info[u'max'] + damage_info[u'min']) / 2
        speed = weapon_info[u'weaponSpeed']
        type = weaponMap[ tmpItem['data'][u'itemSubClass'] ]
        enchant = CharacterData.enchants[item_data[u'tooltipParams'][u'enchant']]
        return [damage, speed, type, enchant]

    def get_mh(self):
        item_data = self.raw_data['data'][u'items'][u'mainHand']
        weapon_data = get_item_cached(self.region, item_data[u'id'])
#        weapon_data = get_item_cached(self.region, 85924)
        return self.get_weapon(weapon_data, item_data)

    def get_oh(self):
        item_data = self.raw_data['data'][u'items'][u'offHand']
        weapon_data = get_item_cached(self.region, item_data[u'id'])
        return self.get_weapon(weapon_data, item_data)
    
    def get_mh_type(self):
        return self.get_mh()[2]

    def get_trinket_proc(self, item_data):
        id = item_data[u'id']
        if id in CharacterData.trinkets:
            return CharacterData.trinkets[id]
        else:
            return item_data[u'name'] # fallback, this will most likely be rejected by shadowcraft

    def get_trinket_procs(self):
        trinket1 = self.raw_data['data'][u'items'][u'trinket1']
        trinket2 = self.raw_data['data'][u'items'][u'trinket2']
        return [self.get_trinket_proc(trinket1), self.get_trinket_proc(trinket2)]

    def get_procs(self):
        procs = []
        procs += self.get_trinket_procs()
        return procs

    def get_set_bonuses(self):
        set_bonuses = []
        for set_name in CharacterData.sets:
            s = CharacterData.sets[set_name]
            pieces = s['pieces']
            pieces_found = 0
            for p in pieces:
                if self.raw_data['data'][u'items'][p][u'name'] == pieces[p]:
                    pieces_found += 1
#                   print 'found set piece, set: %s, pieces so far: %d' % (set_name, pieces_found)
                    if pieces_found in s['set_bonus']:
                        set_bonuses.append(s['set_bonus'][pieces_found])
        return set_bonuses

    def get_gear_buffs(self):
        gear_buffs = []
        gear_buffs += self.get_set_bonuses()
        return gear_buffs

    def get_stats(self):
        stats_data = self.raw_data['data'][u'stats']
        agi = stats_data[u'agi']
        str = stats_data[u'str']
        ap = stats_data[u'attackPower']
        crit = stats_data[u'critRating']
        hit = stats_data[u'hitRating']
        exp = stats_data[u'expertiseRating']
        haste = stats_data[u'hasteRating']
        mast = stats_data[u'masteryRating']
#        ret = [str, agi + 956, 250, crit, hit, exp, haste, mast]
#        pp.pprint(ret)
        return [str, agi, ap - 2 * agi, crit, hit, exp, haste, mast]

    def get_gear_stats(self):
        #           
        lst = {'agi': 0, 'str':0, 'int':0, 'spirit':0, 'stam':0, 'crit':0, 'hit':0, 'exp':0, 'haste':0, 'mastery':0, 'ap':0, 'pvp_power':0, 'pvp_resil':0}
        reforge = ('none', 'none')
        reforgeID = None
        gemColorToSocketColors = {u'RED': (u'RED'), u'YELLOW':(u'YELLOW'), u'BLUE':(u'BLUE'), u'META':(u'META'), u'COGWHEEL':(u'COGWHEEL'),
                                  u'ORANGE':(u'RED', u'YELLOW'), u'PURPLE':(u'RED', u'BLUE'), u'GREEN':(u'YELLOW', u'BLUE')}
        verboseStatMap = {'Agility':'agi', 'Strength':'str', 'Stamina':'stam', 'Critical Strike':'crit', 'Hit':'hit',
                          'Expertise':'exp', 'Haste':'haste', 'Mastery':'mastery', 'Increased Critical Effect':'chaotic_metagem',
                          'PvP Resilience':'pvp_resil', 'PvP Power':'pvp_power'}
        #Loops over every item
        for p in self.raw_data['data'][u'items']:
            try:
                #ilvl is included in the gear array for some unknown reason, lets ignore it
                if p != 'averageItemLevelEquipped' and p != 'averageItemLevel':
                    tmpItem = get_item_cached(self.region, self.raw_data['data'][u'items'][p][u'id'])
                    self.verbosePrint('\n' + p + ': ' + self.raw_data['data'][u'items'][p][u'name'])
                    params = self.raw_data['data'][u'items'][p][u'tooltipParams']
                    #grab the reforge if it exists
                    if u'reforge' in self.raw_data['data'][u'items'][p][u'tooltipParams']:
                        reforgeID = self.raw_data['data'][u'items'][p][u'tooltipParams'][u'reforge']
                    #if we have data on the reforge
                    if reforgeID in CharacterData.reforgeMap.keys():
                        reforge = CharacterData.reforgeMap[reforgeID]
                    #for each stat on the gear
                    for key in tmpItem[u'data'][u'bonusStats']:
                        if key[u'stat'] in CharacterData.statMap and CharacterData.statMap[key[u'stat']] == reforge[0]:
                            #if a reforge was found
                            tmpVal = math.ceil(key[u'amount'] * .6)
                            lst[ CharacterData.statMap[key[u'stat']] ] += tmpVal
                            lst[ reforge[1] ] += key[u'amount'] - tmpVal
                            self.verbosePrint('Reforge found: +' + str(tmpVal) + ' ' + reforge[0] + ', +' + str(key[u'amount'] - tmpVal) + ' ' + reforge[1])
                        else:
                            #otherwise, no reforge
                            lst[ CharacterData.statMap[key[u'stat']] ] += key[u'amount']
                            self.verbosePrint('+' + str(key[u'amount']) + ' ' + CharacterData.statMap[key[u'stat']])
                    #prevents cached reforges from affecting subsequent items
                    reforge = ('none', 'none')
                    #add stats from gems, check if socket colors are matched along the way
                    if u'socketInfo' in tmpItem['data']:
                        socketInfo = tmpItem['data'][u'socketInfo']
                        socketBonusActivated = True  # we'll find out if this is not true as we process each gem
                    else:
                        socketInfo = None
                        socketBonusActivated = False
                    gemCount = 0
                    for gemNumber in range(3):
                        gemId = 'gem' + str(gemNumber)
                        if gemId in params.keys():
                            gemCount += 1
                            tmpGem = get_item_cached(self.region, params[gemId])
                            if not socketInfo == None:
                                sockets = socketInfo[u'sockets']
                                if gemNumber < len(sockets):
                                    if not sockets[gemNumber][u'type'] in gemColorToSocketColors[tmpGem['data'][u'gemInfo'][u'type'][u'type']]:
                                        socketBonusActivated = False
                                        self.verbosePrint(tmpGem['data'][u'name'] + ' does not match socket of color ' + sockets[gemNumber][u'type'] + ', socket bonus not activated!')
                            for entry in tmpGem['data'][u'gemInfo'][u'bonus'][u'name'].split(' and '):
                                tmpLst = entry.split(' ')
                                if not '%' in tmpLst[0]:
                                    tmpVal = int(tmpLst[0][1:])
                                    tmpStat = verboseStatMap[' '.join(tmpLst[1:])]
                                    lst[tmpStat] += tmpVal
                                    self.verbosePrint(tmpGem['data'][u'name'] + ': +' + str(tmpVal) + ' ' + tmpStat)
                                else:
                                    self.chaotic_metagem = True
                                    self.verbosePrint(tmpGem['data'][u'name'] + ' is a meta gem')
                    #add stats from socket bonuses
                    if socketBonusActivated == True and gemCount >= len(socketInfo[u'sockets']):
                        for entry in socketInfo[u'socketBonus'].split(' and '): #similar to gem treatment... is there ever a socket bonus that gives multiple stats?
                            tmpLst = entry.split(' ')
                            tmpVal = int(tmpLst[0][1:])
                            tmpStat = verboseStatMap[ ' '.join(tmpLst[1:]) ]
                            lst[ tmpStat ] += tmpVal
                            self.verbosePrint('Socket bonus +' + str(tmpVal) + ' ' + tmpStat)
                    #add stats from enchants
                    if u'enchant' in params.keys():
                        if not type( CharacterData.enchants[ params[u'enchant'] ] ) == type(''):
                            for key in CharacterData.enchants[ params[u'enchant'] ]:
                                lst[ key['stat'] ] += key['value']
                                self.verbosePrint('Enchant +' + str(key['value']) + ' ' + key['stat'])
                        else:
                            self.verbosePrint(CharacterData.enchants[params[u'enchant']])
                    else:
                        self.verbosePrint('Unenchanted')
            except Exception as inst:
                #it's okay, we can keep going, just so long as we pretend to handle the exception
                print "\n"
                print "Error at slot: ", p
                print "Error type:    ", type(inst)
                raise
        if self.verbose:
            pp.pprint(lst)
        return lst
        #return [lst['str'], lst['agi'], lst['int'], lst['spirit'], lst['stam'], lst['ap'], lst['crit'], lst['hit'], lst['exp'], lst['haste'], lst['mastery']]
    
    def has_chaotic_metagem(self):
        return self.chaotic_metagem
        
    def get_current_spec_data(self):
        specs_data = self.raw_data['data'][u'talents']
        if u'selected' in specs_data[0]:
            current_spec_data = specs_data[0]
        else:
            current_spec_data = specs_data[1]

        return current_spec_data

    def get_talents(self):
        spec_data = self.get_current_spec_data()
        talents = [""] * 6
        for t in spec_data[u'talents']:
            talents[t[u'tier']] = str(t[u'column'] + 1)
        return "".join(talents)

    def get_glyphs(self):
        glyphs = []
        spec_data = self.get_current_spec_data()
        glyphs_data = spec_data[u'glyphs']
        for g in (glyphs_data[u'major'] + glyphs_data[u'minor']):
            glyph_name = g[u'name']
            if glyph_name in CharacterData.glyphs:
                glyphs.append(CharacterData.glyphs[glyph_name])
        return glyphs

    def verbosePrint(self, str):
        if self.verbose:
            print str
