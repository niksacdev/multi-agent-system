# Data Models

Type-safe data structures powering the multi-agent loan processing system.

## Overview

All data models use **Pydantic v2** for runtime validation and type safety. Our models are:

- **Privacy-First**: Use secure `applicant_id` instead of SSN
- **Type-Safe**: Full type annotations with runtime validation
- **Domain-Driven**: Models reflect real loan processing concepts
- **Extensible**: Easy to add fields without breaking existing code

## Core Models

### Loan Application

The primary input structure for loan processing.

**File**: [`loan_processing/models/application.py`](../loan_processing/models/application.py)

```python
class LoanApplication(BaseModel):
    application_id: str           # Unique application identifier
    applicant_id: str            # Secure ID (never SSN)
    applicant_name: str
    loan_amount: Decimal
    loan_purpose: LoanPurpose
    annual_income: Decimal
    employment_status: str
    credit_score: Optional[int]
    existing_debt: Decimal
    down_payment: Decimal
    property_value: Optional[Decimal]
    additional_data: Dict[str, Any]  # Flexible extension point
```

**Privacy Features**:
- No SSN storage - uses secure `applicant_id`
- Sensitive data in `additional_data` can be encrypted
- Audit trail maintained separately

### Agent Assessment

Standardized output from each agent's evaluation.

**File**: [`loan_processing/models/assessment.py`](../loan_processing/models/assessment.py)

```python
class AgentAssessment(BaseModel):
    agent_name: str
    agent_type: str
    assessment_timestamp: datetime
    status: AssessmentStatus  # COMPLETE, FAILED, PENDING
    confidence_score: float    # 0.0 to 1.0
    
    # Flexible result structure
    assessment_result: Dict[str, Any]
    
    # Decision support
    risk_factors: List[str]
    recommendations: List[str]
    
    # Audit trail
    tools_used: List[str]
    processing_time_ms: int
```

**Key Features**:
- Standardized across all agent types
- Flexible `assessment_result` for agent-specific data
- Built-in observability with tools used and timing

### Loan Decision

Final output after all agents complete processing.

**File**: [`loan_processing/models/decision.py`](../loan_processing/models/decision.py)

```python
class LoanDecision(BaseModel):
    application_id: str
    decision_id: str
    
    # Core decision
    decision: DecisionStatus  # APPROVED, DENIED, CONDITIONAL, MANUAL_REVIEW
    decision_timestamp: datetime
    
    # Decision details
    approved_amount: Optional[Decimal]
    interest_rate: Optional[Decimal]
    term_months: Optional[int]
    
    # Reasoning
    primary_reason: str
    supporting_reasons: List[str]
    conditions: List[str]  # For conditional approvals
    
    # Agent assessments
    agent_assessments: List[AgentAssessment]
    
    # Compliance
    regulatory_checks: Dict[str, bool]
    fcra_compliant: bool
    ecoa_compliant: bool
```

## Validation Examples

### Input Validation

```python
# Automatic validation on creation
app = LoanApplication(
    application_id="app-123",
    applicant_id="usr-456",  # Secure ID, not SSN
    loan_amount=Decimal("250000"),
    annual_income=Decimal("75000"),
    # Missing required field raises ValidationError
)
```

### Type Safety

```python
# Type checking at runtime
app.credit_score = "high"  # ValidationError: not an integer
app.loan_amount = -1000    # ValidationError: must be positive
```

### Serialization

```python
# Easy API integration
json_data = app.model_dump_json()
restored = LoanApplication.model_validate_json(json_data)
```

## Domain Enums

### Loan Purpose
```python
class LoanPurpose(str, Enum):
    HOME_PURCHASE = "home_purchase"
    REFINANCE = "refinance"
    HOME_EQUITY = "home_equity"
    DEBT_CONSOLIDATION = "debt_consolidation"
```

### Decision Status
```python
class DecisionStatus(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    CONDITIONAL = "conditional_approval"
    MANUAL_REVIEW = "manual_review"
```

### Assessment Status
```python
class AssessmentStatus(str, Enum):
    COMPLETE = "complete"
    FAILED = "failed"
    PENDING = "pending"
    TIMEOUT = "timeout"
```

## Integration with Agents

### Agent Input
```python
# Agents receive standardized context
context = {
    "application": loan_application.model_dump(),
    "previous_assessments": [assessment.model_dump() for assessment in assessments]
}
```

### Agent Output
```python
# Agents produce typed assessments
assessment = AgentAssessment(
    agent_name="Credit Agent",
    agent_type="credit",
    assessment_result={
        "credit_score": 720,
        "credit_tier": "excellent",
        "debt_to_income_ratio": 0.28
    },
    confidence_score=0.92
)
```

## Benefits

1. **Type Safety**: Catch errors at development time
2. **Validation**: Automatic input validation
3. **Documentation**: Models serve as API documentation
4. **Serialization**: Easy JSON/dict conversion
5. **Privacy**: Built-in privacy compliance
6. **Extensibility**: Add fields without breaking code

## Implementation Files

- [`loan_processing/models/application.py`](../loan_processing/models/application.py) - Application model
- [`loan_processing/models/assessment.py`](../loan_processing/models/assessment.py) - Assessment model
- [`loan_processing/models/decision.py`](../loan_processing/models/decision.py) - Decision model
- [`loan_processing/models/__init__.py`](../loan_processing/models/__init__.py) - Model exports

See actual code files for complete implementation details.