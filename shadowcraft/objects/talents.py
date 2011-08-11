from shadowcraft.core import exceptions

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
        if name in self.allowed_talents:
            return 0
        object.__getattribute__(self, name)

    def set_talent(self, talent_name, talent_value):
        if talent_name not in self.allowed_talents:
            raise InvalidTalentException(_('Invalid talent name {talent_name}').format(talent_name=talent_name))
        max_talent_value, talent_tier = self.allowed_talents[talent_name]
        if talent_value < 0 or talent_value > max_talent_value:
            raise InvalidTalentException(_('Invalid value {talent_value} for talent {talent_name}').format(talent_value=talent_value, talent_name=talent_name))

        setattr(self, talent_name, int(talent_value))

    def __init__(self, talent_string = '', **kwargs):
        if not talent_string:
            for talent_name in kwargs:
                self.set_talent(talent_name, kwargs[talent_name])
        else:
            if len(talent_string) != len(self.allowed_talents):
                raise InvalidTalentException(_('Invalid talent string {talent_string}').format(talent_string=talent_string))
            self.populate_talents_from_list([int(c) for c in list(talent_string)])

    def talents_in_tree(self):
        points = 0
        for talent_name in self.allowed_talents:
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

class ClassTalents(object):
    # override in subclasses to return a list of three TalentTree classes
    # available to this class
    @classmethod
    def treeClasses(cls):
        NotImplemented

    def __init__(self, string1, string2, string3):
        self.trees = list()
        self.spec = None
        self.cachedAttrs = list()

        # Instantiate the three trees using the specified strings. While we're
        # at it, find the tree with the most talents to determine spec. Since
        # the specced tree always has more talent points than the other two,
        # this works.
        maxTalents = 0
        for (treeClass, string) in zip(self.treeClasses(), [string1, string2, string3]):
            tree = treeClass(string)
            if maxTalents < tree.talents_in_tree():
                maxTalents = tree.talents_in_tree()
                self.spec = treeClass
            self.trees.append(tree)

        # build up a dict of talents to trees for quicker access in __getattr__
        self.treeForTalent = dict()
        for tree in self.trees:
            for name in tree.allowed_talents:
                self.treeForTalent[name] = tree

    def is_specced(self, treeClass):
        return self.spec == treeClass

    def get_talent_tier(self, name):
        max_talent_value, talent_tier = self.treeForTalent[name].allowed_talents[name]
        return talent_tier

    def reset_cache(self):
        for name in self.cachedAttrs:
            delattr(self, name)
        del self.cachedAttrs[:]
            
    def __getattr__(self, name):
        # If someone tries to access a talent defined on one of the trees,
        # access it through that tree.
        if name in self.treeForTalent:
            # self.cachedAttrs.append(name)
            r = getattr(self.treeForTalent[name], name)            
            # setattr(self, name, r)
            return r
            
        object.__getattribute__(self, name)
