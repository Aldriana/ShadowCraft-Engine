# All the imports here are either base python or shadowcraft files with the exception of wx,
# which can be downloaded from http://www.wxpython.org/download.php (I worked with windows 2.6/64)
from os import path
import sys
sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))

from shadowcraft.calcs.rogue.Aldriana import AldrianasRogueDamageCalculator
from shadowcraft.calcs.rogue.Aldriana import settings

from shadowcraft.core import exceptions
from shadowcraft.core import i18n

from shadowcraft.objects import buffs
from shadowcraft.objects import race
from shadowcraft.objects import stats
from shadowcraft.objects import procs
from shadowcraft.objects.rogue import rogue_talents
from shadowcraft.objects.rogue import rogue_glyphs

import ui_data
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
        "head": 0,
        "neck": 0,
        "shoulders": 0,
        "back": 0,
        "chest": 0,
        "wrists": 0,
        "hands": 0,
        "waist": 0,
        "legs": 0,
        "feet": 0,
        "ring1": 0,
        "ring2": 0,
        "trinket1": 0,
        "trinket2": 0,
        "mainhand": 0,
        "offhand": 0,
        "ranged": 0
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
    enchants = {}
    gems = {}
    reforges = {}

    def __init__(self, parent, calculator):
        wx.Panel.__init__(self, parent)
        self.calculator = calculator

        grid_sizer = wx.FlexGridSizer(cols = 6)
        for slot in self.gear_slots:
            self.create_ui_for_slot(grid_sizer, slot)
        self.SetSizer(grid_sizer)
        self.Fit()

    def create_ui_for_slot(self, sizer, slot):
        label = wx.StaticText(self, -1, label = string.capwords(slot))
        sizer.Add(label, flag = wx.ALIGN_RIGHT)
        item_cb = self.create_item_ui_for_slot(slot)
        sizer.Add(item_cb)
        if not slot in ('trinket1', 'trinket2', 'neck', 'waist', 'ranged'):
            ench_label = wx.StaticText(self, -1, label = "Enchant")
            sizer.Add(ench_label, flag = wx.ALIGN_RIGHT)
            enchant_cb = self.create_enchant_ui_for_slot(self, slot)
            if not enchant_cb == None:
                sizer.Add(enchant_cb)
            else:
                sizer.Add((10, 10))
        else:
            sizer.Add((2, 2))
            sizer.Add((2, 2))

        gem_selecter = self.create_gem_ui_for_slot(slot)
        #In order to get gems set for initial items, have to do update here
        self.update_item_for_slot(self.get_items_for_slot(slot)[0], slot)
        self.update_gems_for_slot(slot)
        sizer.Add(gem_selecter)
        
        reforging_panel = self.create_reforging_ui_for_slot(slot)
        sizer.Add(reforging_panel)

    def create_item_ui_for_slot(self, slot):
        cb = None
        cb = wx.ComboBox(self, -1, style = wx.CB_READONLY, name = slot)
        cb.SetItems(self.get_items_for_slot(slot))
        cb.SetSelection(0)
        cb.Bind(wx.EVT_COMBOBOX, lambda evt, slot=slot:self.on_item_selected(evt, slot))
        return cb

    def create_gem_ui_for_slot(self, slot):
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.gems[slot] = {}
        for color in ('meta', 'red', 'yellow', 'blue', 'prismatic'):
            panel = wx.Panel(self, -1)
            gem_sizer = wx.BoxSizer(wx.HORIZONTAL)
            panel.SetSizer(gem_sizer)
            color_block = wx.StaticText(panel, -1, label = "   ")
            gem_sizer.Add(color_block)
            if color == 'meta':
                color_block.SetBackgroundColour('WHITE')
            elif color == 'prismatic':
                color_block.SetBackgroundColour('GREY')
            else:
                color_block.SetBackgroundColour(color.upper())
            cb = wx.ComboBox(panel, -1, style = wx.CB_READONLY)
            cb.Bind(wx.EVT_COMBOBOX, self.on_gem_selected)
            cb.SetItems([''] + ui_data.gems.keys())
            cb.SetSelection(0)
            panel.Hide()

            gem_sizer.Add(cb, 0, wx.EXPAND)
            self.gems[slot][color] = cb
            vbox.Add(panel, 0, wx.EXPAND)
        return vbox

    def create_enchant_ui_for_slot(self, master, slot):
        cb = None
        enchants = [''] + self.get_enchants_for_slot(slot).keys()
        cb = wx.ComboBox(master, -1, style = wx.CB_READONLY)
        cb.SetItems(enchants)
        cb.Bind(wx.EVT_COMBOBOX, self.on_enchant_selected)
        self.enchants[slot] = cb
        return cb

    def create_reforging_ui_for_slot(self, slot):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        reforge_from = self.current_gear[slot].reforgable_from()
        reforge_to = self.current_gear[slot].reforgable_to()
        if len(reforge_from) > 0:
            cb_from = wx.ComboBox(self, -1, style = wx.CB_READONLY)
            cb_from.SetItems([''] + reforge_from)
            sizer.Add(cb_from, 2, wx.EXPAND)
            cb_to = wx.ComboBox(self, -1, style = wx.CB_READONLY)
            cb_to.SetItems([''] + reforge_to)
            sizer.Add(cb_to, 2, wx.EXPAND)
            btn_reforge = wx.Button(self, -1, label = "Reforge")
            btn_reforge.Bind(wx.EVT_BUTTON, lambda evt, slot=slot: self.on_reforge(evt, slot))
            sizer.Add(btn_reforge, 2, wx.EXPAND)
            btn_restore = wx.Button(self, -1, label = "Restore")
            btn_restore.Bind(wx.EVT_BUTTON, lambda evt, slot=slot: self.on_restore(evt, slot))
            btn_restore.Hide()
            sizer.Add(btn_restore, 2, wx.EXPAND)
            self.reforges[slot] = {'from': cb_from, 'to': cb_to, 'reforge': btn_reforge, 'restore': btn_restore}
        return sizer

    def populate_combobox_for_slot(self, combobox, slot):
        options = self.get_items_for_slot(slot)
        combobox.SetItems(options)
        combobox.SetStringSelection(options[0])

    def get_items_for_slot(self, slot):
        item_names = []
        items_dict = getattr(ui_data, slot)
        item_names = items_dict.keys()
        return item_names

    def get_gems(self):
        return ui_data.gems.keys()

    def get_enchants_for_slot(self, slot):
        enchants = []
        if slot in ('mainhand', 'offhand'):
            enchants = ui_data.enchants['melee_weapons']
        elif slot in ('ring1', 'ring2'):
            enchants = ui_data.enchants['rings']
        else:
            enchants = ui_data.enchants[slot]
        return enchants

    def update_gems_for_slot(self, slot):
        for color in self.gems[slot].keys():
            self.gems[slot][color].SetSelection(0)
            self.gems[slot][color].GetParent().Hide()
        item = self.current_gear[slot]
        for color in item.sockets:
            self.gems[slot][color].GetParent().Show()
        self.Layout()

    def update_item_for_slot(self, item_name, slot):
        items_dict = getattr(ui_data, slot)
        item = None
        if slot in ('mainhand', 'offhand', 'ranged'):
            item = ui_data.Weapon(item_name, **items_dict[item_name])
        else:
            item = ui_data.Item(item_name, **items_dict[item_name])
        self.current_gear[slot] = item

    #Event handler for selecting a combo box entry
    def on_item_selected(self, e, slot):
        item_name = e.GetString()
        self.update_item_for_slot(item_name, slot)
        self.update_gems_for_slot(slot)
        self.calculator.calculate()
        #Clear the (no longer true) reforge settings
        self.reset_reforging_ui_for_slot(slot)

    def on_reforge(self, e, slot):
        reforge_from = self.reforges[slot]['from'].GetValue()
        reforge_to = self.reforges[slot]['to'].GetValue()
        if len(reforge_from) > 0 and len(reforge_to) > 0:
            self.current_gear[slot].reforge(reforge_from, reforge_to)
            self.reforges[slot]['reforge'].Hide()
            self.reforges[slot]['restore'].Show()
            self.Layout()
            self.calculator.calculate()

    def on_restore(self, e, slot):
        #Restoring the item to its dictionary definition
        print self.current_gear[slot].name
        self.update_item_for_slot(self.current_gear[slot].name, slot)
        self.reset_reforging_ui_for_slot(slot)
        self.calculator.calculate()

    def reset_reforging_ui_for_slot(self, slot):
        reforge_from = self.current_gear[slot].reforgable_from()
        reforge_to = self.current_gear[slot].reforgable_to()        
        if len(reforge_from) > 0:
            self.reforges[slot]['from'].SetItems([''] + reforge_from)
            self.reforges[slot]['from'].SetSelection(0)
            self.reforges[slot]['to'].SetItems([''] + reforge_to)
            self.reforges[slot]['to'].SetSelection(0)
            self.reforges[slot]['restore'].Hide()
            self.reforges[slot]['reforge'].Show()
            self.Layout()

    def on_gem_selected(self, e):
        self.calculator.calculate()

    def on_enchant_selected(self, e):
        self.calculator.calculate()

    def get_stats(self):
        current_stats = {'str': 0, 'agi': 0, 'ap': 0, 'crit': 0, 'hit': 0, 'exp': 0, 'haste': 0, 'mastery': 0, 'procs': [], 'gear_buffs': []}
        current_stats['procs'] = []
        current_stats['gear_buffs'] = ['leather_specialization'] #Assuming this rather than give equipment an armor type
        enchant_slots = self.enchants.keys()

        tier11_count = 0
        tier12_count = 0
        for slot in self.gear_slots:
            for stat in self.stats:
                current_stats[stat] += getattr(self.current_gear[slot], stat)
            gear_buff = self.current_gear[slot].gear_buff
            if 'tier_11' == gear_buff:
                tier11_count += 1
            elif 'tier_12' == gear_buff:
                tier12_count += 1
            elif len(gear_buff) > 0:
                current_stats['gear_buffs'].append(gear_buff)
            if len(self.current_gear[slot].proc) > 0:
                current_stats['procs'].append(self.current_gear[slot].proc)
            get_bonus = True
            for slot_color in self.current_gear[slot].sockets:
                gem_name = self.gems[slot][slot_color].GetValue()
                if len(gem_name) > 0:
                    gem = ui_data.gems[gem_name]
                    for stat in gem[1]:
                        if stat == 'proc':
                            current_stats['procs'] += gem[1][stat]
                        elif stat == 'gear_buff':
                            current_stats['gear_buffs'] += gem[1][stat]
                        else:
                            current_stats[stat] += gem[1][stat]
                    if not slot_color in gem[0] and slot_color != 'prismatic':
                        get_bonus = False
            if get_bonus and len(self.current_gear[slot].bonus_stat) > 0:
                current_stats[self.current_gear[slot].bonus_stat] += self.current_gear[slot].bonus_value
            if slot in enchant_slots and slot not in ('mainhand', 'offhand'):
                enchant_name = self.enchants[slot].GetValue()
                if len(enchant_name) > 0:
                    enchant_data = ui_data.enchants[slot][enchant_name]
                    for stat in enchant_data.keys():
                        current_stats[stat] += enchant_data[stat]
        if tier11_count >= 2:
            current_stats['gear_buffs'].append('rogue_t11_2pc')
            if tier11_count >= 4:
                current_stats['procs'].append('rogue_t11_4pc')
        if tier12_count >= 2:
            current_stats['gear_buffs'].append('rogue_t12_2pc')
            if tier12_count >= 4:
                current_stats['gear_buffs'].append('rogue_t12_4pc')
                
        mh = self.current_gear['mainhand']
        enchant = None
        if len(self.enchants['mainhand'].GetValue()) > 0:
            enchant = ui_data.enchants['melee_weapons'][self.enchants['mainhand'].GetValue()]
        mainhand = stats.Weapon(mh.damage, mh.speed, mh.type, enchant)
        current_stats['mh'] = mainhand

        oh = self.current_gear['offhand']
        enchant = None
        if len(self.enchants['offhand'].GetValue()) > 0:
            enchant = ui_data.enchants['melee_weapons'][self.enchants['offhand'].GetValue()]
        offhand = stats.Weapon(oh.damage, oh.speed, oh.type,  enchant)
        current_stats['oh'] = offhand

        rngd = self.current_gear['ranged']
        ranged = stats.Weapon(rngd.damage, rngd.speed, rngd.type)
        current_stats['ranged'] = ranged

        current_stats['procs'] = procs.ProcsList(*set(current_stats['procs']))

        current_stats['gear_buffs'] = stats.GearBuffs(*set(current_stats['gear_buffs']))

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
            #Funky ui stuff to get reasonable columns
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
            if ui_data.default_talents.has_key(talent):
                combo.SetSelection(ui_data.default_talents[talent])
            self.talents[talent] = combo
            spec_box.Add(combo)

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
        cb.SetItems([''] + options)
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
        vbox.Add(results_area, 2, wx.EXPAND | wx.BOTTOM)

        self.SetSizer(vbox)
        self.Fit()
        self.initializing = False
        self.calculate()

    def no_edit_text_box(self):
        panel = wx.Panel(self, -1)
        tb = wx.TextCtrl(self, -1, style = wx.TE_READONLY)
        tb.SetBackgroundColour(panel.GetBackgroundColour())
        return tb

    def create_multiline_with_label(self, label, key):
        vbox =  wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, -1, label = label))
        multi = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE | wx.TE_READONLY)
        vbox.Add(multi, 2, wx.EXPAND | wx.ALL)
        setattr(self, key, multi)
        return vbox
    
    def create_results_area(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        dps_box = wx.FlexGridSizer(cols = 2)
        dps_box.Add(wx.StaticText(self, -1, style = wx.ALIGN_RIGHT, label = "DPS: "))
        self.dps = self.no_edit_text_box()
        dps_box.Add(self.dps, 2, wx.BOTTOM)
        hbox.Add(dps_box, 2, wx.BOTTOM | wx.EXPAND)

        sizer = wx.FlexGridSizer(cols = 2)
        for stat in GearPage.stats:
            sizer.Add(wx.StaticText(self, -1, label = stat))
            stat_box = wx.TextCtrl(self, -1, style = wx.TE_READONLY)
            setattr(self, stat, stat_box)
            sizer.Add(stat_box)
        hbox.Add(sizer, 2, wx.EXPAND)
        
        hbox.Add(self.create_multiline_with_label("EP Values", 'ep_box'), 2, wx.EXPAND |  wx.ALL)
        #TODO: add talents comparions here
        hbox.Add(self.create_multiline_with_label("DPS Breakdown", 'dps_breakdown'), 2, wx.EXPAND |  wx.ALL)

        return hbox

    def calculate(self):
        if not self.initializing:
            gear_stats = self.gear_page.get_stats()
            my_stats = stats.Stats(**gear_stats)
            my_talents = rogue_talents.RogueTalents(*self.talents_page.get_talents())
            my_glyphs = rogue_glyphs.RogueGlyphs(*self.talents_page.get_glyphs())
            my_buffs = buffs.Buffs(*self.buffs_page.current_buffs)
            my_race = race.Race(self.settings_page.get_race())
            test_settings = settings.Settings(self.settings_page.get_cycle(), response_time = self.settings_page.get_response_time())

            self.error_area.SetLabel("")
            try:
                calculator = AldrianasRogueDamageCalculator(my_stats, my_talents, my_glyphs, my_buffs, my_race, test_settings)
                dps = calculator.get_dps()
                ep_values = calculator.get_ep()
                dps_breakdown = calculator.get_dps_breakdown()

            except exceptions.InvalidInputException as e:
                self.error_area.SetLabel(str(e))
            
            self.dps.SetValue(str(dps))
            self.ep_box.SetValue(self.pretty_print(ep_values))
            self.dps_breakdown.SetValue(self.pretty_print(dps_breakdown))
            for stat in GearPage.stats:
                tc = getattr(self, stat)
                tc.SetValue(str(gear_stats[stat]))
                
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
