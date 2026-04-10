# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C)  2016-2019 Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Additions to Anki's card reviewer
"""

from aqt import gui_hooks
from aqt.reviewer import Reviewer

olc_hotkey_reveal = "g"

def onHintRevealHotkey(reviewer):
    if reviewer.state != "answer":
        return
    reviewer.web.eval("""
        var btn = document.getElementById("btn-reveal");
        if (btn) { btn.click(); };
    """)


def onReviewerShortcuts(shortcuts, reviewer):
    """Add our shortcut to the reviewer's shortcut list"""
    shortcuts.append(
        (olc_hotkey_reveal, lambda: onHintRevealHotkey(reviewer)))


def initializeReviewer():
    gui_hooks.reviewer_did_init.append(
        lambda reviewer: None  # placeholder for any init we need
    )
    # In modern Anki, we use the state_shortcuts_will_change hook
    # or simply append to reviewer shortcuts via the available hook
    try:
        gui_hooks.reviewer_will_init_shortcuts.append(onReviewerShortcuts)
    except AttributeError:
        # Fallback: monkey-patch _shortcutKeys for older 2.1.x
        original = Reviewer._shortcutKeys
        def patched(self):
            keys = original(self)
            keys.append(
                (olc_hotkey_reveal, lambda r=self: onHintRevealHotkey(r)))
            return keys
        Reviewer._shortcutKeys = patched
