# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C) 2016-2019  Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Global settings dialog
"""

from aqt.qt import QDialog, QDialogButtonBox, QAction
from aqt import mw

from ..libaddon.gui.about import get_about_string

from ..config import config
from ..consts import *

from .forms import settings_global


class OlcOptionsGlobal(QDialog):
    """Global options dialog"""

    def __init__(self, mw):
        super(OlcOptionsGlobal, self).__init__(parent=mw)
        self.f = settings_global.Ui_Dialog()
        self.f.setupUi(self)
        self.setupUI()
        self.fndict = list(zip((i for i in OLC_FIDS_PRIV if i != "tx"),
            [self.f.le_og, self.f.le_st, self.f.le_fl]))
        self.fsched = (self.f.cb_ns_new, self.f.cb_ns_rev, self.f.cb_sfc)
        self.fopts = (self.f.cb_ncf, self.f.cb_ncl,
                      self.f.cb_incr, self.f.cb_gfc)
        self.setupValues(config["synced"])

    def setupUI(self):
        self.f.buttonBox.accepted.connect(self.onAccept)
        self.f.buttonBox.rejected.connect(self.onReject)
        self.f.buttonBox.button(
            QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.onRestore)
        about_string = get_about_string()
        self.f.htmlAbout.setHtml(about_string)

    def setupValues(self, values):
        before, prompt, after = values["dflts"]
        before = before if before is not None else -1
        after = after if after is not None else -1
        self.f.sb_before.setValue(before)
        self.f.sb_after.setValue(after)
        self.f.sb_cloze.setValue(prompt)
        self.f.le_model.setText(",".join(values["olmdls"]))
        for idx, cb in enumerate(self.fsched):
            cb.setChecked(values["sched"][idx])
        for idx, cb in enumerate(self.fopts):
            cb.setChecked(values["dflto"][idx])
        for key, fnedit in self.fndict:
            fnedit.setText(values["flds"][key])

    def onAccept(self):
        reset_req = False
        try:
            reset_req = self.renameFields()
        except (KeyError, AttributeError, IndexError) as e:
            from aqt.utils import showInfo
            showInfo("Could not rename fields: %s" % str(e))
            return
        before = self.f.sb_before.value()
        after = self.f.sb_after.value()
        prompt = self.f.sb_cloze.value()
        before = before if before != -1 else None
        after = after if after != -1 else None
        config["synced"]['dflts'] = [before, prompt, after]
        config["synced"]['sched'] = [i.isChecked() for i in self.fsched]
        config["synced"]["dflto"] = [i.isChecked() for i in self.fopts]
        config["synced"]["olmdls"] = [n.strip() for n in self.f.le_model.text().split(",") if n.strip()]
        config.save(reset=reset_req)
        self.close()

    def onRestore(self):
        self.setupValues(config.defaults["synced"])
        for key, lnedit in self.fndict:
            lnedit.setModified(True)

    def onReject(self):
        self.close()

    def renameFields(self):
        """Check for modified names and rename fields accordingly"""
        modified = False
        model = mw.col.models.by_name(OLC_MODEL)
        if not model:
            return modified
        flds = model['flds']
        for key, fnedit in self.fndict:
            if not fnedit.isModified():
                continue
            name = fnedit.text()
            oldname = config["synced"]['flds'][key]
            if name is None or not name.strip() or name == oldname:
                continue
            field_names = mw.col.models.field_names(model)
            if oldname not in field_names:
                continue
            idx = field_names.index(oldname)
            fld = flds[idx]
            if fld:
                mw.col.models.rename_field(model, fld, name)
                config["synced"]['flds'][key] = name
                modified = True
        return modified


def invokeOptionsGlobal():
    dialog = OlcOptionsGlobal(mw)
    return dialog.exec()


def initializeOptions():
    config.setConfigAction(invokeOptionsGlobal)
    options_action = QAction("Cloze Over&lapper Options...", mw)
    options_action.triggered.connect(invokeOptionsGlobal)
    mw.form.menuTools.addAction(options_action)
