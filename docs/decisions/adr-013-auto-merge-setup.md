# Auto-Merge Setup Guide

This repository is configured to automatically merge PRs when all checks pass, using **squash and merge** to maintain a clean commit history.

## How Auto-Merge Works

1. **Create a PR** with your changes
2. **Add the `auto-merge` label** to enable automatic merging
3. **All checks must pass** (tests, code quality, etc.)
4. **PR automatically merges** using squash and merge
5. **Branch is deleted** after successful merge

## Required Repository Settings

### 1. Enable Auto-Merge in Repository Settings

Go to Settings → General → Pull Requests:
- ✅ Allow squash merging
- ❌ Allow merge commits (disabled)
- ❌ Allow rebase merging (disabled)
- ✅ Automatically delete head branches

### 2. Configure Branch Protection Rules

Go to Settings → Branches → Add rule for `main`:

**Protect matching branches:**
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
  - Required checks:
    - `Core Tests`
    - `Architecture Validation` 
    - `Code Quality`
    - `Expert Review`
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging
- ❌ Require approvals (0 - we rely on automated checks)

### 3. Create Required Labels

Create these labels in your repository (Issues → Labels → New label):

| Label | Description | Color |
|-------|-------------|-------|
| `auto-merge` | Automatically merge when checks pass | Green (#0E8A16) |
| `ready-to-merge` | PR is ready for automatic merge | Green (#2EA44F) |
| `do-not-merge` | Prevent automatic merging | Red (#D93F0B) |
| `work-in-progress` | PR is still being worked on | Yellow (#FEF2C0) |

## Using Auto-Merge

### Enable Auto-Merge on a PR

```bash
# Using GitHub CLI
gh pr view --add-label "auto-merge"

# Or using GitHub's native auto-merge
gh pr merge --auto --squash
```

### Prevent Auto-Merge

Add any of these labels to prevent automatic merging:
- `do-not-merge`
- `work-in-progress`

Or mark the PR as a draft.

## Workflow Details

The auto-merge workflow (`/.github/workflows/auto-merge.yml`) provides two methods:

1. **pascalgn/merge-action**: Community action that handles auto-merge
2. **GitHub native auto-merge**: Uses `gh pr merge --auto` (fallback option)

Both methods:
- Use **squash merge** exclusively
- Delete the branch after merging
- Require all checks to pass
- Respect blocking labels

## Benefits

- **Clean commit history**: Squash merge creates one commit per feature
- **Automated workflow**: No manual merge needed when checks pass
- **Quality gates**: All tests and checks must pass
- **Consistent merging**: Same merge strategy for all PRs
- **No merge conflicts**: Requires branches to be up-to-date

## Troubleshooting

If auto-merge isn't working:

1. **Check PR labels**: Ensure `auto-merge` or `ready-to-merge` is present
2. **Check blocking labels**: Remove `do-not-merge` or `work-in-progress`
3. **Check PR status**: Ensure PR is not a draft
4. **Check CI status**: All required checks must be passing
5. **Check branch status**: Branch must be up-to-date with main

## Manual Override

To manually merge without auto-merge:

```bash
# Squash and merge manually
gh pr merge PR_NUMBER --squash

# Or use the GitHub UI with squash merge
```