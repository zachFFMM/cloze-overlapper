# Changelog

All notable changes to Cloze Overlapper will be documented here.

This is a fork maintained by [zachFFMM](https://github.com/zachFFMM). Originally created by [Glutanimate](https://glutanimate.com/).

## [Unreleased]

## [1.0.1] - 2026-04-30

### Added

- `crowdanki_uuid` is now set on the overlap note type so decks survive CrowdAnki round-trips without creating duplicate note types
- Existing installs get the UUID backfilled automatically on the next profile open
- Imported note types that match the overlap field structure are auto-registered so editing them does not trigger the "Can only generate overlapping clozes on…" warning

## [1.0.0] - 2026-04-10

### Breaking Changes

- **New cloze syntax**: Changed from `[[oc1::text]]` to `{{oc1::text}}` to match standard Anki cloze conventions
- **Simplified card generation**: Replaced complex before/prompt/after algorithm with simple incremental reveal
- **Simplified settings**: Replaced 7 settings (3 spinboxes + 4 checkboxes) with 2 checkboxes
- **No more Full card**: N items = exactly N cards

### Added

- Anki 25.x / Python 3.13 compatibility (updated vendored importer for PEP 451)
- Show all context option — reveals everything except the current blank
- Auto-generate on add — no manual button click needed
- Hidden internal fields — users only see Original, Title, Remarks, Sources
- Dark mode support via `.nightMode` CSS
- Generate button works like standard Anki cloze — highlights increment automatically
- Remove button strips all `{{oc...}}` markers from all fields at once

### Fixed

- Runtime crash when generating clozes on new (unsaved) notes
- `editor.widget` crash on Anki 25.x that prevented toolbar buttons from appearing
- `_addCards` monkey-patch not being called (Anki 25.x uses `_add_current_note`)
- V3 scheduler tooltip firing on every profile open
- Legacy JS function calls guarded for modern Anki editor
- `editorSaveThen` handles missing `saveNow` method

### Changed

- Card styling modernized — clean layout matching standard Anki cloze look
- All monkey-patches guarded with `hasattr` for forward compatibility

## [0.4.0-alpha.0] - 2019-02-01

### Changed

- Smaller adjustments to the card template
- Committed updated template to docs folder

## [0.4.0-dev.3] - 2019-01-28

### Added

- Automatically scroll to cloze item
- Cloze reveal button that uncovers clozes in place
- Hint reveal hotkey (G)
- New button icons
- anki21: Support for V2 Scheduler

### Changed

- Override sibling-spacing in review queue by default

### Fixed

- Card content shifting between front/back
- anki21: Dialog layout issues and tab focus order
- anki21: JS asynchronicity issues when saving note content
- anki21: Adding ordered/unordered list

## [0.4.0-dev.2] - 2019-01-26

### Changed

- Extensively refactored add-on

### Fixed

- anki21 compatibility issues

## [0.4.0-dev.1] - 2019-01-25

### Added

- Preliminary support for Anki 2.1 (thanks to @zjosua)

## [0.3.0] - 2017-03-07

### Added

- Option to disable full cloze card generation
- Option to automatically suspend full cloze cards on creation

## [0.2.1] - 2017-03-03

### Added

- Hotkey and button to remove clozes from selected text (Alt+Shift+R)

## [0.2.0] - 2017-03-01

First stable public release.

## [0.1.2] - 2017-02-27

### Added

- Improved card layout (centered on screen)
- Auto-scroll to cloze on answer side

## [0.1.1] - 2017-02-26

### Added

- Support for imported note types out of the box

## [0.1.0] - 2017-02-26

First public pre-release.

---

[Unreleased]: https://github.com/zachFFMM/cloze-overlapper/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/zachFFMM/cloze-overlapper/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.4.0-alpha.0...v1.0.0
[0.4.0-alpha.0]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.4.0-dev.3...v0.4.0-alpha.0
[0.4.0-dev.3]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.4.0-dev.2...v0.4.0-dev.3
[0.4.0-dev.2]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.4.0-dev.1...v0.4.0-dev.2
[0.4.0-dev.1]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.3.0...v0.4.0-dev.1
[0.3.0]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/zachFFMM/cloze-overlapper/releases/tag/v0.1.0

---

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
