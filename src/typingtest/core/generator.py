"""Word generator — builds random paragraphs from language word lists or code snippets."""

from __future__ import annotations

import json
import random
from importlib import resources
from pathlib import Path


# ── Available code languages ──────────────────────────────────────────

CODE_LANGUAGES = ["python", "typescript", "javascript", "rust", "go"]


def _bundled_path(language: str) -> Path:
    """Resolve the path to a bundled language JSON file."""
    pkg = resources.files("typingtest") / "data" / "languages"
    return Path(str(pkg / f"{language}.json"))


def _code_path(language: str) -> Path:
    """Resolve the path to a bundled code snippets JSON file."""
    pkg = resources.files("typingtest") / "data" / "code"
    return Path(str(pkg / f"{language}.json"))


def load_words(language: str) -> list[str]:
    """Load the word list for a given language."""
    path = _bundled_path(language)
    if not path.exists():
        raise FileNotFoundError(f"Language file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["words"]


def load_code_snippets(language: str) -> list[str]:
    """Load code snippets for a given programming language."""
    path = _code_path(language)
    if not path.exists():
        raise FileNotFoundError(f"Code file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["snippets"]


def generate_paragraph(language: str, word_count: int = 30) -> str:
    """Pick random words and join them into a paragraph."""
    words = load_words(language)
    chosen = [random.choice(words) for _ in range(word_count)]
    return " ".join(chosen)


def generate_code_snippet(language: str) -> str:
    """Pick a random code snippet for the given programming language."""
    snippets = load_code_snippets(language)
    return random.choice(snippets)
