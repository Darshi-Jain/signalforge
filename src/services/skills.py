from __future__ import annotations

from pathlib import Path


SKILLS_DIR = Path("skills")


def load_skill(name: str) -> str:
    path = SKILLS_DIR / f"{name}.md"

    if not path.exists():
        raise ValueError(f"Unknown skill: {name}")

    return path.read_text()
