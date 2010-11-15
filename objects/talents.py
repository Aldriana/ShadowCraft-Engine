from core import exceptions

class InvalidTalentException(exceptions.InvalidInputException):
    pass


class TalentTree(object):
    # Base class for talent trees.  Any general property of that any talent 
    # tree will need to have should be defined here.  Note that constructing
    # one of these directly is almost completely useless; always subclass and
    # define allowed_talents as appropriate for your tree before using.

    # Allowed_talents is a dictionary of talent_name: max_value entries.
    allowed_talents = {}

    def __getattr__(self, name):
        # If someone tries to access a talent that is defined for the tree but
        # has not had a value assigned to it yet (i.e., the initialization did
        # not put any points into it), we return 0 for the value of the talent.
        if name in self.allowed_talents.keys():
            return 0
        object.__getattribute__(self, name)

    def set_talent(self, talent_name, talent_value):
        if talent_name not in self.allowed_talents.keys():
            raise InvalidTalentException(_('Invalid talent name {talent_name}').format(talent_name=talent_name))
        if talent_value < 0 or talent_value > self.allowed_talents[talent_name]:
            raise InvalidTalentException(_('Invalid value {talent_value} for talent {talent_name}').format(talent_value=talent_value, talent_name=talent_name))

        setattr(self, talent_name, int(talent_value))

    def __init__(self, talent_string = '', **kwargs):
        if not talent_string:
            for talent_name in kwargs.keys():
                self.set_talent(talent_name, kwargs[talent_name])
        else:
            if len(talent_string) != len(self.allowed_talents):
                raise InvalidTalentException(_('Invalid talent string {talent_string}').format(talent_string=talent_string))
            self.populate_talents_from_list([int(c) for c in list(talent_string)])

    def talents_in_tree(self):
        points = 0
        for talent_name in self.allowed_talents.keys():
            points += getattr(self, talent_name, 0)
        return points

    def populate_talents_from_list(self, values_list):
        # Replace this function with something that actually works when
        # subclassing in order to allow the constructor to accept a compacted
        # string input - i.e, passing in '0333230113022110321' instead of a
        # full dictionary of input values.

        # Again, this should probably fail more elegantly with an actual error
        # message, but again, I'm being lazy.
        assert False
