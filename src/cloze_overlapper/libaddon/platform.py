# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2019  Aristotelis P. <https//glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Constants providing information on current system and Anki platform
"""

import sys
import os

from aqt import mw
from anki import version as anki_version

__all__ = ["ANKI20", "SYS_ENCODING", "MODULE_ADDON",
           "MODULE_LIBADDON", "DIRECTORY_ADDONS", "JSPY_BRIDGE",
           "PATH_ADDON", "PATH_USERFILES", "PLATFORM"]

PYTHON3 = True
ANKI20 = False
SYS_ENCODING = sys.getfilesystemencoding()

name_components = __name__.split(".")

MODULE_ADDON = name_components[0]
MODULE_LIBADDON = name_components[1]

DIRECTORY_ADDONS = mw.addonManager.addonsFolder()
JSPY_BRIDGE = "pycmd"

PATH_ADDON = os.path.join(DIRECTORY_ADDONS, MODULE_ADDON)
PATH_USERFILES = os.path.join(PATH_ADDON, "user_files")

if sys.platform == "darwin":
    PLATFORM = "mac"
elif sys.platform == "win32":
    PLATFORM = "win"
else:
    PLATFORM = "lin"

def checkAnkiVersion(lower, upper=None):
    """Check whether anki version is in specified range"""
    from ._vendor.packaging import version
    if upper is not None:
        ankiv_parsed = version.parse(anki_version)
        return (ankiv_parsed >= version.parse(lower) and
                ankiv_parsed < version.parse(upper))
    return version.parse(anki_version) >= version.parse(lower)
