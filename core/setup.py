import gettext

def init_shadowcraft():
    init_i18n()

def init_i18n():
    gettext.install('ShadowCraft-Engine', './locale', unicode=False)
    #self.presLan_es = gettext.translation("ShadowCraft-Engine", "./locale", languages=['es'])
