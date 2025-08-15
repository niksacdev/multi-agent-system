"""Persona loader.

Reads markdown instruction files from `agent-persona/`. Falls back to a
minimal default if the file is missing. Intentionally no caching to allow
hot-reload during development edits.
"""
from __future__ import annotations

from pathlib import Path
from typing import Final

PERSONA_DIR_NAME: Final[str] = "agent-persona"


def load_persona(persona_key: str) -> str:
    """Return persona markdown for the given key or a default fallback.

    Args:
        persona_key: e.g. "credit", "income", "risk", "intake".
    """
    # Path to agents/shared/agent-persona directory
    personas_dir = Path(__file__).parent.parent / "agent-persona"
    path = personas_dir / f"{persona_key}-agent-persona.md"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"You are the {persona_key} agent. Provide concise, structured domain outputs as JSON when appropriate."


__all__ = ["load_persona"]
