'''
Created on Oct 24, 2012

@author: Nicolas Rebagliati (nicolas.rebagliati@aenima-x.com.ar)
'''
# -*- coding: utf-8 -*-

import os.path
import black_hole.settings
import gettext

TRANSLATION_DOMAIN = "BlackHole"
DEFAULT_LANGUAGE = 'en-us'
AVAILABLE_LANGUAGES = ['es','es-AR','en-us']
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")
if black_hole.settings.LANGUAGE_CODE not in AVAILABLE_LANGUAGES:
    LANGUAGE = DEFAULT_LANGUAGE
else:
    LANGUAGE = black_hole.settings.LANGUAGE_CODE
LANGUAGES = [LANGUAGE]
lang = gettext.translation(TRANSLATION_DOMAIN, LOCALE_DIR, LANGUAGES)
lang.install()
