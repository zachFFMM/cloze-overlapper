<p align="center"><img src="screenshots/demo1.gif"></p>

<h2 align="center">Cloze Overlapper for Anki</h2>

<p align="center">
<a title="Latest (pre-)release" href="https://github.com/zachFFMM/cloze-overlapper/releases"><img src ="https://img.shields.io/github/release-pre/zachFFMM/cloze-overlapper.svg?colorB=brightgreen"></a>
<a title="License: GNU AGPLv3" href="https://github.com/zachFFMM/cloze-overlapper/blob/master/LICENSE"><img  src="https://img.shields.io/badge/license-GNU AGPLv3-green.svg"></a>
</p>

> List memorization made easy!

This is an add-on for the spaced-repetition flashcard app [Anki](https://apps.ankiweb.net/). It facilitates **memorizing enumerations**, lists, or any other type of sequential information by generating overlapping cloze cards that incrementally reveal each item.

### Table of Contents <!-- omit in toc -->

- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Settings](#settings)
- [Building](#building)
- [License and Credits](#license-and-credits)

### How It Works

Type items using `{{oc1::text}}` syntax in the **Original** field (just like standard Anki cloze, but with `oc` instead of `c`). Each item gets its own card, revealed incrementally:

For `{{oc1::blue}} {{oc2::red}} {{oc3::green}}`:

| Card | Front | Back |
|------|-------|------|
| 1 | `[___]` `...` `...` | `blue` `...` `...` |
| 2 | `blue` `[___]` `...` | `blue` `red` `...` |
| 3 | `blue` `red` `[___]` | `blue` `red` `green` |

3 items = exactly 3 cards. No extra "full cloze" card.

### Installation

1. Download or clone this repository
2. Copy the contents of `src/cloze_overlapper/` into Anki's `addons21/cloze_overlapper/` folder
3. Restart Anki

The add-on will create a **"Cloze (overlapping)"** note type automatically on first run.

### Usage

1. Select the **"Cloze (overlapping)"** note type
2. In the **Original** field, type your items using `{{oc1::item}}` syntax
   - Use the toolbar **generate button** to wrap highlighted text (works like the standard cloze button)
   - Or type the syntax manually
3. Click **Add** — cards are generated automatically

The internal fields (Text1-20, Settings, Full) are hidden in the editor. You only see Original, Title, Remarks, and Sources.

**Toolbar buttons:**
- **Generate** (Alt+Shift+C): Wrap selected text in `{{ocN::}}`
- **Options** (Alt+Shift+O): Per-note cloze settings
- **Remove** (Alt+Shift+U): Strip all cloze markers from note

### Settings

Two options available in **Tools → Cloze Overlapper Options** or per-note via the options button:

| Setting | Default | Effect |
|---------|---------|--------|
| **Show previous answers** | ON | Previously revealed items shown as context. OFF = all items are blanks. |
| **Show all context** | OFF | All items except the current cloze are revealed (both previous and future). |

### Compatibility

- **Anki**: 2.1.45+ through 25.x
- **Python**: 3.9 through 3.13
- **Qt**: Qt5 and Qt6
- **Platforms**: Windows, macOS, Linux, AnkiMobile, AnkiDroid (cards are standard cloze)

### Building

With [Anki add-on builder](https://github.com/glutanimate/anki-addon-builder/) installed:

    git clone https://github.com/zachFFMM/cloze-overlapper.git
    cd cloze-overlapper
    aab build

### License and Credits

*Cloze Overlapper* was originally created by [Aristotelis P.](https://glutanimate.com/) (Glutanimate). This fork is maintained by [zachFFMM](https://github.com/zachFFMM) with updates for modern Anki compatibility (2.1.45+ and Qt6).

With code contributions from: [zjosua](https://github.com/zjosua)

Cloze Overlapper is free and open-source software. The add-on code that runs within Anki is released under the GNU AGPLv3 license, extended by a number of additional terms. For more information please see the [LICENSE](https://github.com/zachFFMM/cloze-overlapper/blob/master/LICENSE) file that accompanied this program.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY.
