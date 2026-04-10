# -*- coding: utf-8 -*-

# Simplified settings dialog for Cloze Overlapper

from aqt.qt import (
    QDialog, QVBoxLayout,
    QLabel, QRadioButton, QButtonGroup,
    QDialogButtonBox, QSpacerItem, QSizePolicy
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setWindowTitle("Overlapping Cloze Settings")
        Dialog.resize(320, 180)

        layout = QVBoxLayout(Dialog)

        layout.addWidget(QLabel("<b>Context Mode</b>"))

        self.bg_mode = QButtonGroup(Dialog)

        self.rb_none = QRadioButton("Show none (all items hidden)")
        self.rb_none.setToolTip("Every card shows only the current cloze. All other items are hidden.")
        layout.addWidget(self.rb_none)
        self.bg_mode.addButton(self.rb_none, 0)

        self.rb_previous = QRadioButton("Show previous answers")
        self.rb_previous.setToolTip("Items before the current cloze are revealed as context.")
        layout.addWidget(self.rb_previous)
        self.bg_mode.addButton(self.rb_previous, 1)

        self.rb_all = QRadioButton("Show all except current")
        self.rb_all.setToolTip("All items except the current cloze are revealed.")
        layout.addWidget(self.rb_all)
        self.bg_mode.addButton(self.rb_all, 2)

        layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(self.buttonBox)
