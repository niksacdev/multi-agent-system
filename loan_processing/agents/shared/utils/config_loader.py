"""
Shared configuration loader for agent systems.

This module provides centralized configuration loading that can be used
across different agent providers while maintaining consistent configuration
access patterns.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigurationLoader:
    """Loads and validates agent configuration from YAML files."""

    _config_cache: dict[str, Any] | None = None

    @classmethod
    def load_config(cls, force_reload: bool = False) -> dict[str, Any]:
        """Load agent configuration from YAML file."""
        if cls._config_cache is not None and not force_reload:
            return cls._config_cache

        config_path = Path(__file__).parent.parent / "config" / "agents.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Agent configuration file not found: {config_path}")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Validate required sections
        required_sections = ["agents", "mcp_servers", "metadata"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required section '{section}' in agent configuration")

        cls._config_cache = config
        return config

    @classmethod
    def get_agent_config(cls, agent_type: str) -> dict[str, Any]:
        """Get configuration for a specific agent type."""
        config = cls.load_config()

        if agent_type not in config["agents"]:
            available_types = list(config["agents"].keys())
            raise ValueError(f"Unknown agent type: {agent_type}. Available types: {available_types}")

        return config["agents"][agent_type]

    @classmethod
    def get_mcp_server_config(cls, server_type: str) -> dict[str, Any]:
        """Get configuration for a specific MCP server."""
        config = cls.load_config()

        if server_type not in config["mcp_servers"]:
            raise ValueError(f"Unknown MCP server type: {server_type}")

        return config["mcp_servers"][server_type]

    @classmethod
    def list_agent_types(cls) -> list[str]:
        """Get list of available agent types from configuration."""
        config = cls.load_config()
        return list(config["agents"].keys())

    @classmethod
    def list_mcp_server_types(cls) -> list[str]:
        """Get list of available MCP server types from configuration."""
        config = cls.load_config()
        return list(config["mcp_servers"].keys())

    @classmethod
    def get_agent_capabilities(cls, agent_type: str) -> list[str]:
        """Get capabilities of a specific agent type."""
        agent_config = cls.get_agent_config(agent_type)
        return agent_config.get("capabilities", [])

    @classmethod
    def reload_configuration(cls) -> None:
        """Force reload of configuration from disk."""
        cls.load_config(force_reload=True)


__all__ = ["ConfigurationLoader"]
