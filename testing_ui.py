from calcs.rogue.Aldriana import AldrianasRogueDamageCalculator
from calcs.rogue.Aldriana import settings

from objects import buffs
from objects import race
from objects import stats
from objects import procs
from objects.rogue import rogue_talents
from objects.rogue import rogue_glyphs

from core import i18n

import wx
import string
import items

    
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
        
        grid_sizer = wx.GridSizer(cols = 5)
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
    def __init__(self, parent, calculator):
        wx.Panel.__init__(self, parent)
        self.calculator = calculator

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

class TestGUI(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title = "ShadowCraft")
        nb = wx.Notebook(self)
        
        self.gear_page = GearPage(nb, self)
        self.talents_page = TalentsPage(nb, self)
        self.buffs_page = BuffsPage(nb, self)
        self.settings_page = SettingsPage(nb, self)
        
        nb.AddPage(self.gear_page, "Gear")
        nb.AddPage(self.talents_page, "Talents")
        nb.AddPage(self.buffs_page, "Buffs")
        nb.AddPage(self.settings_page, "Settings")
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(nb, 0, wx.EXPAND)
        self.SetSizer(vbox)
        self.Fit()
       
    def calculate(self):
        my_stats = stats.Stats(*self.gear_page.get_stats())
        #talents = 
        #glyphs = 
        my_buffs = buffs.Buffs(*self.buffs_page.current_buffs)
    
if __name__ == "__main__":
    app = wx.App(False)
    gui = TestGUI();
    gui.Show()
    app.MainLoop()