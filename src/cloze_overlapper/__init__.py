# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C) 2016-2019  Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Module-level entry point for the add-on into Anki 2.1+
"""

from ._version import __version__  # noqa: F401


def initializeAddon():
    """Initializes add-on after performing a few checks"""

    from .consts import ADDON
    from .libaddon.consts import setAddonProperties

    setAddonProperties(ADDON)

    from aqt import gui_hooks

    from .gui.options_global import initializeOptions
    from .gui import initializeQtResources
    from .template import initializeModels
    from .editor import initializeEditor
    from .sched import initializeScheduler
    from .reviewer import initializeReviewer

    def delayedInit():
        initializeModels()
        initializeScheduler()

    gui_hooks.profile_did_open.append(delayedInit)

    initializeQtResources()
    initializeOptions()
    initializeEditor()
    initializeReviewer()

initializeAddon()
