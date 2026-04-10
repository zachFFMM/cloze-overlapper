# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings_note.ui'
# Hand-translated for modern Anki (Qt6/Qt5 compat via aqt.qt)

from aqt.qt import (
    QDialog, QVBoxLayout, QGridLayout,
    QLabel, QSpinBox, QCheckBox,
    QDialogButtonBox, QSpacerItem, QSizePolicy, Qt
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setWindowTitle("Overlapping Cloze Note Settings")
        Dialog.resize(390, 217)

        self.verticalLayout_2 = QVBoxLayout(Dialog)
        self.verticalLayout = QVBoxLayout()

        # Context Cues and Prompts
        grid1 = QGridLayout()
        grid1.addWidget(QLabel("<b>Context Cues and Prompts</b>"), 0, 0, 1, 3)

        lbl_before = QLabel("Context Before")
        lbl_before.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid1.addWidget(lbl_before, 1, 0)
        lbl_cloze = QLabel("Cloze Prompts")
        lbl_cloze.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid1.addWidget(lbl_cloze, 1, 1)
        lbl_after = QLabel("Context After")
        lbl_after.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid1.addWidget(lbl_after, 1, 2)

        self.sb_before = QSpinBox()
        self.sb_before.setMinimum(-1)
        self.sb_before.setSpecialValueText("all")
        self.sb_before.setToolTip("Number of context cues before the prompt.<br>"
                                  "Set to -1/'all' to show all previous items as context")
        grid1.addWidget(self.sb_before, 2, 0)

        self.sb_cloze = QSpinBox()
        self.sb_cloze.setMinimum(1)
        self.sb_cloze.setToolTip("Number of items to prompt for per card")
        grid1.addWidget(self.sb_cloze, 2, 1)

        self.sb_after = QSpinBox()
        self.sb_after.setMinimum(-1)
        self.sb_after.setSpecialValueText("all")
        self.sb_after.setToolTip("Number of context cues after the prompt.<br>"
                                 "Set to -1/'all' to show all following items as context")
        grid1.addWidget(self.sb_after, 2, 2)

        self.verticalLayout.addLayout(grid1)

        # Other Cloze Generation Options
        grid2 = QGridLayout()
        grid2.addWidget(QLabel("<b>Other Cloze Generation Options</b>"), 0, 0, 1, 2)

        self.cb_ncf = QCheckBox("No cues for first item")
        self.cb_ncf.setToolTip("Don't provide any context cues for first cloze item")
        grid2.addWidget(self.cb_ncf, 1, 0)

        self.cb_incr = QCheckBox("Gradual build-up/-down")
        self.cb_incr.setToolTip("For notes that have multiple clozes revealed per card,<br>"
                                "gradually build up to full reveal count at the start,<br>"
                                "and vice-versa in the end")
        grid2.addWidget(self.cb_incr, 1, 1)

        self.cb_ncl = QCheckBox("No cues for last item")
        self.cb_ncl.setToolTip("Don't provide any context cues for last cloze item")
        grid2.addWidget(self.cb_ncl, 2, 0)

        self.cb_gfc = QCheckBox("Don't generate full cloze")
        self.cb_gfc.setToolTip("Disable cards that prompt you for all items at once")
        grid2.addWidget(self.cb_gfc, 2, 1)

        self.verticalLayout.addLayout(grid2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        # Spacer
        self.verticalLayout_2.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Button box
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.verticalLayout_2.addWidget(self.buttonBox)
