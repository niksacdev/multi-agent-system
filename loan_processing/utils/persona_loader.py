"""Persona loader.

Reads markdown instruction files from `agent-persona/`. Falls back to a
minimal default if the file is missing. Intentionally no caching to allow
hot-reload during development edits.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

PERSONA_DIR_NAME: Final[str] = "agent-persona"


class PersonaLoader:
    """Loads agent persona instructions from markdown files."""

    @classmethod
    def load_persona(cls, persona_key: str) -> str:
        """Return persona markdown for the given key or a default fallback.

        Args:
            persona_key: e.g. "credit", "income", "risk", "intake".
        """
        # Path to agents/agent-persona directory
        personas_dir = Path(__file__).parent.parent / "agents" / "agent-persona"
        path = personas_dir / f"{persona_key}-agent-persona.md"
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return (
                f"You are the {persona_key} agent. Provide concise, structured domain outputs as JSON when appropriate."
            )

    @classmethod
    def get_persona_path(cls, persona_key: str) -> Path:
        """Get the file path for a persona.

        Args:
            persona_key: e.g. "credit", "income", "risk", "intake".

        Returns:
            Path to the persona markdown file
        """
        personas_dir = Path(__file__).parent.parent / "agents" / "agent-persona"
        return personas_dir / f"{persona_key}-agent-persona.md"

    @classmethod
    def persona_exists(cls, persona_key: str) -> bool:
        """Check if a persona file exists.

        Args:
            persona_key: e.g. "credit", "income", "risk", "intake".

        Returns:
            True if the persona file exists
        """
        return cls.get_persona_path(persona_key).exists()

    @classmethod
    def list_available_personas(cls) -> list[str]:
        """Get list of available persona keys.

        Returns:
            List of available persona keys (without -agent-persona.md suffix)
        """
        personas_dir = Path(__file__).parent.parent / "agents" / "agent-persona"
        if not personas_dir.exists():
            return []

        personas = []
        for persona_file in personas_dir.glob("*-agent-persona.md"):
            persona_key = persona_file.name.replace("-agent-persona.md", "")
            personas.append(persona_key)

        return sorted(personas)


# Convenience function for backward compatibility
def load_persona(persona_key: str) -> str:
    """Convenience function for loading persona. Delegates to PersonaLoader.load_persona()."""
    return PersonaLoader.load_persona(persona_key)


__all__ = ["PersonaLoader", "load_persona"]
