#!/usr/bin/env bash
# Opt-in, one agent job per invocation; never merges or deploys.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v codex >/dev/null || { echo 'Codex CLI missing' >&2; exit 1; }
command -v gh >/dev/null || { echo 'GitHub CLI missing' >&2; exit 1; }
command -v git >/dev/null || { echo 'git missing' >&2; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo 'Refusing run with uncommitted changes'; exit 1; }
[[ -n "$(git remote get-url origin)" ]] || { echo 'No origin remote'; exit 1; }
# Require authenticated gh and abort if any PR is pending manual review.
gh auth status >/dev/null
if [[ "$(gh pr list --state open --json number --jq 'length')" != "0" ]]; then
  echo 'Open PR exists; automation paused for human review.'
  exit 0
fi
if [[ "$(git branch --show-current)" != 'main' ]]; then
  git switch main
fi
git pull --ff-only origin main
python3 scripts/agent_build.py --execute --commit --push --draft-pr
