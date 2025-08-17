"""
Tests for orchestration pattern configurations.

Tests YAML pattern files, validation, and configuration structure.
"""

from pathlib import Path

import pytest
import yaml

from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationEngine


class TestPatternFileStructure:
    """Test the structure and validity of pattern configuration files."""

    def setup_method(self):
        """Setup test environment."""
        self.patterns_dir = Path("loan_processing/agents/shared/config")
        self.expected_patterns = ["sequential", "parallel"]

    def test_pattern_files_exist(self):
        """Test that expected pattern files exist."""
        for pattern_name in self.expected_patterns:
            pattern_file = self.patterns_dir / f"{pattern_name}.yaml"
            assert pattern_file.exists(), f"Pattern file {pattern_file} not found"

    def test_pattern_files_valid_yaml(self):
        """Test that all pattern files contain valid YAML."""
        for pattern_name in self.expected_patterns:
            pattern_file = self.patterns_dir / f"{pattern_name}.yaml"

            with open(pattern_file) as f:
                try:
                    config = yaml.safe_load(f)
                    assert config is not None
                    assert isinstance(config, dict)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {pattern_file}: {e}")

    def test_pattern_required_fields(self):
        """Test that all patterns have required top-level fields."""
        required_fields = ["name", "description", "pattern_type", "version", "agents"]

        for pattern_name in self.expected_patterns:
            pattern_file = self.patterns_dir / f"{pattern_name}.yaml"

            with open(pattern_file) as f:
                config = yaml.safe_load(f)

            for field in required_fields:
                assert field in config, f"Missing required field '{field}' in {pattern_file}"
                assert config[field], f"Empty required field '{field}' in {pattern_file}"


class TestSequentialPatternConfiguration:
    """Test the sequential pattern configuration."""

    @pytest.fixture
    def sequential_config(self):
        """Load sequential pattern configuration."""
        pattern_file = Path("loan_processing/agents/shared/config/sequential.yaml")
        with open(pattern_file) as f:
            return yaml.safe_load(f)

    def test_sequential_metadata(self, sequential_config):
        """Test sequential pattern metadata."""
        assert sequential_config["name"] == "sequential_loan_processing"
        assert sequential_config["pattern_type"] == "sequential"
        assert sequential_config["version"] == "1.0.0"
        assert "sequential processing" in sequential_config["description"].lower()

    def test_sequential_agents_configuration(self, sequential_config):
        """Test sequential agents configuration."""
        agents = sequential_config["agents"]
        assert len(agents) == 4  # intake, credit, income, risk

        # Verify agent order and types
        expected_order = ["intake", "credit", "income", "risk"]
        actual_order = [agent["type"] for agent in agents]
        assert actual_order == expected_order

        # Verify each agent has required fields
        for i, agent in enumerate(agents):
            assert "type" in agent
            assert "name" in agent
            assert "required" in agent
            assert "timeout_seconds" in agent
            assert "description" in agent
            assert "success_conditions" in agent

            # All agents should be required
            assert agent["required"] is True

            # Verify dependency chain (except first agent)
            if i > 0:
                assert "depends_on" in agent
                assert expected_order[i - 1] in agent["depends_on"]

    def test_sequential_handoff_rules(self, sequential_config):
        """Test sequential handoff rules."""
        handoff_rules = sequential_config["handoff_rules"]
        assert len(handoff_rules) == 3  # intake->credit, credit->income, income->risk

        expected_handoffs = [("intake", "credit"), ("credit", "income"), ("income", "risk")]

        for i, rule in enumerate(handoff_rules):
            expected_from, expected_to = expected_handoffs[i]

            assert rule["from"] == expected_from
            assert rule["to"] == expected_to
            assert "conditions" in rule
            assert "context_fields" in rule
            assert "failure_action" in rule

            # Verify conditions are not empty
            assert len(rule["conditions"]) > 0
            assert len(rule["context_fields"]) > 0

    def test_sequential_decision_matrix(self, sequential_config):
        """Test sequential decision matrix configuration."""
        decision_matrix = sequential_config["decision_matrix"]

        # Required decision types
        required_decisions = ["auto_approve", "conditional_approval", "manual_review", "auto_deny"]
        for decision_type in required_decisions:
            assert decision_type in decision_matrix

            decision_config = decision_matrix[decision_type]
            assert "description" in decision_config
            assert "conditions" in decision_config
            assert len(decision_config["conditions"]) > 0

    def test_sequential_monitoring_config(self, sequential_config):
        """Test sequential monitoring configuration."""
        monitoring = sequential_config["monitoring"]

        assert "track_metrics" in monitoring
        assert "audit_points" in monitoring

        # Verify metrics are specified
        metrics = monitoring["track_metrics"]
        assert "processing_duration_by_agent" in metrics
        assert "success_rate_by_agent" in metrics


class TestParallelPatternConfiguration:
    """Test the parallel pattern configuration."""

    @pytest.fixture
    def parallel_config(self):
        """Load parallel pattern configuration."""
        pattern_file = Path("loan_processing/agents/shared/config/parallel.yaml")
        with open(pattern_file) as f:
            return yaml.safe_load(f)

    def test_parallel_metadata(self, parallel_config):
        """Test parallel pattern metadata."""
        assert parallel_config["name"] == "parallel_loan_processing"
        assert parallel_config["pattern_type"] == "parallel"
        assert parallel_config["version"] == "1.0.0"
        assert "parallel processing" in parallel_config["description"].lower()

    def test_parallel_agents_configuration(self, parallel_config):
        """Test parallel initial agents configuration."""
        agents = parallel_config["agents"]

        # Should only have initial stage agents (intake)
        initial_agents = [agent for agent in agents if agent.get("execution_stage") == "initial"]
        assert len(initial_agents) == 1
        assert initial_agents[0]["type"] == "intake"

    def test_parallel_branches_configuration(self, parallel_config):
        """Test parallel branches configuration."""
        parallel_branches = parallel_config["parallel_branches"]
        assert len(parallel_branches) == 2  # credit_branch, income_branch

        # Verify branch structure
        branch_names = [branch["branch_name"] for branch in parallel_branches]
        assert "credit_branch" in branch_names
        assert "income_branch" in branch_names

        for branch in parallel_branches:
            assert "branch_name" in branch
            assert "agents" in branch
            assert len(branch["agents"]) == 1  # One agent per branch

            agent = branch["agents"][0]
            assert "type" in agent
            assert "depends_on" in agent
            assert "intake" in agent["depends_on"]  # Both depend on intake

    def test_parallel_synthesis_agents(self, parallel_config):
        """Test parallel synthesis agents configuration."""
        synthesis_agents = parallel_config["synthesis_agents"]
        assert len(synthesis_agents) == 1  # risk agent

        risk_agent = synthesis_agents[0]
        assert risk_agent["type"] == "risk"
        assert "depends_on" in risk_agent
        assert "credit" in risk_agent["depends_on"]
        assert "income" in risk_agent["depends_on"]

    def test_parallel_synchronization_config(self, parallel_config):
        """Test parallel synchronization configuration."""
        sync_config = parallel_config["synchronization"]

        assert "wait_for_all_branches" in sync_config
        assert "branch_timeout_seconds" in sync_config
        assert "partial_completion_threshold" in sync_config
        assert "failure_handling" in sync_config

        # Verify specific settings
        assert isinstance(sync_config["wait_for_all_branches"], bool)
        assert isinstance(sync_config["branch_timeout_seconds"], int)
        assert isinstance(sync_config["partial_completion_threshold"], float)
        assert 0.0 <= sync_config["partial_completion_threshold"] <= 1.0

    def test_parallel_performance_config(self, parallel_config):
        """Test parallel performance configuration."""
        performance = parallel_config["performance"]

        assert "target_processing_time" in performance
        assert "branch_optimization" in performance
        assert "caching" in performance
        assert "resource_limits" in performance

        # Verify caching configuration
        caching = performance["caching"]
        assert "enabled" in caching
        assert "cache_duration" in caching
        assert "cache_keys" in caching


class TestPatternConsistency:
    """Test consistency between different patterns."""

    @pytest.fixture
    def all_configs(self):
        """Load all pattern configurations."""
        configs = {}
        patterns_dir = Path("loan_processing/orchestration/patterns")

        for pattern_file in patterns_dir.glob("*.yaml"):
            with open(pattern_file) as f:
                configs[pattern_file.stem] = yaml.safe_load(f)

        return configs

    def test_agent_types_consistency(self, all_configs):
        """Test that all patterns use the same agent types."""
        expected_agent_types = {"intake", "credit", "income", "risk"}

        for pattern_name, config in all_configs.items():
            # Collect agent types from all sections
            agent_types = set()

            # From agents section
            for agent in config.get("agents", []):
                agent_types.add(agent["type"])

            # From parallel branches (if present)
            for branch in config.get("parallel_branches", []):
                for agent in branch.get("agents", []):
                    agent_types.add(agent["type"])

            # From synthesis agents (if present)
            for agent in config.get("synthesis_agents", []):
                agent_types.add(agent["type"])

            assert agent_types == expected_agent_types, f"Inconsistent agent types in {pattern_name}"

    def test_timeout_values_reasonable(self, all_configs):
        """Test that timeout values are reasonable."""
        min_timeout = 30  # 30 seconds minimum
        max_timeout = 600  # 10 minutes maximum

        for pattern_name, config in all_configs.items():
            # Check all agent timeout configurations
            all_agents = []
            all_agents.extend(config.get("agents", []))

            for branch in config.get("parallel_branches", []):
                all_agents.extend(branch.get("agents", []))

            all_agents.extend(config.get("synthesis_agents", []))

            for agent in all_agents:
                if "timeout_seconds" in agent:
                    timeout = agent["timeout_seconds"]
                    assert min_timeout <= timeout <= max_timeout, (
                        f"Unreasonable timeout {timeout}s for {agent['type']} in {pattern_name}"
                    )

    def test_decision_matrix_consistency(self, all_configs):
        """Test that decision matrices are consistent across patterns."""
        required_decision_types = {"auto_approve", "conditional_approval", "manual_review", "auto_deny"}

        for pattern_name, config in all_configs.items():
            decision_matrix = config.get("decision_matrix", {})

            # All patterns should have all decision types
            actual_types = set(decision_matrix.keys())
            assert required_decision_types.issubset(actual_types), (
                f"Missing decision types in {pattern_name}: {required_decision_types - actual_types}"
            )


class TestPatternValidation:
    """Test pattern validation logic."""

    def test_orchestration_engine_loads_patterns(self):
        """Test that OrchestrationEngine can load all patterns."""
        engine = OrchestrationEngine()

        # Test loading sequential pattern
        sequential_config = engine._load_pattern("sequential")
        assert sequential_config["pattern_type"] == "sequential"

        # Test loading parallel pattern
        parallel_config = engine._load_pattern("parallel")
        assert parallel_config["pattern_type"] == "parallel"

    def test_pattern_caching(self):
        """Test that patterns are cached after first load."""
        engine = OrchestrationEngine()

        # Load pattern twice
        config1 = engine._load_pattern("sequential")
        config2 = engine._load_pattern("sequential")

        # Should be the same object (cached)
        assert config1 is config2

        # Cache should contain the pattern
        assert "sequential" in engine._pattern_cache

    def test_invalid_pattern_handling(self):
        """Test handling of invalid pattern names."""
        engine = OrchestrationEngine()

        with pytest.raises(FileNotFoundError):
            engine._load_pattern("nonexistent_pattern")

    def test_agent_success_conditions_valid(self):
        """Test that agent success conditions are valid."""
        engine = OrchestrationEngine()

        for pattern_name in ["sequential", "parallel"]:
            config = engine._load_pattern(pattern_name)

            # Check all agents in the pattern
            all_agents = []
            all_agents.extend(config.get("agents", []))

            for branch in config.get("parallel_branches", []):
                all_agents.extend(branch.get("agents", []))

            all_agents.extend(config.get("synthesis_agents", []))

            for agent in all_agents:
                success_conditions = agent.get("success_conditions", [])

                # Each condition should be a non-empty string
                for condition in success_conditions:
                    assert isinstance(condition, str)
                    assert len(condition.strip()) > 0

                    # Basic syntax validation (should contain comparison operators)
                    valid_operators = ["==", "!=", ">=", "<=", ">", "<", "in", "not in"]
                    has_operator = any(op in condition for op in valid_operators)
                    assert has_operator, f"Invalid condition syntax: {condition}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
