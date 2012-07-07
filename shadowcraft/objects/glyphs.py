from shadowcraft.objects import glyphs_data

class Glyphs(object):

    def __init__(self, game_class='rogue', *args):
        self.allowed_glyphs = glyphs_data.glyphs[game_class]
        for arg in args:
            if arg in self.allowed_glyphs:
                setattr(self, arg, True)

    def __getattr__(self, name):
        # Any glyph we haven't assigned a value to, we don't have.
        if name in self.allowed_glyphs:
            return False
        object.__getattribute__(self, name)
