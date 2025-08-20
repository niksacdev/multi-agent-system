# Observability Security Guidelines

## Overview

This document outlines security requirements and best practices for logging in the Multi-Agent Loan Processing System to ensure compliance with data privacy regulations and prevent exposure of sensitive customer information.

## Data Classification

### ✅ SAFE TO LOG (Always Permitted)

**System Identifiers:**
- `application_id` - UUID-based application identifier
- `applicant_id` - UUID-based applicant identifier (NOT SSN)
- `session_id` - Correlation ID for request tracking
- `correlation_id` - System-generated tracking identifier

**Technical Metadata:**
- `component` - System component name
- `operation` - Function/method name
- `processing_time_seconds` - Performance metrics
- `error_type` - Exception class names
- `status` - Operation status (success/failure)

**Safe Business Data:**
- `pattern_id` - Orchestration pattern identifier
- `decision_status` - Loan decision outcome (approved/denied/review)
- `risk_level` - Risk assessment level (low/medium/high)
- `qualification_status` - General qualification assessment

### ⚠️ CONDITIONAL LOGGING (Requires Sanitization)

**Document References:**
- `document_path` - File paths (ensure no PII in filenames)
- `document_type` - Document classification
- `tax_year` - Tax year for transcript requests

### 🚫 NEVER LOG (PII & Sensitive Data)

**Personal Identifiable Information:**
- `full_name` / `applicant_name` - Customer names
- `employer_name` - Employer information  
- `address` - Physical addresses
- `email` - Email addresses
- `phone` - Phone numbers
- `ssn` - Social Security Numbers

**Financial Information:**
- `loan_amount` - Specific loan amounts
- `monthly_income` - Income figures
- `salary` / `annual_income` - Salary information
- `monthly_debt_payments` - Debt payment amounts
- `interest_rate` - Interest rates
- `account_number` - Bank account numbers
- `routing_number` - Bank routing numbers

**Authentication Data:**
- API keys, passwords, tokens
- Authentication credentials
- Session tokens (other than correlation IDs)

## Implementation Guidelines

### 1. Logging Statement Examples

#### ✅ CORRECT - Safe Logging
```python
logger.info("Retrieving credit report", 
           applicant_id=applicant_id,
           component="verification_service")

logger.info("Loan processing completed", 
           application_id=application.application_id,
           decision_status=decision.decision.value,
           processing_time_seconds=processing_time,
           component="console_app")
```

#### 🚫 INCORRECT - PII Violation
```python
# ❌ NEVER DO THIS
logger.info("Processing application", 
           applicant_name=application.applicant_name,  # PII
           loan_amount=application.loan_amount,        # Financial data
           employer_name=employer_name)                # PII
```

### 2. Error Handling

#### ✅ CORRECT - Safe Error Logging
```python
try:
    result = process_application(application)
except Exception as e:
    logger.error("Application processing failed", 
                application_id=application.application_id,
                error_type=type(e).__name__,
                component="processor")
```

#### 🚫 INCORRECT - Error with PII
```python
# ❌ NEVER DO THIS
logger.error(f"Failed to process {customer_name}: {str(e)}")
```

### 3. Correlation Context Usage

Always use correlation context for request tracking:

```python
async with correlation_context(f"app_{application.application_id}") as session_id:
    logger.info("Starting processing", 
               application_id=application.application_id,
               session_id=session_id,
               component="processor")
    # All subsequent logs will include correlation_id automatically
```

## Compliance Requirements

### Data Privacy Regulations
- **GDPR Article 25**: Data protection by design and by default
- **CCPA**: California Consumer Privacy Act compliance
- **GLBA**: Gramm-Leach-Bliley Act for financial data
- **SOX**: Sarbanes-Oxley Act audit trail requirements

### Audit Requirements
- All business operations must be traceable via `application_id` and `correlation_id`
- Error conditions must be logged with sufficient detail for debugging
- Performance metrics must be captured for SLA monitoring
- No sensitive data should appear in audit logs

## Security Controls

### 1. Automatic PII Detection (Future Enhancement)
```python
def validate_log_entry(entry: dict) -> bool:
    """Validate log entry doesn't contain PII before logging."""
    sensitive_fields = [
        'full_name', 'applicant_name', 'employer_name', 
        'address', 'email', 'phone', 'ssn',
        'loan_amount', 'monthly_income', 'salary'
    ]
    return not any(field in entry for field in sensitive_fields)
```

### 2. Data Sanitization Utility
```python
def sanitize_log_data(data: dict) -> dict:
    """Remove PII and sensitive data from log entries."""
    sensitive_fields = [
        'full_name', 'applicant_name', 'employer_name', 
        'address', 'email', 'phone', 'ssn',
        'loan_amount', 'monthly_income', 'annual_income',
        'monthly_debt_payments', 'interest_rate'
    ]
    return {k: v for k, v in data.items() if k not in sensitive_fields}
```

## Azure Application Insights Configuration

When using Azure Application Insights:

1. **Enable IP Address Anonymization**
2. **Configure Data Retention Policies** (max 730 days)
3. **Set Up Access Controls** (RBAC for log access)
4. **Enable Export Controls** (prevent unauthorized data export)

## Incident Response

### If PII is Accidentally Logged:

1. **Immediate Action**: Stop the logging component
2. **Assess Impact**: Identify affected log entries and timeframe
3. **Data Removal**: Purge sensitive entries from logs
4. **Notification**: Report to security team and data protection officer
5. **Review**: Update logging code to prevent recurrence

## Code Review Checklist

Before committing logging code, verify:

- [ ] No PII (names, addresses, emails, phone numbers)
- [ ] No financial amounts (loan amounts, income, payments)
- [ ] No authentication data (passwords, keys, tokens)
- [ ] Safe identifiers used (`application_id`, `applicant_id`)
- [ ] Appropriate correlation context
- [ ] Error handling without sensitive data
- [ ] Component and operation clearly identified

## Monitoring and Alerts

Set up alerts for:
- Unusual patterns in log volume
- Error rate thresholds
- Performance degradation
- Security-related events

## Training Requirements

All developers must:
1. Read and understand this security guide
2. Complete data privacy training
3. Understand PII identification and handling
4. Know incident response procedures

---

**Remember**: When in doubt, don't log it. It's better to have insufficient logging than to expose customer data.