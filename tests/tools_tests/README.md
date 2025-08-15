# MCP Servers Test Suite

This directory contains comprehensive tests for the Multi-Agent System's MCP (Model Context Protocol) servers.

## Overview

The test suite covers three main MCP servers:

1. **Application Verification MCP Server** (Port 8010)
   - Mock implementation with realistic data simulation
   - Tests credit reports, employment verification, bank data, tax transcripts, and asset verification

2. **Document Processing MCP Server** (Port 8011)
   - MCP client-based implementation 
   - Tests text extraction, document classification, format validation, structured data extraction, and format conversion

3. **Financial Calculations MCP Server** (Port 8012)
   - Business logic implementation with realistic calculations
   - Tests DTI ratios, loan affordability, payment calculations, credit utilization, and debt service ratios

## Test Structure

```
tests/
├── mcp_servers/
│   ├── __init__.py
│   ├── test_integration.py          # Cross-server integration tests
│   ├── test_utils.py               # Common test utilities and fixtures
│   ├── application_verification/
│   │   ├── __init__.py
│   │   └── test_server.py          # Application verification tests
│   ├── document_processing/
│   │   ├── __init__.py
│   │   └── test_server.py          # Document processing tests
│   └── financial_calculations/
│       ├── __init__.py
│       └── test_server.py          # Financial calculations tests
```

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type server

# Run with verbose output and HTML coverage report
python run_tests.py -v --html
```

### Using pytest directly

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run all MCP server tests
pytest tests/mcp_servers/ -v

# Run with coverage
pytest tests/mcp_servers/ --cov=mcp_servers --cov-report=html

# Run specific test file
pytest tests/mcp_servers/application_verification/test_server.py -v

# Run integration tests only
pytest tests/mcp_servers/test_integration.py -v

# Run tests matching a pattern
pytest tests/mcp_servers/ -k "credit_report" -v
```

## Test Categories

### Unit Tests
- Test individual service implementations
- Test MCP server tool wrappers
- Test edge cases and error handling
- Test mathematical calculations and business logic

### Integration Tests
- Test complete loan application workflows
- Test cross-server data consistency
- Test error handling across services
- Test realistic business scenarios

### Edge Case Tests
- Test boundary conditions
- Test invalid inputs
- Test error recovery
- Test performance with extreme values

## Key Test Features

- **Comprehensive Coverage**: 90%+ code coverage requirement
- **Mock Services**: Realistic mock implementations with controlled randomization
- **Integration Testing**: End-to-end workflow validation
- **Edge Case Testing**: Boundary conditions and error scenarios
- **Performance Testing**: Response time and resource usage validation
