#!/bin/bash
# ═══════════════════════════════════════════════════════
# Clarion Release Script
# Creates a tagged release from develop → main
#
# Usage: bash scripts/release.sh 1.0.0
# ═══════════════════════════════════════════════════════

set -e

VERSION="${1:?Usage: bash scripts/release.sh <version>}"

echo "═══════════════════════════════════════════════════════"
echo "Clarion Release v${VERSION}"
echo "═══════════════════════════════════════════════════════"

# Pre-flight checks
echo "→ Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Working directory not clean. Commit or stash changes first."
    exit 1
fi

echo "→ Updating branches..."
git checkout develop && git pull origin develop
git checkout main && git pull origin main

echo "→ Creating release branch..."
git checkout -b "release/v${VERSION}" develop

echo "→ Updating version in pyproject.toml..."
sed -i.bak "s/version = \".*\"/version = \"${VERSION}\"/" backend/pyproject.toml
rm -f backend/pyproject.toml.bak

echo "→ Updating version in package.json..."
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${VERSION}\"/" frontend/package.json
rm -f frontend/package.json.bak

git add .
git commit -m "chore: bump version to ${VERSION}"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Release branch created: release/v${VERSION}"
echo ""
echo "Next steps:"
echo "  1. Push:   git push -u origin release/v${VERSION}"
echo "  2. Test:   Run full QA suite against this branch"
echo "  3. PR:     Create PR to main, merge when ready"
echo "  4. Tag:    git checkout main && git pull"
echo "             git tag -a v${VERSION} -m 'Clarion v${VERSION}'"
echo "             git push origin v${VERSION}"
echo "  5. Merge:  git checkout develop && git merge main && git push"
echo "  6. Clean:  git branch -d release/v${VERSION}"
echo "═══════════════════════════════════════════════════════"
