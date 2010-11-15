import gettext
import os.path
import locale
import __builtin__

__builtin__._ = gettext.gettext

SUPPORTED_LANGUAGES = ['es_ES', 'es']       # Add here languages as we create .mo files
TRANSLATION_DOMAIN = 'SCE'                  # Domain: this needs to be the name of our .mo files
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")

def set_language(language):
    # This function will install gettext as the _() function and use the
    # language specified. It won't traslate anything if given a not supported
    # language. Note that the 'local' value only makes sense when not running from
    # the hosted online version.
    if language == 'local':
        # Setting up a list of locales in your machine, append those
        # that we have, and asign them to the _() function
        languages_list = []
        default_local_language, encoding = locale.getdefaultlocale()
        if (default_local_language):
            languages_list = [default_local_language]
        lang = os.environ.get('LANGUAGE', None)
        if (lang):
            languages_list += lang.split(":")
        languages_list += SUPPORTED_LANGUAGES
        gettext.translation(TRANSLATION_DOMAIN, LOCALE_DIR, languages=languages_list).install(unicode=True)

    elif language in SUPPORTED_LANGUAGES:
        gettext.translation(TRANSLATION_DOMAIN, LOCALE_DIR, languages=[language]).install(unicode=True)
