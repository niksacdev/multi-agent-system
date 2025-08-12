# Data Models

The data structures that power the loan processing system.

## Overview

All data models use **Pydantic v2** for type safety and validation. Models are designed to be:

- **Extensible**: Easy to add new fields
- **Type-safe**: Full type annotations
- **Privacy-compliant**: No sensitive data like SSN

## Core Models

### Loan Application

The main input to the system.

**File**: [`loan_processing/models/application.py`](../loan_processing/models/application.py)

```python
class LoanApplication(BaseModel):
    application_id: str  # UUID format
    applicant_id: str    # Internal ID (replaces SSN for privacy)
    loan_amount: Decimal
    loan_purpose: LoanPurpose
    # ... see file for complete definition
```

### Loan Decision

The output from agent processing.

**File**: [`loan_processing/models/decision.py`](../loan_processing/models/decision.py)

```python
class LoanDecision(BaseModel):
    application_id: str
    decision: LoanDecisionStatus  # APPROVED, REJECTED, PENDING
    decision_reason: str
    confidence_score: float
    # ... see file for complete definition
```

### Assessment Results

What agents produce during processing.

**File**: [`loan_processing/models/assessment.py`](../loan_processing/models/assessment.py)

```python
class CreditAssessment(BaseModel):
    applicant_id: str  # Privacy-compliant identifier
    credit_score: int
    risk_level: RiskLevel
    assessment_details: dict[str, Any]
    # ... see file for complete definition
```

## Key Features

### Privacy-First Design

- Use internal `applicant_id` (UUID format)
- Sensitive fields are clearly marked
- All data access is logged

### Type Safety

Every field is fully typed:

```python
# Good: Type-safe
loan_amount: Decimal
application_date: datetime

# Avoid: Untyped
data: dict  # Too generic
```

### Validation

Pydantic automatically validates:

- **Required fields**: Must be present
- **Format checks**: Email, phone, UUID formats
- **Range validation**: Min/max values
- **Custom rules**: Business logic validation

## Usage Examples

### Creating an Application

```python
from loan_processing.models.application import LoanApplication
from decimal import Decimal

app = LoanApplication(
    application_id="app-123",
    applicant_id="user-456",  # Internal ID, not SSN
    loan_amount=Decimal("250000"),
    loan_purpose=LoanPurpose.HOME_PURCHASE
)
```

### Processing Results

```python
from loan_processing.models.decision import LoanDecision

decision = LoanDecision(
    application_id=app.application_id,
    decision=LoanDecisionStatus.APPROVED,
    confidence_score=0.85
)
```

## File Structure

```text
loan_processing/models/
├── __init__.py
├── application.py    # Input data
├── assessment.py     # Agent outputs
└── decision.py       # Final results
```

See the actual model files for complete field definitions and validation rules.
