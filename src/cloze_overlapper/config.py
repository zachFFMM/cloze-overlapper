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


def parseNoteSettings(html):
    """Return note settings. Fall back to defaults if necessary."""
    options, settings, opts, sets = None, None, None, None
    dflt_set, dflt_opt = config["synced"]["dflts"], config["synced"]["dflto"]
    if not html:
        return (dflt_set, dflt_opt)
    field = strip_html(html)

    lines = field.replace(" ", "").split("|")
    if not lines:
        return (dflt_set, dflt_opt)
    settings = lines[0].split(",")
    if len(lines) > 1:
        options = lines[1].split(",")

    if not options and not settings:
        return (dflt_set, dflt_opt)

    if not settings:
        sets = dflt_set
    else:
        sets = []
        for idx, item in enumerate(settings[:3]):
            try:
                sets.append(int(item))
            except ValueError:
                sets.append(None)
        length = len(sets)
        if length == 3 and isinstance(sets[1], int):
            pass
        elif length == 2 and isinstance(sets[0], int):
            sets = [sets[1], sets[0], sets[1]]
        elif length == 1 and isinstance(sets[0], int):
            sets = [dflt_set[0], sets[0], dflt_set[2]]
        else:
            sets = dflt_set

    if not options:
        opts = dflt_opt
    else:
        opts = []
        for i in range(4):
            try:
                if options[i] == "y":
                    opts.append(True)
                else:
                    opts.append(False)
            except IndexError:
                opts.append(dflt_opt[i])

    return (sets, opts)


def createNoteSettings(setopts):
    """Create plain text settings string"""
    set_str = ",".join(str(i) if i is not None else "all" for i in setopts[0])
    opt_str = ",".join("y" if i else "n" for i in setopts[1])
    return set_str + " | " + opt_str


config_defaults = {
    "synced": {
        "dflts": [1, 1, 0],
        "dflto": [False, False, False, False],
        "flds": OLC_FLDS,
        "sched": [True, True, False],
        "olmdls": [OLC_MODEL],
        "version": ADDON.VERSION
    }
}

config = ConfigManager(mw, config_dict=config_defaults,
                       conf_key="olcloze")
