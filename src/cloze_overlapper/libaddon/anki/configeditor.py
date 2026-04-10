# -*- coding: utf-8 -*-

# Libaddon for Anki
# Updated for modern Anki (2.1.45+)

"""
Add-on configuration editor (legacy compat)
"""

import os
import json

import aqt
from aqt.qt import QDialog, QDialogButtonBox
from aqt.utils import tooltip

from ..consts import ADDON
from ..platform import PATH_ADDON

from ..gui.dialog_htmlview import HTMLViewer

class ConfigEditor(QDialog):

    def __init__(self, config_manager, parent):
        super(ConfigEditor, self).__init__(parent=parent)
        self.mgr = config_manager
        self.form = aqt.forms.editaddon.Ui_Dialog()
        self.form.setupUi(self)
        self.setWindowTitle("{} Configuration".format(ADDON.NAME))
        self.setupWidgets()
        self.updateText(self.mgr["local"])
        self.exec()

    def setupWidgets(self):
        button_box = self.form.buttonBox
        restore_btn = button_box.addButton(
            QDialogButtonBox.StandardButton.RestoreDefaults)
        help_btn = button_box.addButton(
            QDialogButtonBox.StandardButton.Help)
        help_btn.clicked.connect(self.onHelpRequested)
        restore_btn.clicked.connect(self.onRestoreDefaults)

    def updateText(self, conf):
        self.form.text.setPlainText(
            json.dumps(conf, ensure_ascii=False, sort_keys=True,
                       indent=4, separators=(',', ': ')))

    def onRestoreDefaults(self):
        default_conf = self.mgr.defaults["local"]
        self.updateText(default_conf)
        tooltip("Restored defaults", parent=self)

    def onHelpRequested(self):
        docs_path = os.path.join(PATH_ADDON, "config.md")
        if not os.path.exists(docs_path):
            return False
        with open(docs_path, "r") as f:
            try:
                from .._vendor import markdown2
                html = markdown2.markdown(f.read())
            except ImportError:
                html = "<pre>" + f.read() + "</pre>"
        dialog = HTMLViewer(html, title="{} Configuration Help".format(
            ADDON.NAME), parent=self)
        dialog.show()

    def accept(self):
        txt = self.form.text.toPlainText()
        try:
            new_conf = json.loads(txt)
        except ValueError as e:
            from aqt.utils import showInfo
            showInfo("Invalid configuration, restoring previous config: " +
                     str(e))
            return
        if not isinstance(new_conf, dict):
            from aqt.utils import showInfo
            showInfo("Invalid configuration, restoring previous config: "
                     "top level object must be a map")
            return

        self.mgr["local"] = new_conf
        self.mgr.save(storage_name="local")
        super(ConfigEditor, self).accept()
