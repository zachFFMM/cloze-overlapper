# CrowdAnki Compatibility

This document describes the changes made in v1.0.1 to make Cloze Overlapper notes portable via [CrowdAnki](https://github.com/Stvad/CrowdAnki).

## Problem

CrowdAnki identifies note types across collections using a `crowdanki_uuid` key on the model dict. Without it, every fresh install generates a new identity — two users sharing a deck via CrowdAnki end up with duplicate note types instead of a matched one.

## What Was Changed

All changes are isolated to `src/cloze_overlapper/template.py` and a small hook in `src/cloze_overlapper/__init__.py`.

### 1. UUID on new installs

In `addModel()`, a `crowdanki_uuid` is set before the model is added to the collection:

```python
import uuid
model["crowdanki_uuid"] = str(uuid.uuid4())
```

### 2. UUID backfill for existing installs

`initializeModels()` now checks for a missing `crowdanki_uuid` and backfills it on the first profile open after upgrading:

```python
if "crowdanki_uuid" not in model:
    model["crowdanki_uuid"] = str(uuid.uuid4())
    mw.col.models.save(model)
```

### 3. Auto-register imported overlap models

When a deck is imported via CrowdAnki into a collection that doesn't already know the note type name, editing any imported note would show a "Can only generate overlapping clozes on…" warning. The `_autoRegisterOverlapModels()` helper now scans all note types on profile open and registers any that match the overlap field structure (Original, Settings, Full, and at least Text1–Text3).

## Verification

To confirm the UUID was applied in a live Anki install, open the Debug Console (`Ctrl+Shift+;`) and run:

```python
mw.col.models.by_name("Cloze (overlapping)").get("crowdanki_uuid")
```

This should return a UUID string. If it returns `None`, the backfill did not run — check that the add-on is on v1.0.1 or later.

## Out of Scope

- Card templates and CSS — already export cleanly through CrowdAnki
- Per-note Settings field — plain text, already survives export
- Making editing work without the add-on installed — recipients still need the add-on to generate cards
