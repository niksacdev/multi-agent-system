"""
System configuration for the loan processing system.

This module handles ALL system configuration including:
- AI service settings (OpenAI, Azure OpenAI, etc.)
- Data service connectivity (MCP servers)
- Processing patterns
- Business logic configuration

Client applications should not manage these settings.
"""

import os
from dataclasses import dataclass
from enum import Enum

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()


class AgentProviderType(Enum):
    """Agent SDK/framework provider types."""

    OPENAI_AGENTS_SDK = "openai_agents_sdk"
    AUTOGEN = "autogen"
    SEMANTIC_KERNEL = "semantic_kernel"


class AIModelProviderType(Enum):
    """AI model service provider types."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"


@dataclass
class AgentProviderConfig:
    """Agent SDK/framework configuration."""

    provider_type: AgentProviderType

    @classmethod
    def from_env(cls) -> "AgentProviderConfig":
        """Load agent provider configuration from environment variables."""
        provider_str = os.getenv("LOAN_PROCESSING_AGENT_PROVIDER", "openai_agents_sdk").lower()

        # Map string to enum
        provider_map = {
            "openai_agents_sdk": AgentProviderType.OPENAI_AGENTS_SDK,
            "autogen": AgentProviderType.AUTOGEN,
            "semantic_kernel": AgentProviderType.SEMANTIC_KERNEL,
        }
        provider_type = provider_map.get(provider_str, AgentProviderType.OPENAI_AGENTS_SDK)

        return cls(provider_type=provider_type)

    def validate(self) -> list[str]:
        """Validate agent provider configuration."""
        errors = []

        # For now, only OpenAI Agents SDK is implemented
        if self.provider_type != AgentProviderType.OPENAI_AGENTS_SDK:
            errors.append(
                f"Agent provider '{self.provider_type.value}' is not yet implemented. Use 'openai_agents_sdk'."
            )

        return errors


@dataclass
class AIModelConfig:
    """AI model service provider configuration."""

    provider_type: AIModelProviderType
    api_key: str | None = None
    model: str = "gpt-4"

    # Azure OpenAI specific
    azure_api_key: str | None = None
    azure_endpoint: str | None = None
    azure_api_version: str = "2024-02-01"

    # Anthropic specific
    anthropic_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "AIModelConfig":
        """Load AI model service configuration from environment variables."""
        provider_str = os.getenv("LOAN_PROCESSING_AI_MODEL_PROVIDER", "openai").lower()

        # Map string to enum
        provider_map = {
            "openai": AIModelProviderType.OPENAI,
            "azure_openai": AIModelProviderType.AZURE_OPENAI,
            "anthropic": AIModelProviderType.ANTHROPIC,
        }
        provider_type = provider_map.get(provider_str, AIModelProviderType.OPENAI)

        return cls(
            provider_type=provider_type,
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("LOAN_PROCESSING_DEFAULT_MODEL", "gpt-4"),
            azure_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

    def validate(self) -> list[str]:
        """Validate AI model service configuration."""
        errors = []

        if self.provider_type == AIModelProviderType.OPENAI:
            if not self.api_key:
                errors.append("OPENAI_API_KEY is required for OpenAI provider")
        elif self.provider_type == AIModelProviderType.AZURE_OPENAI:
            if not self.azure_api_key:
                errors.append("AZURE_OPENAI_API_KEY is required for Azure OpenAI provider")
            if not self.azure_endpoint:
                errors.append("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI provider")
        elif self.provider_type == AIModelProviderType.ANTHROPIC:
            if not self.anthropic_api_key:
                errors.append("ANTHROPIC_API_KEY is required for Anthropic provider")

        return errors


@dataclass
class DataConfig:
    """Data service connectivity configuration (MCP servers)."""

    application_verification_port: int = 8010
    document_processing_port: int = 8011
    financial_calculations_port: int = 8012
    connection_timeout: int = 30

    @classmethod
    def from_env(cls) -> "DataConfig":
        """Load data service configuration from environment variables."""
        return cls(
            application_verification_port=int(os.getenv("MCP_APP_VERIFICATION_PORT", "8010")),
            document_processing_port=int(os.getenv("MCP_DOCUMENT_PROCESSING_PORT", "8011")),
            financial_calculations_port=int(os.getenv("MCP_FINANCIAL_CALCULATIONS_PORT", "8012")),
            connection_timeout=int(os.getenv("MCP_CONNECTION_TIMEOUT", "30")),
        )


@dataclass
class SystemConfig:
    """Complete system configuration."""

    agent_provider: AgentProviderConfig
    ai_model: AIModelConfig
    data_services: DataConfig
    debug: bool = False

    @classmethod
    def from_env(cls) -> "SystemConfig":
        """Load complete system configuration from environment variables."""
        return cls(
            agent_provider=AgentProviderConfig.from_env(),
            ai_model=AIModelConfig.from_env(),
            data_services=DataConfig.from_env(),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )

    def validate(self) -> list[str]:
        """Validate complete system configuration."""
        errors = []
        errors.extend(self.agent_provider.validate())
        errors.extend(self.ai_model.validate())
        # Could add data service connectivity checks here
        return errors

    # Backward compatibility property for existing code
    @property
    def ai(self) -> AIModelConfig:
        """Backward compatibility: access ai_model as 'ai'."""
        return self.ai_model


def get_system_config() -> SystemConfig:
    """Get system configuration."""
    return SystemConfig.from_env()
