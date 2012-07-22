from shadowcraft.core import exceptions

class Util(object):
# This should have its own GameClass(object) architecture at some point.

    GAME_CLASS_NUMBER = {
        1:"warrior", 2:"paladin", 3:"hunter", 4:"rogue", 5:"priest",
        6:"death_knight", 7:"shaman", 8:"mage", 9:"warlock", 10:"monk", 11:"druid"
    } # monk? (Pathal: #10 according to wowhead and armory api)

    AGI_CRIT_INTERCEPT_VALUES = [
        0.000000000000000,    0.000000000000000,    0.006519999820739,   -0.015320000238717,   -0.002950000111014,
        0.031764999032021,    0.000000000000000,    0.029219999909401,    0.034540001302958,    0.026219999417663,
        0.000000000000000,    0.074754998087883,
    ]

    def get_class_number(self, game_class):
        for i in self.GAME_CLASS_NUMBER.keys():
            if self.GAME_CLASS_NUMBER[i] == game_class:
                return i
        raise exceptions.InvalidInputException(_('{game_class} is not a supported game class').format(game_class=game_class))

    def get_agi_intercept(self, game_class):
        return self.AGI_CRIT_INTERCEPT_VALUES[self.get_class_number(game_class)]
