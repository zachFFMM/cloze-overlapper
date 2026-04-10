# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C)  2016-2019 Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Modifications to Anki's scheduling

Note: In modern Anki with the V3 scheduler, sibling burying is controlled
via deck options and can be configured per-deck. The old approach of
monkey-patching _burySiblings no longer works reliably.

This module now provides a simplified approach:
- For V3 scheduler: Users should configure burying via deck options
- The module still attempts to hook into the scheduler for backwards
  compatibility where possible
"""

from aqt import mw
from .template import checkModel


def myBurySiblings(self, card, _old):
    """Skip sibling burying for our note type if so configured"""
    if not checkModel(card.note_type(), fields=False, notify=False):
        return _old(self, card)
    sched_conf = mw.col.conf.get("olcloze", {}).get("sched", None)
    if not sched_conf:
        return _old(self, card)
    override_new, override_review, bury_full = sched_conf
    if override_new and override_review:
        return
    return _old(self, card)


def initializeScheduler():
    """Initialize scheduler modifications.

    In modern Anki (V3 scheduler), _burySiblings is no longer easily
    patchable. We attempt to patch it if the method exists, but
    users should configure sibling burying via deck options instead.
    """
    try:
        # Try to find the scheduler class and patch it
        sched = mw.col.sched
        sched_cls = type(sched)
        if hasattr(sched_cls, '_burySiblings'):
            original = sched_cls._burySiblings
            def patched(self, card):
                if not checkModel(card.note_type(), fields=False, notify=False):
                    return original(self, card)
                sched_conf = mw.col.conf.get("olcloze", {}).get("sched", None)
                if not sched_conf:
                    return original(self, card)
                override_new, override_review, bury_full = sched_conf
                if override_new and override_review:
                    return
                return original(self, card)
            sched_cls._burySiblings = patched
        else:
            pass  # V3 scheduler — burying is configured via deck options
    except Exception:
        pass  # scheduler patching not available — users can use deck options
