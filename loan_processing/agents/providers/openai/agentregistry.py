"""
Agent Registry for configuration-driven agent creation.

This module provides centralized agent configuration and creation,
loading all agent definitions from external configuration files.
No hardcoded agent configurations - everything is configuration-driven.
"""

from __future__ import annotations

from typing import Any

from agents import Agent
from agents.mcp.server import MCPServerSse

from loan_processing.agents.shared.utils import ConfigurationLoader, OutputFormatGenerator, load_persona


class MCPServerFactory:
    """Factory for creating MCP server instances."""

    _server_cache: dict[str, MCPServerSse] = {}

    @classmethod
    def get_server(cls, server_type: str) -> MCPServerSse:
        """Get or create an MCP server instance."""
        if server_type not in cls._server_cache:
            cls._server_cache[server_type] = cls._create_server(server_type)
        return cls._server_cache[server_type]

    @classmethod
    def _create_server(cls, server_type: str) -> MCPServerSse:
        """Create a new MCP server instance from configuration."""
        server_config = ConfigurationLoader.get_mcp_server_config(server_type)
        return MCPServerSse(params={"url": server_config["url"]})


class AgentRegistry:
    """Central registry for agent types and configurations."""

    @classmethod
    def create_agent(cls, agent_type: str, model: str | None = None) -> Agent:
        """
        Create a configuration-driven agent instance.

        Agents are created based on external configuration files,
        making it easy to add new agent types without code changes.

        Args:
            agent_type: Type of agent to create (defined in agents.yaml)
            model: OpenAI model to use (e.g., "gpt-4")

        Returns:
            Configured Agent instance without hardcoded workflow dependencies

        Raises:
            ValueError: If agent_type is not defined in configuration
        """
        # Load agent configuration
        agent_config = ConfigurationLoader.get_agent_config(agent_type)

        # Create MCP server instances for this agent
        mcp_servers = [MCPServerFactory.get_server(server_type) for server_type in agent_config["mcp_servers"]]

        # Load persona instructions (without handoff configurations)
        persona_instructions = load_persona(agent_config["persona_file"])

        # Add structured output requirements for orchestration
        enhanced_instructions = OutputFormatGenerator.add_structured_output_instructions(
            persona_instructions, agent_config.get("output_format", {})
        )

        return Agent(
            name=agent_config["name"],
            instructions=enhanced_instructions,
            model=model,
            mcp_servers=mcp_servers,
            # No handoffs - orchestrator manages workflow
        )

    @classmethod
    def get_agent_info(cls, agent_type: str) -> dict[str, Any]:
        """Get information about an agent type from configuration."""
        return ConfigurationLoader.get_agent_config(agent_type).copy()

    @classmethod
    def list_agent_types(cls) -> list[str]:
        """Get list of available agent types from configuration."""
        return ConfigurationLoader.list_agent_types()

    @classmethod
    def get_agent_capabilities(cls, agent_type: str) -> list[str]:
        """Get capabilities of a specific agent type."""
        return ConfigurationLoader.get_agent_capabilities(agent_type)

    @classmethod
    def reload_configuration(cls) -> None:
        """Force reload of configuration from disk."""
        ConfigurationLoader.reload_configuration()
        # Clear MCP server cache to pick up any URL changes
        MCPServerFactory._server_cache.clear()


__all__ = ["AgentRegistry", "MCPServerFactory"]
