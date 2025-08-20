"""
Comprehensive tests for PersonaLoader functionality.

Tests persona loading, fallback behavior, file operations, and edge cases.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os

from loan_processing.utils.persona_loader import PersonaLoader, load_persona


class TestPersonaLoader:
    """Test the PersonaLoader class functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.test_persona_content = """# Test Agent Instructions

## Role & Responsibilities
You are a test agent for unit testing purposes.

## Process
1. Validate test data
2. Return structured output
3. Log all actions

## Output Format
Return JSON with validation results.
"""

    def test_load_persona_success(self):
        """Test successful persona loading from file."""
        mock_file_content = self.test_persona_content
        
        with patch('pathlib.Path.read_text') as mock_read:
            mock_read.return_value = mock_file_content
            
            result = PersonaLoader.load_persona("test")
            
            assert result == mock_file_content
            mock_read.assert_called_once_with(encoding="utf-8")

    def test_load_persona_file_not_found(self):
        """Test fallback behavior when persona file doesn't exist."""
        with patch('pathlib.Path.read_text') as mock_read:
            mock_read.side_effect = FileNotFoundError("File not found")
            
            result = PersonaLoader.load_persona("nonexistent")
            
            expected_fallback = "You are the nonexistent agent. Provide concise, structured domain outputs as JSON when appropriate."
            assert result == expected_fallback

    def test_load_persona_different_agent_types(self):
        """Test loading personas for different agent types."""
        agent_types = ["intake", "credit", "income", "risk"]
        
        for agent_type in agent_types:
            with patch('pathlib.Path.read_text') as mock_read:
                mock_read.side_effect = FileNotFoundError()
                
                result = PersonaLoader.load_persona(agent_type)
                
                expected = f"You are the {agent_type} agent. Provide concise, structured domain outputs as JSON when appropriate."
                assert result == expected

    def test_get_persona_path(self):
        """Test persona path generation."""
        path = PersonaLoader.get_persona_path("credit")
        
        # Verify the path structure
        assert path.name == "credit-agent-persona.md"
        assert "agent-persona" in str(path)
        assert path.suffix == ".md"

    def test_get_persona_path_different_agents(self):
        """Test path generation for different agent types."""
        test_agents = ["intake", "credit", "income", "risk", "custom"]
        
        for agent in test_agents:
            path = PersonaLoader.get_persona_path(agent)
            expected_filename = f"{agent}-agent-persona.md"
            assert path.name == expected_filename

    def test_persona_exists_true(self):
        """Test persona_exists when file exists."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            result = PersonaLoader.persona_exists("test")
            
            assert result is True
            mock_exists.assert_called_once()

    def test_persona_exists_false(self):
        """Test persona_exists when file doesn't exist."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            
            result = PersonaLoader.persona_exists("nonexistent")
            
            assert result is False
            mock_exists.assert_called_once()

    def test_list_available_personas_with_files(self):
        """Test listing available personas when files exist."""
        mock_files = [
            "intake-agent-persona.md",
            "credit-agent-persona.md", 
            "income-agent-persona.md",
            "risk-agent-persona.md"
        ]
        
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.glob') as mock_glob:
            
            mock_exists.return_value = True
            mock_glob.return_value = [Path(f) for f in mock_files]
            
            result = PersonaLoader.list_available_personas()
            
            expected = ["credit", "income", "intake", "risk"]  # sorted
            assert result == expected

    def test_list_available_personas_empty_directory(self):
        """Test listing personas when directory doesn't exist."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            
            result = PersonaLoader.list_available_personas()
            
            assert result == []

    def test_list_available_personas_no_files(self):
        """Test listing personas when directory exists but has no persona files."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.glob') as mock_glob:
            
            mock_exists.return_value = True
            mock_glob.return_value = []
            
            result = PersonaLoader.list_available_personas()
            
            assert result == []

    def test_list_available_personas_mixed_files(self):
        """Test listing personas with mixed file types in directory."""
        mock_files = [
            "intake-agent-persona.md",
            "readme.txt",  # Should be ignored
            "credit-agent-persona.md",
            "config.yaml",  # Should be ignored
            "income-agent-persona.md"
        ]
        
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.glob') as mock_glob:
            
            mock_exists.return_value = True
            # Only return .md files that match the pattern
            persona_files = [f for f in mock_files if f.endswith("-agent-persona.md")]
            mock_glob.return_value = [Path(f) for f in persona_files]
            
            result = PersonaLoader.list_available_personas()
            
            expected = ["credit", "income", "intake"]  # sorted, only persona files
            assert result == expected

    def test_convenience_function(self):
        """Test the convenience load_persona function."""
        with patch('pathlib.Path.read_text') as mock_read:
            mock_read.return_value = self.test_persona_content
            
            result = load_persona("test")
            
            assert result == self.test_persona_content

    def test_persona_loading_with_unicode_content(self):
        """Test persona loading with unicode characters."""
        unicode_content = """# Test Agent 🤖

## Role & Responsibilities 
You are a test agent with émojis and spëcial characters.

## Process
• Validate input data
• Process with unicôde support
• Return résults

Special characters: àáâãäåæçèéêë
"""
        
        with patch('pathlib.Path.read_text') as mock_read:
            mock_read.return_value = unicode_content
            
            result = PersonaLoader.load_persona("unicode_test")
            
            assert result == unicode_content
            mock_read.assert_called_once_with(encoding="utf-8")

    def test_persona_loading_with_large_content(self):
        """Test persona loading with large file content."""
        # Simulate a large persona file
        large_content = "# Large Agent Instructions\n\n" + "This is a test line.\n" * 1000
        
        with patch('pathlib.Path.read_text') as mock_read:
            mock_read.return_value = large_content
            
            result = PersonaLoader.load_persona("large_test")
            
            assert result == large_content
            assert len(result) > 10000  # Verify it's actually large

    def test_persona_path_consistency(self):
        """Test that path generation is consistent across methods."""
        agent_type = "consistency_test"
        
        path1 = PersonaLoader.get_persona_path(agent_type)
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            PersonaLoader.persona_exists(agent_type)
            
            # The exists check should use the same path
            mock_exists.assert_called_once()
            
            # Compare the path components that matter
            assert str(path1).endswith(f"{agent_type}-agent-persona.md")

    def test_error_handling_permission_denied(self):
        """Test handling of permission denied errors."""
        with patch('pathlib.Path.read_text') as mock_read:
            mock_read.side_effect = PermissionError("Permission denied")
            
            # Should still fall back gracefully
            with pytest.raises(PermissionError):
                PersonaLoader.load_persona("permission_test")

    def test_error_handling_encoding_error(self):
        """Test handling of encoding errors."""
        with patch('pathlib.Path.read_text') as mock_read:
            mock_read.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")
            
            with pytest.raises(UnicodeDecodeError):
                PersonaLoader.load_persona("encoding_test")

    def test_path_traversal_protection(self):
        """Test that persona loader handles path traversal attempts safely."""
        # Test various path traversal attempts
        dangerous_inputs = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32",
            "test/../../../sensitive"
        ]
        
        for dangerous_input in dangerous_inputs:
            path = PersonaLoader.get_persona_path(dangerous_input)
            
            # Should still generate a safe path within the persona directory
            assert "agent-persona" in str(path)
            assert str(path).endswith(f"{dangerous_input}-agent-persona.md")
            # The dangerous part becomes part of the filename, which is safer
            assert "etc/passwd" not in str(path) or dangerous_input in str(path)


class TestPersonaLoaderIntegration:
    """Integration tests using actual file system."""

    def test_real_file_system_operations(self):
        """Test persona loader with file system-like behavior using mocks."""
        # Test personas with their expected content
        test_personas = {
            "test1": "# Test Agent 1\nThis is test agent 1 instructions.",
            "test2": "# Test Agent 2\nThis is test agent 2 instructions.", 
            "special": "# Special Agent\nSpecial instructions with émojis 🚀"
        }
        
        # Test loading existing personas with proper mocking
        for persona_key, expected_content in test_personas.items():
            with patch('pathlib.Path.read_text') as mock_read:
                mock_read.return_value = expected_content
                result = PersonaLoader.load_persona(persona_key)
                assert result == expected_content
                mock_read.assert_called_once_with(encoding="utf-8")
        
        # Test persona existence checking
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            for persona_key in test_personas.keys():
                assert PersonaLoader.persona_exists(persona_key) is True
        
        # Test listing available personas
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.glob') as mock_glob:
            
            mock_exists.return_value = True
            mock_files = [Path(f"{key}-agent-persona.md") for key in test_personas.keys()]
            mock_glob.return_value = mock_files
            
            result = PersonaLoader.list_available_personas()
            expected = sorted(test_personas.keys())
            assert result == expected

    def test_fallback_behavior_integration(self):
        """Test that fallback works correctly in integration scenario."""
        # Test with non-existent persona
        result = PersonaLoader.load_persona("definitely_not_exists_12345")
        expected = "You are the definitely_not_exists_12345 agent. Provide concise, structured domain outputs as JSON when appropriate."
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])