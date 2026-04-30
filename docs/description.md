<!-- BANNER -->

Cloze Overlapper turns ordered lists and sequences into overlapping cloze flashcards. Each item is tested in the context of what came before it — making sequence memorization a natural part of your review workflow rather than a manual card-building exercise.

### COMPATIBILITY

Supports Anki 2.1.45 through 25.x (Qt5 and Qt6, Python 3.9–3.13). Cards are standard Anki cloze and work on AnkiMobile and AnkiDroid without any mobile add-on.

<!-- CHANGELOG -->

### BACKGROUND

Memorizing ordered information — classifications, steps in a process, ranked lists — is one of the harder things to do well in Anki. Standard flashcards work best when each card is atomic, but sequences are inherently chained: knowing item B depends on knowing item A, knowing C depends on B.

The classic solution is **overlapping cards**: A→B, B→C, C→D. Each answer becomes the prompt for the next card, building a chain of associations through the whole sequence. The problem is creating these cards by hand is tedious enough that most people skip it.

This add-on automates the entire process. Write your list once using `{{oc1::item}}` syntax, and the cards are generated automatically.

### HOW IT WORKS

For a sequence `{{oc1::blue}} {{oc2::red}} {{oc3::green}}`, the add-on generates three cards:

| Card | Front | Back |
|------|-------|------|
| 1 | `[?]` `...` `...` | **blue** `...` `...` |
| 2 | `blue` `[?]` `...` | `blue` **red** `...` |
| 3 | `blue` `red` `[?]` | `blue` `red` **green** |

N items = exactly N cards.

### SETTINGS

Two settings control how context is shown:

- **Show previous answers** (default: on) — previously revealed items appear as context on the front
- **Show all context** (off by default) — every item except the current blank is shown

<!-- SUPPORT -->

### CREDITS AND LICENSE

Originally created by [Aristotelis P.](https://glutanimate.com/) (Glutanimate). This fork is maintained by [zachFFMM](https://github.com/zachFFMM) with updates for Anki 25.x, Qt6, and Python 3.13 compatibility.

With code contributions from: zjosua

Licensed under the GNU AGPLv3. Source available on [GitHub](https://github.com/zachFFMM/cloze-overlapper). Pull requests welcome.
