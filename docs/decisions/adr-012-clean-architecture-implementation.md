# ADR-012: Clean Architecture Implementation (Domain Models and Utilities Structure)

## Status
Accepted

## Context
The system's folder structure violated clean architecture principles by placing domain models and shared utilities under a specific component (`agents/`), creating improper dependency relationships and limiting reusability across system components.

### Problem Statement
The original folder structure had architectural issues:

```
loan_processing/
├── agents/
│   ├── shared/
│   │   ├── models/           # Domain models nested under agents
│   │   └── utils/           # Shared utilities nested under agents
│   └── providers/openai/
└── tools/
```

**Issues Identified:**
1. **Domain Models Coupled to Implementation**: Core business models (`LoanApplication`, `LoanDecision`) were nested under the agents implementation
2. **Improper Dependency Direction**: Domain models could depend on agents layer (violation of clean architecture)
3. **Limited Reusability**: Models and utilities weren't accessible to tools, future APIs, or external integrations
4. **Namespace Pollution**: Unnecessary "shared" namespace adding complexity
5. **Scaling Problems**: When adding new components (APIs, batch jobs), they couldn't easily access core models

### Clean Architecture Principles Violated
- **Domain Independence**: Domain models should be in the innermost layer, not dependent on infrastructure
- **Dependency Rule**: Dependencies should point inward toward the domain, not outward
- **Reusability**: Core models should be accessible to all layers

## Alternatives Considered

### Option 1: Keep Current Structure
**Pros:** No migration needed, familiar to current developers
**Cons:** Violates clean architecture, limits future extensibility, creates coupling issues

### Option 2: Move Only Models to Top-Level
**Pros:** Fixes domain model placement, simpler migration
**Cons:** Utilities still nested, inconsistent architecture

### Option 3: Complete Clean Architecture Restructure
**Pros:** Proper architecture alignment, maximum reusability, future-proof
**Cons:** Requires comprehensive migration, updates to all imports

### Option 4: Create Services Layer
**Pros:** Adds business logic layer
**Cons:** Premature for current system complexity, can be added later

## Decision
**Selected Option 3: Complete Clean Architecture Restructure**

Move both `models/` and `utils/` to the top level of `loan_processing/` and remove unnecessary "shared" namespace.

### New Architecture
```
loan_processing/
├── config/                    # System configuration
├── models/                    # Core domain models (MOVED UP)
│   ├── application.py         # LoanApplication, ApplicationData
│   ├── decision.py           # LoanDecision, AssessmentResult  
│   └── assessment.py         # Various assessment types
├── utils/                     # Shared utilities (MOVED UP)
│   ├── safe_evaluator.py     # Security utilities
│   ├── config_loader.py      # Configuration loading
│   └── persona_loader.py     # Agent persona loading
├── agents/
│   ├── agent-persona/         # Agent instruction files
│   └── providers/openai/     # Provider-specific agent code
└── tools/                    # MCP servers and services
```

## Implementation

### Migration Process
1. **Move Domain Models**: `agents/shared/models/` → `loan_processing/models/`
2. **Move Shared Utilities**: `agents/shared/utils/` → `loan_processing/utils/`
3. **Remove Empty Shared Directory**: Delete `agents/shared/`
4. **Update All Import Statements**: Change from `loan_processing.agents.shared.X` to `loan_processing.X`
5. **Update Configuration Paths**: Fix relative paths in utilities
6. **Update GitHub Actions**: Modify test coverage and validation paths

### Import Statement Changes
```python
# Before (problematic)
from loan_processing.agents.shared.models import LoanApplication
from loan_processing.agents.shared.utils import SafeConditionEvaluator

# After (clean architecture)
from loan_processing.models import LoanApplication
from loan_processing.utils import SafeConditionEvaluator
```

### Path Updates Required
- **Persona Loader**: Updated to find agent personas in correct relative location
- **Config Loader**: Updated to find configuration files in consolidated config directory
- **Test Coverage**: Updated GitHub Actions to reference new paths
- **Documentation**: Updated all references in README, CLAUDE.md, and guides

## Consequences

### Positive
- **Clean Architecture Compliance**: Domain models are now in the innermost layer
- **Proper Dependency Direction**: All layers depend inward toward domain models
- **Enhanced Reusability**: Models and utilities accessible to all components
- **Future Extensibility**: Easy to add APIs, batch jobs, external integrations
- **Simplified Imports**: Cleaner, more intuitive import statements
- **Reduced Coupling**: Components depend on abstractions rather than implementations
- **Better Testing**: Domain models can be tested independently

### Negative
- **Migration Complexity**: Required updating many import statements
- **Initial Confusion**: Developers need to learn new import patterns
- **Temporary Disruption**: Risk of breaking changes during migration

### Risk Mitigation
- **Comprehensive Testing**: Ran full test suite after each migration step
- **Gradual Migration**: Moved one component at a time with validation
- **Backward Compatibility**: Where possible, maintained compatibility
- **Documentation Updates**: Updated all references to new structure

## Architectural Benefits

### Domain-Driven Design Alignment
```python
# Domain models are now properly layered
loan_processing/
├── models/          # Domain layer (innermost)
├── utils/           # Application layer utilities  
├── agents/          # Application layer (agent orchestration)
└── tools/           # Infrastructure layer (MCP servers)
```

### Dependency Flow (Clean Architecture)
```
Infrastructure (tools/) → Application (agents/) → Domain (models/)
```

### Reusability Examples
```python
# Now all components can access domain models
from loan_processing.models import LoanApplication

# Future API server
class LoanAPIServer:
    def process_loan(self, app: LoanApplication) -> LoanDecision:
        # Can directly use domain models

# Future batch processor  
class BatchProcessor:
    def process_applications(self, apps: List[LoanApplication]):
        # Can directly use domain models

# External integrations
from loan_processing.models import LoanApplication
from loan_processing.utils import validate_application
```

## Implementation Details

### Models Organization
```python
# loan_processing/models/
application.py      # LoanApplication, applicant data models
decision.py        # LoanDecision, decision status enums  
assessment.py      # Assessment results, scoring models
```

### Utils Organization
```python  
# loan_processing/utils/
safe_evaluator.py    # Safe condition evaluation (security)
config_loader.py     # YAML configuration loading
persona_loader.py    # Agent persona file loading
output_formatter.py  # Structured output formatting
```

### Import Patterns
```python
# Recommended import style for domain models
from loan_processing.models.application import LoanApplication
from loan_processing.models.decision import LoanDecision

# Or module-level imports
from loan_processing.models import application, decision
from loan_processing.utils import safe_evaluator
```

## Testing Strategy
- **Domain Model Tests**: Can now test models independently of agents
- **Utility Tests**: Utilities tested in isolation from business logic  
- **Integration Tests**: Verify all layers work together properly
- **Import Tests**: Validate all import statements resolve correctly

## Future Enhancements

### Services Layer (Future)
```python
loan_processing/
├── models/          # Domain models
├── services/        # Business logic services (future)
│   ├── loan_processor.py
│   ├── risk_calculator.py  
│   └── decision_engine.py
├── utils/           # Cross-cutting utilities
├── agents/          # Agent orchestration
└── tools/           # Infrastructure
```

### Interface Definitions (Future)
```python
loan_processing/
├── interfaces/      # Abstract interfaces (future)
│   ├── assessment.py
│   ├── storage.py
│   └── notification.py
```

## Validation

### Architecture Compliance Check
- ✅ Domain models independent of infrastructure
- ✅ Proper dependency direction (inward)
- ✅ Models accessible to all components
- ✅ No circular dependencies
- ✅ Clean import statements

### Testing Validation
- ✅ All 38 tests passing after migration
- ✅ No functional regressions
- ✅ Import statements resolve correctly
- ✅ Configuration paths working

## Related Decisions
- ADR-011: Configuration Provider Separation
- Future: Service layer introduction
- Future: Interface abstraction patterns

## References
- Clean Architecture by Robert C. Martin
- Domain-Driven Design principles
- Python project structure best practices
- Hexagonal Architecture patterns
- Dependency Inversion Principle