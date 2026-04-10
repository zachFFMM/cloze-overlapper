# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C) 2016-2019  Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Handles add-on configuration
"""

from aqt import mw
try:
    from anki.utils import strip_html
except ImportError:
    from anki.utils import stripHTML as strip_html

from .libaddon.anki.configmanager import ConfigManager

from .consts import *

# Context modes
MODE_NONE = 0       # all items hidden except current cloze
MODE_PREVIOUS = 1   # show previous items as context
MODE_ALL = 2        # show all items except current cloze


def parseNoteSettings(html):
    """Parse note settings field. Returns context_mode int (0/1/2)."""
    field = strip_html(html).strip()
    if not field:
        return config["synced"].get("context_mode", MODE_PREVIOUS)
    try:
        mode = int(field)
        if mode in (MODE_NONE, MODE_PREVIOUS, MODE_ALL):
            return mode
    except ValueError:
        pass
    # Legacy compat
    return config["synced"].get("context_mode", MODE_PREVIOUS)


def createNoteSettings(context_mode):
    """Create plain text settings string."""
    return str(context_mode)


config_defaults = {
    "synced": {
        "context_mode": MODE_PREVIOUS,
        "flds": OLC_FLDS,
        "sched": [True, True, False],
        "olmdls": [OLC_MODEL],
        "version": ADDON.VERSION
    }
}

config = ConfigManager(mw, config_dict=config_defaults,
                       conf_key="olcloze")
