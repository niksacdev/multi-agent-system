"""Pytest configuration and shared fixtures."""

import sys
from unittest.mock import MagicMock

# Mock the OpenAI Agents SDK to avoid import conflicts with local agents module
# Our project has loan_processing/agents/ which conflicts with the SDK's agents package

# Create mock modules before any test imports
mock_agents = MagicMock()
mock_agents_mcp = MagicMock()
mock_agents_mcp_server = MagicMock()

# Create mock classes with minimal attributes needed for tests
class MockAgent:
    """Mock Agent class from OpenAI SDK."""
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name", "Mock Agent")
        self.model = kwargs.get("model", "gpt-4")
        self.tools = kwargs.get("tools", [])
        self.mcp_servers = kwargs.get("mcp_servers", [])

class MockMCPServerSse:
    """Mock MCPServerSse class from OpenAI SDK."""
    def __init__(self, **params):
        self.params = params if params else {"url": "http://localhost:8010/sse"}

# Inject mocks into sys.modules before any imports
sys.modules["agents"] = mock_agents
sys.modules["agents.mcp"] = mock_agents_mcp
sys.modules["agents.mcp.server"] = mock_agents_mcp_server

# Attach classes to mocked modules
mock_agents.Agent = MockAgent
mock_agents_mcp_server.MCPServerSse = MockMCPServerSse
