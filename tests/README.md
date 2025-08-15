# MCP Servers Test Suite

This directory contains comprehensive tests for the MCP (Model Context Protocol) servers used in the loan processing multi-agent system.

## Test Structure

```
tests/
├── mcp_servers/
│   ├── application_verification/
│   │   └── test_server.py          # Tests for application verification MCP server
│   ├── document_processing/
│   │   └── test_server.py          # Tests for document processing MCP server
│   ├── financial_calculations/
│   │   └── test_server.py          # Tests for financial calculations MCP server
│   ├── test_integration.py         # Integration tests across all servers
│   └── test_utils.py               # Test utilities and fixtures
├── __init__.py
└── README.md                       # This file
```

## MCP Servers Overview

The loan processing system uses three MCP servers:

### 1. Application Verification MCP Server (Port 8010)
- **Service**: `ApplicationVerificationServiceImpl`
- **Purpose**: Mock implementation for external data verification
- **Tools**:
  - `retrieve_credit_report`: Get credit bureau data
  - `verify_employment`: Verify employment status and income
  - `get_bank_account_data`: Retrieve bank account information
  - `get_tax_transcript_data`: Get tax transcript data
  - `verify_asset_information`: Verify asset ownership and value

### 2. Document Processing MCP Server (Port 8011)
- **Service**: `MCPDocumentProcessingService`
- **Purpose**: MCP client-based implementation for document analysis
- **Tools**:
  - `extract_text_from_document`: OCR text extraction
  - `classify_document_type`: Document type classification
  - `validate_document_format`: Format validation
  - `extract_structured_data`: Structured data extraction
  - `convert_document_format`: Document format conversion

### 3. Financial Calculations MCP Server (Port 8012)
- **Service**: `FinancialCalculationsServiceImpl`
- **Purpose**: Mathematical calculations and financial analysis
- **Tools**:
  - `calculate_debt_to_income_ratio`: DTI ratio calculation
  - `calculate_loan_affordability`: Loan affordability assessment
  - `calculate_monthly_payment`: Monthly payment calculation
  - `calculate_credit_utilization_ratio`: Credit utilization analysis
  - `calculate_total_debt_service_ratio`: Total debt service ratio

## Running Tests

### Prerequisites

Install test dependencies:
```bash
uv add pytest pytest-cov pytest-asyncio
```

### Quick Start

Run all tests:
```bash
python run_tests.py
```

Or use pytest directly:
```bash
pytest tests/mcp_servers/ -v
```

### Test Categories

**Unit Tests**: Test individual components in isolation
```bash
python run_tests.py --type unit
```

**Integration Tests**: Test interactions between MCP servers
```bash
python run_tests.py --type integration
```

**Server Tests**: Test MCP server tools and service implementations
```bash
python run_tests.py --type server
```

### Coverage Reporting

Generate coverage report:
```bash
python run_tests.py --html
```

This creates an HTML coverage report in `htmlcov/index.html`.

### Test Options

```bash
python run_tests.py --help
```

Available options:
- `--type {all,unit,integration,server}`: Test type to run
- `-v, --verbose`: Enable verbose output
- `--no-coverage`: Disable coverage reporting
- `--html`: Generate HTML coverage report
- `--quick`: Run quick tests only

## Test Design Principles

### 1. Service Layer Testing
Each MCP server has two main components tested:
- **Service Implementation**: Business logic and calculations
- **MCP Server Tools**: Tool wrappers that call the service

### 2. Mock Strategy
- **Application Verification**: Uses realistic mock data with randomization
- **Document Processing**: Uses mock MCP client with configurable responses
- **Financial Calculations**: Tests actual mathematical implementations

### 3. Edge Case Coverage
Tests include:
- Invalid inputs (zero/negative values)
- Boundary conditions (exact thresholds)
- Error handling and graceful degradation
- Data consistency validation

### 4. Integration Testing
Comprehensive workflows testing:
- Complete loan application processing
- Multi-service data verification
- Error propagation and handling
- Data consistency across services

## Test Data

### Mock Data Helpers
The `test_utils.py` module provides:
- `MCPTestHelpers`: Mock data generators
- `LoanApplicationTestData`: Complete application scenarios
- Common fixtures for all test modules

### Test Scenarios
Three main application profiles:
- **Excellent Credit**: High income, excellent credit, low risk
- **Marginal Credit**: Average income, fair credit, moderate risk  
- **High Risk**: Low income, poor credit, high risk

## Assertions and Validations

### Financial Validations
- Credit scores: 300-850 range
- DTI ratios: Reasonable percentages
- Payment amounts: Non-negative values
- Utilization ratios: 0-100% range

### Response Structure
- Required fields presence
- Correct response types
- JSON serialization compatibility
- Error response formats

### Business Logic
- Qualification thresholds
- Risk assessment consistency
- Recommendation logic
- Calculation accuracy

## Continuous Integration

The test suite is designed for CI/CD integration:
- Fast execution (< 5 minutes)
- Clear pass/fail criteria
- Detailed error reporting
- Coverage thresholds (90%+)

## Debugging Tests

### Verbose Output
```bash
pytest tests/mcp_servers/ -v -s
```

### Single Test
```bash
pytest tests/mcp_servers/application_verification/test_server.py::TestApplicationVerificationServiceImpl::test_retrieve_credit_report -v
```

### Failed Tests Only
```bash
pytest tests/mcp_servers/ --lf
```

### Coverage for Specific Module
```bash
pytest tests/mcp_servers/financial_calculations/ --cov=mcp_servers.financial_calculations --cov-report=term-missing
```

## Contributing Tests

When adding new MCP server functionality:

1. **Add Unit Tests**: Test the service implementation directly
2. **Add Tool Tests**: Test the MCP tool wrappers
3. **Update Integration Tests**: Include new functionality in workflows
4. **Add Edge Cases**: Test error conditions and boundary cases
5. **Update Mock Data**: Add realistic test data for new features

### Test Naming Convention
- `test_<functionality>`: Basic functionality test
- `test_<functionality>_<scenario>`: Specific scenario test
- `test_<functionality>_edge_case`: Edge case or error condition
- `test_<functionality>_integration`: Integration with other services

## Performance Considerations

- Tests use async/await patterns matching the MCP server implementations
- Mock data is generated efficiently without external dependencies
- Integration tests validate timing and response characteristics
- Coverage reporting tracks test execution performance

## Security Testing

While not security-focused, tests validate:
- Input sanitization and validation
- Error message safety (no sensitive data leakage)
- Data consistency and integrity
- Proper handling of invalid/malicious inputs
