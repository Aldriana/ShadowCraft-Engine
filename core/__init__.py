import gettext

class Setup:
    def init_shadowcraft(object):
        gettext.install('ShadowCraft-Engine', './locale', unicode=False)
        #self.presLan_es = gettext.translation("ShadowCraft-Engine", "./locale", languages=['es'])
