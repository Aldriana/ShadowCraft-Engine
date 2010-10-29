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
        # The asserts in this function are sort of a placeholder.  Once we
        # figure out how we're going to communicate errors between the front
        # end the back end, these should probably raise real exceptions with
        # useful information in them instead, but for now this is fine.

        assert talent_name in self.allowed_talents.keys()
        assert talent_value == int(talent_value)
        assert talent_value >= 0
        assert talent_value <= self.allowed_talents[talent_name]

        setattr(self, talent_name, int(talent_value))

    def __init__(self, talent_string = '', **kwargs):
        if not talent_string:
            for talent_name in kwargs.keys():
                self.set_talent(talent_name, kwargs[talent_name])
        else:
            # Another lazy sanity-check assert.  Should be replaced at some point.
            assert len(talent_string) == len(self.allowed_talents)
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
