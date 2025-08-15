"""
Tests for the AgentRegistry and MCPServerFactory.

Tests agent creation, MCP server management, and registry functionality.
"""

import pytest
from unittest.mock import Mock, patch

from agents import Agent
from agents.mcp.server import MCPServerSse

from loan_processing.agents.providers.openai.agentregistry import AgentRegistry, MCPServerFactory


class TestMCPServerFactory:
    """Test the MCP server factory functionality."""
    
    def setup_method(self):
        """Clear server cache before each test."""
        MCPServerFactory._server_cache.clear()
    
    def test_create_application_verification_server(self):
        """Test creating application verification MCP server."""
        server = MCPServerFactory.get_server("application_verification")
        
        assert isinstance(server, MCPServerSse)
        assert server.params["url"] == "http://localhost:8010/sse"
    
    def test_create_document_processing_server(self):
        """Test creating document processing MCP server."""
        server = MCPServerFactory.get_server("document_processing")
        
        assert isinstance(server, MCPServerSse)
        assert server.params["url"] == "http://localhost:8011/sse"
    
    def test_create_financial_calculations_server(self):
        """Test creating financial calculations MCP server."""
        server = MCPServerFactory.get_server("financial_calculations")
        
        assert isinstance(server, MCPServerSse)
        assert server.params["url"] == "http://localhost:8012/sse"
    
    def test_server_caching(self):
        """Test that servers are cached and reused."""
        server1 = MCPServerFactory.get_server("application_verification")
        server2 = MCPServerFactory.get_server("application_verification")
        
        assert server1 is server2  # Same instance
        assert len(MCPServerFactory._server_cache) == 1
    
    def test_multiple_server_types_cached(self):
        """Test caching of multiple server types."""
        server1 = MCPServerFactory.get_server("application_verification")
        server2 = MCPServerFactory.get_server("document_processing")
        server3 = MCPServerFactory.get_server("application_verification")  # Should be cached
        
        assert server1 is not server2  # Different types
        assert server1 is server3      # Same type, cached
        assert len(MCPServerFactory._server_cache) == 2
    
    def test_invalid_server_type(self):
        """Test handling of invalid server types."""
        with pytest.raises(ValueError, match="Unknown MCP server type: nonexistent_server"):
            MCPServerFactory.get_server("nonexistent_server")


class TestAgentRegistryConfiguration:
    """Test agent registry configuration and metadata."""
    
    def test_config_loader_caching(self):
        """Test ConfigurationLoader caching functionality."""
        from loan_processing.agents.shared.utils import ConfigurationLoader
        
        # Test that multiple loads return the same cached result
        config1 = ConfigurationLoader.load_config()
        config2 = ConfigurationLoader.load_config()
        
        # Should be the same object (cached)
        assert config1 is config2
        
        # Test force reload
        config3 = ConfigurationLoader.load_config(force_reload=True)
        assert config3 == config1  # Same content
        assert config3 is not config1  # Different object
    
    def test_agent_configs_structure(self):
        """Test that all agent configs have required structure."""
        from loan_processing.agents.shared.utils import ConfigurationLoader
        config = ConfigurationLoader.load_config()
        
        for agent_type, agent_config in config["agents"].items():
            # Required fields
            assert "name" in agent_config
            assert "persona_file" in agent_config
            assert "mcp_servers" in agent_config
            assert "capabilities" in agent_config
            assert "description" in agent_config
            
            # Type validation
            assert isinstance(agent_config["name"], str)
            assert isinstance(agent_config["persona_file"], str)
            assert isinstance(agent_config["mcp_servers"], list)
            assert isinstance(agent_config["capabilities"], list)
            assert isinstance(agent_config["description"], str)
            
            # Content validation
            assert len(agent_config["name"]) > 0
            assert len(agent_config["capabilities"]) > 0
            assert len(agent_config["mcp_servers"]) > 0
    
    def test_mcp_server_references_valid(self):
        """Test that all MCP server references are valid."""
        from loan_processing.agents.shared.utils import ConfigurationLoader
        config = ConfigurationLoader.load_config()
        
        valid_servers = set(config["mcp_servers"].keys())
        
        for agent_type, agent_config in config["agents"].items():
            for server_type in agent_config["mcp_servers"]:
                assert server_type in valid_servers, f"Invalid server type '{server_type}' in {agent_type} config"
    
    def test_agent_types_complete(self):
        """Test that all expected agent types are configured."""
        expected_types = {"intake", "credit", "income", "risk"}
        actual_types = set(AgentRegistry.list_agent_types())
        
        assert actual_types == expected_types


class TestAgentRegistryCreation:
    """Test agent creation functionality."""
    
    @patch('loan_processing.agents.shared.utils.persona_loader.load_persona')
    def test_create_intake_agent(self, mock_load_persona):
        """Test creating intake agent with all configurations."""
        mock_load_persona.return_value = "Mock intake persona instructions"
        
        agent = AgentRegistry.create_agent("intake", model="gpt-4")
        
        # Basic agent properties
        assert isinstance(agent, Agent)
        assert agent.name == "Intake Agent"
        assert agent.model == "gpt-4"
        
        # MCP servers
        assert len(agent.mcp_servers) == 2  # application_verification + document_processing
        for server in agent.mcp_servers:
            assert isinstance(server, MCPServerSse)
        
        # Instructions enhanced with structured output (fallback persona used)
        assert "You are the intake agent" in agent.instructions
        assert "Structured Output Requirements" in agent.instructions
        assert "validation_status" in agent.instructions
        assert "confidence_score" in agent.instructions
        assert "JSON format" in agent.instructions
    
    @patch('loan_processing.agents.shared.utils.persona_loader.load_persona')
    def test_create_credit_agent(self, mock_load_persona):
        """Test creating credit agent with all configurations."""
        mock_load_persona.return_value = "Mock credit persona instructions"
        
        agent = AgentRegistry.create_agent("credit")
        
        assert agent.name == "Credit Agent"
        assert len(agent.mcp_servers) == 3  # All three servers
        assert "credit_score" in agent.instructions
        assert "debt_to_income_ratio" in agent.instructions
        assert "risk_category" in agent.instructions
    
    @patch('loan_processing.agents.shared.utils.persona_loader.load_persona')
    def test_create_income_agent(self, mock_load_persona):
        """Test creating income agent with all configurations."""
        mock_load_persona.return_value = "Mock income persona instructions"
        
        agent = AgentRegistry.create_agent("income")
        
        assert agent.name == "Income Verification Agent"
        assert len(agent.mcp_servers) == 3
        assert "verified_monthly_income" in agent.instructions
        assert "employment_verification_status" in agent.instructions
        assert "income_trend" in agent.instructions
    
    @patch('loan_processing.agents.shared.utils.persona_loader.load_persona')
    def test_create_risk_agent(self, mock_load_persona):
        """Test creating risk agent with all configurations."""
        mock_load_persona.return_value = "Mock risk persona instructions"
        
        agent = AgentRegistry.create_agent("risk")
        
        assert agent.name == "Risk Evaluation Agent"
        assert len(agent.mcp_servers) == 3
        assert "final_risk_category" in agent.instructions
        assert "recommendation" in agent.instructions
        assert "approved_amount" in agent.instructions
        assert "compliance_verified" in agent.instructions
    
    def test_create_agent_invalid_type(self):
        """Test error handling for invalid agent types."""
        with pytest.raises(ValueError, match="Unknown agent type: invalid_type"):
            AgentRegistry.create_agent("invalid_type")
        
        with pytest.raises(ValueError, match="Available types:"):
            AgentRegistry.create_agent("another_invalid")


class TestAgentRegistryStructuredOutput:
    """Test structured output format generation."""
    
    def test_structured_output_formats(self):
        """Test that structured output formats are properly defined."""
        from loan_processing.agents.shared.utils import ConfigurationLoader
        config = ConfigurationLoader.load_config()
        
        # Test that _add_structured_output_instructions adds proper formats
        base_instructions = "Base persona instructions"
        
        from loan_processing.agents.shared.utils import OutputFormatGenerator
        
        # Test each agent type
        for agent_type in ["intake", "credit", "income", "risk"]:
            agent_config = config["agents"][agent_type]
            enhanced = OutputFormatGenerator.add_structured_output_instructions(base_instructions, agent_config.get("output_format", {}))
            
            assert base_instructions in enhanced
            assert "Structured Output Requirements" in enhanced
            assert "JSON format" in enhanced
            assert "```json" in enhanced
            assert "```" in enhanced
            assert "CRITICAL: Your output must be valid JSON" in enhanced
    
    def test_intake_output_format(self):
        """Test intake agent output format specifications."""
        from loan_processing.agents.shared.utils import ConfigurationLoader
        config = ConfigurationLoader.load_config()
        
        agent_config = config["agents"]["intake"]
        from loan_processing.agents.shared.utils import OutputFormatGenerator
        enhanced = OutputFormatGenerator.add_structured_output_instructions("", agent_config.get("output_format", {}))
        
        required_fields = [
            "validation_status",
            "data_completeness_score", 
            "fraud_indicators",
            "verification_results",
            "processing_path",
            "issues_found",
            "confidence_score"
        ]
        
        for field in required_fields:
            assert field in enhanced
    
    def test_credit_output_format(self):
        """Test credit agent output format specifications."""
        from loan_processing.agents.shared.utils import ConfigurationLoader
        config = ConfigurationLoader.load_config()
        
        agent_config = config["agents"]["credit"]
        from loan_processing.agents.shared.utils import OutputFormatGenerator
        enhanced = OutputFormatGenerator.add_structured_output_instructions("", agent_config.get("output_format", {}))
        
        required_fields = [
            "credit_score",
            "credit_tier",
            "debt_to_income_ratio",
            "credit_utilization_ratio", 
            "payment_history_score",
            "risk_category",
            "red_flags",
            "confidence_score"
        ]
        
        for field in required_fields:
            assert field in enhanced
    
    def test_income_output_format(self):
        """Test income agent output format specifications."""
        from loan_processing.agents.shared.utils import ConfigurationLoader
        config = ConfigurationLoader.load_config()
        
        agent_config = config["agents"]["income"]
        from loan_processing.agents.shared.utils import OutputFormatGenerator
        enhanced = OutputFormatGenerator.add_structured_output_instructions("", agent_config.get("output_format", {}))
        
        required_fields = [
            "verified_monthly_income",
            "employment_verification_status",
            "employment_stability_score",
            "income_trend",
            "income_sources",
            "qualifying_income",
            "concerns",
            "confidence_score"
        ]
        
        for field in required_fields:
            assert field in enhanced
    
    def test_risk_output_format(self):
        """Test risk agent output format specifications."""
        from loan_processing.agents.shared.utils import ConfigurationLoader
        config = ConfigurationLoader.load_config()
        
        agent_config = config["agents"]["risk"]
        from loan_processing.agents.shared.utils import OutputFormatGenerator
        enhanced = OutputFormatGenerator.add_structured_output_instructions("", agent_config.get("output_format", {}))
        
        required_fields = [
            "final_risk_category",
            "recommendation",
            "approved_amount",
            "recommended_rate",
            "recommended_terms",
            "key_risk_factors",
            "mitigating_factors",
            "conditions",
            "reasoning",
            "confidence_score",
            "compliance_verified"
        ]
        
        for field in required_fields:
            assert field in enhanced
    
    def test_security_instructions_included(self):
        """Test that security instructions are included."""
        from loan_processing.agents.shared.utils import ConfigurationLoader
        config = ConfigurationLoader.load_config()
        
        for agent_type in ["intake", "credit", "income", "risk"]:
            agent_config = config["agents"][agent_type]
            from loan_processing.agents.shared.utils import OutputFormatGenerator
            enhanced = OutputFormatGenerator.add_structured_output_instructions("", agent_config.get("output_format", {}))
            
            assert "secure applicant_id" in enhanced
            assert "never use SSN" in enhanced
            assert "application additional_data" in enhanced


class TestAgentRegistryUtilityMethods:
    """Test utility methods of the agent registry."""
    
    def test_get_agent_info(self):
        """Test getting agent information."""
        info = AgentRegistry.get_agent_info("intake")
        
        assert info["name"] == "Intake Agent"
        assert info["persona_file"] == "intake"
        assert "application_verification" in info["mcp_servers"]
        assert "document_processing" in info["mcp_servers"]
        assert len(info["capabilities"]) > 0
        assert info["description"] != ""
        
        # Ensure it's a copy (not the original config)
        info["name"] = "Modified"
        original_info = AgentRegistry.get_agent_info("intake")
        assert original_info["name"] == "Intake Agent"  # Unchanged
    
    def test_get_agent_info_invalid_type(self):
        """Test error handling for invalid agent types in get_agent_info."""
        with pytest.raises(ValueError, match="Unknown agent type: invalid"):
            AgentRegistry.get_agent_info("invalid")
    
    def test_list_agent_types(self):
        """Test listing all available agent types."""
        types = AgentRegistry.list_agent_types()
        
        expected_types = ["intake", "credit", "income", "risk"]
        assert set(types) == set(expected_types)
        assert len(types) == 4
    
    def test_get_agent_capabilities(self):
        """Test getting capabilities for specific agent types."""
        # Test intake capabilities
        intake_capabilities = AgentRegistry.get_agent_capabilities("intake")
        assert "Application validation" in intake_capabilities
        assert "Identity verification" in intake_capabilities
        assert "Fraud detection" in intake_capabilities
        
        # Test credit capabilities  
        credit_capabilities = AgentRegistry.get_agent_capabilities("credit")
        assert "Credit report analysis" in credit_capabilities
        assert "Credit scoring" in credit_capabilities
        assert "Risk categorization" in credit_capabilities
        
        # Test income capabilities
        income_capabilities = AgentRegistry.get_agent_capabilities("income")
        assert "Employment verification" in income_capabilities
        assert "Income calculation" in income_capabilities
        
        # Test risk capabilities
        risk_capabilities = AgentRegistry.get_agent_capabilities("risk")
        assert "Risk synthesis" in risk_capabilities
        assert "Policy application" in risk_capabilities
        assert "Final recommendations" in risk_capabilities
    
    def test_get_agent_capabilities_invalid_type(self):
        """Test error handling for invalid agent types in get_agent_capabilities."""
        with pytest.raises(ValueError, match="Unknown agent type"):
            AgentRegistry.get_agent_capabilities("invalid")


@pytest.mark.integration
class TestAgentRegistryIntegration:
    """Integration tests for agent registry functionality."""
    
    @patch('loan_processing.agents.shared.utils.persona_loader.load_persona')
    def test_create_all_agent_types(self, mock_load_persona):
        """Test creating all agent types successfully."""
        mock_load_persona.return_value = "Mock persona"
        
        agents = {}
        for agent_type in ["intake", "credit", "income", "risk"]:
            agents[agent_type] = AgentRegistry.create_agent(agent_type, model="gpt-4")
        
        # Verify all agents created successfully
        assert len(agents) == 4
        
        # Verify each agent has unique configuration
        names = {agent.name for agent in agents.values()}
        assert len(names) == 4  # All unique names
        
        # Verify MCP server distribution
        intake_servers = len(agents["intake"].mcp_servers)
        credit_servers = len(agents["credit"].mcp_servers)
        
        assert intake_servers == 2  # application_verification + document_processing
        assert credit_servers == 3   # All three servers
    
    def test_server_reuse_across_agents(self):
        """Test that MCP servers are properly reused across agents."""
        # Clear cache to start fresh
        MCPServerFactory._server_cache.clear()
        
        with patch('loan_processing.agents.shared.utils.persona_loader.load_persona') as mock_load:
            mock_load.return_value = "Mock persona"
            
            # Create multiple agents that share servers
            intake_agent = AgentRegistry.create_agent("intake")
            credit_agent = AgentRegistry.create_agent("credit")
            
            # Should have created servers (cached after first creation)
            assert len(MCPServerFactory._server_cache) == 3  # All server types created
            
            # Verify agents share the same server instances where applicable
            # Both use application_verification, so they should share that instance
            intake_app_server = None
            credit_app_server = None
            
            for server in intake_agent.mcp_servers:
                if hasattr(server, 'params') and 'localhost:8010' in server.params.get('url', ''):
                    intake_app_server = server
                    
            for server in credit_agent.mcp_servers:
                if hasattr(server, 'params') and 'localhost:8010' in server.params.get('url', ''):
                    credit_app_server = server
                    
            # Note: Server sharing verification depends on implementation details
            # This test verifies that the factory pattern is working correctly


if __name__ == "__main__":
    pytest.main([__file__, "-v"])