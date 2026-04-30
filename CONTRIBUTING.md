# Contributing

Issues and pull requests are welcome.

## Reporting a Bug

1. Verify you're on the latest version — redownload from [Releases](https://github.com/zachFFMM/cloze-overlapper/releases) if unsure
2. Restart Anki and reproduce the issue with other add-ons disabled
3. Open a [bug report](https://github.com/zachFFMM/cloze-overlapper/issues/new?template=bug_report.md) and include your Anki debug info (**Help → About → Copy Debug Info**)

## Requesting a Feature

Open a [feature request](https://github.com/zachFFMM/cloze-overlapper/issues/new?template=feature_request.md) and describe your use case. What problem are you trying to solve, and what would an ideal solution look like?

## Submitting a Pull Request

- Test on a recent Anki build (2.1.45+)
- Keep the change focused — one thing per PR
- For larger changes, open an issue first to discuss the approach

## Development Setup

```bash
git clone https://github.com/zachFFMM/cloze-overlapper.git
cd cloze-overlapper
pip install aab
aab build
```

Copy `src/cloze_overlapper/` into Anki's `addons21/` folder and restart Anki to load the development version.

### Source Map

| File | Purpose |
|------|---------|
| `src/cloze_overlapper/overlapper.py` | Core cloze generation logic |
| `src/cloze_overlapper/generator.py` | Card field assembly |
| `src/cloze_overlapper/editor.py` | Editor toolbar integration |
| `src/cloze_overlapper/reviewer.py` | Review-time hooks |
| `src/cloze_overlapper/template.py` | Note type definition and initialization |
| `src/cloze_overlapper/sched.py` | Sibling scheduling overrides |
| `src/cloze_overlapper/config.py` | Settings management |
| `src/cloze_overlapper/gui/` | Options dialogs |
