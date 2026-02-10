# ⌨️ typing-cli

A beautiful and fast CLI typing test — right from your terminal.

Practice your typing speed with real-time WPM tracking, accuracy stats, animated pixel-art F1 car, multiple languages, and color themes.

[![PyPI version](https://img.shields.io/pypi/v/typing-cli.svg)](https://pypi.org/project/typing-cli/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

```
  __               _                        ___ 
 / /___  ______  (_)___  ____ _        ____/ (_)
/ __/ / / / __ \/ / __ \/ __ `/  ____ / __/ / / 
/ /_/ /_/ / /_/ / / / / / /_/ /  /___// /_/ / /  
\__/\__, / .___/_/_/ /_/\__, /        \__/_/_/   
   /____/_/            /____/                     
```

## 🚀 Installation

```bash
pip install typing-cli
```

Then launch with:
```bash
python -m typingtest
```

On first launch the app **automatically** adds `typing-cli` to your PATH.  
Restart your terminal and from then on just type:
```bash
typing-cli
```

### From source

```bash
git clone https://github.com/lecoffre/typing-cli.git
cd typing-cli
pip install -e .
```

## ▶️ Usage

```bash
typing-cli
```

If the command is not found, you can always run:

```bash
python -m typingtest
```

The app launches in your terminal. Start typing!

## 🔄 Update

The app checks for updates automatically on launch.  
If a new version is available, press **Ctrl+U** on the splash screen to update instantly.

You can also update manually:
```bash
pip install --user --upgrade typing-cli
```

## 🗑️ Uninstall

```bash
pip uninstall typing-cli -y
```

## ⌨️ Keyboard Shortcuts

| Shortcut       | Action                     |
|----------------|----------------------------|
| `Tab`          | Restart test               |
| `Escape`       | Back / Quit                |
| `Ctrl+T`       | Change theme               |
| `Ctrl+L`       | Change language            |
| `Ctrl+M`       | Switch mode (words/code)   |
| `Ctrl+H`       | View score history         |
| `Ctrl+U`       | Update to latest version   |
| `Ctrl++/-`     | Zoom in/out                |
| `Ctrl+Q`       | Quit                       |

## 🌍 Languages

Built-in:
- 🇬🇧 English (200 most common words)
- 🇫🇷 French (200 most common words)

## 🎨 Themes

- **Midnight** — deep dark blues (default)
- **Forest** — earthy greens
- **Sunset** — warm amber tones
- **Ocean** — cool cyan palette
- **Mono** — minimal grayscale

## 📊 Features

- Real-time WPM & accuracy tracking
- Per-character coloring (correct / incorrect / cursor)
- Animated pixel-art F1 car reflecting your speed
- Gamification: streak, combo, milestones, rank system
- Code typing mode
- Score history with date, WPM, accuracy
- Multiple languages & themes
- Splash screen with ASCII art
- Auto-update: notifies and updates from the CLI
- Clean, extensible architecture

## 🛠️ Development

```bash
git clone https://github.com/lecoffre/typing-cli.git
cd typing-cli
pip install -e .

# Run directly
python -m typingtest
```

## 🤝 Contributing

Contributions are welcome! Feel free to open issues and pull requests.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

[MIT](LICENSE)
