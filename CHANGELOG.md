# Changelog

All notable changes to Cloze Overlapper will be documented here. You can click on each release number to be directed to a detailed log of all code commits for that particular release. The download links will direct you to the GitHub release page, allowing you to manually install a release if you want.

This is a fork maintained by [zachFFMM](https://github.com/zachFFMM). Originally created by [Glutanimate](https://glutanimate.com/).

## [Unreleased]

## [1.0.0] - 2026-04-10

### Breaking Changes

- **New cloze syntax**: Changed from `[[oc1::text]]` to `{{oc1::text}}` to match standard Anki cloze conventions
- **Simplified card generation**: Replaced complex before/prompt/after algorithm with simple incremental reveal pattern
- **Simplified settings**: Replaced 7 settings (3 spinboxes + 4 checkboxes) with 2 checkboxes: "Show previous answers" and "Show all context"
- **No more Full card**: The extra "Full" cloze card is no longer generated. N items = exactly N cards.

### Added

- **Anki 25.x / Python 3.13 compatibility**: Updated vendored importer for PEP 451 (find_spec/exec_module)
- **Show all context option**: New setting to reveal all items except the current cloze (both previous and future)
- **Auto-generate on add**: Overlapping clozes are automatically generated when adding a note — no manual button click needed
- **Hidden internal fields**: Text1-20, Full, and Settings fields are hidden in the editor. Users only see Original, Title, Remarks, Sources.
- **Dark mode support**: Card styling includes `.nightMode` CSS for Anki's dark theme
- **Generate button reworked**: Now works like standard Anki cloze — highlight text, click to wrap in `{{oc1::}}`, highlight next, click for `{{oc2::}}`
- **Remove button reworked**: Strips all `{{oc...}}` markers from all fields at once

### Fixed

- Runtime crash when generating clozes on new (unsaved) notes (`No such note: '0'`)
- `editor.widget` crash on Anki 25.x that prevented all toolbar buttons from appearing
- `_addCards` monkey-patch not being called (Anki 25.x calls `_add_current_note` instead)
- V3 scheduler tooltip firing on every profile open
- Legacy JS function calls (`focusField`, `saveField`, `wrap`) guarded for modern Anki editor
- `editorSaveThen` now handles missing `saveNow` method

### Changed

- Card styling modernized — clean layout matching standard Anki cloze look
- All monkey-patches guarded with `hasattr` for forward compatibility

## [0.4.0-alpha.0] - 2019-02-01

### Changed

- Smaller adjustments to the card template
- Committed updated template to docs folder

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.4.0-alpha.0) -->

## [0.4.0-dev.3] - 2019-01-28

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.4.0-dev.3) -->

### Added

- Automatically scroll to cloze item
- Cloze reveal button that uncovers clozes in place
- Hint reveal hotkey (G)
- Beautiful new button icons
- anki21: Support for V2 Scheduler

### Changed

- Override sibling-spacing in review queue by default
- Introduced comment markers to templates that should make programmatic parsing and automated template updates easier in the future.
- Updated About section with support for Patreons & Contributors

### Fixed

- Card content shifting between front/back
- Backwards compatibility with anki20
- anki21: Dialog layout issues
- anki21: Dialog tab focus order
- anki21: JS asynchronicity issues when saving note content
- anki21: Adding ordered/unordered list

## [0.4.0-dev.2] - 2019-01-26

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.4.0-dev.2) -->

### Changed

- Extensively refactored add-on

### Fixed

- anki21 compat issues

## [0.4.0-dev.1] - 2019-01-25

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.4.0-dev.1) -->

### Added

- Preliminary support for Anki 2.1 (thanks to @zjosua for his help with this!)

### Changed

- Changed the following hotkeys to avoid conflicts with global shortcuts and
  other popular add-ons:
  - Multi-line cloze: Ctrl+Shift+K
  - Multi-line cloze alternate: Ctrl+Alt+Shift+K
  - Remove Clozes: Alt+Shift+U
- Reduced cloze item limit to one. This allows using the Overlapping Cloze note
  type like a regular Cloze note type when only one item is clozed.


## [0.3.0] - 2017-03-07

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.3.0) -->

### Added

- Option to disable full cloze card generation (thanks to smh, dtconan18, Jon, and everyone else who suggested this)
- Option to automatically suspend full cloze cards on creation

### Fixed

- More checks to prevent rare missing config errors (thanks to Chris for the bug report)

## [0.2.1] - 2017-03-03

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.2.1) -->

### Added

- Add a hotkey and button to remove clozes from selected text (Alt+Shift+R), also works with regular clozes

### Changed

- Moved key binding definitions to the top of main.py, allowing advanced users to manually customize them
- Reduced minimum number of cloze items to two

### Fixed

- List toggling now works properly again (thanks to Devin for the report!)
- Sanity check to prevent empty notes if the user doesn't add enough items to cloze

## [0.2.0] - 2017-03-01

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.2.0) -->

First stable public release.

### Changed

- Card template:
  - More consistent spacing across front and back
  - Decoupled cloze text width from other sections
  - More intelligent cloze scrolling

### Fixed:

- smaller bug fixes

## [0.1.2] - 2017-02-27

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.1.2) -->

### Added

- Vastly improved card layout (content is still left-aligned, but now centered on the screen)
- Automatically scroll to cloze on the answer side (this is somewhat experimental. Let me know if you run into any issues, especially on mobile!)

### Changed

- Updated template colors
- Smaller improvements to the templates and styling

## [0.1.1] - 2017-02-26

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.1.1) -->

### Added

- Support imported note types right out of the box

### Fixed 

- Encoding error when working with lists

## [0.1.0] - 2017-02-26

<!-- ### [Download](https://github.com/glutanimate/cloze-overlapper/releases/tag/v0.1.0) -->

First public pre-release.

## [0.0.1] - 2016-??-??

Early version of the add-on for internal use.


[Unreleased]: https://github.com/zachFFMM/cloze-overlapper/compare/v1.0.0...HEAD
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
[0.1.0]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.1.0...v0.1.1
[0.0.1]: https://github.com/zachFFMM/cloze-overlapper/compare/v0.1.0...v0.1.1


-----

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).