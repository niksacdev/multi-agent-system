"""
Utility functions for the console application.
"""

import subprocess
import time
from typing import List, Dict, Any

from config.settings import get_app_config, MCPServerConfig


def start_mcp_servers_from_config() -> List[subprocess.Popen]:
    """
    Start all MCP servers based on application configuration.
    
    Returns:
        List of process objects for the started servers.
    """
    config = get_app_config()
    processes = []
    
    print("Starting MCP servers based on configuration...")
    
    for server_config in config.mcp_servers:
        if not server_config.required:
            continue
            
        print(f"Starting {server_config.name} server on port {server_config.port}...")
        try:
            process = subprocess.Popen(
                ["uv", "run", "python", "-m", server_config.module],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            processes.append(process)
            time.sleep(2)  # Give server time to start
            print(f"✓ {server_config.name} server started")
        except Exception as e:
            print(f"❌ Failed to start {server_config.name}: {e}")

    if processes:
        print(f"\n✅ {len(processes)} MCP servers started successfully!")
    return processes


def start_mcp_servers() -> List[subprocess.Popen]:
    """
    Legacy function for manual MCP server starting.
    Prefer start_mcp_servers_from_config() for configuration-based approach.
    """
    servers = [
        {
            "name": "Application Verification",
            "port": 8010,
            "module": "loan_processing.tools.mcp_servers.application_verification.server",
        },
        {
            "name": "Document Processing", 
            "port": 8011,
            "module": "loan_processing.tools.mcp_servers.document_processing.server",
        },
        {
            "name": "Financial Calculations",
            "port": 8012,
            "module": "loan_processing.tools.mcp_servers.financial_calculations.server",
        },
    ]

    processes = []
    for server in servers:
        print(f"Starting {server['name']} server on port {server['port']}...")
        try:
            process = subprocess.Popen(
                ["uv", "run", "python", "-m", server["module"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            processes.append(process)
            time.sleep(2)  # Give server time to start
            print(f"✓ {server['name']} server started")
        except Exception as e:
            print(f"❌ Failed to start {server['name']}: {e}")

    if processes:
        print(f"\n✅ {len(processes)} MCP servers started successfully!")
    return processes


def stop_mcp_servers(processes: List[subprocess.Popen]):
    """Stop all MCP server processes."""
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    print("🛑 All MCP servers stopped")


def check_mcp_servers_health() -> Dict[str, bool]:
    """
    Check if MCP servers are running based on configuration.
    
    Returns:
        Dictionary mapping server names to health status.
    """
    config = get_app_config()
    health_status = {}
    
    # This is a simplified check - in production you'd ping the actual servers
    for server_config in config.mcp_servers:
        # For now, just check if the module exists
        try:
            import importlib
            importlib.import_module(server_config.module)
            health_status[server_config.name] = True
        except ImportError:
            health_status[server_config.name] = False
    
    return health_status


def format_currency(amount: float) -> str:
    """Format a currency amount for display."""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format a percentage value for display."""
    return f"{value:.2%}"


def format_duration(seconds: float) -> str:
    """Format a duration in seconds for display."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def validate_input_choice(prompt: str, valid_choices: List[str], default: str = None) -> str:
    """
    Validate user input against a list of valid choices.
    
    Args:
        prompt: The prompt to display to the user
        valid_choices: List of valid input choices
        default: Default choice if user enters nothing
        
    Returns:
        The validated choice
    """
    while True:
        choice = input(prompt).strip()
        
        if not choice and default:
            return default
            
        if choice in valid_choices:
            return choice
            
        print(f"Invalid choice. Please choose from: {', '.join(valid_choices)}")


def print_section_header(title: str, width: int = 80):
    """Print a formatted section header."""
    print("=" * width)
    print(title.center(width))
    print("=" * width)


def print_subsection_header(title: str, width: int = 40):
    """Print a formatted subsection header."""
    print(title)
    print("-" * width)


def print_config_summary():
    """Print a summary of the current configuration."""
    config = get_app_config()
    
    print("📋 CONFIGURATION SUMMARY:")
    print("-" * 40)
    print(f"Application: {config.name} v{config.version}")
    print(f"Environment: {config.environment}")
    print(f"Provider: {config.agent_provider.provider_type.value}")
    print(f"Patterns: {len(config.orchestration_patterns)} available")
    print(f"MCP Servers: {len(config.mcp_servers)} configured")
    print(f"Results Directory: {config.results_directory}")
    print()