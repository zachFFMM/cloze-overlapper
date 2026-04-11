# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C)  2016-2019 Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Manages note type and templates
"""

from anki.consts import MODEL_CLOZE

from aqt import mw

from .config import config
from .utils import showTT, warnUser
from .consts import *

card_front = """\
{{#Title}}<div class="title">{{Title}}</div>{{/Title}}
<div class="text">
    <div id="clozed">
        {{cloze:Text1}}
        {{cloze:Text2}}
        {{cloze:Text3}}
        {{cloze:Text4}}
        {{cloze:Text5}}
        {{cloze:Text6}}
        {{cloze:Text7}}
        {{cloze:Text8}}
        {{cloze:Text9}}
        {{cloze:Text10}}
        {{cloze:Text11}}
        {{cloze:Text12}}
        {{cloze:Text13}}
        {{cloze:Text14}}
        {{cloze:Text15}}
        {{cloze:Text16}}
        {{cloze:Text17}}
        {{cloze:Text18}}
        {{cloze:Text19}}
        {{cloze:Text20}}
    </div>
    <div class="hidden">
        <div><span class="cloze">[...]</span></div>
        <div>{{Original}}</div>
    </div>
</div>

<script>
(function() {
    var cloze = document.getElementsByClassName("cloze")[0];
    if (!cloze) return;
    var rect = cloze.getBoundingClientRect();
    if (rect.bottom >= window.innerHeight) {
        var middle = rect.top + window.pageYOffset - window.innerHeight / 2;
        window.scrollTo(0, middle);
    }
})();
</script>\
"""

card_back = """\
{{#Title}}<div class="title">{{Title}}</div>{{/Title}}
<div class="text">
    <div id="clozed">
        {{cloze:Text1}}
        {{cloze:Text2}}
        {{cloze:Text3}}
        {{cloze:Text4}}
        {{cloze:Text5}}
        {{cloze:Text6}}
        {{cloze:Text7}}
        {{cloze:Text8}}
        {{cloze:Text9}}
        {{cloze:Text10}}
        {{cloze:Text11}}
        {{cloze:Text12}}
        {{cloze:Text13}}
        {{cloze:Text14}}
        {{cloze:Text15}}
        {{cloze:Text16}}
        {{cloze:Text17}}
        {{cloze:Text18}}
        {{cloze:Text19}}
        {{cloze:Text20}}
    </div>
    <div class="hidden">
        <div><span class="cloze">[...]</span></div>
        <div>{{Original}}</div>
    </div>
</div>

<hr>

<button id="btn-reveal" onclick="olToggle();">Show All</button>
<div class="hidden"><div id="original">{{Original}}</div></div>

{{#Remarks}}
<div class="extra-entry">
    <div class="extra-descr">Remarks</div><div>{{Remarks}}</div>
</div>
{{/Remarks}}
{{#Sources}}
<div class="extra-entry">
    <div class="extra-descr">Sources</div><div>{{Sources}}</div>
</div>
{{/Sources}}

<script>
(function() {
    // Strip OC syntax from reveal hint
    var hint = document.getElementById("original");
    if (hint) {
        hint.innerHTML = hint.innerHTML.replace(
            /\\{\\{oc(\\d+)::(.*?)(::(.*?))?\\}\\}/mg, "<span class='cloze'>$2</span>");
    }
    // Scroll to first cloze
    var cloze = document.getElementsByClassName("cloze")[0];
    if (cloze) {
        var rect = cloze.getBoundingClientRect();
        if (rect.bottom >= window.innerHeight) {
            var middle = rect.top + window.pageYOffset - window.innerHeight / 2;
            window.scrollTo(0, middle);
        }
    }
})();
function olToggle() {
    var orig = document.getElementById('original');
    var clozed = document.getElementById('clozed');
    var tmp = orig.innerHTML;
    orig.innerHTML = clozed.innerHTML;
    clozed.innerHTML = tmp;
}
</script>\
"""

card_css = """\
.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}

.text {
  display: inline-block;
  text-align: left;
}

.hidden {
  display: block;
  line-height: 0;
  height: 0;
  overflow: hidden;
  visibility: hidden;
}

.title {
  font-weight: bold;
  font-size: 1.1em;
  margin-bottom: 0.8em;
}

.cloze {
  font-weight: bold;
  color: blue;
}

.nightMode .cloze {
  color: lightblue;
}

.olc-context {
  color: inherit;
  font-weight: normal;
}

.nightMode .olc-context {
  color: inherit;
}

hr {
  border: none;
  border-top: 1px solid #ccc;
  margin: 12px 0;
}

.nightMode hr {
  border-top-color: #555;
}

#btn-reveal {
  font-size: 14px;
  padding: 6px 16px;
  margin: 8px 0;
  cursor: pointer;
  background: #eee;
  border: 1px solid #ccc;
  border-radius: 4px;
}

#btn-reveal:hover {
  background: #ddd;
}

.nightMode #btn-reveal {
  background: #444;
  border-color: #666;
  color: #ddd;
}

.card21 #btn-reveal {
  display: none;
}

.extra-entry {
  margin-top: 0.8em;
  font-size: 0.9em;
  text-align: left;
}

.extra-descr {
  font-weight: bold;
  margin-bottom: 0.2em;
}
\
"""


def checkModel(model, fields=True, notify=True):
    """Sanity checks for the model and fields"""
    mname = model["name"]
    is_olc = False
    if mname in config["synced"]["olmdls"] or mname.startswith(OLC_MODEL):
        is_olc = True
    if notify and not is_olc:
        olc_types = sorted(set([OLC_MODEL] + config["synced"]["olmdls"]))
        showTT("Reminder", "Can only generate overlapping clozes<br>"
               "on the following note types:<br><br>{}".format(
                   ", ".join("'{0}'".format(i) for i in olc_types))
               )
    if not is_olc or not fields:
        return is_olc
    flds = [f['name'] for f in model['flds']]
    complete = True
    for fid in OLC_FIDS_PRIV:
        fname = config["synced"]["flds"][fid]
        if fid == "tx":
            complete = all(fname + str(i) in flds for i in range(1, 4))
        else:
            complete = fname in flds
        if not complete:
            break
    if not complete:
        warnUser("Note Type", "Looks like your note type is not configured properly. "
                 "Please make sure that the fields list includes "
                 "all of the following fields:<br><br><i>%s</i>" % ", ".join(
                     config["synced"]["flds"][fid] if fid != "tx" else "Text1-TextN" for fid in OLC_FIDS_PRIV))
    return complete


def addModel(col):
    """Add add-on note type to collection"""
    models = col.models
    model = models.new(OLC_MODEL)
    model['type'] = MODEL_CLOZE
    for i in OLC_FLDS_IDS:
        if i == "tx":
            for i in range(1, OLC_MAX+1):
                fld = models.new_field(OLC_FLDS["tx"]+str(i))
                fld["size"] = 12
                models.add_field(model, fld)
            continue
        fld = models.new_field(OLC_FLDS[i])
        if i == "st":
            fld["sticky"] = True
        if i == "fl":
            fld["size"] = 12
        models.add_field(model, fld)
    template = models.new_template(OLC_CARD)
    template['qfmt'] = card_front
    template['afmt'] = card_back
    model['css'] = card_css
    model['sortf'] = 1
    models.add_template(model, template)
    models.add(model)
    return model


def updateTemplate(col):
    """Update add-on card templates"""
    print("Updating {} card template".format(OLC_MODEL))
    model = col.models.by_name(OLC_MODEL)
    template = model['tmpls'][0]
    template['qfmt'] = card_front
    template['afmt'] = card_back
    model['css'] = card_css
    col.models.save(model)
    return model


def initializeModels():
    model = mw.col.models.by_name(OLC_MODEL)
    if not model:
        model = addModel(mw.col)
