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
        self.ed.web.eval("saveField('key');")
        setopts = parseNoteSettings(self.note[self.flds["st"]])
        settings, options = setopts
        before, prompt, after = settings
        if before is None:
            before = -1
        if after is None:
            after = -1
        self.f.sb_before.setValue(before)
        self.f.sb_after.setValue(after)
        self.f.sb_cloze.setValue(prompt)
        for idx, cb in enumerate((self.f.cb_ncf, self.f.cb_ncl,
                                  self.f.cb_incr, self.f.cb_gfc)):
            cb.setChecked(options[idx])

    def onAccept(self):
        before = self.f.sb_before.value()
        after = self.f.sb_after.value()
        prompt = self.f.sb_cloze.value()

        before = before if before != -1 else None
        after = after if after != -1 else None

        settings = [before, prompt, after]
        options = [i.isChecked() for i in (
            self.f.cb_ncf, self.f.cb_ncl,
            self.f.cb_incr, self.f.cb_gfc)]
        setopts = (settings, options)
        settings_fld = createNoteSettings(setopts)
        self.note[self.flds["st"]] = settings_fld

        self.ed.loadNote()

        if self.ed.currentField is not None:
            self.ed.web.eval("focusField(%d);" % self.ed.currentField)
        else:
            self.ed.web.eval("focusField(0);")

        self.ed.onOlClozeButton(parent=self.parent_window)

        self.close()

    def onReject(self):
        self.close()
