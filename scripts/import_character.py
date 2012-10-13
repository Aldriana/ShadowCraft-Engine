# -*- coding: utf-8 -*-
from os import path
import sys
import pprint
import shelve

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
             11 : 'draenie',
             22 : 'worgen',
             24 : 'pandaren'}

    enchants = {4441 : 'windsong',
                4443 : 'elemental_force',
                4444 : 'dancing_steel'}

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


    def __init__(self, region, realm, name):
        self.region = region
        self.realm = realm
        self.name = name
        self.raw_data = None

    def do_import(self):
        self.raw_data = wowapi.get_character(self.region , self.realm, self.name, ['talents', 'items', 'stats'])

    def get_race(self):
        return CharacterData.races[self.raw_data[u'data'][u'race']]

    def get_weapon(self, weapon_data, item_data):
        weapon_info = weapon_data['data'][u'weaponInfo']
        damage_info = weapon_info[u'damage']
        damage = (damage_info[u'max'] + damage_info[u'min']) / 2
        speed = weapon_info[u'weaponSpeed']
        # FIXME: need better weapon type recognition here
        if speed <= 1.8:
            type = 'dagger'
        else:
            type = 'axe'
        enchant = CharacterData.enchants[item_data[u'tooltipParams'][u'enchant']]
        return [damage, speed, type, enchant]

    def get_mh(self):
        item_data = self.raw_data['data'][u'items'][u'mainHand']
        weapon_data = get_item_cached(self.region, item_data[u'id'])
#        weapon_data = get_item_cached(self.region, 85924)
        ret = self.get_weapon(weapon_data, item_data)
        return ret

    def get_oh(self):
        item_data = self.raw_data['data'][u'items'][u'offHand']
        weapon_data = get_item_cached(self.region, item_data[u'id'])
        ret = self.get_weapon(weapon_data, item_data)
        return ret

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
        ret = [str, agi, ap - 2 * agi, crit, hit, exp, haste, mast]
#        ret = [str, agi + 956, 250, crit, hit, exp, haste, mast]
#        pp.pprint(ret)
        return ret
    
    def get_gear_stats(self):
        #           
        lst = {'agi': 0, 'str':0, 'stam':0, 'crit':0, 'hit':0, 'exp':0, 'haste':0, 'mastery':0, 'ap':0, 'pvp_power':0, 'pvp_resil':0}
        statMap = {3:'agi', 7:'stam', 31:'hit', 32:'crit', 36:'haste', 37:'exp', 49:'mastery', 35:'pvp_resil', 57:'pvp_power'}
        #print "getting gear stats"
        for p in self.raw_data['data'][u'items']:
            try:
                #print p
                #print self.raw_data['data'][u'items'][p]
                tmpItem = get_item_cached(self.region, self.raw_data['data'][u'items'][p][u'id'])
                #print tmpItem[u'data'][u'bonusStats']
                for key in tmpItem[u'data'][u'bonusStats']:
                    if key[u'stat'] == 3:
                        #print "agi"
                        lst['agi'] += key[u'amount']
                    if key[u'stat'] == 7:
                        #print "stam"
                        lst['stam'] += key[u'amount']
                    if key[u'stat'] == 31:
                        #print "hit"
                        lst['hit'] += key[u'amount']
                    if key[u'stat'] == 32:
                        #print "crit"
                        lst['crit'] += key[u'amount']
                    if key[u'stat'] == 36:
                        #print "haste"
                        lst['haste'] += key[u'amount']
                    if key[u'stat'] == 37:
                        #print "exp"
                        lst['exp'] += key[u'amount']
                    if key[u'stat'] == 49:
                        #print "mastery"
                        lst['mastery'] += key[u'amount']
                    if key[u'stat'] == 35:
                        #print "pvp_power"
                        lst['pvp_power'] += key[u'amount']
                    if key[u'stat'] == 57:
                        #print "pvp_resil"
                        lst['pvp_resil'] += key[u'amount']
                    #print key
            except:
                #it's okay, we can keep going
                p
        return [lst['str'], lst['agi'], lst['ap'], lst['crit'], lst['hit'], lst['exp'], lst['haste'], lst['mastery']]
        #return self.raw_data['data'][u'items']

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
