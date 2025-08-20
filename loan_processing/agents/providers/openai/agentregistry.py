"""
Agent Registry for configuration-driven agent creation.

This module provides centralized agent configuration and creation,
loading all agent definitions from external configuration files.
No hardcoded agent configurations - everything is configuration-driven.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from loan_processing.utils import get_logger, log_execution  # noqa: E402

from agents import Agent
from agents.mcp.server import MCPServerSse

from loan_processing.config.settings import AIModelConfig, AIModelProviderType
from loan_processing.utils import ConfigurationLoader, OutputFormatGenerator, PersonaLoader

# Initialize logging
logger = get_logger(__name__)


class MCPServerFactory:
    """Factory for creating MCP server instances."""

    _server_cache: dict[str, MCPServerSse] = {}

    @classmethod
    def get_server(cls, server_type: str) -> MCPServerSse:
        """Get or create an MCP server instance."""
        if server_type not in cls._server_cache:
            logger.info("Creating new MCP server instance", 
                       server_type=server_type, component="mcp_server_factory")
            cls._server_cache[server_type] = cls._create_server(server_type)
        else:
            logger.debug("Using cached MCP server instance", 
                        server_type=server_type, component="mcp_server_factory")
        return cls._server_cache[server_type]

    @classmethod
    def _create_server(cls, server_type: str) -> MCPServerSse:
        """Create a new MCP server instance from configuration."""
        logger.info("Creating MCP server from configuration", 
                   server_type=server_type, component="mcp_server_factory")
        
        try:
            server_config = ConfigurationLoader.get_mcp_server_config(server_type)
            server_url = server_config["url"]
            
            logger.info("MCP server configuration loaded", 
                       server_type=server_type, 
                       server_url=server_url,
                       component="mcp_server_factory")
            
            return MCPServerSse(params={"url": server_url})
            
        except Exception as e:
            logger.error("Failed to create MCP server", 
                        server_type=server_type,
                        error_message=str(e),
                        error_type=type(e).__name__,
                        component="mcp_server_factory")
            raise


class AgentRegistry:
    """Central registry for agent types and configurations."""

    def __init__(self, ai_model_config: AIModelConfig | None = None):
        """Initialize the agent registry with AI model service configuration."""
        self.ai_model_config = ai_model_config
        
        logger.info("Agent registry initialized", 
                   has_ai_config=ai_model_config is not None,
                   provider_type=ai_model_config.provider_type.value if ai_model_config else None,
                   component="agent_registry")

    @log_execution(component="agent_registry", operation="create_configured_agent")
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
        logger.info("Creating configured agent", 
                   agent_type=agent_type, 
                   model=model,
                   component="agent_registry")
        
        try:
            # Load agent configuration
            agent_config = ConfigurationLoader.get_agent_config(agent_type)
            logger.info("Agent configuration loaded", 
                       agent_type=agent_type,
                       agent_name=agent_config.get("name"),
                       mcp_servers=agent_config.get("mcp_servers", []),
                       component="agent_registry")

            # Create MCP server instances for this agent (agents choose tools autonomously)
            mcp_servers = [MCPServerFactory.get_server(server_type) for server_type in agent_config["mcp_servers"]]
            logger.info("MCP servers initialized for agent", 
                       agent_type=agent_type,
                       server_count=len(mcp_servers),
                       component="agent_registry")

            # Load persona instructions (without handoff configurations)
            persona_instructions = PersonaLoader.load_persona(agent_config["persona_file"])
            logger.debug("Persona instructions loaded", 
                        agent_type=agent_type,
                        persona_file=agent_config["persona_file"],
                        component="agent_registry")

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
            
            logger.info("Agent model configuration determined", 
                       agent_type=agent_type,
                       effective_model=effective_model,
                       provider_type=self.ai_model_config.provider_type.value if self.ai_model_config else "unknown",
                       component="agent_registry")

            agent = Agent(
                name=agent_config["name"],
                instructions=enhanced_instructions,
                model=effective_model,
                mcp_servers=mcp_servers,
                # No handoffs - orchestrator manages workflow, agents choose tools
            )
            
            logger.info("Agent created successfully", 
                       agent_type=agent_type,
                       agent_name=agent_config["name"],
                       component="agent_registry")
            
            return agent
            
        except Exception as e:
            logger.error("Failed to create configured agent", 
                        agent_type=agent_type,
                        error_message=str(e),
                        error_type=type(e).__name__,
                        component="agent_registry")
            raise

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
        logger.info("Reloading agent configuration", component="agent_registry")
        
        try:
            ConfigurationLoader.reload_configuration()
            # Clear MCP server cache to pick up any URL changes
            cache_size = len(MCPServerFactory._server_cache)
            MCPServerFactory._server_cache.clear()
            
            logger.info("Configuration reloaded successfully", 
                       cleared_cache_entries=cache_size,
                       component="agent_registry")
                       
        except Exception as e:
            logger.error("Failed to reload configuration", 
                        error_message=str(e),
                        error_type=type(e).__name__,
                        component="agent_registry")
            raise


__all__ = ["AgentRegistry", "MCPServerFactory"]
