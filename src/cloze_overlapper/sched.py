# -*- coding: utf-8 -*-

# Cloze Overlapper Add-on for Anki
#
# Copyright (C)  2016-2019 Aristotelis P. <https://glutanimate.com/>
# Updated for modern Anki (2.1.45+)

"""
Modifications to Anki's scheduling

Ensures sibling cards from Cloze Overlapper notes:
1. Are not buried (so they all appear in the same session)
2. Appear in sequential order (card 1, card 2, card 3...)

In modern Anki (V3 scheduler), this is achieved by:
- Disabling sibling burying in deck config
- Setting sequential due positions on new cards
- Configuring decks for ascending new-card order
- Hooking the reviewer to requeue the next sibling after answering
"""

import time as _time
import os as _os

from aqt import mw, gui_hooks
from aqt.utils import tooltip as _tooltip
from .template import checkModel
from .config import config


# --- Diagnostic logging ---

_LOG_PATH = _os.path.join(
    _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
    "olc_sched_debug.log",
)


def _log(msg):
    """Append a timestamped line to the debug log."""
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write("[{}] {}\n".format(
                _time.strftime("%H:%M:%S"), msg))
    except Exception:
        pass


# --- Deck config: disable burying and set ascending order ---

def _configure_deck(did):
    """Configure a deck for OLC: disable burying, ascending new-card order."""
    sched_conf = config["synced"].get("sched", None)
    if not sched_conf:
        return

    override_new, override_review, _bury_full = sched_conf

    try:
        deck = mw.col.decks.get(did)
        if not deck:
            return

        # Filtered decks don't have a regular config; their bury behavior
        # is inherited from the home deck of each card. Skip configuring
        # them directly — the reviewer hook handles ordering at runtime.
        if deck.get('dyn'):
            return

        conf_id = deck.get('conf', 1)
        dconf = mw.col.decks.get_config(conf_id)
        if not dconf:
            return

        changed = False

        # Disable sibling burying
        if override_new and dconf.get('new', {}).get('bury', True):
            dconf.setdefault('new', {})['bury'] = False
            changed = True
        if override_review and dconf.get('rev', {}).get('bury', True):
            dconf.setdefault('rev', {})['bury'] = False
            changed = True

        # Set new card order to ascending position (0 = in order added)
        if dconf.get('new', {}).get('order', 0) != 0:
            dconf.setdefault('new', {})['order'] = 0
            changed = True

        if changed:
            mw.col.decks.save(dconf)
    except Exception:
        pass


# --- Sequential card positioning ---

def setSequentialPositions(note):
    """Set sequential due positions for new cards of an OLC note.

    Ensures cards appear in order (ord 0, ord 1, ord 2...) when the
    deck is configured for ascending new-card order.
    """
    if not checkModel(note.note_type(), fields=False, notify=False):
        return

    cards = sorted(note.cards(), key=lambda c: c.ord)
    new_cards = [c for c in cards if c.type == 0]
    if not new_cards:
        return

    # Use the first card's due as the base position
    base = new_cards[0].due
    for i, card in enumerate(new_cards):
        target = base + i
        if card.due != target:
            card.due = target
            mw.col.update_card(card)


# --- Reviewer hook: requeue next sibling ---

def _on_did_answer_card(reviewer, card, ease):
    """After answering an OLC card, force the immediate next sibling to appear next."""
    _log("HOOK FIRED: card_id={} ord={} type={} queue={}".format(
        card.id, card.ord, card.type, card.queue))
    try:
        nt = card.note_type()
        is_olc = checkModel(nt, fields=False, notify=False)
        _log("  note_type='{}' is_olc={}".format(nt.get("name"), is_olc))
        if not is_olc:
            return

        note = card.note()
        siblings = sorted(note.cards(), key=lambda c: c.ord)
        current_ord = card.ord
        _log("  note has {} siblings: ords={}".format(
            len(siblings), [s.ord for s in siblings]))

        next_sib = None
        for sib in siblings:
            if sib.ord > current_ord:
                next_sib = sib
                break

        if next_sib is None:
            _log("  no next sibling (answered last card)")
            return
        _log("  next_sib: id={} ord={} type={} queue={} due={}".format(
            next_sib.id, next_sib.ord, next_sib.type,
            next_sib.queue, next_sib.due))

        if next_sib.queue == -1:
            _log("  next_sib is suspended — leaving alone")
            return
        if next_sib.queue < 0:
            _log("  unburying next_sib (was queue={})".format(next_sib.queue))
            next_sib.queue = next_sib.type
            next_sib.mod = int(_time.time())
            mw.col.update_card(next_sib)

        today = mw.col.sched.today
        changed = False
        old_due = next_sib.due

        # In V3 + filtered decks, the queue value can mismatch the type
        # (e.g. type=0 new cards may show queue=2). The reliable way to
        # force a card to the front is to set its `due` lower than every
        # other card in the same queue.
        if next_sib.queue == 1:
            # Intraday learning — due is a unix timestamp; set to now
            next_sib.due = int(_time.time())
            next_sib.mod = int(_time.time())
            mw.col.update_card(next_sib)
            _log("  learning card: due={} (was {})".format(
                next_sib.due, old_due))
            changed = True
        elif next_sib.queue in (0, 2, 3):
            try:
                min_due = mw.col.db.scalar(
                    "SELECT MIN(due) FROM cards WHERE queue=? AND id!=?",
                    next_sib.queue, next_sib.id)
                new_due = (min_due - 1) if min_due is not None else -1
            except Exception as e:
                _log("  MIN(due) lookup FAILED: {}".format(e))
                new_due = old_due - 1000  # fallback: just go lower
            next_sib.due = new_due
            next_sib.mod = int(_time.time())
            mw.col.update_card(next_sib)
            _log("  queue={}: due={} (was {})".format(
                next_sib.queue, new_due, old_due))
            changed = True
        else:
            _log("  next_sib in unhandled queue {} — skipping".format(
                next_sib.queue))

        if changed:
            # Try multiple V3-compatible queue rebuilds
            try:
                mw.col.sched.reset()
                _log("  called sched.reset()")
            except Exception as e:
                _log("  sched.reset() FAILED: {}".format(e))
            try:
                mw.reset()
                _log("  called mw.reset()")
            except Exception as e:
                _log("  mw.reset() FAILED: {}".format(e))
            _tooltip("OLC: next → ord {}".format(next_sib.ord),
                     period=800)

    except Exception as e:
        _log("  EXCEPTION: {}".format(e))


# --- Per-note deck configuration ---

def disableBuryingForNote(note):
    """Configure the deck(s) a note's cards are in for OLC."""
    if not checkModel(note.note_type(), fields=False, notify=False):
        return
    cards = note.cards()
    seen_dids = set()
    for card in cards:
        if card.did not in seen_dids:
            seen_dids.add(card.did)
            _configure_deck(card.did)


# --- Initialization ---

def _find_decks_with_olc_notes():
    """Find all deck IDs that contain Cloze Overlapper notes."""
    dids = set()
    olc_models = config["synced"].get("olmdls", [])
    for model_name in olc_models:
        model = mw.col.models.by_name(model_name)
        if not model:
            continue
        mid = model['id']
        nids = mw.col.models.nids(mid)
        for nid in nids:
            note = mw.col.get_note(nid)
            for card in note.cards():
                dids.add(card.did)
    return dids


def _migrate_due_order_for_olc_notes():
    """One-pass repair: for every OLC note, make new-card due values
    monotonically increase with ord, so V3's queue picks ord 0 first,
    then ord 1, etc. Only touches cards whose dues are out of order."""
    olc_models = config["synced"].get("olmdls", [])
    repaired = 0
    notes_seen = 0
    try:
        for model_name in olc_models:
            model = mw.col.models.by_name(model_name)
            if not model:
                continue
            mid = model['id']
            for nid in mw.col.models.nids(mid):
                notes_seen += 1
                note = mw.col.get_note(nid)
                cards = sorted(note.cards(), key=lambda c: c.ord)
                target_cards = [c for c in cards
                                if c.type == 0 and c.queue >= 0]
                if len(target_cards) < 2:
                    continue
                dues = [c.due for c in target_cards]
                if dues == sorted(dues):
                    continue
                base = min(dues)
                for i, card in enumerate(target_cards):
                    target_due = base + i
                    if card.due != target_due:
                        card.due = target_due
                        mw.col.update_card(card)
                        repaired += 1
    except Exception as e:
        _log("MIGRATION FAILED: {}".format(e))
    if repaired:
        _log("MIGRATION: repaired {} cards across {} notes scanned".format(
            repaired, notes_seen))


def initializeScheduler():
    """Initialize scheduler modifications.

    - Repairs ord/due mismatches on existing OLC notes
    - Configures all decks with OLC notes: no burying, ascending order
    - Hooks the reviewer to requeue siblings in order after answering
    """
    sched_conf = config["synced"].get("sched", None)
    if not sched_conf:
        return
    override_new, override_review, _bury_full = sched_conf
    if not override_new and not override_review:
        return

    # Configure existing decks
    try:
        dids = _find_decks_with_olc_notes()
        for did in dids:
            _configure_deck(did)
    except Exception:
        pass

    # Repair ord/due mismatches on existing OLC notes
    _migrate_due_order_for_olc_notes()

    # Hook reviewer to enforce sequential sibling ordering
    try:
        gui_hooks.reviewer_did_answer_card.append(_on_did_answer_card)
        _log("=== INITIALIZED: reviewer_did_answer_card hook registered ===")
        try:
            _tooltip("Cloze Overlapper: scheduler hook active",
                     period=2000)
        except Exception:
            pass
    except AttributeError as e:
        _log("INIT FAILED: hook not available: {}".format(e))
