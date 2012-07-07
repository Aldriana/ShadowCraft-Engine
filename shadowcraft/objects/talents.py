from shadowcraft.core import exceptions
from shadowcraft.objects import talents_data

class InvalidTalentException(exceptions.InvalidInputException):
    pass


class Talents(object):

    def __init__(self, talent_string, game_class='rogue', level='90'):
        self.old_talents = talents_data.old_talents  # Making sure nothing breaks for a while.
        self.class_talents = talents_data.talents[game_class]
        self.level = level
        self.allowed_talents = [talent for tier in self.class_talents for talent in tier]
        self.allowed_talents_for_level = self.get_allowed_talents_for_level()
        self.initialize_talents(talent_string)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        # If someone tries to access a talent not initialized (the talent
        # string was shorter than 6) we return False
        if name in self.allowed_talents:
            return False
        # TODO: get rid of all old talent calls in the modeler.
        elif name in self.old_talents:
            return 0
        object.__getattribute__(self, name)

    def get_allowed_talents_for_level(self):
        allowed_talents_for_level = []
        for i in xrange(self.get_top_tier()):
            for talent in self.class_talents[i]:
                allowed_talents_for_level.append(talent)
        return allowed_talents_for_level

    def is_allowed_talent(self, name, check_level=False):
        if check_level:
            return name in self.allowed_talents_for_level
        else:
            return name in self.allowed_talents

    def get_top_tier(self):
        levels = (15, 30, 45, 60, 75, 90)
        top_tier = 0
        for i in levels:
            if self.level >= i:
                top_tier += 1
        return top_tier

    def initialize_talents(self, talent_string):
        assert len(talent_string) <= 6
        j = 0
        for i in talent_string:
            assert int(i) in range(4)
            if int(i) == 0:
                pass
            else:
                setattr(self, self.class_talents[j][int(i) - 1], True)
            j += 1

    def reset_talents(self):
        for talent in self.allowed_talents:
            setattr(self, talent, False)

    def get_tier_for_talent(self, name):
        if name not in self.allowed_talents:
            return None
        tier = 0
        for i in xrange(6):
            if name in self.class_talents[i]:
                return i

    def set_talent(self, name):
        # Clears talents in the tier and sets the new one
        if name not in self.allowed_talents:
            return False
        for talent in self.class_talents[self.get_tier_for_talent(name)]:
            setattr(self, talent, False)
        setattr(self, name, True)
