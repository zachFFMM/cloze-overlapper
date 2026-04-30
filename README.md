<p align="center"><img src="screenshots/demo1.gif"></p>

<h2 align="center">Cloze Overlapper for Anki</h2>

<p align="center">
<a title="Latest release" href="https://github.com/zachFFMM/cloze-overlapper/releases"><img src="https://img.shields.io/github/release-pre/zachFFMM/cloze-overlapper.svg?colorB=brightgreen"></a>
<a title="License: GNU AGPLv3" href="https://github.com/zachFFMM/cloze-overlapper/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-GNU%20AGPLv3-green.svg"></a>
</p>

> Sequential memorization, simplified.

Cloze Overlapper is an Anki add-on that turns ordered lists, sequences, and enumerations into overlapping cloze cards. Each new item is tested against the context of everything that came before it — no manual card-splitting required.

Built for **Anki 2.1.45+ through 25.x** with full Qt6 and Python 3.13 support.

---

### Table of Contents

- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Settings](#settings)
- [Compatibility](#compatibility)
- [Building from Source](#building-from-source)
- [Credits](#credits)

---

### How It Works

Write your list in the **Original** field using `{{oc1::item}}` syntax — the same as standard Anki cloze, but with `oc` instead of `c`:

```
{{oc1::blue}} {{oc2::red}} {{oc3::green}}
```

Three items produces exactly three cards:

| Card | Front | Back |
|------|-------|------|
| 1 | `[?]` `...` `...` | **blue** `...` `...` |
| 2 | `blue` `[?]` `...` | `blue` **red** `...` |
| 3 | `blue` `red` `[?]` | `blue` `red` **green** |

Each answer becomes context for the next card. N items = N cards, nothing extra.

---

### Installation

**Manual:**

1. Download or clone this repository
2. Copy the contents of `src/cloze_overlapper/` into Anki's `addons21/` folder:
   ```
   addons21/
   └── cloze_overlapper/   ← paste the contents of src/cloze_overlapper/ here
   ```
3. Restart Anki

A **"Cloze (overlapping)"** note type is created automatically on first run.

**From a release build:** Download the latest `.ankiaddon` from [Releases](https://github.com/zachFFMM/cloze-overlapper/releases) and double-click to install.

---

### Usage

1. Create a new note and select the **"Cloze (overlapping)"** note type
2. In the **Original** field, write your items using `{{oc1::...}}` syntax:
   - Highlight text and click the **Generate** button in the editor toolbar to wrap it automatically (increments the cloze number each time)
   - Or type the syntax manually
3. Click **Add** — overlapping cards are generated automatically on save

The internal fields (Text1–20, Settings, Full) are hidden. You only work with **Original**, **Title**, **Remarks**, and **Sources**.

**Toolbar buttons:**

| Button | Shortcut | What it does |
|--------|----------|--------------|
| Generate | `Alt+Shift+C` | Wrap selected text in `{{ocN::}}` |
| Options | `Alt+Shift+O` | Open per-note settings |
| Remove | `Alt+Shift+U` | Strip all cloze markers from the note |

---

### Settings

Open via **Tools → Cloze Overlapper Options** (global) or the Options toolbar button (per-note).

| Setting | Default | Description |
|---------|---------|-------------|
| **Show previous answers** | On | Already-revealed items appear as context on the front of each card |
| **Show all context** | Off | Every item except the current blank is shown — both before and after |

With both off, all items are blanks on every card (pure recall mode).

---

### Compatibility

| | |
|---|---|
| **Anki** | 2.1.45 – 25.x |
| **Python** | 3.9 – 3.13 |
| **Qt** | Qt5 and Qt6 |
| **Desktop** | Windows, macOS, Linux |
| **Mobile** | AnkiMobile, AnkiDroid (cards render as standard Anki cloze) |

---

### Building from Source

Requires [anki-addon-builder](https://github.com/glutanimate/anki-addon-builder/):

```bash
git clone https://github.com/zachFFMM/cloze-overlapper.git
cd cloze-overlapper
pip install aab
aab build
```

The packaged `.ankiaddon` file will appear in `build/`.

---

### Credits

Cloze Overlapper was originally created by [Aristotelis P.](https://glutanimate.com/) (Glutanimate) and is the foundation this fork is built on. This fork is maintained by [zachFFMM](https://github.com/zachFFMM) and updates the add-on for modern Anki (2.1.45+, Qt6, Python 3.13), simplifies the card generation model, and adds dark mode support.

Additional code contributions by [zjosua](https://github.com/zjosua).

Licensed under the [GNU AGPLv3](https://github.com/zachFFMM/cloze-overlapper/blob/master/LICENSE). This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY.
