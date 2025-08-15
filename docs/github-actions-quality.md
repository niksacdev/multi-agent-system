# Quality Assurance with GitHub Actions

This project uses **GitHub Actions** instead of local git hooks to enforce code quality and testing standards. This approach provides several advantages:

## Why GitHub Actions over Git Hooks?

### ✅ **Server-Side Enforcement**
- **Cannot be bypassed**: Unlike git hooks, GitHub Actions run on GitHub's servers
- **Consistent for all contributors**: Same environment and checks for everyone
- **Required for merging**: Branch protection rules prevent merging failed builds

### ✅ **Comprehensive Validation**
- **Test Suite**: Full 83+ test suite with >90% coverage requirement
- **Code Quality**: Type checking, linting, and formatting validation
- **Architecture**: Domain boundary validation (no SDK imports in models/services)
- **Security**: Dependency vulnerability scanning

### ✅ **Team Collaboration**
- **PR Feedback**: Clear status checks and failure reasons on pull requests
- **Automated Reports**: Coverage reports and test summaries
- **Notifications**: Team alerts when main branch health degrades

## GitHub Actions Workflows

### 🧪 **Test Suite** (`.github/workflows/test.yml`)

Runs on every push and pull request:

```yaml
Triggers: push, pull_request (main, develop branches)
Jobs:
  - test: Run comprehensive test suite + coverage
  - lint: Type checking and code formatting
  - security: Dependency vulnerability scan
  - validate-architecture: Domain boundary checks
```

**Requirements for passing:**
- All 83+ tests pass
- Coverage ≥90%
- No type checking errors
- No linting errors
- Clean architecture boundaries

### 🔒 **Branch Protection** (`.github/workflows/branch-protection.yml`)

Daily health checks for main branch:

```yaml
Triggers: scheduled (daily), manual
Jobs:
  - validate-main-branch: Ensure main branch stays healthy
```

**Alerts if:**
- Main branch tests start failing
- Coverage drops below 90%
- Any quality regression detected

## Developer Workflow

### 1. **Local Development**
```bash
# Required before committing
python run_tests.py --type all

# Optional: quick checks
mypy loan_processing/ mcp_servers/
ruff check .
```

### 2. **Pull Request**
- GitHub Actions automatically run all quality checks
- PR cannot be merged until all checks pass
- Clear feedback on any failures

### 3. **Branch Protection**
Main branch is protected with required status checks:
- ✅ Test Suite must pass
- ✅ Code Quality must pass  
- ✅ Security Scan must pass
- ✅ Architecture Validation must pass

## Status Badges

Add these to your PR descriptions or documentation:

```markdown
![Tests](https://github.com/niksacdev/multi-agent-system/workflows/Test%20Suite/badge.svg)
![Branch Protection](https://github.com/niksacdev/multi-agent-system/workflows/Branch%20Protection/badge.svg)
```

## Benefits

### **For Individual Developers**
- ✅ Clear feedback on code quality
- ✅ Consistent standards across team
- ✅ No need to remember git hook setup
- ✅ Same checks locally and remotely

### **For Team Leads**
- ✅ Guaranteed quality gate enforcement
- ✅ Historical quality metrics
- ✅ Automated alerts for regressions
- ✅ No manual review of basic quality issues

### **For DevOps**
- ✅ Centralized CI/CD configuration
- ✅ Scalable across repositories
- ✅ Integration with external tools
- ✅ Compliance and audit trail

## Troubleshooting

### **Tests Failing on PR**
1. Check the Actions tab for detailed logs
2. Run `python run_tests.py --type all` locally
3. Fix failing tests or coverage issues
4. Push changes to update the PR

### **Coverage Below 90%**
1. Run `python run_tests.py --type all --html`
2. Open `htmlcov/index.html` to see uncovered lines
3. Add tests for missing coverage
4. Verify locally before pushing

### **Architecture Validation Failing**
1. Check for SDK imports in `loan_processing/models/` or `loan_processing/services/`
2. Move SDK-specific code to `providers/` or `agents/` directories
3. Ensure domain layers remain provider-agnostic

This approach ensures **enterprise-grade quality** while maintaining **developer productivity** and **team collaboration**.
