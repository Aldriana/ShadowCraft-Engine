# All the imports here are either base python or shadowcraft files with the exception of wx,
# which can be downloaded from http://www.wxpython.org/download.php (I worked with windows 2.6/64)

from calcs.rogue.Aldriana import AldrianasRogueDamageCalculator
from calcs.rogue.Aldriana import settings

from core import exceptions
from core import i18n

from objects import buffs
from objects import race
from objects import stats
from objects import procs
from objects.rogue import rogue_talents
from objects.rogue import rogue_glyphs

import items
import os
import string
import wx

    
class GearPage(wx.Panel):
    gear_slots =    [
        "head",
        "neck",
        "shoulders",
        "back",
        "chest",
        "wrists",
        "hands",
        "waist",
        "legs",
        "feet",
        "ring1",
        "ring2",
        "trinket1",
        "trinket2",
        "mainhand",
        "offhand",
        "ranged"
                    ]
    current_gear = {
        "head": {},
        "neck": {},
        "shoulders": {},
        "back": {},
        "chest": {},
        "wrists": {},
        "hands": {},
        "waist": {},
        "legs": {},
        "feet": {},
        "ring1": {},
        "ring2": {},
        "trinket1": {},
        "trinket2": {},
        "mainhand": {},
        "offhand": {},
        "ranged": {}
        }
    stats = [
        'str',
        'agi',
        'ap',
        'crit',
        'hit',
        'exp',
        'haste',
        'mastery',
    ]
    
    def __init__(self, parent, calculator):
        wx.Panel.__init__(self, parent)
        self.calculator = calculator
        
        grid_sizer = wx.FlexGridSizer(cols = 5)
        for slot in self.gear_slots:
            self.create_ui_for_slot(grid_sizer, slot)
        self.SetSizer(grid_sizer)
        self.Fit()

    def create_ui_for_slot(self, sizer, slot):
        label = wx.StaticText(self, -1, label = string.capwords(slot))
        sizer.Add(label, flag = wx.ALIGN_RIGHT)
        item_cb = self.create_item_ui_for_slot(self, slot)
        sizer.Add(item_cb)
        if not slot in ('trinket1', 'trinket2', 'neck', 'waist', 'ranged'):
            ench_label = wx.StaticText(self, -1, label = "Enchant")
            sizer.Add(ench_label, flag = wx.ALIGN_RIGHT)
            enchant_cb = self.create_enchant_ui_for_slot(self, slot)
            sizer.Add(enchant_cb)
        else:
            sizer.Add((2, 2))
            sizer.Add((2, 2))
        gem_selecter = self.create_gem_ui_for_slot(self, slot) #Need selected to actually set this ...
        sizer.Add(gem_selecter)

    def create_item_ui_for_slot(self, master, slot):
        cb = None
        slot_items = self.get_items_for_slot(slot)
        if len(slot_items) > 0:
            cb = wx.ComboBox(master, wx.ID_ANY, style = wx.CB_READONLY, name = slot)
            cb.SetItems(slot_items)
            cb.SetStringSelection(slot_items[0])
            items_dict = getattr(items, slot)
            self.current_gear[slot] = items_dict[slot_items[0]] 
            cb.Bind(wx.EVT_COMBOBOX, lambda evt, slot=slot:self.on_item_selected(evt, slot))
        return cb

    def create_gem_ui_for_slot(self, master, slot):
        vbox = wx.BoxSizer(wx.VERTICAL)
        return vbox

    def create_enchant_ui_for_slot(self, master, slot):
        cb = None
        enchants = self.get_enchants_for_slot(slot)
        if len(enchants) > 0:
            cb = wx.ComboBox(master, -1, style = wx.CB_READONLY, name = slot + "_enchant")
            cb.SetItems(enchants)
        return cb

    def populate_combobox_for_slot(self, combobox, slot):
        options = self.get_items_for_slot(slot)
        combobox.SetItems(options)
        combobox.SetStringSelection(options[0])
    
    def get_items_for_slot(self, slot):
        item_names = []
        items_dict = getattr(items, slot)
        item_names = items_dict.keys()
        return item_names
    def get_gems(self):
        return ["gem1", "gem2"]
    def get_enchants_for_slot(self, slot):
        return ["baz", "zif"]

    #Event handler for selecting a combo box entry
    def on_item_selected(self, e, slot):
        items_dict = getattr(items, slot)
        self.current_gear[slot] = items_dict[e.GetString()]
        self.calculator.calculate()

    def on_gem_selected(self, e):
        pass
    def on_enchant_selected(self, e):
        pass
    
    def get_stats(self):  
        current_stats = []
        for stat in self.stats:
            value = 0
            for slot in self.gear_slots:
                if self.current_gear[slot].has_key(stat):
                    value += self.current_gear[slot][stat]
            current_stats.append(value)
        
        #TODO: figure out weapon enchants here
        mh = self.current_gear['mainhand']
        mainhand = stats.Weapon(mh['damage'], mh['speed'], mh['type'])
        current_stats.append(mainhand)
        
        oh = self.current_gear['offhand']
        offhand = stats.Weapon(oh['damage'], oh['speed'], oh['type'])
        current_stats.append(offhand)
        
        rngd = self.current_gear['ranged']
        ranged = stats.Weapon(rngd['damage'], rngd['speed'], rngd['type'])
        current_stats.append(ranged)
     
        proc_names = []
        for slot in self.gear_slots:
            if self.current_gear[slot].has_key('procs'):
                proc_names += self.current_gear[slot]['procs']
        my_procs = procs.ProcsList(*proc_names)
        current_stats.append(my_procs)
     
        gear_buff_names = []
        for slot in self.gear_slots:
            if self.current_gear[slot].has_key('gear_buffs'):
                gear_buff_names += self.current_gear[slot]['gear_buffs']
        my_gear_buffs = stats.GearBuffs(*gear_buff_names)
        current_stats.append(my_gear_buffs)
        
        return current_stats
    
class TalentsPage(wx.Panel):
    assassination_talents = [
        'deadly_momentum',
        'coup_de_grace',
        'lethality',
        'ruthlessness',
        'quickening',
        'puncturing_wounds',
        'blackjack',
        'deadly_brew',
        'cold_blood',
        'vile_poisons',
        'deadened_nerves',
        'seal_fate',
        'murderous_intent',
        'overkill',
        'master_poisoner',
        'improved_expose_armor',
        'cut_to_the_chase',
        'venomous_wounds',
        'vendetta'
        ]
    
    combat_talents = [
        'improved_recuperate',
        'improved_sinister_strike',
        'precision',
        'improved_slice_and_dice',
        'improved_sprint',
        'aggression',
        'improved_kick',
        'lightning_reflexes',
        'revealing_strike',
        'reinforced_leather',
        'improved_gouge',
        'combat_potency',
        'blade_twisting',
        'throwing_specialization',
        'adrenaline_rush',
        'savage_combat',
        'bandits_guile',
        'restless_blades',
        'killing_spree'
        ]
    subtlety_talents = [
        'nightstalker',
        'improved_ambush',
        'relentless_strikes',
        'elusiveness',
        'waylay',
        'opportunity',
        'initiative',
        'energetic_recovery',
        'find_weakness',
        'hemorrhage',
        'honor_among_thieves',
        'premeditation',
        'enveloping_shadows',
        'cheat_death',
        'preparation',
        'sanguinary_vein',
        'slaughter_from_the_shadows',
        'serrated_blades',
        'shadow_dance'
        ]
    
    prime_glyphs = [
        'adrenaline_rush',
        'backstab',
        'eviscerate',
        'hemorrhage',
        'killing_spree',
        'mutilate',
        'revealing_strike',
        'rupture',
        'shadow_dance',
        'sinister_strike',
        'slice_and_dice',
        'vendetta',
        ]
    major_glyphs = [
        'ambush',
        'blade_flurry',
        'blind',
        'cloak_of_shadows',
        'crippling_poison',
        'deadly_throw',
        'evasion',
        'expose_armor',
        'fan_of_knives',
        'feint',
        'garrote',
        'gouge',
        'kick',
        'preparation',
        'sap',
        'sprint',
        'tricks_of_the_trade',
        'vanish',
        ]
    
    minor_glyphs = [
        'blurred_speed',
        'distract',
        'pick_lock',
        'pick_pocket',
        'poisons',
        'safe_fall'
        ]
    
    current_glyphs = []
    talents = {}
    MAX_TALENTS_PER_TIER = 4

    def __init__(self, parent, calculator):
        wx.Panel.__init__(self, parent)
        self.calculator = calculator
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)        
        hbox.Add(self.add_talents(), 0, wx.EXPAND)
        hbox.Add(self.add_glyphs())
        self.SetSizer(hbox)
        
    def add_talents(self):
        talents_box = wx.BoxSizer(wx.VERTICAL)
        talents_box.Add(wx.StaticText(self, -1, label = "Talents"))
        talents_box.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        talents_box.Add(wx.StaticText(self, -1, label = "Assassination"))
        talents_box.Add(self.add_talents_for_spec('assass'), 0, wx.EXPAND)
        talents_box.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        talents_box.Add(wx.StaticText(self, -1, label = "Combat"))
        talents_box.Add(self.add_talents_for_spec('combat'), 0, wx.EXPAND)
        talents_box.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        talents_box.Add(wx.StaticText(self, -1, label = "Subtlety"))
        talents_box.Add(self.add_talents_for_spec('subtlety'), 0, wx.EXPAND)
        
        return talents_box

    def add_talents_for_spec(self, spec):
        spec_box = wx.FlexGridSizer(cols = 2 * self.MAX_TALENTS_PER_TIER)
        talents = []
        talent_data = {}
        if spec == 'assass':
            talents = self.assassination_talents
            talent_data = rogue_talents.Assassination.allowed_talents
        elif spec == 'combat':
            talents = self.combat_talents
            talent_data = rogue_talents.Combat.allowed_talents
        elif spec == 'subtlety':
            talents = self.subtlety_talents
            talent_data = rogue_talents.Subtlety.allowed_talents

        current_tier = 1
        talents_this_tier = 0
        
        for talent in talents:
            if talent_data[talent][1] != current_tier:
                while(talents_this_tier < self.MAX_TALENTS_PER_TIER):
                    spec_box.Add((10, 10))
                    spec_box.Add((10, 10))
                    talents_this_tier += 1
                current_tier += 1
                talents_this_tier = 0
            talents_this_tier += 1
            spec_box.Add(wx.StaticText(self, -1, label = talent), flag = wx.ALIGN_RIGHT)
            combo = self.create_combo_with_max(talent_data[talent][0])
            self.talents[talent] = combo
            spec_box.Add(combo)
            setattr(self, talent, combo)
        return spec_box
    
    def create_combo_with_max(self, max_value):
        cb = wx.ComboBox(self, -1, style = wx.CB_READONLY)
        cb.Bind(wx.EVT_COMBOBOX, self.on_selection)
        for value in range(0, max_value + 1):
            cb.Append(str(value))
        cb.SetSelection(0)
        return cb

    def add_glyphs(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, -1, label = "Glyphs"))
        vbox.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        sizer = wx.FlexGridSizer(cols = 4)
        vbox.Add(sizer)
        
        sizer.Add(wx.StaticText(self, -1, label = "Prime: "))
        sizer.Add(self.add_glyph(self.prime_glyphs))
        sizer.Add(self.add_glyph(self.prime_glyphs))
        sizer.Add(self.add_glyph(self.prime_glyphs))
        
        sizer.Add(wx.StaticText(self, -1, label = "Major: "))
        sizer.Add(self.add_glyph(self.major_glyphs))
        sizer.Add(self.add_glyph(self.major_glyphs))
        sizer.Add(self.add_glyph(self.major_glyphs))
        
        sizer.Add(wx.StaticText(self, -1, label = "Minor: "))
        sizer.Add(self.add_glyph(self.minor_glyphs))
        sizer.Add(self.add_glyph(self.minor_glyphs))
        sizer.Add(self.add_glyph(self.minor_glyphs))
        
        return vbox

    def add_glyph(self, options):
        cb = wx.ComboBox(self, -1, style = wx.CB_READONLY)
        cb.Bind(wx.EVT_COMBOBOX, self.on_selection)
        cb.SetItems(options)
        self.current_glyphs.append(cb)
        return cb
    
    def get_talents(self):
        assassination_string = ''
        combat_string = ''
        subtlety_string = ''
        
        for talent in self.assassination_talents:
            assassination_string += self.talents[talent].GetValue()
        for talent in self.combat_talents:
            combat_string += self.talents[talent].GetValue()
        for talent in self.subtlety_talents:
            subtlety_string += self.talents[talent].GetValue()
            
        return (assassination_string, combat_string, subtlety_string)
        
    def get_glyphs(self):
        glyphs_list = []
        for glyph in self.current_glyphs:
            glyph_name = glyph.GetValue()
            if len(glyph_name) > 0 and glyph_name not in glyphs_list:
                glyphs_list.append(glyph_name)
        return glyphs_list

    def on_selection(self, e):
        self.calculator.calculate()

class BuffsPage(wx.Panel):
    current_buffs = []
    
    def __init__(self, parent, calculator):
        wx.Panel.__init__(self, parent)
        self.calculator = calculator

        self.create_buff_checkboxes()
        
    def create_buff_checkboxes(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        
        for buff in buffs.Buffs.allowed_buffs:
            chk_box = wx.CheckBox(self, -1, buff, name = buff)
            chk_box.SetValue(True)
            vbox.Add(chk_box, 2, wx.BOTTOM)
            chk_box.Bind(wx.EVT_CHECKBOX, lambda event, name = buff: self.on_check_changed(event, name))

        self.current_buffs = list(buffs.Buffs.allowed_buffs)

    def on_check_changed(self, e, name):
        chk_box = e.GetEventObject()
        if (name in self.current_buffs) and (not chk_box.GetValue()):
            self.current_buffs.remove(name)
        elif not (name in self.current_buffs) and (chk_box.GetValue()):
            self.current_buffs.append(name)
        self.calculator.calculate()
        
        
    def get_buff_string(self):
        return ", ".join(self.current_buffs)

class SettingsPage(wx.Panel):
    def __init__(self, parent, calculator):
        wx.Panel.__init__(self, parent)
        self.calculator = calculator
        sizer = wx.FlexGridSizer(cols = 2)
        
        sizer.Add(wx.StaticText(self, -1, label = "Race: "))
        sizer.Add(self.create_race_selector())
        sizer.Add(wx.StaticText(self, -1, label = "Cycle: "))
        sizer.Add(self.create_cycle_selector())
        sizer.Add(wx.StaticText(self, -1, label = "Response Time: "))
        sizer.Add(self.create_response_time_entry())
        
        self.SetSizer(sizer)
        
    def create_race_selector(self):
        races = race.Race.racial_stat_offset.keys()
        cb = self.create_combobox_with_options(races)
        self.race = cb
        return cb
    
    def create_combobox_with_options(self, options):
        cb = wx.ComboBox(self, -1, style = wx.CB_READONLY)
        cb.Bind(wx.EVT_COMBOBOX, self.on_selection)
        cb.SetItems(options)        
        cb.SetSelection(0)
        return cb
    
    def create_cycle_selector(self):
        cycles = ["Assassination", "Combat", "Subtlety"]
        cb = self.create_combobox_with_options(cycles)
        self.cycle = cb
        test_cycle = settings.AssassinationCycle()
        test_settings = settings.Settings(test_cycle, response_time=1)
        return cb

    def create_response_time_entry(self):
        tc = wx.TextCtrl(self, -1, value = '1')
        self.response_time = tc
        return tc
    
    def get_race(self):
        return self.race.GetValue()

    def get_cycle(self):
        cycle = ''
        cur_cycle = self.cycle.GetValue()
        if  cur_cycle == "Assassination":
            cycle = settings.AssassinationCycle()
        elif cur_cycle == "Combat":
            cycle = settings.CombatCycle()
        elif cur_cycle == "Subtlety":
            cycle = settings.SubtletyCycle()
        return cycle

    def get_response_time(self):
        response_time = 1
        if len(self.response_time.GetValue()) > 0:
            reponse_time = float(self.response_time.GetValue())
        return response_time

    def on_selection(self, e):
        self.calculator.calculate()

class TestGUI(wx.Frame):
    ep_stats = [
        'white_hit',
        'spell_hit',
        'yellow_hit',
        'str',
        'agi',
        'haste',
        'crit',
        'mastery',
        'dodge_exp',
        'parry_exp'
        ]
        
    def __init__(self):
        wx.Frame.__init__(self, None, title = "ShadowCraft")
        self.initializing = True
        vbox = wx.BoxSizer(wx.VERTICAL)
        nb = wx.Notebook(self)
        
        self.gear_page = GearPage(nb, self)
        self.talents_page = TalentsPage(nb, self)
        self.buffs_page = BuffsPage(nb, self)
        self.settings_page = SettingsPage(nb, self)
        
        nb.AddPage(self.gear_page, "Gear")
        nb.AddPage(self.talents_page, "Talents")
        nb.AddPage(self.buffs_page, "Buffs")
        nb.AddPage(self.settings_page, "Settings")
        vbox.Add(nb, 0, wx.EXPAND)
        
        self.error_area = wx.StaticText(self, -1)
        self.error_area.SetForegroundColour("Red")
        error_font = self.error_area.GetFont()
        error_font.SetPointSize(16)
        self.error_area.SetFont(error_font)
        vbox.Add(self.error_area)
              
        results_area = self.create_results_area()
        vbox.Add(results_area, 0, wx.EXPAND)
        
        self.SetSizer(vbox)
        self.Fit()
        self.initializing = False
       
    def no_edit_text_box(self):
        panel = wx.Panel(self, -1)
        tb = wx.TextCtrl(self, -1, style = wx.TE_READONLY)
        tb.SetBackgroundColour(panel.GetBackgroundColour())
        return tb

    def create_results_area(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        dps_box = wx.FlexGridSizer(cols = 2)
        dps_box.Add(wx.StaticText(self, -1, style = wx.ALIGN_RIGHT, label = "DPS: "))
        self.dps = self.no_edit_text_box()
        self.dps.SetValue("Over 9000")
        dps_box.Add(self.dps, 2, wx.BOTTOM)
        hbox.Add(dps_box, 2, wx.BOTTOM)
        
        ep_box = wx.FlexGridSizer(cols = 2)
        for ep_stat in self.ep_stats:
            ep_box.Add(wx.StaticText(self, -1, style = wx.ALIGN_RIGHT, label = "%(ep)s: " % {'ep': ep_stat}))
            ep_value = self.no_edit_text_box()
            ep_box.Add(ep_value, 2, wx.BOTTOM)
            setattr(self, ep_stat, ep_value)
        hbox.Add(ep_box, 2, wx.BOTTOM)
        
        #TODO: add talents comparions here
        
        breakdown_box = wx.BoxSizer(wx.VERTICAL)
        breakdown_box.Add(wx.StaticText(self, -1, label = "DPS Breakdown"))
        dps_breakdown = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE | wx.TE_READONLY)
        breakdown_box.Add(dps_breakdown, 0, wx.EXPAND)
        self.dps_breakdown = dps_breakdown
        hbox.Add(breakdown_box, 1, wx.EXPAND)
        
        return hbox
        
    def calculate(self):
        if not self.initializing:
            my_stats = stats.Stats(*self.gear_page.get_stats())
            my_talents = rogue_talents.RogueTalents(*self.talents_page.get_talents())
            my_glyphs = rogue_glyphs.RogueGlyphs(*self.talents_page.get_glyphs())
            my_buffs = buffs.Buffs(*self.buffs_page.current_buffs)
            my_race = race.Race(self.settings_page.get_race())
            test_settings = settings.Settings(self.settings_page.get_cycle(), self.settings_page.get_response_time())
            
            self.error_area.SetLabel("")
            try:
                calculator = AldrianasRogueDamageCalculator(my_stats, my_talents, my_glyphs, my_buffs, my_race, test_settings)
                self.dps.SetValue(str(calculator.get_dps()))
                ep_values = calculator.get_ep()
                dps_breakdown = calculator.get_dps_breakdown()
                self.dps_breakdown.SetValue(self.pretty_print(dps_breakdown))
                
                for ep_stat in self.ep_stats:
                    ep_text = getattr(self, ep_stat)
                    ep_text.SetValue(str(ep_values[ep_stat]))
                

            except exceptions.InvalidInputException as e:
                self.error_area.SetLabel(str(e))
    
    def pretty_print(self, my_dict):
        ret_str = ''
        max_len = max(len(entry[0]) for entry in my_dict.items())
        dict_values = my_dict.items()
        dict_values.sort(key=lambda entry: entry[1], reverse=True)
        for value in dict_values:
            ret_str += value[0] + ':' + ' ' * (max_len - len(value[0])) + str(value[1]) + os.linesep
    
        return ret_str
    
if __name__ == "__main__":
    app = wx.App(False)
    gui = TestGUI();
    gui.Show()
    app.MainLoop()