# -*- coding: utf-8 -*-

# Simplified global settings for Cloze Overlapper

from aqt.qt import (
    QDialog, QVBoxLayout, QGridLayout, QTabWidget, QWidget,
    QLabel, QCheckBox, QRadioButton, QButtonGroup, QLineEdit, QTextBrowser,
    QDialogButtonBox, QSizePolicy
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setWindowTitle("Cloze Overlapper Options")
        Dialog.resize(421, 400)
        Dialog.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,
                             QSizePolicy.Policy.MinimumExpanding)

        self.verticalLayout = QVBoxLayout(Dialog)
        self.tabWidget = QTabWidget(Dialog)

        # Tab 1: Cloze Generation
        self.tab = QWidget()
        tab1_layout = QVBoxLayout(self.tab)

        tab1_layout.addWidget(QLabel("<b>Default Context Mode</b>"))

        self.bg_mode = QButtonGroup(self.tab)

        self.rb_none = QRadioButton("Show none (all items hidden)")
        tab1_layout.addWidget(self.rb_none)
        self.bg_mode.addButton(self.rb_none, 0)

        self.rb_previous = QRadioButton("Show previous answers")
        tab1_layout.addWidget(self.rb_previous)
        self.bg_mode.addButton(self.rb_previous, 1)

        self.rb_all = QRadioButton("Show all except current")
        tab1_layout.addWidget(self.rb_all)
        self.bg_mode.addButton(self.rb_all, 2)

        tab1_layout.addStretch()
        self.tabWidget.addTab(self.tab, "Cloze Generation")

        # Tab 2: General
        self.tab_2 = QWidget()
        tab2_layout = QVBoxLayout(self.tab_2)

        grid3 = QGridLayout()
        grid3.addWidget(QLabel("<b>Scheduling</b>"), 0, 0)

        self.cb_ns_new = QCheckBox("Override sibling-spacing for new overlapping clozes")
        grid3.addWidget(self.cb_ns_new, 1, 0)

        self.cb_ns_rev = QCheckBox("Override sibling-spacing for overlapping cloze reviews")
        grid3.addWidget(self.cb_ns_rev, 2, 0)

        self.cb_sfc = QCheckBox("Automatically suspend full cloze cards initially")
        grid3.addWidget(self.cb_sfc, 3, 0)

        tab2_layout.addLayout(grid3)

        grid4 = QGridLayout()
        grid4.addWidget(QLabel("<b>Field Names</b>"), 0, 0, 1, 3)

        grid4.addWidget(QLabel("Original"), 1, 0, 1, 2)
        self.le_og = QLineEdit()
        grid4.addWidget(self.le_og, 1, 2)

        grid4.addWidget(QLabel("Settings"), 2, 0, 1, 2)
        self.le_st = QLineEdit()
        grid4.addWidget(self.le_st, 2, 2)

        grid4.addWidget(QLabel("Full"), 3, 0, 1, 2)
        self.le_fl = QLineEdit()
        grid4.addWidget(self.le_fl, 3, 2)

        grid4.addWidget(QLabel("<b>Overlapping Cloze Note Types</b>"), 4, 0, 1, 3)
        grid4.addWidget(QLabel("Names"), 5, 0, 1, 2)
        self.le_model = QLineEdit()
        grid4.addWidget(self.le_model, 5, 2)

        tab2_layout.addLayout(grid4)
        tab2_layout.addStretch()
        self.tabWidget.addTab(self.tab_2, "General")

        # Tab 3: About
        self.tab_3 = QWidget()
        tab3_layout = QVBoxLayout(self.tab_3)
        tab3_layout.setContentsMargins(2, 2, 2, 2)
        self.htmlAbout = QTextBrowser()
        self.htmlAbout.setOpenExternalLinks(True)
        tab3_layout.addWidget(self.htmlAbout)
        self.tabWidget.addTab(self.tab_3, "About")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        self.verticalLayout.addWidget(self.buttonBox)

        self.tabWidget.setCurrentIndex(0)
