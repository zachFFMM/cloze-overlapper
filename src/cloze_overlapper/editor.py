# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C)  2016-2019 Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Additions to Anki's note editor
"""

import os
import re

from aqt.qt import QShortcut, QKeySequence, Qt
from aqt import mw, gui_hooks
from aqt.editor import Editor
from aqt.addcards import AddCards
from aqt.utils import tooltip, showInfo
import sys

from .libaddon.platform import PATH_ADDON

from .overlapper import ClozeOverlapper
from .gui.options_note import OlcOptionsNote
from .template import checkModel
from .config import config
from .consts import OLC_MAX
from .utils import showTT


# Hotkey definitions

olc_hotkey_generate = "Alt+Shift+C"
olc_hotkey_options = "Alt+Shift+O"
olc_hotkey_cremove = "Alt+Shift+U"
olc_hotkey_olist = "Ctrl+Alt+Shift+."
olc_hotkey_ulist = "Ctrl+Alt+Shift+,"
olc_hotkey_mcloze = "Ctrl+Shift+K"
olc_hotkey_mclozealt = "Ctrl+Alt+Shift+K"

# Javascript

js_cloze_multi = """
var increment = %s;
var highest = %d;
function clozeChildren(container) {
    children = container.childNodes
    for (i = 0; i < children.length; i++) {
        var child = children[i]
        var contents = child.innerHTML
        var textOnly = false;
        if (typeof contents === 'undefined'){
            // handle text nodes
            var contents = child.textContent
            textOnly = true;}
        if (increment){idx = highest+i} else {idx = highest}
        contents = '%s' + idx + '::' + contents + '%s'
        if (textOnly){
            child.textContent = contents}
        else {
            child.innerHTML = contents}}
}
if (typeof window.getSelection != "undefined") {
    // get selected HTML
    var sel = window.getSelection();
    if (sel.rangeCount) {
        var container = document.createElement("div");
        for (var i = 0, len = sel.rangeCount; i < len; ++i) {
            container.appendChild(sel.getRangeAt(i).cloneContents());}}
    // wrap each topmost child with cloze tags; TODO: Recursion
    clozeChildren(container);
    // workaround for duplicate list items:
    var clozed = container.innerHTML.replace(/^(<li>)/, "")
    document.execCommand('insertHTML', false, clozed);
    if (typeof saveField !== 'undefined') saveField('key');
}
"""

js_cloze_remove = """
function getSelectionHtml() {
    // Based on an SO answer by Tim Down
    var html = "";
    if (typeof window.getSelection != "undefined") {
        var sel = window.getSelection();
        if (sel.rangeCount) {
            var container = document.createElement("div");
            for (var i = 0, len = sel.rangeCount; i < len; ++i) {
                container.appendChild(sel.getRangeAt(i).cloneContents());
            }
            html = container.innerHTML;
        }
    } else if (typeof document.selection != "undefined") {
        if (document.selection.type == "Text") {
            html = document.selection.createRange().htmlText;
        }
    }
    return html;
}
if (typeof window.getSelection != "undefined") {
    // get selected HTML
    var sel = getSelectionHtml();
    sel = sel.replace(/%s/mg, "$2");
    // workaround for duplicate list items:
    var sel = sel.replace(/^(<li>)/, "")
    document.execCommand('insertHTML', false, sel);
    if (typeof saveField !== 'undefined') saveField('key');
}
"""


# CSS to hide internal fields (Text1-20, Full, Settings) in the editor
HIDE_FIELDS_CSS = """
.olc-hidden-field {
    display: none !important;
}
"""

HIDE_FIELDS_JS = """
(function() {
    var fieldNames = %s;
    var labels = document.querySelectorAll('.field-container .label-name, .fname');
    labels.forEach(function(label) {
        var name = label.textContent.trim();
        if (fieldNames.indexOf(name) !== -1) {
            var container = label.closest('.field-container') || label.closest('.editingArea')?.parentElement;
            if (container) container.style.display = 'none';
        }
    });
})();
"""


def getHiddenFieldNames():
    """Get list of field names that should be hidden in the editor"""
    flds = config["synced"]["flds"]
    names = [flds["st"], flds["fl"]]  # Settings, Full
    for i in range(1, OLC_MAX + 1):
        names.append(flds["tx"] + str(i))  # Text1-Text20
    return names


def onEditorDidLoad(editor):
    """Hide internal fields when an OLC note is loaded"""
    if not editor.note:
        return
    if not checkModel(editor.note.note_type(), fields=False, notify=False):
        return
    import json
    names = getHiddenFieldNames()
    editor.web.eval(HIDE_FIELDS_JS % json.dumps(names))


def onEditorDidLoadDelayed(editor):
    """Delayed hide to ensure fields are rendered"""
    from aqt.qt import QTimer
    if not editor.note:
        return
    if not checkModel(editor.note.note_type(), fields=False, notify=False):
        return
    QTimer.singleShot(100, lambda: onEditorDidLoad(editor))


# EDITOR

# Button callback wrappers

def editorSaveThen(callback):
    def onSaved(editor, *args, **kwargs):
        if hasattr(editor, 'saveNow'):
            editor.saveNow(lambda: callback(editor, *args, **kwargs))
        else:
            # Modern Anki may not have saveNow; call directly
            callback(editor, *args, **kwargs)
    return onSaved


def JSformatFieldThen(editor, field_idx, commands, callback):
    cmd_str = "\n".join("""document.execCommand("{}");""".format(cmd)
                        for cmd in commands)

    js = """
if (typeof focusField !== 'undefined') focusField(%(field_idx)d);
%(cmd_str)s
if (typeof saveField !== 'undefined') saveField('key');
""" % {"field_idx": field_idx, "cmd_str": cmd_str}

    editor.web.evalWithCallback(js, lambda res: callback())


# Utility

def refreshEditor(editor):
    if hasattr(editor, 'loadNote'):
        editor.loadNote()
    focus = editor.currentField or 0
    editor.web.eval(
        "if (typeof focusField !== 'undefined') focusField({});".format(focus))

# Button callbacks

def onInsertCloze(self, _old):
    """Handles cloze-wraps when the add-on model is active"""
    if not checkModel(self.note.note_type(), fields=False, notify=False):
        return _old(self)
    highest = 0
    for name, val in self.note.items():
        m = re.findall(r"\{\{oc(\d+)::", val)
        if m:
            highest = max(highest, sorted([int(x) for x in m])[-1])
    if not self.mw.app.keyboardModifiers() & Qt.KeyboardModifier.AltModifier:
        highest += 1
    highest = max(1, highest)
    self.web.eval(
        "if (typeof wrap !== 'undefined') wrap('{{oc%d::', '}}');" % highest)


@editorSaveThen
def onInsertMultipleClozes(self):
    """Wraps each line in a separate cloze"""
    model = self.note.note_type()
    if not re.search('{{(.*:)*cloze:', model['tmpls'][0]['qfmt']):
        if self.addMode:
            tooltip("Warning, cloze deletions will not work until "
                    "you switch the type at the top to Cloze.")
        else:
            showInfo("To make a cloze deletion on an existing note, you need to change it "
                     "to a cloze type first, via Edit>Change Note Type.")
            return
    if checkModel(model, fields=False, notify=False):
        cloze_re = r"\{\{oc(\d+)::"
        wrap_pre, wrap_post = "{{oc", "}}"
    else:
        cloze_re = r"\{\{c(\d+)::"
        wrap_pre, wrap_post = "{{c", "}}"
    highest = 0
    for name, val in self.note.items():
        m = re.findall(cloze_re, val)
        if m:
            highest = max(highest, sorted([int(x) for x in m])[-1])
    increment = "false"
    if not self.mw.app.keyboardModifiers() & Qt.KeyboardModifier.AltModifier:
        highest += 1
        increment = "true"
    highest = max(1, highest)
    self.web.eval(js_cloze_multi % (
        increment, highest, wrap_pre, wrap_post))


@editorSaveThen
def onRemoveClozes(editor):
    """Remove all cloze markers from the current field"""
    if checkModel(editor.note.note_type(), fields=False, notify=False):
        cloze_re = re.compile(r"\{\{oc\d+::(.*?)(?:::[^}]*)?\}\}")
    else:
        cloze_re = re.compile(r"\{\{c\d+::(.*?)(?:::[^}]*)?\}\}")
    # Strip cloze markers from all fields
    changed = False
    for name, val in editor.note.items():
        cleaned = cloze_re.sub(r"\1", val)
        if cleaned != val:
            editor.note[name] = cleaned
            changed = True
    if changed:
        refreshEditor(editor)


@editorSaveThen
def onOlOptionsButton(self):
    """Invoke note-specific options dialog"""
    if not checkModel(self.note.note_type()):
        return False
    options = OlcOptionsNote(self.parentWindow)
    options.exec()


@editorSaveThen
def onOlClozeButton(editor, markup=None, parent=None):
    """Wrap selected text in {{ocN::}} markers, like standard cloze button"""
    if not checkModel(editor.note.note_type(), fields=False, notify=False):
        return False
    # Find highest existing oc number across all fields
    highest = 0
    for name, val in editor.note.items():
        m = re.findall(r"\{\{oc(\d+)::", val)
        if m:
            highest = max(highest, sorted([int(x) for x in m])[-1])
    highest += 1
    highest = max(1, highest)
    editor.web.eval(
        "if (typeof wrap !== 'undefined') wrap('{{oc%d::', '}}');" % highest)

# ADDCARDS

# Callbacks

def onAddCards(self, _old):
    """Automatically generate overlapping clozes before adding cards"""
    editor = self.editor
    note = editor.note

    if not note or not checkModel(note.note_type(), notify=False):
        return _old(self)

    overlapper = ClozeOverlapper(editor.note, silent=True)
    ret, total = overlapper.add()

    if ret is False:
        return

    refreshEditor(editor)

    oldret = _old(self)
    if total:
        showTT("Info", "Added %d overlapping cloze cards" % total, period=1000)

    return oldret


def onAddNote(addcards, note, _old):
    """Suspend full cloze card if option active"""
    note = _old(addcards, note)
    if not note or not checkModel(note.note_type(), fields=False, notify=False):
        return note
    sched_conf = config["synced"].get("sched", None)
    if not sched_conf or not sched_conf[2]:
        return note
    maxfields = ClozeOverlapper.getMaxFields(
        note.note_type(), config["synced"]["flds"]["tx"])
    last = note.cards()[-1]
    if last.ord == maxfields:  # is full cloze (ord starts at 0)
        mw.col.sched.suspend_cards([last.id])
    return note


# BUTTONS / HOTKEYS

icon_path = os.path.join(PATH_ADDON, "gui", "resources", "icons")
icon_generate = os.path.join(icon_path, "oc_generate.svg")
icon_options = os.path.join(icon_path, "oc_options.svg")
icon_remove = os.path.join(icon_path, "oc_remove.svg")

tooltip_generate = "Generate overlapping clozes ({})".format(
    olc_hotkey_generate)
tooltip_options = "Overlapping cloze options ({})".format(
    olc_hotkey_options)
tooltip_remove = "Remove all cloze markers in selected text ({})".format(
    olc_hotkey_cremove)


def _get_editor_widget(editor):
    """Get a suitable parent widget for shortcuts, compatible across Anki versions."""
    for attr in ("widget", "web", "parentWindow"):
        w = getattr(editor, attr, None)
        if w is not None:
            return w
    return None


def onSetupEditorButtons(buttons, editor):
    """Add buttons and hotkeys"""
    try:
        b = editor.addButton(icon_generate, "OlCloze", onOlClozeButton,
                             tooltip_generate, keys=olc_hotkey_generate)
        buttons.append(b)
    except Exception:
        pass

    try:
        b = editor.addButton(icon_options, "OlOptions", onOlOptionsButton,
                             tooltip_options, keys=olc_hotkey_options)
        buttons.append(b)
    except Exception:
        pass

    try:
        b = editor.addButton(icon_remove, "RemoveClozes", onRemoveClozes,
                             tooltip_remove, keys=olc_hotkey_cremove)
        buttons.append(b)
    except Exception:
        pass

    try:
        setupAdditionalHotkeys(editor)
    except Exception:
        pass

    return buttons

def setupAdditionalHotkeys(editor):
    parent = _get_editor_widget(editor)
    if parent is None:
        return

    add_ol_cut = QShortcut(QKeySequence(olc_hotkey_olist), parent)
    add_ol_cut.activated.connect(lambda o="ol": onOlClozeButton(editor, o))
    add_ul_cut = QShortcut(QKeySequence(olc_hotkey_ulist), parent)
    add_ul_cut.activated.connect(lambda o="ul": onOlClozeButton(editor, o))

    mult_cloze_cut1 = QShortcut(QKeySequence(olc_hotkey_mcloze), parent)
    mult_cloze_cut1.activated.connect(lambda: onInsertMultipleClozes(editor))
    mult_cloze_cut2 = QShortcut(QKeySequence(olc_hotkey_mclozealt), parent)
    mult_cloze_cut2.activated.connect(lambda: onInsertMultipleClozes(editor))


# MAIN

def _wrap_method(cls, method_name, wrapper, pos="around"):
    """Monkey-patch a method on a class, compatible with modern Anki."""
    original = getattr(cls, method_name)
    if pos == "around":
        def patched(self, *args, **kwargs):
            return wrapper(self, *args, _old=original, **kwargs)
        setattr(cls, method_name, patched)


def initializeEditor():
    # Editor widget - wrap onCloze for our custom cloze syntax
    if hasattr(Editor, "onCloze"):
        _wrap_method(Editor, "onCloze", onInsertCloze)
    Editor.onOlClozeButton = onOlClozeButton
    Editor.onOlOptionsButton = onOlOptionsButton
    Editor.onInsertMultipleClozes = onInsertMultipleClozes
    Editor.onRemoveClozes = onRemoveClozes

    gui_hooks.editor_did_init_buttons.append(onSetupEditorButtons)

    # Hide internal fields when editor loads a note
    gui_hooks.editor_did_load_note.append(onEditorDidLoadDelayed)

    # AddCard windows - wrap _addCards and addNote
    # Method names vary across Anki versions
    for method_name in ("_add_current_note", "_addCards"):
        if hasattr(AddCards, method_name):
            _wrap_method(AddCards, method_name, onAddCards)
            break
    if hasattr(AddCards, "addNote"):
        _wrap_method(AddCards, "addNote", onAddNote)
