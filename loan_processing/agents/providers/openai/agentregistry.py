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

from loan_processing.config.settings import AIModelConfig, AIModelProviderType
from loan_processing.utils import ConfigurationLoader, OutputFormatGenerator, load_persona


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

    def __init__(self, ai_model_config: AIModelConfig | None = None):
        """Initialize the agent registry with AI model service configuration."""
        self.ai_model_config = ai_model_config

    def create_configured_agent(self, agent_type: str, model: str | None = None) -> Agent:
        """
        Create a configuration-driven agent instance.

        Agents are created based on external configuration files,
        making it easy to add new agent types without code changes.
        Agents remain autonomous in their tool selection.

        Args:
            agent_type: Type of agent to create (defined in agents.yaml)
            model: AI model to use (optional, uses AI config default if not provided)

        Returns:
            Configured Agent instance without hardcoded workflow dependencies

        Raises:
            ValueError: If agent_type is not defined in configuration
        """
        # Load agent configuration
        agent_config = ConfigurationLoader.get_agent_config(agent_type)

        # Create MCP server instances for this agent (agents choose tools autonomously)
        mcp_servers = [MCPServerFactory.get_server(server_type) for server_type in agent_config["mcp_servers"]]

        # Load persona instructions (without handoff configurations)
        persona_instructions = load_persona(agent_config["persona_file"])

        # Add structured output requirements for orchestration
        enhanced_instructions = OutputFormatGenerator.add_structured_output_instructions(
            persona_instructions, agent_config.get("output_format", {})
        )

        # Determine model to use (preserves agent autonomy while using AI model config)
        effective_model = model
        if not effective_model and self.ai_model_config:
            if self.ai_model_config.provider_type == AIModelProviderType.AZURE_OPENAI:
                # For Azure OpenAI, use deployment name
                effective_model = self.ai_model_config.azure_endpoint  # This should be the deployment name
            else:
                # For OpenAI, use configured model
                effective_model = self.ai_model_config.model

        return Agent(
            name=agent_config["name"],
            instructions=enhanced_instructions,
            model=effective_model,
            mcp_servers=mcp_servers,
            # No handoffs - orchestrator manages workflow, agents choose tools
        )

    @classmethod
    def create_agent(cls, agent_type: str, model: str | None = None) -> Agent:
        """
        Backward compatibility method for creating agents without AI config.

        Note: This will use environment variables for AI configuration.
        Prefer using an AgentRegistry instance with explicit AI config.
        """
        from loan_processing.config.settings import get_system_config

        system_config = get_system_config()
        registry = cls(system_config.ai_model)
        return registry.create_configured_agent(agent_type, model)

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
