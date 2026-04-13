# Clarion — Git & GitHub Management Guide

## 1. Initial Repository Setup

### Create the GitHub repository

```bash
# On GitHub: Create a new private repository named "clarion"
# Do NOT initialise with README, .gitignore, or license (we already have them)

# On your local machine:
cd /path/to/clarion
git init
git add .
git commit -m "feat: phase 0+1+2 scaffold — 109 files

- Docker Compose (7 containers), FastAPI app factory, module registry
- React 18 + TypeScript + Tailwind frontend shell
- 6 dashboard layout presets (Editorial, Command Center, Executive, Operations, Magazine, Flow)
- 11 widget component stubs with layout-agnostic rendering
- JWT auth with bcrypt, role-based access control, protected routes
- Login page, token refresh, auth context with real JWT flow
- Theme token system (3-layer merge: base → org → user)
- Alembic migration: 12 tables including theme_config, user_preferences
- CI pipeline (6 jobs: lint, unit, contract, anon, security, docker)
- Design tokens: blue palette, Geist Sans, density modes, dark mode"

git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/clarion.git
git push -u origin main
```

### Create the develop branch

```bash
git checkout -b develop
git push -u origin develop
```

### Configure branch protection (GitHub Settings → Branches)

**For `main`:**
- Require pull request reviews before merging: 1 approval
- Require status checks to pass: `Backend Unit Tests`, `Frontend Lint & Test`, `Docker Build Smoke Test`
- Require branches to be up to date before merging
- Do not allow force pushes

**For `develop`:**
- Require status checks to pass: `Backend Lint`, `Backend Unit Tests`, `Contract Tests`
- Allow force pushes only for admins (for rebasing)


## 2. Branching Strategy

```
main ─────────────────────────────────── production releases (tagged)
  │
  └─ develop ─────────────────────────── integration branch
       │
       ├─ feature/phase-3-sf-sync ────── individual feature work
       ├─ feature/phase-4-anonymisation
       ├─ bugfix/fix-token-refresh
       └─ ...
```

| Branch | Purpose | Merges To | Created From |
|--------|---------|-----------|--------------|
| `main` | Production-ready tagged releases | — | `release/*` or `hotfix/*` |
| `develop` | Integration of all features | `main` via release branch | `main` (once) |
| `feature/*` | Individual phase/feature work | `develop` via PR | `develop` |
| `bugfix/*` | Bug fixes | `develop` via PR | `develop` |
| `release/*` | Release prep and final QA | `main` + `develop` | `develop` |
| `hotfix/*` | Critical production fix | `main` + `develop` | `main` |


## 3. Daily Workflow

### Starting a new phase (e.g., Phase 3)

```bash
# Always start from latest develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/phase-3-sf-sync

# Work, commit frequently with conventional commits
git add .
git commit -m "feat(sync): add Salesforce CLI wrapper with bulk query support"

# Push to remote (first time)
git push -u origin feature/phase-3-sf-sync

# Subsequent pushes
git push
```

### Commit message convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

**Types:**
- `feat` — new feature (triggers minor version bump)
- `fix` — bug fix (triggers patch version bump)
- `refactor` — code change that neither fixes nor adds
- `docs` — documentation only
- `test` — adding or updating tests
- `chore` — tooling, dependencies, configs
- `style` — formatting, no logic change
- `perf` — performance improvement
- `ci` — CI/CD changes

**Scopes** (match our modules):
`sync`, `cases`, `reviews`, `analytics`, `predictions`, `notifications`, `chatbot`, `anonymisation`, `accounts`, `auth`, `admin`, `layout`, `theme`, `db`, `ci`

**Examples:**
```bash
git commit -m "feat(sync): implement SF case header sync with field mapping"
git commit -m "feat(sync): add CaseFeed event extraction with HTML stripping"
git commit -m "fix(auth): handle expired refresh token gracefully"
git commit -m "refactor(layout): extract grid renderer into shared component"
git commit -m "test(sync): add contract tests for SF priority mapping"
git commit -m "docs: update PRD v1.5 with Phase 3 sync requirements"
git commit -m "chore(deps): upgrade fastapi to 0.116.0"
```

### Keeping your branch up to date

```bash
# While working on a feature branch, regularly sync with develop
git checkout develop
git pull origin develop
git checkout feature/phase-3-sf-sync
git rebase develop

# If conflicts arise:
# 1. Git will pause and show conflicting files
# 2. Edit the files to resolve conflicts
# 3. git add <resolved-files>
# 4. git rebase --continue
# 5. Repeat until done

# Force push after rebase (only on YOUR feature branch, never on develop/main)
git push --force-with-lease
```


## 4. Pull Request Workflow

### Creating a PR

```bash
# Ensure branch is up to date with develop
git checkout develop && git pull
git checkout feature/phase-3-sf-sync && git rebase develop
git push --force-with-lease

# On GitHub: Create Pull Request
# Base: develop ← Compare: feature/phase-3-sf-sync
```

### PR title format
Same as commit convention:
```
feat(sync): Salesforce case sync with field mapping and CaseFeed extraction
```

### PR description template
```markdown
## What this does
Brief description of the change.

## Phase
Phase 3 — Salesforce Sync & Data Layer

## Changes
- Added SF CLI wrapper with bulk SOQL queries
- Implemented case header sync with priority mapping (2 - High → P2)
- Added CaseFeed extraction with HTML stripping
- Email address parsing (semicolon-separated)
- Thread ID extraction from Subject

## Testing
- [ ] Unit tests pass locally
- [ ] Contract tests pass
- [ ] Tested with Octave SF org data
- [ ] No PII in test fixtures

## Database changes
- New migration: 002_case_tables.py
- Tables: cases, case_events, case_feeds

## Screenshots (if UI changes)
[Attach if relevant]
```

### After PR is approved and CI passes

```bash
# On GitHub: Click "Squash and merge" (recommended for feature branches)
# This creates a single clean commit on develop

# Clean up locally
git checkout develop
git pull origin develop
git branch -d feature/phase-3-sf-sync
```


## 5. Release Process

### When ready to release (e.g., v1.0.0)

```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# Final QA, bug fixes go here as commits
git commit -m "fix(auth): correct token expiry header"

# When ready, merge to main
git push -u origin release/v1.0.0
# Create PR: main ← release/v1.0.0
# After merge:

# Tag the release on main
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Clarion v1.0.0 — Initial release"
git push origin v1.0.0

# Merge back to develop (captures any release fixes)
git checkout develop
git merge main
git push origin develop

# Clean up
git branch -d release/v1.0.0
git push origin --delete release/v1.0.0
```


## 6. Hotfix Process

### Critical production bug

```bash
# Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/fix-critical-auth-bypass

# Fix, test, commit
git commit -m "fix(auth): prevent token reuse after logout"

# PR to main, then merge
# Tag: v1.0.1
git checkout main && git pull
git tag -a v1.0.1 -m "Hotfix: auth token reuse prevention"
git push origin v1.0.1

# Merge hotfix back to develop
git checkout develop
git merge main
git push origin develop
```


## 7. Working with Claude on Phases

Each conversation with Claude produces a zip of updated files. Here's how to integrate:

```bash
# 1. Ensure you're on a clean feature branch
git checkout develop && git pull
git checkout -b feature/phase-3-sf-sync

# 2. Unzip Claude's output into your project
cd /path/to/clarion
# Back up first if nervous:
cp -r . ../clarion-backup

# Extract — this overwrites existing files and adds new ones
unzip -o ~/Downloads/Clarion_Phase3_Scaffold.zip -d /tmp/clarion-update
cp -r /tmp/clarion-update/clarion/* .

# 3. Review what changed
git status                    # See all modified/new files
git diff                      # See line-by-line changes
git diff --stat               # Summary of changes

# 4. Stage selectively or all at once
git add .                     # Stage everything
# OR stage selectively:
git add backend/app/modules/sync/
git add backend/alembic/versions/002_case_tables.py

# 5. Commit with descriptive message
git commit -m "feat(sync): phase 3 scaffold — SF sync, case tables, field mapping

- SF CLI wrapper with bulk SOQL support
- Case header/event/feed sync with configurable schedule  
- Priority mapping (SF format → P1-P4)
- CaseFeed HTML stripping for AI consumption
- Email address parsing and thread ID extraction
- Alembic migration 002: cases, case_events, case_feeds tables
- Contract tests for sync module schemas"

# 6. Push and create PR
git push -u origin feature/phase-3-sf-sync
```

### If Claude updates existing files you've modified

```bash
# Use git diff to review before committing
git diff backend/app/main.py

# If you want to keep your version of specific files:
git checkout HEAD -- path/to/your/version.py

# If you want to merge both changes (yours + Claude's):
# Edit the file manually, then git add
```


## 8. Useful Git Commands

```bash
# See commit history (compact)
git log --oneline --graph -20

# See what's on develop that you don't have
git log HEAD..origin/develop --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Stash work temporarily
git stash
git stash pop

# Find which commit introduced a bug
git bisect start
git bisect bad          # current commit is bad
git bisect good v1.0.0  # this tag was good
# Git walks you through commits to test

# See who changed a line
git blame backend/app/main.py

# Check CI status from terminal (requires GitHub CLI)
gh pr checks
```


## 9. Project File Structure for Git

```
clarion/
├── .github/workflows/ci.yml    # CI pipeline — don't edit without testing
├── .gitignore                   # Already configured
├── .env.example                 # Template — NEVER commit .env
├── backend/
│   ├── alembic/versions/        # Migrations — sequential, never rename
│   ├── app/                     # Source code
│   └── tests/                   # Tests mirror app/ structure
├── frontend/
│   ├── src/                     # Source code
│   └── package.json             # Lock file committed
├── docker-compose.yml           # Dev environment
├── CONTRIBUTING.md              # This file
└── README.md                    # Project overview
```

### Never commit:
- `.env` (contains secrets)
- `node_modules/`
- `__pycache__/`
- `.pytest_cache/`
- `dist/`, `build/`
- Any file containing API keys, passwords, or PII

These are already in `.gitignore`.


## 10. Phase-to-Branch Mapping

| Phase | Branch Name | Key Files |
|-------|-------------|-----------|
| 0 | `main` (initial) | Scaffold, Docker, CI |
| 1 | `feature/phase-1-frontend-shell` | Layout system, widgets, sidebar |
| 2 | `feature/phase-2-auth-rbac` | JWT, login, role enforcement |
| 3 | `feature/phase-3-sf-sync` | SF CLI, case sync, migrations |
| 4 | `feature/phase-4-anonymisation` | PII detection, tokenisation |
| 5 | `feature/phase-5-ai-integration` | Ollama, Claude, OpenAI routing |
| 6 | `feature/phase-6-case-reviews` | Review framework, rubric, AI draft |
| 7 | `feature/phase-7-analytics` | Charts, predictions, dashboards |
| 8 | `feature/phase-8-notifications` | Alert rules, email, in-app |
| 9 | `feature/phase-9-chatbot` | AI chatbot, tool integration |
| 10 | `feature/phase-10-admin` | Admin panel, settings, health |
| 11 | `feature/phase-11-docs` | User guide, help system |
| 12 | `feature/phase-12-security` | Pen test, hardening |
| 13 | `feature/phase-13-qa-release` | E2E tests, release prep |
