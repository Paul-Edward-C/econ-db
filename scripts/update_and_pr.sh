#!/usr/bin/env bash
# update_and_pr.sh — run the data loader and open a PR against main.
#
# Usage:  scripts/update_and_pr.sh ["commit message"]
#
# Defaults the commit message to "Data update YYYY-MM-DD".
# Refuses to run only if there are uncommitted changes OUTSIDE app/db/
# (raw CSVs dropped under app/db/ are the expected input to this script).
# Branches off the latest origin/main, runs load_new_v2.py, commits any
# changes, pushes, and opens a PR via the gh CLI.

set -euo pipefail

REPO="/Users/paul/Documents/ghost/econ-db"
APP="$REPO/app"
MSG="${1:-Data update $(date +%Y-%m-%d)}"

cd "$REPO"

# 1. Refuse if there are uncommitted changes outside app/db/
#    (app/db/ is where raw CSVs are dropped between runs — expected to be dirty)
DIRTY_OUTSIDE=$(git status --porcelain -- . ':!app/db')
if [[ -n "$DIRTY_OUTSIDE" ]]; then
    echo "ERROR: uncommitted changes outside app/db/ in $REPO" >&2
    echo "$DIRTY_OUTSIDE" >&2
    echo >&2
    echo "Stash or commit them before running this script." >&2
    exit 1
fi

# 2. Fetch main and fast-forward the local main
echo "-> Updating main from origin"
git fetch origin main
git checkout main
git merge --ff-only origin/main

# 3. Create a fresh branch off main (append HHMM if branch already exists today)
BRANCH="data-update-$(date +%Y-%m-%d)"
if git show-ref --verify --quiet "refs/heads/$BRANCH" \
   || git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
    BRANCH="$BRANCH-$(date +%H%M)"
fi
echo "-> Creating branch $BRANCH off main"
git checkout -b "$BRANCH"

# 4. Run the data loader (pre-flight: file must exist; abort with clear message on failure)
LOADER="$APP/load_new_v2.py"
if [[ ! -f "$LOADER" ]]; then
    echo "ERROR: loader not found at $LOADER" >&2
    exit 2
fi

echo "-> Running load_new_v2.py in $APP"
cd "$APP"
if ! python load_new_v2.py; then
    rc=$?
    echo "ERROR: load_new_v2.py exited $rc - aborting before any git operations." >&2
    cd "$REPO"
    git checkout main
    git branch -D "$BRANCH"
    exit $rc
fi

# 5. Back to repo root; bail early if the loader produced no changes
cd "$REPO"
if git diff --quiet && git diff --cached --quiet; then
    echo "No changes produced by load_new_v2.py - nothing to PR."
    git checkout main
    git branch -D "$BRANCH"
    exit 0
fi

# 6. Commit, push, and open PR
echo "-> Committing with message: $MSG"
git add .
git commit -m "$MSG"

echo "-> Pushing $BRANCH to origin"
git push -u origin "$BRANCH"

echo "-> Opening PR"
gh pr create --base main --head "$BRANCH" \
    --title "$MSG" \
    --body "Automated data refresh on $(date +%Y-%m-%d)."

echo ""
echo "Done."
