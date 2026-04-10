# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C) 2016-2019  Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Note settings dialog
"""

from aqt.qt import QDialog

from ..config import config, parseNoteSettings, createNoteSettings
from ..config import MODE_NONE, MODE_PREVIOUS, MODE_ALL

from .forms import settings_note

class OlcOptionsNote(QDialog):
    """Note-specific options dialog"""

    def __init__(self, parent):
        super(OlcOptionsNote, self).__init__(parent=parent)
        self.f = settings_note.Ui_Dialog()
        self.f.setupUi(self)
        self.f.buttonBox.accepted.connect(self.onAccept)
        self.f.buttonBox.rejected.connect(self.onReject)
        self.parent_window = parent
        self.ed = parent.editor
        self.note = self.ed.note
        self.flds = config["synced"]["flds"]
        self.setupValues()

    def setupValues(self):
        mode = parseNoteSettings(self.note[self.flds["st"]])
        if mode == MODE_NONE:
            self.f.rb_none.setChecked(True)
        elif mode == MODE_ALL:
            self.f.rb_all.setChecked(True)
        else:
            self.f.rb_previous.setChecked(True)

    def onAccept(self):
        mode = self.f.bg_mode.checkedId()
        self.note[self.flds["st"]] = createNoteSettings(mode)

        if hasattr(self.ed, 'loadNote'):
            self.ed.loadNote()

        self.close()

    def onReject(self):
        self.close()
