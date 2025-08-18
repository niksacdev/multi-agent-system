"""
Configuration management for the console application.

This module provides a clean, environment-based configuration system 
that's completely decoupled from the loan_processing backend module.
"""

import os
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum


class ProviderType(Enum):
    """Agent provider types."""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"


@dataclass
class OrchestrationUIConfig:
    """Orchestration UI configuration (not business logic)."""
    discovery_method: str
    default_selection: str
    show_pattern_details: bool
    enable_comparison: bool


@dataclass 
class BackendConfig:
    """Backend connectivity configuration."""
    mode: str  # "direct" or "api"
    
    # Future API mode settings
    api_base_url: Optional[str] = None
    api_timeout_seconds: int = 30


@dataclass
class AgentProviderConfig:
    """Agent provider configuration supporting both OpenAI and Azure OpenAI."""
    provider_type: ProviderType
    api_key: Optional[str] = None
    model_default: str = "gpt-4"
    
    # Azure OpenAI specific
    azure_api_key: Optional[str] = None
    azure_api_base: Optional[str] = None
    azure_api_version: str = "2024-02-01"
    azure_deployment_name: str = "gpt-4"
    
    def get_effective_config(self) -> Dict[str, Any]:
        """Get the effective configuration for the selected provider."""
        if self.provider_type == ProviderType.AZURE_OPENAI:
            return {
                "provider_type": "azure_openai",
                "api_key": self.azure_api_key,
                "api_base": self.azure_api_base,
                "api_version": self.azure_api_version,
                "deployment_name": self.azure_deployment_name,
                "model": self.azure_deployment_name
            }
        else:
            return {
                "provider_type": "openai",
                "api_key": self.api_key,
                "model": self.model_default
            }


@dataclass
class AppConfig:
    """Complete application configuration."""
    name: str
    version: str
    environment: str
    debug: bool
    agent_provider: AgentProviderConfig
    orchestration_ui: OrchestrationUIConfig
    backend: BackendConfig
    results_directory: str
    show_detailed_output: bool
    auto_save_results: bool


class ConfigurationLoader:
    """Loads and manages application configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "app_config.yaml"
        self.config_path = config_path
        self._config: Optional[AppConfig] = None
    
    def load_config(self) -> AppConfig:
        """Load configuration from YAML file with environment variable substitution."""
        if self._config is not None:
            return self._config
        
        # Load YAML configuration
        with open(self.config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        
        # Substitute environment variables
        resolved_config = self._substitute_env_vars(raw_config)
        
        # Parse configuration
        self._config = self._parse_config(resolved_config)
        return self._config
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """Recursively substitute environment variables in configuration."""
        if isinstance(config, dict):
            return {key: self._substitute_env_vars(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            # Parse environment variable with optional default
            env_expr = config[2:-1]  # Remove ${ and }
            if ":-" in env_expr:
                env_var, default = env_expr.split(":-", 1)
                return os.getenv(env_var, default)
            else:
                return os.getenv(env_expr)
        else:
            return config
    
    def _parse_config(self, config: Dict[str, Any]) -> AppConfig:
        """Parse the resolved configuration into structured objects."""
        
        # Parse agent provider
        provider_config = config["agent_provider"]
        provider_type = ProviderType(provider_config["provider_type"])
        
        agent_provider = AgentProviderConfig(
            provider_type=provider_type,
            api_key=provider_config.get("api_key"),
            model_default=provider_config.get("model_default", "gpt-4"),
            azure_api_key=provider_config.get("azure_api_key"),
            azure_api_base=provider_config.get("azure_api_base"), 
            azure_api_version=provider_config.get("azure_api_version", "2024-02-01"),
            azure_deployment_name=provider_config.get("azure_deployment_name", "gpt-4")
        )
        
        # Parse orchestration UI config
        orch_config = config["orchestration"]
        orchestration_ui = OrchestrationUIConfig(
            discovery_method=orch_config["discovery_method"],
            default_selection=orch_config["default_selection"],
            show_pattern_details=orch_config["show_pattern_details"],
            enable_comparison=orch_config["enable_comparison"]
        )
        
        # Parse backend configuration
        backend_config = config["backend"]
        backend = BackendConfig(
            mode=backend_config["mode"],
            api_base_url=backend_config.get("api_base_url"),
            api_timeout_seconds=backend_config.get("api_timeout_seconds", 30)
        )
        
        # Parse UI settings
        ui_config = config["ui"]
        
        return AppConfig(
            name=config["app"]["name"],
            version=config["app"]["version"],
            environment=config["app"]["environment"],
            debug=bool(config["app"]["debug"]),
            agent_provider=agent_provider,
            orchestration_ui=orchestration_ui,
            backend=backend,
            results_directory=ui_config["results_directory"],
            show_detailed_output=bool(ui_config["show_detailed_output"]),
            auto_save_results=bool(ui_config["auto_save_results"])
        )
    
    def get_backend_patterns(self):
        """
        Get orchestration patterns from backend.
        
        This method should query the backend for available patterns.
        For now, it directly imports from the backend module.
        Future: Replace with API call when backend becomes service.
        """
        # Import backend configuration to get available patterns
        # This is the proper place for backend queries
        try:
            import sys
            from pathlib import Path
            
            # Add project root to path
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            
            from loan_processing.agents.shared.utils.config_loader import ConfigurationLoader as BackendLoader
            
            backend_loader = BackendLoader()
            backend_configs = backend_loader.get_available_configurations()
            
            # Convert backend patterns to a simple format for UI
            patterns = []
            for config_name, config_data in backend_configs.items():
                if config_name != "agents":  # Skip the agents config
                    patterns.append({
                        "id": config_name,
                        "name": config_name.replace("_", " ").title(),
                        "description": f"{config_name} orchestration pattern",
                        "workflow": [],  # Backend doesn't expose workflow details to UI
                        "available": True
                    })
            
            return patterns
            
        except Exception as e:
            # Fallback to hardcoded patterns during development
            return [
                {
                    "id": "sequential",
                    "name": "Sequential Processing", 
                    "description": "Agents process in sequence",
                    "workflow": [],
                    "available": True
                },
                {
                    "id": "parallel",
                    "name": "Parallel Processing",
                    "description": "Credit and Income agents run in parallel",
                    "workflow": [],
                    "available": True  
                }
            ]
    
    def validate_configuration(self) -> List[str]:
        """Validate the configuration and return any issues."""
        issues = []
        config = self.load_config()
        
        # Validate agent provider
        if config.agent_provider.provider_type == ProviderType.OPENAI:
            if not config.agent_provider.api_key:
                issues.append("OPENAI_API_KEY is required for OpenAI provider")
        elif config.agent_provider.provider_type == ProviderType.AZURE_OPENAI:
            if not config.agent_provider.azure_api_key:
                issues.append("AZURE_OPENAI_KEY is required for Azure OpenAI provider")
            if not config.agent_provider.azure_api_base:
                issues.append("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI provider")
        
        # Validate default pattern exists in backend
        try:
            backend_patterns = self.get_backend_patterns()
            pattern_ids = [p["id"] for p in backend_patterns]
            if config.orchestration_ui.default_selection not in pattern_ids:
                issues.append(f"Default pattern '{config.orchestration_ui.default_selection}' not found in backend patterns")
        except Exception as e:
            issues.append(f"Cannot validate patterns: {e}")
        
        # Validate results directory can be created
        results_dir = Path(config.results_directory)
        try:
            results_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create results directory '{config.results_directory}': {e}")
        
        return issues


# Global configuration loader instance
_config_loader: Optional[ConfigurationLoader] = None


def get_config_loader() -> ConfigurationLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigurationLoader()
    return _config_loader


def get_app_config() -> AppConfig:
    """Get the application configuration."""
    return get_config_loader().load_config()


def get_available_patterns():
    """Get available orchestration patterns from backend."""
    return get_config_loader().get_backend_patterns()


def get_pattern_by_id(pattern_id: str):
    """Get orchestration pattern by ID from backend."""
    patterns = get_available_patterns()
    for pattern in patterns:
        if pattern["id"] == pattern_id:
            return pattern
    return None