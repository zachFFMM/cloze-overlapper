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

from ..config import config, MODE_NONE, MODE_PREVIOUS, MODE_ALL
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
        self.setupValues(config["synced"])

    def setupUI(self):
        self.f.buttonBox.accepted.connect(self.onAccept)
        self.f.buttonBox.rejected.connect(self.onReject)
        self.f.buttonBox.button(
            QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.onRestore)
        about_string = get_about_string()
        self.f.htmlAbout.setHtml(about_string)

    def setupValues(self, values):
        mode = values.get("context_mode", MODE_PREVIOUS)
        if mode == MODE_NONE:
            self.f.rb_none.setChecked(True)
        elif mode == MODE_ALL:
            self.f.rb_all.setChecked(True)
        else:
            self.f.rb_previous.setChecked(True)

        self.f.le_model.setText(",".join(values["olmdls"]))
        for idx, cb in enumerate(self.fsched):
            cb.setChecked(values["sched"][idx])
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
        config["synced"]["context_mode"] = self.f.bg_mode.checkedId()
        config["synced"]['sched'] = [i.isChecked() for i in self.fsched]
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
