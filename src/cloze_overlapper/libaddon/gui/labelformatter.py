# -*- coding: utf-8 -*-

# Libaddon for Anki
# Updated for modern Anki (2.1.45+)

"""
Utilities to fill out predefined data in dialog text labels
"""

from aqt.qt import QLabel, QPushButton, QRegularExpression, Qt

from ..consts import ADDON

format_dict = {
    "ADDON_NAME": ADDON.NAME,
    "ADDON_VERSION": ADDON.VERSION,
}


def formatLabels(dialog, linkhandler=None):
    for widget in dialog.findChildren(
            (QLabel, QPushButton), QRegularExpression(".*"),
            Qt.FindChildOption.FindChildrenRecursively):
        if widget.objectName().startswith("fmt"):
            widget.setText(widget.text().format(**format_dict))
        if linkhandler and isinstance(widget, QLabel):
            widget.linkActivated.connect(linkhandler)
