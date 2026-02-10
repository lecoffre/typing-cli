# Developer Guide — typing-cli

## 🔧 Local Setup

```bash
git clone https://github.com/lecoffre/typing-cli.git
cd typing-cli
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -e .
```

Run locally:
```bash
typing-cli                    # if PATH is set
python -m typingtest          # always works
```

---

## 📦 Useful pip Commands

| Command | What it does |
|---------|-------------|
| `pip install --user typing-cli` | Install for current user |
| `pip install --user --upgrade typing-cli` | Update to latest |
| `pip install -e .` | Install in dev (editable) mode |
| `pip uninstall typing-cli -y` | Uninstall |
| `pip show typing-cli` | Show installed version & location |
| `pip install --user typing-cli==0.3.0` | Install a specific version |

---

## 🚀 Release Process

### 1. Bump version (2 files, must match)

| File | Line |
|------|------|
| `src/typingtest/__init__.py` | `__version__ = "X.Y.Z"` |
| `pyproject.toml` | `version = "X.Y.Z"` |

### 2. Commit & tag

```bash
git add -A
git commit -m "release: vX.Y.Z — short description"
git tag vX.Y.Z
git push origin main --tags
```

### 3. Create GitHub Release

1. Go to https://github.com/lecoffre/typing-cli/releases/new
2. Select tag `vX.Y.Z`
3. Title: `vX.Y.Z`
4. Description: changelog / what's new
5. Click **Publish release**

### 4. Wait & verify

- GitHub Actions builds & publishes to PyPI automatically (~1-2 min)
- Check: https://pypi.org/project/typing-cli/
- Test: `pip install --user --upgrade typing-cli && typing-cli`

---

## 📋 Version Convention

| Bump | When |
|------|------|
| `0.X.0` → `0.X+1.0` | New feature |
| `0.X.Y` → `0.X.Y+1` | Bug fix |
| `0.X.Y` → `1.0.0` | Stable public release |

---

## 🏗️ Project Structure

```
src/typingtest/
├── __init__.py          # __version__
├── __main__.py          # CLI entry point + auto-PATH
├── core/
│   ├── config.py        # User config (theme, language)
│   ├── updater.py       # PyPI update check + self-update
│   ├── engine.py        # Typing engine (WPM, accuracy)
│   └── gamification.py  # Streak, combo, ranks
└── ui/
    ├── app.py           # Main Textual app + themes
    ├── screens/         # Splash, Typing, Result, History
    └── widgets/         # TypingArea, StatsBar, F1 car
```

---

## ⚠️ Gotchas

- **Always bump both** `__init__.py` AND `pyproject.toml` — mismatch = broken release
- **Tag format**: must be `vX.Y.Z` (with the `v`) to trigger the workflow
- **PyPI is immutable**: once a version is published, you can't overwrite it — bump again if you mess up
- **`--user` flag**: needed on systems where Python is installed globally (no admin rights)
