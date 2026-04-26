# Plan: Make Cloze Overlapper Compatible with CrowdAnki

Paste this into Claude Code from the repo root
(`ClaudsHouse/Projects/cloze-overlapper/`).

## Goal

Make notes created with Cloze Overlapper survive a round trip through
CrowdAnki export/import. Specifically:

1. The note type gets a stable `crowdanki_uuid` so CrowdAnki can identify
   it across collections instead of creating duplicates.
2. Existing users who already have the note type get the UUID backfilled
   on next startup.
3. A recipient importing a deck whose note type matches our structure
   but has a different name gets it auto-registered as an overlap model
   (so they don't see the "Can only generate overlapping clozes on…"
   warning when they try to edit).

All changes are isolated to `src/cloze_overlapper/template.py` plus one
small hook wiring change in `src/cloze_overlapper/__init__.py`. No
changes to the card templates, CSS, editor, reviewer, or generator are
needed.

## Context — why these three changes

- CrowdAnki identifies note types across collections with a
  `crowdanki_uuid` key on the model dict. Our `addModel()` in
  `template.py` doesn't set one, so every fresh install gets a new
  identity. Two users with Cloze Overlapper installed will fail to
  match each other's note types on import → duplicated models.
- Existing installs already have a note type with no UUID. We need to
  migrate them once, on profile open.
- The addon tracks "which note type names are overlap models" in
  `config["synced"]["olmdls"]` (see `config.py`). On import into a
  collection that doesn't already know the imported model name, editing
  any imported note shows a reminder popup. We can auto-register any
  model that has the full set of required fields (`Original`,
  `Settings`, `Text1…TextN`, `Full`).

## Step-by-step

### Step 1 — Add a stable UUID when creating the model

File: `src/cloze_overlapper/template.py`

1. Add `import uuid` at the top of the file (after the existing
   imports).
2. In `addModel(col)`, right before `models.add(model)`, add:
   ```python
   model["crowdanki_uuid"] = str(uuid.uuid4())
   ```

That's it for new installs.

### Step 2 — Backfill UUID on existing installs

File: `src/cloze_overlapper/template.py`

In `initializeModels()`, after fetching the model by name, add a
migration branch that sets `crowdanki_uuid` if missing and saves the
model. Final shape:

```python
def initializeModels():
    model = mw.col.models.by_name(OLC_MODEL)
    if not model:
        model = addModel(mw.col)
        return
    # Backfill crowdanki_uuid for users who installed before this change
    if "crowdanki_uuid" not in model:
        model["crowdanki_uuid"] = str(uuid.uuid4())
        mw.col.models.save(model)
    # Auto-register any other overlap-shaped models we find (step 3)
    _autoRegisterOverlapModels(mw.col)
```

Keep the existing `initializeModels()` return behavior if anything
upstream depends on it — currently nothing does (it's called from
`__init__.py`'s `delayedInit` and the return value is ignored).

### Step 3 — Auto-register imported overlap-shaped models

File: `src/cloze_overlapper/template.py`

Add a new helper below `initializeModels()`:

```python
def _autoRegisterOverlapModels(col):
    """Scan for note types that look like overlap models (imported via
    CrowdAnki or similar) and add their names to config["synced"]["olmdls"]
    so editing them doesn't warn the user."""
    from .config import config

    known = set(config["synced"]["olmdls"])
    flds_cfg = config["synced"]["flds"]
    required_singletons = [flds_cfg[fid] for fid in OLC_FIDS_PRIV if fid != "tx"]
    tx_name = flds_cfg["tx"]

    added = False
    for model in col.models.all():
        name = model["name"]
        if name in known:
            continue
        field_names = {f["name"] for f in model["flds"]}
        # Needs all non-tx private fields...
        if not all(f in field_names for f in required_singletons):
            continue
        # ...and at least Text1, Text2, Text3 (same minimum as checkModel)
        if not all(tx_name + str(i) in field_names for i in range(1, 4)):
            continue
        known.add(name)
        added = True

    if added:
        config["synced"]["olmdls"] = sorted(known)
        config.save()
```

Notes:
- `OLC_FIDS_PRIV = ['og', 'st', 'tx', 'fl']` — see `consts.py`. We treat
  `tx` specially (it's a prefix, not a single field).
- Mirrors the same minimum-fields check as `checkModel()` in the same
  file — 3+ Text fields is enough to qualify.
- `config.save()` is the method exposed by `libaddon`'s `ConfigManager`.
  If that specific call fails, check `libaddon/anki/configmanager.py`
  for the correct method name (it may be `.save_all()` or just
  assignment through `__setitem__`) — do a quick grep before assuming.

### Step 4 — Verify no other call sites need updating

Grep for existing references:

```
rg "crowdanki_uuid" src/
rg "initializeModels" src/
rg "olmdls" src/
```

Expected:
- `crowdanki_uuid` should have zero hits before this change.
- `initializeModels` is called once from `__init__.py` — no signature
  change needed.
- `olmdls` is read in `template.py:checkModel`, `config.py`, and
  `gui/options_global*.py`. We're only writing to it, so readers are
  fine.

### Step 5 — Build and sanity-check

From `Projects/cloze-overlapper/`:

```
aab build
```

`aab` (anki-addon-builder) is the declared build tool in
`requirements.txt`. If it errors on a missing `aab` binary, install
with `pip install aab` (note: the Windows shell here uses `py -m pip`).

There are no unit tests in this repo, so verification is manual:

1. Install the freshly built `.ankiaddon` into a clean Anki profile.
2. Open Anki → the "Cloze (overlapping)" note type should exist and,
   in `Tools → Manage Note Types → (select) → Fields… / Cards…`, the
   underlying model dict should have a `crowdanki_uuid`. Easiest way
   to confirm: `Debug Console` (Ctrl+Shift+;) →
   ```python
   mw.col.models.by_name("Cloze (overlapping)").get("crowdanki_uuid")
   ```
   Should return a UUID string.
3. Repeat with an existing profile that had the old version installed
   — same check should now return a UUID (migrated on first open).
4. Rename the note type to something like "Cloze (overlapping) v2" and
   restart Anki. Confirm that the new name shows up in
   `config["synced"]["olmdls"]` — either via the debug console
   (`mw.addonManager.getConfig("olcloze")`) or by editing a note of
   that type and confirming the "Can only generate…" warning does NOT
   fire.
5. Round-trip test (only if you have CrowdAnki installed): export a
   deck containing an overlap note → delete the deck and note type →
   import via CrowdAnki → confirm the note type comes back with the
   same UUID and no duplicates are created.

### Step 6 — Update `_version.py` and `addon.json` changelog

Bump the patch version in `src/cloze_overlapper/_version.py` and add a
one-line note to `addon.json`'s changelog (or wherever the changelog
lives in this fork). Message suggestion:

> Add `crowdanki_uuid` to the overlap note type and auto-register
> imported overlap-shaped note types — makes decks portable via
> CrowdAnki.

### Step 7 — Commit

The sub-repo permissions file only allows `git:*` inside
`Projects/cloze-overlapper/`, so commit from inside that directory:

```
git add src/cloze_overlapper/template.py src/cloze_overlapper/_version.py addon.json
git commit -m "Add crowdanki_uuid and auto-register imported overlap models"
```

Don't push unless I ask.

## Out of scope (intentionally)

- **Card templates and CSS.** These already export cleanly through
  CrowdAnki; no changes needed.
- **Per-note Settings field migration.** Already plain text, already
  survives export.
- **GUI changes.** No new options screens needed — this is transparent
  to the user.
- **Making edits work without the addon installed.** Not possible
  without re-implementing the cloze generator; recipients still need
  the addon to edit, only to review.

## If something goes sideways

- If `config.save()` doesn't exist on `ConfigManager`, check
  `libaddon/anki/configmanager.py` for the actual persistence method.
  `libaddon` is vendored, so the source is right there.
- If `aab build` fails with a Qt/Anki version complaint, the target is
  pinned to `anki21` in `addon.json` — that's expected and fine.
- If a clean install throws on first profile open because
  `initializeModels()` runs before the collection is ready, the hook
  is `profile_did_open` (wired in `__init__.py`), which fires after
  the collection is loaded — should be safe. If it isn't, move the
  `_autoRegisterOverlapModels` call into a separate
  `profile_did_open` hook that runs after `delayedInit`.
